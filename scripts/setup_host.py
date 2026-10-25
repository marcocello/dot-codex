"""Reconcile a user-owned Ubuntu installation; reuse the harness installer."""
from __future__ import annotations

from datetime import datetime, timezone
import getpass
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

from install_runtime import DEFAULT_VERSION, systemd_quote
from setup_support import (Journal, SetupError, ask, atomic_write, command, download,
                           fingerprint, private_directory, save_json, verified_archive, yes)

WACLI_VERSION = "0.25.0"
WACLI_DIGESTS = {
    "linux_amd64": "9cbee5b7779b5670bd16dcf8feda2294a11e4acc801d9837ef9cd1a6619fc73c",
    "linux_arm64": "9282c3eabe4a445db057ac1e379b14648bbccb94d7b486f0b960ed8dde63ff82",
    "darwin_amd64": "b8a8919fbcd16e3c258bf9c98b851d7986c4efd4344db95dc1a6a06075054f50",
    "darwin_arm64": "ede9170ac661c8bef9c5fd449b29611301c0b63947a9ffad818dd9ec981a47a1",
}


def local_env(state):
    return {**os.environ, "PATH": str(Path.home() / ".local/bin") + os.pathsep + os.environ.get("PATH", ""),
            "TELEGRAM_TO_AGENTS_HOME": str(state / "telegram"),
            "WHATSAPP_AUTH_DIR": str(state / "baileys"), "WHATSAPP_AUTO_REPLY": "1"}


def persistent_tools(state):
    from install_state import Transaction, installation_lock
    target = private_directory(state / "runtime")
    path = Path.home() / ".local/share/dot-codex"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        if path.resolve() != target:
            raise SetupError("Existing dot-codex tool storage points elsewhere; preserve it and select its state location explicitly")
        return "Codex tool storage already persists beside the workspace"
    if path.exists():
        if not path.is_dir():
            raise SetupError("Existing Codex tool storage is not a directory")
        # Copy first; the transaction retains the original directory until the new link is committed.
        for source in path.rglob("*"):
            relative = source.relative_to(path)
            destination = target / relative
            if source.is_symlink():
                if destination.is_symlink() and os.readlink(destination) == os.readlink(source):
                    continue
                if destination.exists() or destination.is_symlink():
                    raise SetupError("Persistent tool storage differs; existing directories were preserved")
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.symlink_to(os.readlink(source))
            elif source.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
            elif source.is_file():
                if destination.exists() and destination.read_bytes() != source.read_bytes():
                    raise SetupError("Persistent tool storage differs; existing directories were preserved")
                destination.parent.mkdir(parents=True, exist_ok=True)
                if not destination.exists():
                    shutil.copy2(source, destination)
    with installation_lock(Path.home()) as install_state:
        transaction = Transaction(install_state)
        try:
            if path.exists():
                transaction.move_path(path, path.with_name("dot-codex.backup-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")))
            else:
                transaction.remember(path)
            path.symlink_to(target)
            transaction.commit()
        except BaseException:
            transaction.rollback()
            raise
    return "Codex packages and service helper persist beside the workspace; original storage retained when migrated"


def prerequisites(env):
    if platform.system() != "Linux" or not Path("/etc/os-release").is_file():
        raise SetupError("Host supervision requires Ubuntu with systemd. On macOS select --mode azure; use --component all for local development.")
    os_release = Path("/etc/os-release").read_text()
    if 'ID=ubuntu' not in os_release or 'VERSION_ID="24.04"' not in os_release:
        raise SetupError("Host setup supports Ubuntu 24.04; use the VM profile or explicit component setup elsewhere")
    if sys.version_info < (3, 11):
        raise SetupError("Python 3.11 or newer is required")
    if not all(shutil.which(name, path=env["PATH"]) for name in ("curl", "git", "systemctl", "loginctl", "bwrap")) or not Path("/usr/share/apparmor/extra-profiles/bwrap-userns-restrict").is_file() or command(
        [sys.executable, "-c", "import ensurepip,sqlite3; assert sqlite3.sqlite_version_info >= (3,42,0)"],
        env=env, capture=True, check=False).returncode:
        command(["sudo", "apt-get", "update"], env=env)
        command(["sudo", "apt-get", "install", "-y", "ca-certificates", "curl", "git", "python3-venv", "python3-pip", "sqlite3", "bubblewrap", "apparmor-profiles", "apparmor-utils"], env=env)
    configure_sandbox(env)
    if not shutil.which("node", path=env["PATH"]) or command(
        ["node", "-e", "process.exit(Number(process.versions.node.split('.')[0]) >= 24 ? 0 : 1)"],
        env=env, capture=True, check=False).returncode:
        install_node(env)
    command(["node", "--version"], env=env, capture=True)
    command(["npm", "--version"], env=env, capture=True)
    return "Ubuntu prerequisites and Node verified"


def configure_sandbox(env, root=Path("/")):
    probe = ["bwrap", "--unshare-user", "--ro-bind", "/", "/", "--", "/usr/bin/true"]
    if not command(probe, env=env, capture=True, check=False).returncode:
        return "Bubblewrap user namespace verified"
    source = root / "usr/share/apparmor/extra-profiles/bwrap-userns-restrict"
    target = root / "etc/apparmor.d/bwrap-userns-restrict"
    if not source.is_file():
        raise SetupError("Ubuntu bubblewrap AppArmor profile is missing; verify apparmor-profiles installation")
    if not target.exists():
        command(["sudo", "install", "-m", "0644", source, target], env=env)
    # Load the existing administrator profile when present. Never replace it or disable userns restrictions globally.
    command(["sudo", "/usr/sbin/apparmor_parser", "-r", target], env=env)
    if command(probe, env=env, capture=True, check=False).returncode:
        raise SetupError("Bubblewrap user namespaces remain blocked by host policy; inspect the existing AppArmor profile before retrying")
    return "Bubblewrap profile and user namespace verified"


def install_node(env):
    import tarfile
    version = "24.11.1"
    arch = {"x86_64": "x64", "aarch64": "arm64"}.get(platform.machine())
    if not arch:
        raise SetupError("Unsupported Node architecture")
    name = f"node-v{version}-linux-{arch}"
    base = f"https://nodejs.org/dist/v{version}/"
    managed = Path.home() / ".local/share/dot-codex/node"
    managed.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=managed.parent) as tmp:
        tmp = Path(tmp)
        archive, hashes = tmp / "node.tar.gz", tmp / "SHASUMS256.txt"
        download(base + name + ".tar.gz", archive)
        download(base + "SHASUMS256.txt", hashes)
        expected = next((line.split()[0] for line in hashes.read_text().splitlines() if line.split()[-1] == name + ".tar.gz"), None)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
            raise SetupError("Node release checksum mismatch")
        with tarfile.open(archive) as package:
            # Python's data filter excludes escaping links and special files.
            package.extractall(tmp, filter="data")
        release = managed / name
        if not release.exists():
            managed.mkdir(exist_ok=True)
            shutil.move(tmp / name, release)
        bin_dir = Path.home() / ".local/bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        for binary in ("node", "npm", "npx"):
            target = bin_dir / binary
            if target.exists() or target.is_symlink():
                if not target.is_symlink() or managed not in target.resolve().parents:
                    raise SetupError(f"Existing {target} is owned elsewhere; select a supported Node on PATH")
                target.unlink()
            target.symlink_to(release / "bin" / binary)


def persistent_checkout(root, selected, env):
    destination = Path(selected["destination"]).expanduser().absolute()
    if any(character in str(destination) for character in "\n\r\x00"):
        raise SetupError("Harness paths must not contain control characters")
    if destination.resolve() == root.resolve():
        return root
    if not destination.exists():
        command([sys.executable, root / "scripts/install.py", "copy", "--destination", destination, "--yes"], env=env)
    marker = destination / ".dot-codex-copy.json"
    if marker.is_file() and json.loads(marker.read_text()).get("source") == str(root):
        # Complete an interrupted supplement without overwriting independent edits.
        from setup_export import setup_files
        for name in setup_files(root):
            source, target = root / name, destination / name
            if source.is_symlink():
                raise SetupError(f"Review source symlink before copying: {name}")
            if source.is_file():
                if target.exists() and target.read_bytes() != source.read_bytes():
                    raise SetupError(f"Copied checkout contains independent changes: {name}")
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    shutil.copy2(source, target)
    if not all((destination / name).is_file() for name in ("secondbrain.sh", "skills.toml", "scripts/setup_platform.py")):
        raise SetupError(f"Destination is not a complete harness checkout: {destination}. Preserve it and choose another destination.")
    if command(["git", "-C", destination, "rev-parse", "--show-toplevel"], env=env, capture=True).stdout.strip() != str(destination.resolve()):
        raise SetupError("Destination must be its own Git checkout")
    return destination.resolve()


def installer(root, env, phase, *extra):
    command([sys.executable, root / "scripts/install.py", phase, "--yes", *extra], env=env)


def codex_install(root, state, env):
    binary = Path.home() / ".local/bin/codex"
    receipt = state / "codex-binary.json"
    current = json.loads(receipt.read_text()) if receipt.is_file() else {}
    if not binary.is_file() or current.get("sha256") != hashlib.sha256(binary.read_bytes()).hexdigest() or current.get("version") != DEFAULT_VERSION:
        installer(root, env, "cli")
    result = command([binary, "--version"], env=env, capture=True)
    if DEFAULT_VERSION not in result.stdout:
        raise SetupError("Installed Codex version does not match the harness release")
    save_json(receipt, {"version": DEFAULT_VERSION, "sha256": hashlib.sha256(binary.read_bytes()).hexdigest()})
    return f"Codex {DEFAULT_VERSION} verified"


def activate(root, env):
    active = Path.home() / ".codex"
    if not active.is_symlink() or active.resolve() != root:
        installer(root, env, "harness", "--mode", "merge")
    if not active.is_symlink() or active.resolve() != root:
        raise SetupError("Harness activation did not select the desired checkout")
    return "Persistent harness activated"


def applications(root, state, selected, env):
    venv = root / ".venv"
    if not venv.exists():
        command([sys.executable, "-m", "venv", venv], env=env)
    python = venv / "bin/python"
    if not python.is_file():
        raise SetupError("Existing .venv has no Python; inspect it before setup")
    manifests = [root / f"backend/{name}/pyproject.toml" for name in ("context", "telegram")]
    desired = fingerprint(manifests) + selected["memory"]["backend"]
    stamp = state / "applications.json"
    existing = json.loads(stamp.read_text()) if stamp.is_file() else {}
    healthy = all((venv / "bin" / name).is_file() for name in ("secondbrain-context", "telegram-to-agents"))
    healthy = healthy and not command([python, "-m", "pip", "check"], env=env, capture=True, check=False).returncode
    if existing.get("python") != desired or not healthy:
        package = str(root / "backend/context") + ("[pinecone]" if selected["memory"]["backend"] == "pinecone" else "")
        command([python, "-m", "pip", "install", "-e", package, "-e", root / "backend/telegram"], env=env)
    node_root = root / "backend/whatsapp"
    node_hash = fingerprint([node_root / "package-lock.json"])
    node_healthy = (node_root / "node_modules/.package-lock.json").is_file()
    if node_healthy:
        node_healthy = not command(["npm", "ls", "--depth=0", "--json"], cwd=node_root, env=env, capture=True, check=False).returncode
    if existing.get("node") != node_hash or not node_healthy:
        command(["npm", "ci"], cwd=node_root, env=env)
    command([venv / "bin/secondbrain-context", "--help"], env=env, capture=True)
    command([venv / "bin/telegram-to-agents", "--version"], env=env, capture=True)
    save_json(stamp, {"python": desired, "node": node_hash})
    return "backend/context, backend/telegram and backend/whatsapp installed"


def install_wacli(env):
    target = Path.home() / ".local/bin/wacli"
    if target.is_file():
        version = command([target, "--version"], env=env, capture=True, check=False)
        found = re.search(r"\b(\d+)\.(\d+)\.(\d+)\b", version.stdout)
        if not version.returncode and found and tuple(map(int, found.groups())) >= (0, 25, 0):
            return "Existing compatible wacli verified"
        if not target.is_symlink():
            backup = target.with_name("wacli.backup-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f"))
            shutil.copy2(target, backup)
            backup.chmod(0o600)
    system = platform.system().lower()
    arch = {"x86_64": "amd64", "aarch64": "arm64", "arm64": "arm64"}.get(platform.machine())
    key = f"{system}_{arch}"
    if key not in WACLI_DIGESTS:
        raise SetupError("No verified wacli release for this platform")
    name = f"wacli_{WACLI_VERSION}_{key}.tar.gz"
    verified_archive(f"https://github.com/openclaw/wacli/releases/download/v{WACLI_VERSION}/{name}",
                     WACLI_DIGESTS[key], target, "wacli")
    command([target, "--version"], env=env, capture=True)
    return f"Verified wacli {WACLI_VERSION} installed"


def context_command(root, config, env, *args, capture=False):
    return command([root / ".venv/bin/secondbrain-context", *args, "--config", config], env=env, capture=capture)


def context_config(root, state, selected, env, interactive):
    path = state / "context.toml"
    if path.exists():
        context_command(root, path, env, "doctor", capture=True)
        existing = tomllib.loads(path.read_text())
        if existing.get("search", {}).get("backend", "qdrant") != selected["memory"]["backend"]:
            raise SetupError("Saved context backend differs from setup choices; reconcile context.toml explicitly to preserve existing data")
        if not selected.get("_review_sources"):
            for choice, provider in (("outlook", "microsoft_graph"), ("whatsapp", "wacli")):
                if selected[choice] and not any(source["provider"] == provider and source["enabled"] for source in existing.get("sources", [])):
                    raise SetupError(f"Selected {choice} is disabled or absent in existing context.toml; configure its scope explicitly or deselect it with --reconfigure")
            return "Existing context scopes and enablement preserved"
        # Explicitly declining a provider disables its retrieval immediately, without erasing data.
        parts = re.split(r"(?m)(?=^\[\[sources\]\]\s*(?:#.*)?$)", path.read_text())
        for number, block in enumerate(parts):
            if not block.startswith("[[sources]]"):
                continue
            source = tomllib.loads(block)["sources"][0]
            choice = "outlook" if source["provider"] == "microsoft_graph" else "whatsapp"
            if not selected[choice] and source["enabled"]:
                changed, count = re.subn(r"(?m)^enabled\s*=\s*true([ \t]*(?:#.*)?)$", r"enabled = false\1", block, count=1)
                if count != 1:
                    raise SetupError("Disable this provider explicitly in context.toml; its custom formatting was preserved")
                parts[number] = changed
        changed = "".join(parts)
        if changed != path.read_text():
            atomic_write(path, changed)
        actual = tomllib.loads(changed).get("sources", [])
        for choice, provider in (("outlook", "microsoft_graph"), ("whatsapp", "wacli")):
            if not selected[choice] and any(source["provider"] == provider and source["enabled"] for source in actual):
                stop_managed("secondbrain-context.service", env)
                if choice == "whatsapp":
                    stop_managed("secondbrain-wacli.service", env)
                raise SetupError(f"Disable {choice} explicitly in context.toml; custom formatting was preserved and managed collection stopped")
            if selected[choice] and not any(source["provider"] == provider and source["enabled"] for source in actual):
                raise SetupError(f"Existing context configuration has no enabled {choice} source; add/select its explicit scope in context.toml")
        return "Existing context configuration preserved; edit it explicitly to change scopes"
    memory = selected["memory"]
    lines = ["schema = 1", f"workspace = {json.dumps(str(state / 'context'))}", "sync_every_seconds = 300", "", "[search]",
             f"backend = {json.dumps(memory['backend'])}"]
    if memory["backend"] == "pinecone":
        key_path = state / "pinecone.key"
        if not key_path.exists():
            key = os.environ.get("PINECONE_API_KEY", "")
            if not key and not interactive:
                raise SetupError("Pinecone needs PINECONE_API_KEY or the private pinecone.key file")
            key = key or getpass.getpass("Pinecone API key (saved owner-only outside the checkout): ").strip()
            if not key:
                raise SetupError("Pinecone API key is missing")
            atomic_write(key_path, key + "\n")
        lines.extend([f"pinecone_index = {json.dumps(memory['index'])}", f"pinecone_namespace = {json.dumps(memory['namespace'])}",
                      f"api_key_file = {json.dumps(str(key_path))}"])
    since = ask("Import messages received since (ISO timestamp)", selected.get("since", datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")), interactive=interactive)
    if selected["outlook"]:
        mail = dict(selected.get("mail", {}))
        for key, label, default in (("account", "One Outlook mailbox address", ""), ("client_id", "Microsoft public-client app UUID (Mail.Read/User.Read, device flow enabled)", ""),
                                    ("tenant_id", "Microsoft tenant UUID or domain", "organizations"), ("folders", "Mail folders, comma separated", "inbox,sentitems")):
            mail[key] = ask(label, mail.get(key, default), interactive=interactive)
        lines += ["", "[[sources]]", 'id = "outlook"', 'provider = "microsoft_graph"', "enabled = true", "[sources.scope]",
                  *[f"{key} = {json.dumps(mail[key])}" for key in ("account", "client_id", "tenant_id")],
                  f"folders = {json.dumps([x.strip() for x in mail['folders'].split(',') if x.strip()])}", f"since = {json.dumps(since)}"]
    if selected["whatsapp"]:
        store = private_directory(state / "wacli")
        base = [Path.home() / ".local/bin/wacli", "--store", store]
        auth = command([*base, "--read-only", "--json", "doctor"], env=env, capture=True, check=False)
        # Presence alone does not establish a paired session; --connect is checked later.
        if not (store / "session.db").is_file() or auth.returncode:
            if not interactive:
                raise SetupError("WhatsApp pairing is required; rerun interactively")
            command([*base, "auth"], env=env)
        chats = selected.get("chats", [])
        if not chats:
            command([*base, "--read-only", "chats", "list", "--limit", "50"], env=env)
            chats = [value.strip() for value in ask("Selected WhatsApp chat JIDs, comma separated", interactive=interactive).split(",") if value.strip()]
        lines += ["", "[[sources]]", 'id = "whatsapp"', 'provider = "wacli"', "enabled = true", "[sources.scope]",
                  f"store = {json.dumps(str(store))}", f"binary = {json.dumps(str(base[0]))}",
                  f"chats = {json.dumps(chats)}", f"since = {json.dumps(since)}"]
    candidate = state / ".context-candidate.toml"
    atomic_write(candidate, "\n".join(lines) + "\n")
    try:
        context_command(root, candidate, env, "doctor", capture=True)
        os.replace(candidate, path)
    finally:
        candidate.unlink(missing_ok=True)
    return "Explicit context scopes configured"


def login_and_collect(root, state, selected, env, interactive):
    unit = "secondbrain-context.service"
    path = Path.home() / ".config/systemd/user" / unit
    owned = path.is_file() and path.read_text().startswith("# Managed by dot-codex secondbrain setup\n")
    running = owned and not command(["systemctl", "--user", "is-active", "--quiet", unit], env=env, capture=True, check=False).returncode
    if running:
        command(["systemctl", "--user", "stop", unit], env=env)
    try:
        return collect_sources(root, state, selected, env, interactive)
    finally:
        if running:
            command(["systemctl", "--user", "start", unit], env=env)


def collect_sources(root, state, selected, env, interactive):
    config = state / "context.toml"
    data = tomllib.loads(config.read_text())
    for source in data.get("sources", []):
        if not source["enabled"]:
            continue
        if source["provider"] == "microsoft_graph":
            probe = command([root / ".venv/bin/secondbrain-context", "sync", "--source", source["id"], "--no-index", "--config", config],
                            env=env, capture=True, check=False)
            if probe.returncode:
                if not interactive:
                    raise SetupError("Microsoft authentication or collection failed; retry interactively to repair the selected mailbox connection")
                context_command(root, config, env, "login", "--source", source["id"])
        elif source["provider"] == "wacli":
            scope = source["scope"]
            unit = "secondbrain-wacli.service"
            running = not command(["systemctl", "--user", "is-active", "--quiet", unit], env=env, capture=True, check=False).returncode
            if running:
                command(["systemctl", "--user", "stop", unit], env=env)
            try:
                base = [scope.get("binary", "wacli"), "--store", scope["store"]]
                def connected():
                    result = command([*base, "--json", "doctor", "--connect"], env=env, capture=True, check=False)
                    if result.returncode:
                        return False
                    live = json.loads(result.stdout)
                    return live.get("data", live).get("connected") is True
                authenticated = connected()
                if not authenticated and interactive:
                    print("WhatsApp needs an authenticated connection; scan the pairing QR if requested.", flush=True)
                    command([*base, "auth"], env=env)
                    authenticated = connected()
                if not authenticated:
                    raise SetupError("WhatsApp has not confirmed login; repeat setup after repairing pairing")
            finally:
                if running:
                    command(["systemctl", "--user", "start", unit], env=env)
    for _ in range(100):
        result = json.loads(context_command(root, config, env, "sync", capture=True).stdout)
        if not any(source.get("more") for source in result.get("sources", [])):
            break
    else:
        raise SetupError("Initial collection is still pending after bounded work; repeat setup to resume")
    for _ in range(100):
        if not result.get("pending_index", 0):
            break
        result = json.loads(context_command(root, config, env, "index", "--limit", "1000", capture=True).stdout)
    else:
        raise SetupError("Index work remains pending; repeat setup to continue")
    return "Selected sources and initial index verified"


def pinecone(root, state, selected, env, interactive):
    args = [root / ".venv/bin/python", root / "scripts/setup_pinecone.py", "--config", state / "context.toml"]
    result = command(args, env=env, capture=True, check=False)
    if result.returncode == 3:
        cloud = ask("Pinecone cloud", selected["memory"].get("cloud", "aws"), interactive=interactive)
        region = ask("Pinecone region", selected["memory"].get("region", "eu-west-1"), interactive=interactive)
        print(f"Create Pinecone index {selected['memory']['index']} in {cloud}/{region}. This is a billable cloud resource.")
        if not interactive or not yes("Create this index with local embeddings and cosine search?", False, interactive=interactive):
            raise SetupError("Pinecone index creation requires explicit interactive approval")
        command([*args, "--create", "--cloud", cloud, "--region", region], env=env, capture=True)
    elif result.returncode:
        raise SetupError("Pinecone is unavailable or incompatible; verify credentials, index and model dimensions")
    return "Pinecone index readiness and embedding dimensions verified"


def register_context_mcp(root, state, env):
    codex = Path.home() / ".local/bin/codex"
    name = "secondbrain-context"
    desired = [str(root / ".venv/bin/secondbrain-context"), "mcp", "--config", str(state / "context.toml")]
    result = command([codex, "mcp", "get", name, "--json"], env=env, capture=True, check=False)
    if result.returncode:
        command([codex, "mcp", "add", name, "--", *desired], env=env, capture=True)
    else:
        current = json.loads(result.stdout)
        if current.get("enabled") is False:
            raise SetupError("Existing context MCP is explicitly disabled; review that preference before enabling retrieval")
        transport = current.get("transport", current)
        if transport.get("command") != desired[0] or transport.get("args", []) != desired[1:]:
            raise SetupError("Existing secondbrain-context MCP differs; preserve it and reconcile the named entry explicitly")
    return "Read-only context MCP registered"


def dependencies(root, state, env):
    installer(root, env, "dependencies")
    return "All declared inventory dependencies reconciled"


def service(name, args, cwd, env, *, extra=None, restart=False):
    path = Path.home() / ".config/systemd/user" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    environment = {key: env[key] for key in ("HOME", "PATH", "CODEX_HOME") if key in env}
    environment.update(extra or {})
    secret_file = Path(env["SECOND_BRAIN_STATE"]) / "tool-secrets.env" if env.get("SECOND_BRAIN_STATE") else None
    inputs_path = Path(env["SECOND_BRAIN_STATE"]) / "service-inputs.json" if env.get("SECOND_BRAIN_STATE") else None
    inputs = json.loads(inputs_path.read_text()) if inputs_path and inputs_path.exists() else {}
    signature = fingerprint([secret_file]) if secret_file and secret_file.exists() else ""
    restart = restart or inputs.get(name) != signature
    marker = "# Managed by dot-codex secondbrain setup\n"
    content = (marker + "[Unit]\nDescription=Secondbrain " + name + "\nAfter=network-online.target\n\n[Service]\nType=simple\n"
               + f"WorkingDirectory={systemd_quote(str(cwd))}\nUMask=0077\nRestart=on-failure\nRestartSec=10\n"
               + (f"EnvironmentFile={systemd_quote(str(secret_file))}\n" if secret_file and secret_file.exists() else "")
               + "".join(f"Environment={systemd_quote(key + '=' + value)}\n" for key, value in environment.items())
               + "ExecStart=" + " ".join(systemd_quote(str(arg), executable=True) for arg in args)
               + "\n\n[Install]\nWantedBy=default.target\n")
    changed = not path.exists() or path.read_text() != content
    if changed and path.exists() and not path.read_text().startswith(marker):
        raise SetupError(f"Existing {name} is owned by another setup; retain its configuration and stop/migrate that service explicitly before adopting it")
    if changed:
        atomic_write(path, content, 0o600)
        command(["systemctl", "--user", "daemon-reload"], env=env)
    command(["systemctl", "--user", "enable", "--now", name], env=env)
    if changed or restart:
        command(["systemctl", "--user", "restart", name], env=env)
    command(["systemctl", "--user", "is-enabled", "--quiet", name], env=env, capture=True)
    command(["systemctl", "--user", "is-active", "--quiet", name], env=env, capture=True)
    if inputs_path:
        inputs[name] = signature
        save_json(inputs_path, inputs)


def stop_managed(name, env):
    path = Path.home() / ".config/systemd/user" / name
    if path.is_file() and path.read_text().startswith("# Managed by dot-codex secondbrain setup\n"):
        command(["systemctl", "--user", "disable", "--now", name], env=env)


def supervise(root, state, selected, env):
    linger = command(["loginctl", "show-user", str(os.getuid()), "--property=Linger", "--value"], env=env, capture=True, check=False)
    if linger.returncode or linger.stdout.strip() != "yes":
        command(["sudo", "loginctl", "enable-linger", str(os.getuid())], env=env)
    if command(["loginctl", "show-user", str(os.getuid()), "--property=Linger", "--value"], env=env, capture=True).stdout.strip() != "yes":
        raise SetupError("User lingering remains disabled; services cannot survive logout")
    config = state / "context.toml"
    whatsapp = False
    for source in tomllib.loads(config.read_text()).get("sources", []):
        if source["enabled"] and source["provider"] == "wacli":
            whatsapp = True
            scope = source["scope"]
            service("secondbrain-wacli.service", [scope.get("binary", "wacli"), "--store", scope["store"], "sync", "--follow"], root, env)
    if not whatsapp:
        stop_managed("secondbrain-wacli.service", env)
    service("secondbrain-context.service", [root / ".venv/bin/secondbrain-context", "watch", "--config", config], root, env)
    return "Ingestion and selected WhatsApp sync enabled and active; reboot not exercised"


def gateways(root, state, selected, env, interactive):
    if selected["telegram"]:
        config = state / "telegram/config/config.json"
        if not config.exists():
            if not interactive:
                raise SetupError("Telegram onboarding is required; rerun interactively")
            token = getpass.getpass("Telegram bot token (owner-only storage): ").strip()
            users = [int(value.strip()) for value in ask("Allowed Telegram user IDs, comma separated").split(",") if value.strip()]
            project = Path(ask("Telegram project root", str(Path.home() / "projects"))).expanduser().resolve()
            if not token or not users or not all(value > 0 for value in users) or not project.is_dir():
                raise SetupError("Telegram needs a token, explicit user IDs and an existing project root")
            private_directory(config.parent)
            save_json(config, {"provider":"codex", "telegram_token":token, "allowed_user_ids":users, "project_root":str(project)})
        data = json.loads(config.read_text())
        if not data.get("telegram_token") or not data.get("allowed_user_ids") or not Path(data.get("project_root", "")).is_dir():
            raise SetupError("Telegram configuration needs token, allowed user IDs and an existing project root")
        command([root / ".venv/bin/python", root / "scripts/setup_telegram.py", config], env=env, capture=True)
        signature = hashlib.sha256(config.read_bytes()).hexdigest()
        receipt = state / "telegram/service-config.sha256"
        restart = not receipt.exists() or receipt.read_text().strip() != signature
        # Never place the token in command arguments or the unit definition.
        service("telegram-to-agents.service", [root / ".venv/bin/telegram-to-agents"], root, env,
                extra={"TELEGRAM_TO_AGENTS_HOME": str(state / "telegram")}, restart=restart)
        atomic_write(receipt, signature + "\n")
    else:
        stop_managed("telegram-to-agents.service", env)
    if selected["baileys"]:
        if not (state / "baileys/creds.json").is_file():
            if not interactive:
                raise SetupError("Baileys pairing is required; repeat setup interactively")
            pair_baileys(root, env)
        service("secondbrain-baileys.service", ["/usr/bin/env", "npm", "start"], root / "backend/whatsapp", env,
                extra={"WHATSAPP_AUTH_DIR": str(state / "baileys"), "WHATSAPP_AUTO_REPLY": "1", "WHATSAPP_PYTHON": str(root / ".venv/bin/python"),
                       "WHATSAPP_STATUS_FILE": str(state / "baileys-status.json")})
        wait_baileys(state / "baileys-status.json")
    else:
        stop_managed("secondbrain-baileys.service", env)
    return "Selected gateways enabled and active"


def wait_baileys(path):
    import time
    print("Waiting for the WhatsApp bot's authenticated connection...", flush=True)
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        try:
            status = json.loads(path.read_text())
            pid = status.get("pid")
            if status.get("connected") is True and type(pid) is int and pid > 1 and abs(time.time() - status.get("at", 0)) < 90:
                os.kill(pid, 0)
                return
        except (OSError, ValueError, TypeError):
            pass
        time.sleep(1)
    raise SetupError("WhatsApp bot has not confirmed a live connection; inspect secondbrain-baileys.service and relink its private session before retrying")


def pair_baileys(root, env):
    import selectors
    import time
    # Pair without sending replies. Start the selected reply service only after pairing succeeds.
    process = subprocess.Popen([shutil.which("node", path=env["PATH"]) or "node",
                                "--import", "tsx", "src/index.ts"], cwd=root / "backend/whatsapp",
                               env={**env, "WHATSAPP_AUTO_REPLY": "0"}, stdout=subprocess.PIPE, text=True)
    try:
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        deadline = time.monotonic() + 300
        while time.monotonic() < deadline and process.poll() is None:
            for key, _ in selector.select(timeout=1):
                line = key.fileobj.readline()
                try:
                    if json.loads(line).get("event") == "connected":
                        return
                except ValueError:
                    pass
        raise SetupError("Baileys pairing did not connect within five minutes; repeat setup")
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def remote_control(root, env, selected, interactive, *, login_only=False):
    binary = Path.home() / ".local/bin/codex"
    if command([binary, "login", "status"], env=env, capture=True, check=False).returncode:
        if not interactive:
            raise SetupError("Codex device login is required; rerun interactively")
        installer(root, env, "login")
    if login_only:
        return "Codex login verified"
    old = command(["systemctl", "cat", "codex-remote-control-bootstrap.service"], env=env, capture=True, check=False)
    if not old.returncode:
        expected = f"ExecStart={Path.home()}/.codex/packages/standalone/current/codex app-server daemon bootstrap --remote-control"
        if "Description=Bootstrap the managed Codex Remote Control daemon after boot" not in old.stdout or expected not in old.stdout:
            if selected["remote_control"]:
                raise SetupError("Existing root Remote Control bootstrap has another owner; migrate it explicitly before adopting user supervision")
        else:
            command(["sudo", "systemctl", "disable", "--now", "codex-remote-control-health.timer", "codex-remote-control-bootstrap.service"], env=env)
    if selected["remote_control"]:
        from install_runtime import require_connection
        healthy = all(not command(["systemctl", "--user", "is-active", "--quiet", name], env=env, capture=True, check=False).returncode
                      for name in ("codex-remote-control.service", "codex-remote-control-health.timer"))
        unit = Path.home() / ".config/systemd/user/codex-remote-control.service"
        secret_file = Path(env["SECOND_BRAIN_STATE"]) / "tool-secrets.env"
        inputs_path = Path(env["SECOND_BRAIN_STATE"]) / "service-inputs.json"
        inputs = json.loads(inputs_path.read_text()) if inputs_path.exists() else {}
        signature = fingerprint([secret_file]) if secret_file.exists() else ""
        environment_changed = inputs.get("codex-remote-control.service") != signature
        healthy = healthy and not environment_changed
        healthy = healthy and unit.is_file() and systemd_quote("PATH=" + env["PATH"]) in unit.read_text()
        if secret_file.exists():
            healthy = healthy and unit.is_file() and f"EnvironmentFile={systemd_quote(str(secret_file))}" in unit.read_text()
        if healthy:
            try:
                require_connection(binary, env)
            except Exception:
                healthy = False
        if not healthy:
            secret_file = Path(env["SECOND_BRAIN_STATE"]) / "tool-secrets.env"
            extra = ["--environment-file", str(secret_file)] if secret_file.exists() else []
            installer(root, env, "service", "--enable-linger", "--service-manager", "systemd", *extra)
        if environment_changed and secret_file.exists():
            print("Applying the tool environment to the managed Codex daemon.", flush=True)
            command([binary, "app-server", "daemon", "restart"], env=env, capture=True)
            require_connection(binary, env)
        inputs["codex-remote-control.service"] = signature
        save_json(inputs_path, inputs)
    else:
        unit = Path.home() / ".config/systemd/user/codex-remote-control.service"
        if unit.is_file() and str(Path.home() / ".local/share/dot-codex/service-health.py") in unit.read_text():
            command(["systemctl", "--user", "disable", "--now", "codex-remote-control.service", "codex-remote-control-health.timer"], env=env)
    return "Codex login and selected Remote Control verified"


def setup(root, state, selected, *, interactive):
    env = local_env(state)
    if not interactive:
        env["SECOND_BRAIN_NO_PROMPT"] = "1"
    journal = Journal(state)
    if not journal.phase("prerequisites", lambda: prerequisites(env)):
        journal.finish()
        return 2
    if not journal.phase("persistent-tools", lambda: persistent_tools(state)):
        journal.finish()
        return 2
    checkout = []
    if not journal.phase("checkout", lambda: checkout.append(persistent_checkout(root, selected, env)) or "Persistent checkout verified"):
        journal.finish()
        return 2
    root = checkout[0]
    env["CODEX_HOME"] = str(root)
    env["SECOND_BRAIN_STATE"] = str(state)
    env["PATH"] = str(root / ".venv/bin") + os.pathsep + env["PATH"]
    from setup_tools import load_secrets, reconcile
    env.update({key:value for key,value in load_secrets(state).items() if key not in env})
    journal.phase("codex", lambda: codex_install(root, state, env))
    journal.phase("harness", lambda: activate(root, env), requires=("codex",))
    journal.phase("applications", lambda: applications(root, state, selected, env))
    journal.phase("codex-login", lambda: remote_control(root, env, selected, interactive, login_only=True), requires=("harness",))
    journal.phase("dependencies", lambda: dependencies(root, state, env), requires=("harness", "codex-login"))
    before_tools = dict(env)
    journal.phase("tool-connections", lambda: reconcile(root, state, env, interactive, review=selected.get("_review_sources", False)), requires=("harness", "applications"))
    if env != before_tools and journal.data["phases"].get("dependencies", {}).get("status") == "incomplete":
        journal.phase("dependencies", lambda: dependencies(root, state, env), requires=("harness", "codex-login"))
    journal.phase("codex-connection", lambda: remote_control(root, env, selected, interactive), requires=("harness", "codex-login"))
    if selected["whatsapp"]:
        journal.phase("wacli", lambda: install_wacli(env))
    journal.phase("context-configuration", lambda: context_config(root, state, selected, env, interactive),
                  requires=("applications", *(("wacli",) if selected["whatsapp"] else ())))
    journal.phase("context-mcp", lambda: register_context_mcp(root, state, env), requires=("harness", "context-configuration"))
    if selected["memory"]["backend"] == "pinecone":
        journal.phase("pinecone", lambda: pinecone(root, state, selected, env, interactive), requires=("context-configuration",))
    journal.phase("context-collection", lambda: login_and_collect(root, state, selected, env, interactive),
                  requires=("context-configuration", *(("pinecone",) if selected["memory"]["backend"] == "pinecone" else ())))
    journal.phase("supervision", lambda: supervise(root, state, selected, env), requires=("context-configuration",))
    journal.phase("gateways", lambda: gateways(root, state, selected, env, interactive), requires=("applications", "codex-connection"))
    failed = journal.finish()
    print(f"\n{'Setup incomplete; repeat the same command to resume' if failed else 'Setup verified'}")
    print(f"Context configuration: {state / 'context.toml'}")
    print("Service definitions were checked; actual reboot survival requires a VM reboot.")
    return 2 if failed else 0
