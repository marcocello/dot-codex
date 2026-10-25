"""Shared private state and checked subprocesses for the setup wizard."""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from datetime import datetime, timezone

from install_state import InstallError, atomic_write, save_json


class SetupError(InstallError):
    pass


def ask(label, default="", *, interactive=True):
    if not interactive:
        if default != "":
            return default
        raise SetupError(f"Missing configuration: {label}. Run setup interactively or provide --config.")
    value = input(f"{label}" + (f" [{default}]" if default != "" else "") + ": ").strip()
    return value or default


def yes(label, default=True, *, interactive=True):
    value = ask(label + " (yes/no)", "yes" if default else "no", interactive=interactive).lower()
    if value not in {"yes", "y", "no", "n"}:
        raise SetupError("Answer yes or no")
    return value in {"yes", "y"}


def command(args, *, cwd=None, env=None, capture=False, check=True, timeout=None):
    # Never print arguments: device commands and provider errors can contain secrets.
    args = list(map(str, args))
    unattended = (os.environ if env is None else env).get("SECOND_BRAIN_NO_PROMPT") == "1"
    if unattended and args[0] == "sudo" and "-n" not in args[1:2]:
        args.insert(1, "-n")
    result = subprocess.run(args, cwd=cwd, env=env, text=True,
                            capture_output=capture, timeout=timeout,
                            stdin=subprocess.DEVNULL if unattended else None)
    if check and result.returncode:
        raise SetupError(f"{Path(str(args[0])).name}: command failed (exit {result.returncode}); retry setup after resolving this step")
    return result


def private_directory(path):
    path = Path(path).expanduser().absolute()
    if any(character in str(path) for character in "\n\r\x00"):
        raise SetupError("Private paths must not contain control characters")
    if any(parent.is_symlink() for parent in (path, *path.parents)):
        raise SetupError(f"Private setup state must not traverse symlinks: {path}")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    path.chmod(0o700)
    return path


@contextmanager
def setup_lock(state):
    state = private_directory(state)
    fd = os.open(state / "setup.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SetupError("Another setup owns this state; wait for it to finish") from None
        yield
    finally:
        os.close(fd)


class Journal:
    def __init__(self, state):
        self.path = state / "setup-status.json"
        previous = json.loads(self.path.read_text()) if self.path.exists() else {}
        self.data = {"schema": 1, "started_at":datetime.now(timezone.utc).isoformat(), "status":"running",
                     "phases":{}, "previous_phases":previous.get("phases", {})}
        save_json(self.path, self.data)
        self.failed = False
        self.started = time.monotonic()
        self.step = 0

    def phase(self, name, action, *, requires=()):
        self.step += 1
        print(f"\n[{self.step}] {name}", flush=True)
        if any(self.data["phases"].get(key, {}).get("status") != "verified" for key in requires):
            self.failed = True
            self.data["phases"][name] = {"status": "pending", "detail": "A prerequisite is incomplete"}
            save_json(self.path, self.data)
            print(f"{name}: pending; prerequisite incomplete", flush=True)
            return False
        try:
            self.data["phases"][name] = {"status":"running", "detail":"Rechecking actual resources"}
            save_json(self.path, self.data)
            detail = action()
            self.data["phases"][name] = {"status": "verified", "detail": detail or "Checked"}
            print(f"{name}: verified", flush=True)
        except (InstallError, OSError, ValueError, subprocess.SubprocessError) as error:
            self.failed = True
            # Exceptions from providers and package managers may carry tokens or source text.
            self.data["phases"][name] = {"status": "incomplete", "detail": "Step failed; retry setup to recheck and resume"}
            print(f"{name}: incomplete; following independent steps can continue", flush=True)
            if isinstance(error, InstallError):
                print(str(error), flush=True)
        save_json(self.path, self.data)
        return self.data["phases"][name]["status"] == "verified"

    def finish(self):
        failed = any(phase["status"] != "verified" for phase in self.data["phases"].values())
        self.data["status"] = "incomplete" if failed else "verified"
        self.data["completed_at"] = datetime.now(timezone.utc).isoformat()
        self.data["duration_seconds"] = round(time.monotonic() - self.started, 2)
        save_json(self.path, self.data)
        incomplete = [name for name, phase in self.data["phases"].items() if phase["status"] != "verified"]
        if incomplete:
            print("\nRemaining steps: " + ", ".join(incomplete), flush=True)
        print(f"Receipt: {self.path}", flush=True)
        return failed


def fingerprint(paths):
    digest = hashlib.sha256()
    for path in sorted(map(Path, paths)):
        digest.update(str(path.name).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def download(url, destination):
    if not url.startswith("https://"):
        raise SetupError("Downloads require HTTPS")
    command(["curl", "--fail", "--location", "--silent", "--show-error", "--proto", "=https",
             "--proto-redir", "=https", "--tlsv1.2", "--connect-timeout", "20", "--max-time", "600",
             "--retry", "3", "--retry-delay", "1", "--retry-max-time", "120", "--retry-connrefused",
             "--output", destination, url])


def verified_archive(url, sha256, destination, member):
    import tarfile
    with tempfile.TemporaryDirectory(prefix="secondbrain-download-") as tmp:
        archive = Path(tmp) / "package.tar.gz"
        download(url, archive)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != sha256:
            raise SetupError("Downloaded archive checksum does not match the published digest")
        with tarfile.open(archive) as package:
            try:
                selected = package.getmember(member)
            except KeyError:
                try:
                    selected = package.getmember("./" + member)
                except KeyError:
                    raise SetupError("Release archive is missing its expected binary") from None
            if not selected.isfile() or selected.size > 300_000_000:
                raise SetupError("Release binary is not a bounded regular file")
            with package.extractfile(selected) as source:
                payload = source.read()
        destination.parent.mkdir(parents=True, exist_ok=True)
        write_binary(destination, payload)


def write_binary(destination, payload):
    if destination.is_symlink():
        raise SetupError("Refusing to replace a symlink with a release binary")
    fd, name = tempfile.mkstemp(dir=destination.parent, prefix=".release-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
        os.chmod(name, 0o700)
        os.replace(name, destination)
    finally:
        Path(name).unlink(missing_ok=True)
