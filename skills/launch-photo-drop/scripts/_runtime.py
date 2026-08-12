#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


SKILL_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = SKILL_ROOT / "assets" / "app"
CODEX_ROOT = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
RUNTIME_ROOT = Path(
    os.environ.get("PHOTO_DROP_RUNTIME_ROOT", CODEX_ROOT / "state" / "launch-photo-drop")
).expanduser()
ACTIVE_RECORD = RUNTIME_ROOT / "active-event.json"
VENV_PYTHON = RUNTIME_ROOT / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def load_record() -> dict[str, Any] | None:
    try:
        value = json.loads(ACTIVE_RECORD.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return value if isinstance(value, dict) else None


def write_record(value: dict[str, Any]) -> None:
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    temporary = ACTIVE_RECORD.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, ACTIVE_RECORD)


def remove_record() -> None:
    ACTIVE_RECORD.unlink(missing_ok=True)


def process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError, OSError):
        return False
    return True


def process_is_photo_drop(pid: int) -> bool:
    if not process_alive(pid):
        return False
    if os.name == "nt":
        return True
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "command="],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and "photo_drop.cli" in result.stdout


def terminate_record(record: dict[str, Any], timeout: float = 20) -> bool:
    try:
        pid = int(record["pid"])
    except (KeyError, TypeError, ValueError):
        return False
    if not process_alive(pid):
        return True
    if not process_is_photo_drop(pid):
        raise RuntimeError(f"Refusing to signal PID {pid}: it is not the recorded Photo Drop process")
    if os.name == "nt":
        os.kill(pid, signal.SIGTERM)
    else:
        process_group = os.getpgid(pid)
        if process_group != pid:
            raise RuntimeError(f"Refusing to signal unexpected process group {process_group} for PID {pid}")
        os.killpg(process_group, signal.SIGTERM)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not process_alive(pid):
            return True
        time.sleep(0.1)
    return False


def read_json_url(url: str, method: str = "GET", timeout: float = 2) -> dict[str, Any] | None:
    try:
        request = Request(url, method=method)
        with urlopen(request, timeout=timeout) as response:
            value = json.load(response)
    except (URLError, TimeoutError, OSError, ValueError):
        return None
    return value if isinstance(value, dict) else None
