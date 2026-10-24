"""Codex package publication, native account commands, and service configuration."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import plistlib
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import uuid

from install_service import connected
from install_state import InstallError, Transaction, atomic_write, environment_files, save_json

DEFAULT_VERSION = "0.151.0"


def run(command, env, label, *, visible=False, timeout=300, check=True, cwd=None, attached=False):
    """Cancel and reap the entire child group; never persist account/provider output."""
    process = subprocess.Popen([str(item) for item in command], env=env,
                               stdout=None if visible else subprocess.PIPE,
                               stderr=None if visible else subprocess.PIPE,
                               text=True, start_new_session=not attached, cwd=cwd)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except (KeyboardInterrupt, subprocess.TimeoutExpired) as error:
        try:
            if attached:
                process.terminate()
            else:
                os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            if attached:
                process.kill()
            else:
                os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
        if isinstance(error, KeyboardInterrupt):
            raise
        raise InstallError(f"{label} timed out; rerun the selected phase.") from None
    if check and process.returncode:
        raise InstallError(f"{label} failed (exit {process.returncode}); rerun that phase after diagnosis.")
    return subprocess.CompletedProcess(command, process.returncode, stdout or "", stderr or "")


def version_of(binary: Path, env: dict) -> str:
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise InstallError(f"Codex executable missing: {binary}. Run ./install.sh cli.")
    result = run([binary, "--version"], env, "Codex version check", timeout=20)
    match = re.fullmatch(r"codex-cli (\S+)\s*", result.stdout)
    if not match:
        raise InstallError(f"Unexpected Codex version response from {binary}.")
    return match[1]


def find_cli(home: Path, requested: str = "codex") -> Path:
    if requested != "codex":
        value = shutil.which(requested) if not Path(requested).is_absolute() else requested
        if value:
            return Path(value).absolute()
        raise InstallError(f"Codex executable unavailable: {requested}. Run ./install.sh cli.")
    for candidate in [home / ".local/bin/codex", shutil.which("codex"),
                      home / ".codex/packages/standalone/current/bin/codex",
                      home / ".codex/packages/standalone/current/codex"]:
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return Path(candidate).absolute()
    raise InstallError("Codex executable unavailable or its link is broken. Run ./install.sh cli.")


def target_name() -> str:
    machine = {"arm64": "aarch64", "aarch64": "aarch64", "x86_64": "x86_64", "amd64": "x86_64"}.get(platform.machine().lower())
    suffix = {"darwin": "apple-darwin", "linux": "unknown-linux-musl"}.get(sys.platform)
    if not machine or not suffix:
        raise InstallError("Managed CLI installation supports macOS/Linux on arm64 or x86_64.")
    return f"{machine}-{suffix}"


def fetch(url: str, destination: Path, env: dict):
    if not url.startswith("https://"):
        raise InstallError("Package downloads require HTTPS.")
    if not shutil.which("curl", path=env.get("PATH")):
        raise InstallError("Install curl before downloading Codex, or supply --package-file and --sha256.")
    run(["curl", "--proto", "=https", "--tlsv1.2", "-fsSL", "--connect-timeout", "15",
         "--max-time", "180", "--retry", "2", "-o", destination, url], env, "Official package download")


def publish_link(path: Path, target: Path):
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}")
    try:
        temporary.symlink_to(target)
        os.replace(temporary, path)  # Never follow an existing symlink-to-directory.
    finally:
        temporary.unlink(missing_ok=True)


def extract_package(archive: Path, stage: Path):
    with tarfile.open(archive, "r:gz") as stream:
        members = stream.getmembers()
        for item in members:
            parts = Path(item.name).parts
            if Path(item.name).is_absolute() or ".." in parts:
                raise InstallError("Unsafe path in Codex package; publication cancelled.")
            if not (item.isfile() or item.isdir()):
                raise InstallError("Unexpected link or special file in Codex package; publication cancelled.")
        # All members are now regular files/directories, with no traversal or link parents.
        for item in members:
            path = stage / item.name
            if item.isdir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                with stream.extractfile(item) as source, path.open("wb") as target:
                    shutil.copyfileobj(source, target)
                os.chmod(path, 0o755 if item.mode & 0o111 else 0o644)
    for name in ("bin/codex", "bin/codex-code-mode-host", "codex-path/rg", "codex-package.json"):
        if not (stage / name).is_file():
            raise InstallError(f"Codex package is missing {name}.")
    if (stage / "codex").exists():
        raise InstallError("Unexpected root entrypoint in Codex package; publication cancelled.")
    # The native daemon invokes <CODEX_HOME>/packages/standalone/current/codex.
    # Match the official installer's generated alias after validating the archive.
    (stage / "codex").symlink_to("bin/codex")


def persist_cli_path(home: Path, transaction: Transaction):
    begin, end = "# BEGIN managed Codex CLI", "# END managed Codex CLI"
    directory = shlex.quote(str(home / ".local/bin"))
    block = (begin + '\ncase ":${PATH-}:" in\n  *:' + directory + ':*) ;;\n'
             '  *) export PATH=' + directory + ':"${PATH-}" ;;\nesac\n' + end)
    for path in environment_files(home):
        original = path.read_text() if path.exists() else ""
        if original.count(begin) != original.count(end) or original.count(begin) > 1:
            raise InstallError(f"Repair the incomplete CLI PATH block in {path}.")
        if begin in original:
            start = original.index(begin)
            finish = original.index(end)
            if finish < start:
                raise InstallError(f"Repair the reversed CLI PATH block in {path}.")
            content = original[:start] + block + original[finish + len(end):]
        else:
            content = original.rstrip() + "\n\n" + block + "\n"
        transaction.remember(path, role="shell")
        atomic_write(path, content, path.stat().st_mode & 0o777 if path.exists() else 0o600)


def install_cli(args, state: Path, env: dict) -> Path:
    if not re.fullmatch(r"\d+\.\d+\.\d+", args.version):
        raise InstallError("--version must be an explicit x.y.z release.")
    target = target_name()
    base = args.user_home / ".local/share/dot-codex/cli"
    releases = base / "releases"
    releases.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".download-", dir=base) as download_dir:
        temporary = Path(download_dir)
        archive = args.package_file
        digest = args.sha256
        if archive is None:
            archive = temporary / "package.tar.gz"
            url = args.package_url
            if not url:
                metadata = temporary / "release.json"
                fetch(f"https://api.github.com/repos/openai/codex/releases/tags/rust-v{args.version}", metadata, env)
                release = json.loads(metadata.read_text())
                name = f"codex-package-{target}.tar.gz"
                asset = next((a for a in release.get("assets", []) if a.get("name") == name), None)
                if not asset or not str(asset.get("digest", "")).startswith("sha256:"):
                    raise InstallError("Official release has no package digest; supply an audited URL/file and --sha256.")
                url = asset["browser_download_url"]
                digest = asset["digest"].removeprefix("sha256:")
            if not digest:
                raise InstallError("--package-url requires --sha256.")
            fetch(url, archive, env)
        if not digest or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
            raise InstallError("Supply --sha256 with a 64-character SHA-256 digest.")
        with archive.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != digest.lower():
            raise InstallError("Codex package SHA-256 mismatch; existing CLI retained.")
        stage = temporary / "stage"
        stage.mkdir()
        extract_package(archive, stage)
        if version_of(stage / "bin/codex", env) != args.version:
            raise InstallError("Codex package version mismatch; existing CLI retained.")
        release_dir = releases / f"{args.version}-{target}-{actual[:12]}"
        reusable = False
        if release_dir.is_dir() and not release_dir.is_symlink():
            alias = release_dir / "codex"
            reusable = alias.is_symlink() and os.readlink(alias) == "bin/codex" and all(
                (release_dir / path.relative_to(stage)).is_file()
                and not (release_dir / path.relative_to(stage)).is_symlink()
                and (path.stat().st_mode & 0o777) == ((release_dir / path.relative_to(stage)).stat().st_mode & 0o777)
                and path.read_bytes() == (release_dir / path.relative_to(stage)).read_bytes()
                for path in stage.rglob("*") if path.is_file() and not path.is_symlink()
            )
        if not reusable:
            # Keep release directories immutable, including when repairing a corrupt prior copy.
            if release_dir.exists() or release_dir.is_symlink():
                release_dir = release_dir.with_name(release_dir.name + "-" + uuid.uuid4().hex[:8])
            os.replace(stage, release_dir)
        current = base / "current"
        binary = args.user_home / ".local/bin/codex"
        binary.parent.mkdir(parents=True, exist_ok=True)
        transaction = Transaction(state)
        try:
            transaction.remember(current)
            transaction.remember(binary)
            publish_link(current, release_dir)
            publish_link(binary, current / "bin/codex")
            if version_of(binary, env) != args.version:
                raise InstallError("Published Codex version does not match the selected release.")
            persist_cli_path(args.user_home, transaction)
            transaction.commit()
        except BaseException:
            transaction.rollback()
            raise
    print(f"Codex {args.version} ready: {binary}", flush=True)
    return binary


def require_login(binary: Path, env: dict):
    if run([binary, "login", "status"], env, "Login status", check=False).returncode:
        raise InstallError("Codex is not signed in. Run ./install.sh login, then retry this phase.")


def require_connection(binary: Path, env: dict):
    result = run([binary, "remote-control", "start", "--json"], env, "Remote Control readiness", timeout=100)
    try:
        ready = connected(json.loads(result.stdout))
    except (ValueError, TypeError):
        ready = False
    if not ready:
        raise InstallError("Remote Control is not connected. Check login/network, then rerun service or pair.")


def service_manager(args) -> str:
    return args.service_manager or ("launchd" if sys.platform == "darwin" else "systemd")


def systemd_quote(value: str, *, executable=False) -> str:
    if executable:
        value = value.replace("$", "$$")
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("%", "%%") + '"'


def prepare_service_package(home: Path, state: Path, binary: Path, codex_home: Path, env: dict):
    """Expose the external CLI root at the native daemon's fixed managed path."""
    packages = codex_home / "packages"
    native_root = packages / "standalone"
    native_binary = native_root / "current/codex"
    if native_binary.is_file() and native_binary.resolve() == binary.resolve():
        version_of(native_binary, env)
        return
    managed = home / ".local/share/dot-codex/cli"
    candidate = managed / "current/codex"
    if not candidate.is_file() or candidate.resolve() != binary.resolve():
        if native_binary.is_file():
            raise InstallError("Native daemon uses a different CLI. Select its executable with --codex-bin, or run ./install.sh cli before retrying service.")
        raise InstallError("Native daemon needs the managed standalone layout. Run ./install.sh cli, then retry service.")
    if packages.is_symlink() or (packages.exists() and not packages.is_dir()):
        raise InstallError("Native package parent must be a real directory; retain the existing path before retrying service.")
    packages.mkdir(parents=True, exist_ok=True)
    transaction = Transaction(state)
    try:
        if native_root.is_dir() and not native_root.is_symlink():
            backup = packages / ("standalone.backup." + uuid.uuid4().hex[:12])
            transaction.move_path(native_root, backup)
            print(f"Previous native package retained: {backup}", flush=True)
        else:
            transaction.remember(native_root)
        publish_link(native_root, managed)
        version_of(native_binary, env)
        transaction.commit()
    except BaseException:
        transaction.rollback()
        raise


def configure_service(args, state: Path, binary: Path, codex_home: Path, env: dict):
    require_login(binary, env)
    if args.user_home != Path.home().resolve():
        raise InstallError("Run the service phase as its intended login user, with that user's HOME.")
    if any(character in str(binary) for character in "\n\r\x00"):
        raise InstallError("Executable paths must not contain control characters.")
    manager = service_manager(args)
    for tool in (("systemctl", "loginctl") if manager == "systemd" else ("launchctl",)):
        if not shutil.which(tool, path=env.get("PATH")):
            raise InstallError(f"{tool} is unavailable. Run service in a login session with {manager}.")
    prepare_service_package(args.user_home, state, binary, codex_home, env)
    helper = args.user_home / ".local/share/dot-codex/service-health.py"
    helper.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(helper, Path(__file__).with_name("install_service.py").read_text(), 0o700)
    command = [sys.executable, str(helper), "--codex-bin", str(binary), "--codex-home", str(codex_home),
               "--user-home", str(args.user_home)]
    if manager == "systemd":
        linger = run(["loginctl", "show-user", str(os.getuid()), "--property=Linger", "--value"],
                     env, "Read boot persistence", check=False)
        if linger.returncode or linger.stdout.strip() != "yes":
            if not args.enable_linger:
                raise InstallError("Linux boot persistence needs lingering. Rerun ./install.sh service --enable-linger (may ask for sudo).")
            run(["sudo", "loginctl", "enable-linger", str(os.getuid())], env, "Enable lingering", visible=True, attached=True)
            if run(["loginctl", "show-user", str(os.getuid()), "--property=Linger", "--value"],
                   env, "Verify lingering").stdout.strip() != "yes":
                raise InstallError("Lingering is still disabled; reboot persistence is not ready.")
        directory = args.user_home / ".config/systemd/user"
        directory.mkdir(parents=True, exist_ok=True)
        common = ("[Unit]\nDescription=Codex managed Remote Control\n\n[Service]\nType=oneshot\n"
                  "KillMode=process\nTimeoutStartSec=240\n"
                  f"Environment={systemd_quote('HOME=' + str(args.user_home))}\n"
                  f"Environment={systemd_quote('CODEX_HOME=' + str(codex_home))}\n")
        boot = directory / "codex-remote-control.service"
        health = directory / "codex-remote-control-health.service"
        timer = directory / "codex-remote-control-health.timer"
        transaction = Transaction(state)
        try:
            for path in (boot, health, timer):
                transaction.remember(path)
            encoded = " ".join(systemd_quote(part, executable=True) for part in command)
            atomic_write(boot, common + "RemainAfterExit=yes\nExecStart=" + encoded +
                         " --bootstrap\n\n[Install]\nWantedBy=default.target\n", 0o644)
            atomic_write(health, common + "ExecStart=" + encoded + "\n", 0o644)
            atomic_write(timer, "[Unit]\nDescription=Check Codex Remote Control\n\n[Timer]\n"
                         "OnBootSec=2min\nOnUnitInactiveSec=1min\nUnit=codex-remote-control-health.service\n"
                         "\n[Install]\nWantedBy=timers.target\n", 0o644)
            transaction.commit()
        except BaseException:
            transaction.rollback()
            raise
        run(["systemctl", "--user", "daemon-reload"], env, "Reload user service definitions")
        run(["systemctl", "--user", "enable", "--now", boot.name, timer.name], env, "Enable boot and health service")
        run(["systemctl", "--user", "restart", boot.name], env, "Start managed Codex service")
        for unit in (boot.name, timer.name):
            run(["systemctl", "--user", "is-active", "--quiet", unit], env, f"Verify active {unit}")
            run(["systemctl", "--user", "is-enabled", "--quiet", unit], env, f"Verify enabled {unit}")
    else:
        directory = args.user_home / "Library/LaunchAgents"
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "com.marcocello.codex-remote-control.plist"
        label = "com.marcocello.codex-remote-control"
        value = {"Label": label, "ProgramArguments": command + ["--watch"], "RunAtLoad": True,
                 "KeepAlive": True, "ThrottleInterval": 60,
                 "EnvironmentVariables": {"HOME": str(args.user_home), "CODEX_HOME": str(codex_home)}}
        transaction = Transaction(state)
        try:
            transaction.remember(path)
            atomic_write(path, plistlib.dumps(value).decode(), 0o600)
            transaction.commit()
        except BaseException:
            transaction.rollback()
            raise
        domain = f"gui/{os.getuid()}"
        run(["launchctl", "bootout", domain + "/" + label], env, "Unload prior LaunchAgent", check=False)
        run(["launchctl", "bootstrap", domain, path], env, "Load Codex LaunchAgent")
        run(["launchctl", "kickstart", domain + "/" + label], env, "Start Codex LaunchAgent")
        run(["launchctl", "print", domain + "/" + label], env, "Verify loaded Codex LaunchAgent")
    save_json(helper.parent / "service.json", {"binary": str(binary), "codex_home": str(codex_home),
                                               "manager": manager})
    require_connection(binary, env)
    print("Remote Control connected; startup configuration verified. An actual reboot is not tested.", flush=True)
