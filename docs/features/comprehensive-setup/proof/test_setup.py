"""Operator journeys with disposable state; provider and OS edges are fixtures."""
import os
from pathlib import Path
import subprocess
import sys
import json
import importlib.util
import shutil

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def test_public_plans_are_read_only(tmp_path):
    env = {**os.environ, "HOME": str(tmp_path)}
    for mode in ("host", "azure"):
        result = subprocess.run([str(ROOT / "secondbrain.sh"), "setup", "--plan", "--mode", mode],
                                env=env, text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
        assert "backend/context" in result.stdout
        assert "backend/telegram" in result.stdout
        assert "Qdrant" in result.stdout
        assert "Pinecone" in result.stdout
        assert "verification" in result.stdout.lower()
    assert list(tmp_path.iterdir()) == []


def test_dependency_interface_remains_explicit():
    result = subprocess.run([str(ROOT / "secondbrain.sh"), "setup", "--component", "all", "--plan"],
                            text=True, capture_output=True)
    assert result.returncode == 0
    assert "npm ci" in result.stdout


def test_noninteractive_missing_choices_fails_without_mutation(tmp_path):
    result = subprocess.run([str(ROOT / "secondbrain.sh"), "setup", "--non-interactive", "--state", str(tmp_path / "state")],
                            env={**os.environ, "HOME": str(tmp_path)}, text=True, capture_output=True)
    assert result.returncode != 0
    assert "config" in (result.stdout + result.stderr).lower()
    assert not (tmp_path / "state").exists()


def test_host_reconcile_real_installer_and_context(tmp_path, monkeypatch):
    """Real installer, inventory, context, units and receipts; OS/account executables are fixtures."""
    import setup_host as host
    fixture = module("guided_fixture", ROOT / "docs/features/guided-installer/tests/test_guided_install.py")
    fixture.FAKE_CODEX = fixture.FAKE_CODEX.replace('elif args == ["login", "status"]:', '''elif args[:2] == ["mcp", "get"]:
    marker = Path(os.environ["HOME"], ".mcp-fixture.json")
    if not marker.exists(): sys.exit(1)
    print(marker.read_text())
elif args[:2] == ["mcp", "add"]:
    command = args[args.index("--")+1:]
    Path(os.environ["HOME"], ".mcp-fixture.json").write_text(json.dumps({"transport":{"command":command[0],"args":command[1:]}}))
    print("{}")
elif args == ["login", "status"]:''')
    run = fixture.GuidedInstallJourneys()
    run.setUp()
    try:
        home, root = run.home, run.repo
        for key, value in run.env.items():
            monkeypatch.setenv(key, value)
        monkeypatch.delenv("CODEX_HOME", raising=False)
        monkeypatch.setenv("CONTEXT7_API_KEY", "MCP-TOKEN-FIXTURE")
        state = home / "projects/.secondbrain"
        state.mkdir(parents=True)
        context_fixture = module("context_fixture", ROOT / "backend/context/tests/test_journey.py")
        archive_root = tmp_path / "archive"
        archive_root.mkdir()
        config, archive, journal = context_fixture.archive.__wrapped__(archive_root)
        binary = archive_root / "wacli-fixture"
        binary.write_text(binary.read_text().replace("args = sys.argv[1:]", '''args = sys.argv[1:]
if args == ["--version"]:
    print("wacli 0.25.0")
    sys.exit(0)
if "doctor" in args:
    print(json.dumps({"success": True, "data": {"connected": True, "authenticated": True}}))
    sys.exit(0)'''))
        shutil.copy2(config, state / "context.toml")
        telegram_config = state / "telegram/config/config.json"
        telegram_config.parent.mkdir(parents=True)
        telegram_config.write_text(json.dumps({"provider":"codex", "telegram_token":"123456789:TELEGRAM-TOKEN-FIXTURE", "allowed_user_ids":[12345], "project_root":str(root)}))
        telegram_config.chmod(0o600)
        local = home / ".local/bin"
        local.mkdir(parents=True)
        shutil.copy2(binary, local / "wacli")
        (home / ".signed-in").touch()
        for name in ("context", "telegram"):
            path = root / "backend" / name
            path.mkdir(parents=True)
            shutil.copy2(ROOT / "backend" / name / "pyproject.toml", path / "pyproject.toml")
        for name in ("install.py", "install_runtime.py"):
            shutil.copy2(ROOT / "scripts" / name, root / "scripts" / name)
        node_root = root / "backend/whatsapp"
        node_root.mkdir()
        shutil.copy2(ROOT / "backend/whatsapp/package-lock.json", node_root / "package-lock.json")
        (root / ".venv/bin").mkdir(parents=True)
        (root / ".venv/bin/python").symlink_to(ROOT / ".venv/bin/python")
        provider = local / "systemctl"
        provider.write_text(f'#!{sys.executable}\n' + '''import json, os, pathlib, sys
args = sys.argv[1:]
path = pathlib.Path(os.environ["HOME"], ".units.json")
units = json.loads(path.read_text()) if path.exists() else []
if args[:1] == ["cat"]: sys.exit(1)
if "is-active" in args or "is-enabled" in args: sys.exit(0 if args[-1] in units else 3)
if "enable" in args or "start" in args:
    units += [x for x in args if x.endswith((".service", ".timer"))]
    path.write_text(json.dumps(sorted(set(units))))
''')
        provider.chmod(0o700)
        loginctl = local / "loginctl"
        loginctl.write_text('#!/bin/sh\nprintf "yes\\n"\n')
        loginctl.chmod(0o700)
        original_command = host.command
        installs = []
        def commands(args, **kwargs):
            words = list(map(str, args))
            if words[1:4] == ["-m", "pip", "install"]:
                installs.append("python")
                for name, module_name in (("secondbrain-context", "secondbrain_context"), ("telegram-to-agents", "telegram_to_agents")):
                    entry = root / ".venv/bin" / name
                    entry.write_text(f'#!{sys.executable}\nfrom {module_name}.__main__ import main\nmain()\n' if name != "secondbrain-context" else f'#!{sys.executable}\nfrom secondbrain_context.cli import main\nraise SystemExit(main())\n')
                    entry.chmod(0o700)
                return subprocess.CompletedProcess(words, 0, "", "")
            if words == ["npm", "ci"]:
                installs.append("node")
                (node_root / "node_modules").mkdir(exist_ok=True)
                (node_root / "node_modules/.package-lock.json").write_text("{}")
                return subprocess.CompletedProcess(words, 0, "", "")
            if words[:2] == ["npm", "ls"]:
                return subprocess.CompletedProcess(words, 0, "{}", "")
            if len(words) > 1 and words[1].endswith("/setup_mcp.py"):
                return subprocess.CompletedProcess(words, 0, json.dumps({"ok":True,"tools":2,"boundary":"MCP provider fixture"}), "")
            if len(words) > 1 and words[1].endswith("/setup_telegram.py"):
                import httpx
                from unittest.mock import patch
                probe = module("telegram_probe_fixture", ROOT / "scripts/setup_telegram.py")
                requests = []
                def api(request):
                    requests.append(request)
                    assert request.method == "GET"
                    assert request.url.host == "api.telegram.org"
                    assert request.url.path.endswith("/getMe")
                    return httpx.Response(200, json={"ok":True, "result":{"id":123456789,"is_bot":True}})
                original_client = httpx.Client
                def fixture_client(*args, **kwargs):
                    return original_client(*args, transport=httpx.MockTransport(api), **kwargs)
                with patch.object(sys, "argv", [words[1], words[2]]), patch.object(httpx, "Client", fixture_client):
                    probe.main()
                assert len(requests) == 1
                return subprocess.CompletedProcess(words, 0, "Telegram provider identity verified", "")
            return original_command(args, **kwargs)
        monkeypatch.setattr(host, "command", commands)
        import setup_tools
        monkeypatch.setattr(setup_tools, "command", commands)
        monkeypatch.setattr(host, "prerequisites", lambda env: "Ubuntu package-manager boundary fixture")
        original_installer = host.installer
        package_args = run.package(host.DEFAULT_VERSION)
        def install(root, env, phase, *extra):
            if phase == "cli":
                extra = (*extra, *package_args[3:7])
            return original_installer(root, env, phase, *extra)
        monkeypatch.setattr(host, "installer", install)
        selected = dict(destination=str(root), memory={"backend": "qdrant"}, telegram=True, baileys=False,
                        remote_control=True, outlook=False, whatsapp=True)
        assert host.setup(root, state, selected, interactive=False) == 0
        assert (home / ".codex").resolve() == root
        assert (home / ".local/share/dot-codex").resolve() == state / "runtime"
        assert (root / "packages/standalone").resolve() == state / "runtime/cli"
        import sqlite3
        with sqlite3.connect(archive_root / "memory/context.sqlite3") as db:
            assert db.execute("SELECT count(*) FROM documents").fetchone()[0] == 2
        units = home / ".config/systemd/user"
        assert str(state / "context.toml") in (units / "secondbrain-context.service").read_text()
        saved = (state / "context.toml").read_bytes()
        assert host.setup(root, state, selected, interactive=False) == 0
        assert installs == ["python", "node"]
        assert (state / "context.toml").read_bytes() == saved
        (root / ".venv/bin/secondbrain-context").unlink()
        assert host.setup(root, state, selected, interactive=False) == 0
        assert installs == ["python", "node", "python"]
        journal.write_text(json.dumps({"changes": [], "fail": True}))
        assert host.setup(root, state, selected, interactive=False) != 0
        receipt = json.loads((state / "setup-status.json").read_text())
        assert receipt["phases"]["context-collection"]["status"] == "incomplete"
        assert "PAIRING-SECRET" not in (state / "setup-status.json").read_text()
        assert "MCP-TOKEN-FIXTURE" not in (units / "codex-remote-control.service").read_text()
        assert "TELEGRAM-TOKEN-FIXTURE" not in (units / "telegram-to-agents.service").read_text()
        assert "MCP-TOKEN-FIXTURE" not in (state / "setup-status.json").read_text()
        assert (state / "setup-status.json").stat().st_mode & 0o077 == 0
    finally:
        run.doCleanups()


def test_protected_azure_payload_never_contains_keys_in_argv(tmp_path):
    from setup_azure import managed_run_command
    seen = []
    secret = "VPN-PRIVATE-KEY-FIXTURE"
    def runner(args, **kwargs):
        seen.append(list(map(str, args)))
        if "put" in args:
            body = Path(args[args.index("--body") + 1][1:])
            assert body.stat().st_mode & 0o077 == 0
            data = json.loads(body.read_text())
            assert data["properties"]["protectedParameters"][0]["value"] == secret
            assert secret not in data["properties"]["source"]["script"]
        out = "austriaeast" if "show" in args else json.dumps({"properties":{"instanceView":{"executionState":"Succeeded","exitCode":0}}})
        return subprocess.CompletedProcess(args, 0, out, "")
    managed_run_command({"subscription_id":"00000000-0000-0000-0000-000000000001", "resource_group_name":"fixture", "vm_name":"fixture"},
                        "echo ready", {"SERVER_BUNDLE":secret}, runner=runner)
    assert all(secret not in " ".join(args) for args in seen)
    assert any("delete" in args for args in seen)


def test_fresh_vpn_bootstrap_crypto_and_restored_trust_guard(tmp_path):
    """Real embedded generator/configurator and OpenSSL; ARM and systemctl are external fixtures."""
    home, fake, vmroot = (tmp_path / name for name in ("home", "bin", "vm"))
    for directory in (home, fake, vmroot):
        directory.mkdir()
    mount = "/home/azureadmin/projects"
    (vmroot / mount.lstrip("/")).mkdir(parents=True)
    private_key, known = home / "ssh-key", home / "known_hosts"
    private_key.write_text("SSH-KEY-FIXTURE")
    known.write_text("HOST-KEY-FIXTURE")
    connection = {"subscription_id":"00000000-0000-0000-0000-000000000001", "resource_group_name":"fixture", "vm_name":"fixture",
        "ssh_fqdn":"fixture.example.invalid", "ssh_username":"azureadmin", "workspace_mount_path":mount,
        "mac_private_key_path":str(private_key), "ssh_host_config_path":str(home / "ssh.conf"), "ssh_known_hosts_path":str(known),
        "openvpn_port":1194, "openvpn_network":"10.250.0.0", "openvpn_netmask":"255.255.255.0", "openvpn_server_address":"10.250.0.1",
        "openvpn_ssh_alias":"fixture-vpn", "openvpn_local_root_path":str(home / "vpn"), "openvpn_client_profile_path":str(home / "vpn/codex-on-vm.ovpn")}
    value = tmp_path / "connection.json"
    value.write_text(json.dumps(connection))
    scripts = {
        "uname": '#!/bin/sh\nprintf "Darwin\\n"\n',
        "terraform": '#!/bin/sh\ncat "$VPN_CONNECTION"\n',
        "systemctl": '#!/bin/sh\nexit 0\n',
        "openvpn": '#!/bin/sh\nexit 0\n',
        "ssh": '#!/bin/sh\necho called >>"$VPN_SSH_LOG"\nexit 1\n',
        "sha256sum": f'#!{sys.executable}\n' + '''import hashlib, pathlib, sys
line = sys.stdin.read().strip()
expected, filename = line.split(None, 1)
sys.exit(0 if hashlib.sha256(pathlib.Path(filename).read_bytes()).hexdigest() == expected else 1)
''',
        "az": f'#!{sys.executable}\n' + '''import base64, json, os, pathlib, subprocess, sys
args = sys.argv[1:]
root = pathlib.Path(os.environ["VPN_FIXTURE"])
if args[:2] == ["vm", "show"]:
    print("austriaeast")
elif "put" in args:
    body = json.loads(pathlib.Path(args[args.index("--body")+1][1:]).read_text())
    props = body["properties"]
    assert "PRIVATE KEY" not in props["source"]["script"]
    env = dict(os.environ)
    env.update({item["name"]:item["value"] for item in props["protectedParameters"]})
    result = subprocess.run(["bash", "-c", props["source"]["script"]], env=env, text=True, capture_output=True)
    (root / "arm-status.json").write_text(json.dumps({"properties":{"instanceView":{"executionState":"Succeeded" if result.returncode == 0 else "Failed", "exitCode":result.returncode}}}))
    if result.returncode:
        (root / "arm-error.txt").write_text(result.stderr)
elif "get" in args:
    print((root / "arm-status.json").read_text())
'''}
    for name, content in scripts.items():
        executable = fake / name
        executable.write_text(content)
        executable.chmod(0o700)
    env = {**os.environ, "HOME":str(home), "PATH":str(fake) + os.pathsep + os.environ["PATH"],
           "CODEX_VM_TEST_MODE":"1", "CODEX_VM_ROOT":str(vmroot), "VPN_CONNECTION":str(value), "VPN_FIXTURE":str(tmp_path),
           "VPN_SSH_LOG":str(tmp_path / "ssh.log"), "SECOND_BRAIN_SETUP_SCRIPTS":str(ROOT / "scripts")}
    helpers = tmp_path / "helpers"
    subprocess.run([ROOT / "scripts/codex-vm.sh", "__extract-helpers", helpers], env=env, check=True, capture_output=True)
    command = [helpers / "scripts/openvpn-setup.sh", "--bootstrap"]
    for _ in range(2):
        result = subprocess.run(command, env=env, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr + ((tmp_path / "arm-error.txt").read_text() if (tmp_path / "arm-error.txt").exists() else "")
    assert not (tmp_path / "ssh.log").exists()
    server = vmroot / mount.lstrip("/") / ".codex-on-vm/openvpn/server"
    assert (server / "server.key").stat().st_mode & 0o077 == 0
    assert not (server / "ca.key").exists()
    assert not (server / "client.key").exists()
    before = (home / "vpn/ca.crt").read_bytes()
    assert before == (server / "ca.crt").read_bytes()
    # A restored disk with different trust must not be silently rotated.
    (server / "ca.crt").write_text("DIFFERENT-CA-FIXTURE")
    result = subprocess.run(command, env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert (home / "vpn/ca.crt").read_bytes() == before
    assert (server / "ca.crt").read_text() == "DIFFERENT-CA-FIXTURE"


def test_backend_identity_is_checked_before_cloud_mutation(tmp_path, monkeypatch):
    import setup_azure
    import pytest
    tf = tmp_path / "deployments/prod/tf"
    tf.mkdir(parents=True)
    (tf / "backend.hcl").write_text('resource_group_name = "another-deployment"\n')
    monkeypatch.setattr(setup_azure, "command", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("Cloud command before identity validation")))
    cloud = dict(subscription="00000000-0000-0000-0000-000000000001", owner="fixture", resource_group="fixture", storage_account="fixturestate", container="tfstate", key="fixture.tfstate", location="austriaeast")
    with pytest.raises(Exception, match="differs"):
        setup_azure.cloud_state(tmp_path, {"azure":cloud}, False)


def test_azure_plan_requires_explicit_approval(tmp_path, monkeypatch):
    import setup_azure
    import pytest
    calls = []
    def runner(args, **kwargs):
        calls.append(list(map(str, args)))
        return subprocess.CompletedProcess(args, 2 if "plan" in args else 0)
    monkeypatch.setattr(setup_azure, "command", runner)
    with pytest.raises(Exception, match="approval"):
        setup_azure.provision(tmp_path, tmp_path, False)
    assert not any("apply" in args for args in calls)
    monkeypatch.setattr(setup_azure, "yes", lambda *args, **kwargs: True)
    setup_azure.provision(tmp_path, tmp_path, True)
    assert any("apply" in args for args in calls)


def test_real_mcp_onboarding_probe(tmp_path):
    config = tmp_path / "context.toml"
    config.write_text('schema = 1\nworkspace = ' + json.dumps(str(tmp_path / "context")) + '\n')
    server = tmp_path / "server.json"
    server.write_text(json.dumps({"command":str(ROOT / ".venv/bin/secondbrain-context"), "args":["mcp", "--config", str(config)]}))
    result = subprocess.run([ROOT / ".venv/bin/python", ROOT / "scripts/setup_mcp.py", server], text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["tools"] == 2


def test_real_codex_mcp_registration_in_disposable_home(tmp_path, monkeypatch):
    import pytest
    import setup_host
    native = shutil.which("codex")
    if not native:
        pytest.skip("Native Codex is unavailable; fixture journey still covers the CLI edge")
    home = tmp_path / "home"
    (home / ".local/bin").mkdir(parents=True)
    (home / ".local/bin/codex").symlink_to(native)
    (home / ".codex").mkdir()
    monkeypatch.setenv("HOME", str(home))
    env = {**os.environ, "HOME":str(home), "CODEX_HOME":str(home / ".codex")}
    state = home / "projects/.secondbrain"
    for _ in range(2):
        setup_host.register_context_mcp(ROOT, state, env)
    result = subprocess.run([native, "mcp", "get", "secondbrain-context", "--json"], env=env, text=True, capture_output=True, check=True)
    transport = json.loads(result.stdout)["transport"]
    assert transport["command"] == str(ROOT / ".venv/bin/secondbrain-context")
    assert transport["args"] == ["mcp", "--config", str(state / "context.toml")]


def test_imported_root_supervisor_is_adopted_without_guessing_ownership(tmp_path, monkeypatch):
    import setup_host
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    calls = []
    def runner(args, **kwargs):
        calls.append(list(map(str, args)))
        output = ""
        if args[:2] == ["systemctl", "cat"]:
            output = "Description=Bootstrap the managed Codex Remote Control daemon after boot\n" + f"ExecStart={home}/.codex/packages/standalone/current/codex app-server daemon bootstrap --remote-control\n"
        return subprocess.CompletedProcess(args, 0, output, "")
    monkeypatch.setattr(setup_host, "command", runner)
    setup_host.remote_control(ROOT, {"SECOND_BRAIN_STATE":str(home)}, {"remote_control":False}, False)
    assert any(args[:4] == ["sudo", "systemctl", "disable", "--now"] for args in calls)


def test_direct_vm_sandbox_preserves_existing_admin_policy(tmp_path, monkeypatch):
    import setup_host
    calls, probes = [], []
    source = tmp_path / "usr/share/apparmor/extra-profiles/bwrap-userns-restrict"
    source.parent.mkdir(parents=True)
    source.write_text("DISTRO-PROFILE-FIXTURE")
    target = tmp_path / "etc/apparmor.d/bwrap-userns-restrict"
    target.parent.mkdir(parents=True)
    target.write_text("ADMIN-PROFILE-FIXTURE")
    def runner(args, **kwargs):
        calls.append(list(map(str, args)))
        if args[0] == "bwrap":
            probes.append(True)
            return subprocess.CompletedProcess(args, 1 if len(probes) == 1 else 0, "", "")
        return subprocess.CompletedProcess(args, 0, "", "")
    monkeypatch.setattr(setup_host, "command", runner)
    setup_host.configure_sandbox({}, tmp_path)
    assert target.read_text() == "ADMIN-PROFILE-FIXTURE"
    assert not any("install" in args for args in calls)
    assert any("/usr/sbin/apparmor_parser" in args for args in calls)


def test_current_source_export_preserves_private_and_independent_files(tmp_path):
    from setup_export import APPLY, bundle
    source = tmp_path / "source"
    source.mkdir()
    subprocess.run(["git", "init", "-q", source], check=True)
    (source / "tracked.py").write_text("old = True\n")
    (source / "removed.py").write_text("removed = True\n")
    (source / ".gitignore").write_text("*.key\n")
    subprocess.run(["git", "-C", source, "add", "."], check=True)
    subprocess.run(["git", "-C", source, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture"], check=True)
    (source / "tracked.py").write_text("current = True\n")
    (source / "removed.py").unlink()
    (source / "private.key").write_text("PRIVATE-FIXTURE")
    (source / "untracked-note.md").write_text("PRIVATE-NOTE")
    (source / "scripts").mkdir()
    (source / "scripts/setup_platform.py").write_text("pass\n")
    outgoing = tmp_path / "out"
    outgoing.mkdir()
    archive = bundle(source, outgoing)
    destination, receipt = tmp_path / "remote", tmp_path / "state/export.json"
    args = [sys.executable, "-c", APPLY, str(archive), str(destination), "https://github.com/example/fixture.git", str(receipt)]
    subprocess.run(args, check=True)
    assert (destination / "tracked.py").read_text() == "current = True\n"
    assert (destination / "scripts/setup_platform.py").is_file()
    assert not (destination / "removed.py").exists()
    assert not (destination / "private.key").exists()
    assert not (destination / "untracked-note.md").exists()
    subprocess.run(args, check=True)
    import fcntl
    with (receipt.parent / "setup.lock").open("r+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        blocked = subprocess.run(args, capture_output=True, text=True)
        assert blocked.returncode != 0
        assert "Remote setup is active" in blocked.stderr
        assert (destination / "tracked.py").read_text() == "current = True\n"
    (destination / "tracked.py").write_text("independent = True\n")
    assert subprocess.run(args, capture_output=True).returncode != 0
    assert "independent" in (destination / "tracked.py").read_text()


def test_pinecone_real_sdk_embeddings_scope_and_erasure(tmp_path, monkeypatch):
    """Only HTTP is replaced; run the installed SDK and real local embedding model."""
    import httpx
    import pytest
    from dataclasses import replace
    from secondbrain_context.config import Configuration, Source, ContextError
    from secondbrain_context.index import Embeddings, VectorIndex
    from secondbrain_context.store import Store
    from secondbrain_context.service import search
    model = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    source = Source("whatsapp", "wacli", True, {"chats":["15550000001@s.whatsapp.net"],"store":"fixture","since":"2026-10-24T00:00:00Z"})
    config = Configuration(tmp_path / "context.toml", tmp_path / "context", model, 300, (source,),
                           "pinecone", "fixture", "secondbrain-fixture", "")
    # Cache/initialize before replacing SDK HTTP transport. This is actual ONNX inference.
    embedder = Embeddings(config)
    assert len(embedder.query("dimension")) == 384
    monkeypatch.setenv("PINECONE_API_KEY", "fixture-key")
    points, requests = {}, []
    def matches(metadata, clause):
        if "$and" in clause:
            return all(matches(metadata, item) for item in clause["$and"])
        return all(metadata.get(key) in condition["$in"] if "$in" in condition else metadata.get(key) == condition["$eq"] for key, condition in clause.items())
    def provider(request):
        path = request.url.path
        data = json.loads(request.content) if request.content else {}
        requests.append((path, data))
        if path == "/indexes/fixture":
            return httpx.Response(200, json={"name":"fixture", "status":{"ready":True,"state":"Ready"},
                "host":"fixture.svc.pinecone.io", "schema":{"fields":{"_values":{"type":"dense_vector","dimension":384,"metric":"cosine"}}},
                "deployment":{"deployment_type":"managed","cloud":"aws","region":"eu-west-1"}, "deletion_protection":"disabled"})
        assert data.get("namespace") == config.pinecone_namespace
        if path == "/vectors/delete":
            for key in list(points):
                if matches(points[key]["metadata"], data["filter"]):
                    del points[key]
            return httpx.Response(200, json={})
        if path == "/vectors/upsert":
            points.update({point["id"]:point for point in data["vectors"]})
            return httpx.Response(200, json={"upsertedCount":len(data["vectors"])})
        if path == "/query":
            selected = [point for point in points.values() if matches(point["metadata"], data["filter"])]
            selected.sort(key=lambda point: sum(x*y for x,y in zip(data["vector"], point["values"])), reverse=True)
            return httpx.Response(200, json={"matches":[{"id":p["id"], "score":0.9, "metadata":p["metadata"]} for p in selected[:data["topK"]]], "namespace":config.pinecone_namespace})
        raise AssertionError("Unexpected SDK route: " + path)
    monkeypatch.setattr(httpx, "HTTPTransport", lambda **kwargs: httpx.MockTransport(provider))
    store = Store(config.workspace)
    store.register(config.sources)
    item = {"native_id":"message-1", "title":"Travel", "text":"The automobile is parked beside the railway station.",
            "ref":{"provider":"wacli","chat_jid":"15550000001@s.whatsapp.net","message_id":"message-1"},
            "occurred_at":"2026-10-24T10:00:00Z", "direction":"received"}
    store.apply_page(source.id, "messages", None, "checkpoint-1", [item])
    index = VectorIndex(config, store)
    index._embedder = embedder
    assert index.drain() == 1
    assert points
    assert all(set(p["metadata"]) == {"document_id","source_id","revision","chunk","workspace_id"} for p in points.values())
    index.close()
    store.close()
    assert search(config, "dove si trova la macchina?", mode="semantic")["results"][0]["ref"]["message_id"] == "message-1"
    store = Store(config.workspace)
    local = VectorIndex(replace(config, backend="qdrant", pinecone_index="", pinecone_namespace=""), store)
    local._embedder = embedder
    assert local.drain() == 1
    assert not points
    local.close()
    remote = VectorIndex(config, store)
    remote._embedder = embedder
    assert remote.drain() == 1
    assert points
    remote.close()
    incompatible = VectorIndex(replace(config, model="BAAI/bge-small-en-v1.5"), store)
    incompatible._embedder = embedder
    with pytest.raises(ContextError, match="Model changed"):
        incompatible.ensure_collection()
    assert points
    incompatible.close()
    store.close()
    disabled = replace(config, sources=(replace(source, enabled=False),))
    assert search(disabled, "automobile", mode="semantic")["results"] == []
    store = Store(config.workspace)
    # A stale remote projection cannot override the current local document revision.
    current = points[next(iter(points))]
    current["metadata"]["revision"] = "stale"
    store.close()
    assert search(config, "automobile", mode="semantic")["results"] == []
    store = Store(config.workspace)
    store.forget(source.id)
    index = VectorIndex(config, store)
    index._embedder = None
    monkeypatch.setattr(type(index), "embedder", property(lambda _: (_ for _ in ()).throw(AssertionError("Erasure must not load a model"))))
    assert index.drain(delete_only=True) == 1
    assert not points
    index.close()
    store.close()
    assert any(path == "/vectors/delete" for path, _ in requests)
