"""Private checkpoints and reversible filesystem publication for the installer."""

from __future__ import annotations

from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import uuid


class InstallError(Exception):
    """An actionable failure whose message contains no provider secrets."""


def atomic_write(path: Path, content: str, mode: int = 0o600) -> None:
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise InstallError(f"Expected a regular file: {path}")
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            os.chmod(temporary, mode)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def save_json(path: Path, value: dict) -> None:
    atomic_write(path, json.dumps(value, indent=2) + "\n")


def environment_files(home: Path) -> list[Path]:
    files = [home / name for name in (".profile", ".zshenv", ".bashrc", ".bash_profile")]
    files.extend(home / name for name in (".zprofile", ".zshrc", ".zlogin", ".bash_login")
                 if (home / name).exists())
    return files


def remove(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def path_identity(path: Path) -> str:
    if path.is_symlink():
        return "link:" + os.readlink(path)
    if path.is_file():
        return "file:" + hashlib.sha256(path.read_bytes()).hexdigest()
    return "directory" if path.exists() else "absent"


@contextmanager
def ignore_interrupts():
    previous = {sig: signal.signal(sig, signal.SIG_IGN) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        yield
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


@contextmanager
def installation_lock(home: Path):
    state = home / ".local/state/dot-codex"
    if state.is_symlink():
        raise InstallError(f"Installer state must be a real directory: {state}")
    state.mkdir(parents=True, mode=0o700, exist_ok=True)
    os.chmod(state, 0o700)
    fd = os.open(state / "install.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise InstallError("Another installer is changing this user home. Wait for it to finish.") from None
        pending = state / "pending.json"
        if pending.exists():
            previous = Transaction.load(state, json.loads(pending.read_text())["transaction"])
            previous.rollback()
            print("Recovered the interrupted filesystem phase; previous configuration restored.", flush=True)
        yield state


class Transaction:
    """Write undo records before mutation; retain committed records for explicit restore."""

    def __init__(self, state: Path):
        self.state = state
        self.directory = state / "transactions" / uuid.uuid4().hex
        self.directory.mkdir(parents=True, mode=0o700)
        self.record = {"actions": [], "committed": False}
        self.persist()
        save_json(state / "pending.json", {"transaction": self.directory.name})

    @classmethod
    def load(cls, state: Path, identifier: str):
        if not identifier or Path(identifier).name != identifier:
            raise InstallError("Invalid installer recovery record.")
        instance = object.__new__(cls)
        instance.state = state
        instance.directory = state / "transactions" / identifier
        instance.record = json.loads((instance.directory / "undo.json").read_text())
        return instance

    def persist(self):
        save_json(self.directory / "undo.json", self.record)

    def remember(self, path: Path, role: str = "generated"):
        if any(action["path"] == str(path) for action in self.record["actions"]):
            return
        action = {"path": str(path), "role": role, "kind": "absent"}
        if path.is_symlink():
            action.update(kind="link", target=os.readlink(path))
        elif path.is_file():
            backup = self.directory / str(len(self.record["actions"]))
            shutil.copy2(path, backup)
            os.chmod(backup, 0o600)
            action.update(kind="file", backup=backup.name, mode=path.stat().st_mode & 0o777)
        elif path.exists():
            raise InstallError(f"Refusing to replace an existing directory: {path}")
        self.record["actions"].append(action)
        self.persist()

    def move_home(self, path: Path, backup: Path):
        self.move_path(path, backup, role="home")

    def move_path(self, path: Path, backup: Path, *, role="generated"):
        self.record["actions"].append({"kind": "move", "role": role, "path": str(path),
                                       "backup": str(backup)})
        self.persist()
        os.replace(path, backup)

    def commit(self):
        for action in self.record["actions"]:
            action["published"] = path_identity(Path(action["path"]))
        self.record["committed"] = True
        self.persist()
        (self.state / "pending.json").unlink(missing_ok=True)

    def rollback(self, *, restore=False):
        with ignore_interrupts():
            for action in reversed(self.record["actions"]):
                if restore and action["role"] not in {"home", "shell"}:
                    continue
                path = Path(action["path"])
                if action["kind"] == "move":
                    backup = Path(action["backup"])
                    if backup.exists() or backup.is_symlink():
                        remove(path)
                        os.replace(backup, path)
                    continue
                remove(path)
                if action["kind"] == "file":
                    path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(self.directory / action["backup"], path)
                    os.chmod(path, action["mode"])
                elif action["kind"] == "link":
                    path.symlink_to(action["target"])
            (self.state / "pending.json").unlink(missing_ok=True)

    def check_restore(self):
        for action in self.record["actions"]:
            if action["role"] in {"home", "shell"}:
                if path_identity(Path(action["path"])) != action.get("published"):
                    raise InstallError(f"Changed since activation; restore manually to preserve edits: {action['path']}")
