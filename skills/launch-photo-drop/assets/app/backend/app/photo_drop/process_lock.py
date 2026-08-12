import fcntl
import json
from pathlib import Path
from typing import IO


class AlreadyRunningError(RuntimeError):
    pass


class ProcessLock:
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.lock_file: IO[str] | None = None
        self.info_path = state_dir / "active.json"

    def acquire(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        if not self.state_dir.is_dir():
            raise NotADirectoryError(self.state_dir)
        self.lock_file = (self.state_dir / "photo-drop.lock").open("a+", encoding="utf-8")
        try:
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            self.lock_file.close()
            self.lock_file = None
            raise AlreadyRunningError(self.describe_active()) from error

    def publish(self, admin_url: str) -> None:
        self.info_path.write_text(json.dumps({"admin_url": admin_url}), encoding="utf-8")

    def describe_active(self) -> str:
        try:
            data = json.loads(self.info_path.read_text(encoding="utf-8"))
            return f"Photo Drop is already running at {data['admin_url']}"
        except (OSError, KeyError, json.JSONDecodeError):
            return "Photo Drop is already starting in this state directory"

    def release(self) -> None:
        if self.lock_file is None:
            return
        fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
        self.lock_file.close()
        self.lock_file = None
