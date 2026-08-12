#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.dont_write_bytecode = True

from _credentials import CredentialError, resolve_ngrok_authtoken
from _runtime import (
    ACTIVE_RECORD,
    APP_ROOT,
    RUNTIME_ROOT,
    VENV_PYTHON,
    load_record,
    process_alive,
    read_json_url,
    remove_record,
    terminate_record,
    write_record,
)


def free_port(preferred: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind(("127.0.0.1", preferred))
        except OSError:
            probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def ensure_runtime() -> None:
    subprocess.check_call(
        [sys.executable, str(Path(__file__).with_name("setup_runtime.py"))],
        stdout=subprocess.DEVNULL,
    )


def existing_event() -> dict[str, object] | None:
    record = load_record()
    if not record:
        return None
    try:
        pid = int(record["pid"])
    except (KeyError, TypeError, ValueError):
        remove_record()
        return None
    if not process_alive(pid):
        remove_record()
        return None
    session = read_json_url(f"{record.get('admin_url', '')}/api/session")
    if session and session.get("state") == "ended":
        if not terminate_record(record):
            raise RuntimeError("Previous ended Photo Drop process did not stop cleanly")
        remove_record()
        return None
    return {"event": "already_running", **record, "session": session}


def readiness_from_log(log_file: Path) -> dict[str, object] | None:
    try:
        lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and value.get("event") == "ready":
            return value
    return None


def stop_failed_child(child: subprocess.Popen[bytes]) -> None:
    if child.poll() is not None:
        return
    if os.name == "nt":
        child.terminate()
    else:
        os.killpg(child.pid, 15)
    try:
        child.wait(timeout=10)
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait(timeout=5)


def main() -> int:
    parser = argparse.ArgumentParser(description="Start a temporary Photo Drop event")
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--event-name", default="Photo Drop")
    parser.add_argument("--ttl-hours", type=float, default=12)
    parser.add_argument("--guest-port", type=int, default=8443)
    parser.add_argument("--admin-port", type=int, default=8444)
    parser.add_argument("--max-session-gib", type=float, default=50)
    parser.add_argument("--free-space-reserve-mib", type=float, default=512)
    parser.add_argument("--startup-timeout", type=float, default=30)
    parser.add_argument("--foreground", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.ttl_hours <= 0:
        parser.error("--ttl-hours must be greater than zero")
    try:
        authtoken = resolve_ngrok_authtoken()
    except CredentialError as error:
        parser.error(str(error))
    os.environ["NGROK_AUTHTOKEN"] = authtoken
    ensure_runtime()
    current = existing_event()
    if current:
        print(json.dumps(current))
        return 0
    destination = args.destination.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    guest_port = free_port(args.guest_port)
    admin_port = free_port(args.admin_port if args.admin_port != guest_port else 0)
    state_dir = RUNTIME_ROOT / "app-state"
    log_dir = RUNTIME_ROOT / "logs"
    state_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(UTC)
    stamp = started_at.strftime("%Y%m%dT%H%M%SZ")
    log_file = log_dir / f"event-{stamp}.log"
    command = [
        str(VENV_PYTHON),
        "-m",
        "photo_drop.cli",
        "start",
        "--destination",
        str(destination),
        "--event-name",
        args.event_name,
        "--state-dir",
        str(state_dir),
        "--ttl-seconds",
        str(round(args.ttl_hours * 3600)),
        "--guest-port",
        str(guest_port),
        "--admin-port",
        str(admin_port),
        "--max-session-bytes",
        str(round(args.max_session_gib * 1024**3)),
        "--free-space-reserve-bytes",
        str(round(args.free_space_reserve_mib * 1024**2)),
        "--no-open",
    ]
    environment = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(
            value for value in (str(APP_ROOT / "backend" / "app"), os.environ.get("PYTHONPATH")) if value
        ),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    if args.foreground:
        os.execvpe(command[0], command, environment)
    with log_file.open("ab", buffering=0) as output:
        child = subprocess.Popen(
            command,
            cwd=APP_ROOT,
            env=environment,
            stdout=output,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    deadline = time.monotonic() + args.startup_timeout
    while time.monotonic() < deadline:
        ready = readiness_from_log(log_file)
        if ready:
            record = {
                "pid": child.pid,
                "provider": "ngrok",
                "event_name": ready.get("event_name", args.event_name),
                "destination": str(destination),
                "started_at": started_at.isoformat(),
                "expires_at": (started_at + timedelta(hours=args.ttl_hours)).isoformat(),
                "guest_url": ready["guest_url"],
                "admin_url": ready["admin_url"],
                "guest_listener_url": ready["guest_listener_url"],
                "log_file": str(log_file),
            }
            write_record(record)
            print(json.dumps({"event": "ready", **record}))
            return 0
        if child.poll() is not None:
            break
        time.sleep(0.1)
    stop_failed_child(child)
    remove_record()
    try:
        detail = "\n".join(log_file.read_text(encoding="utf-8", errors="replace").splitlines()[-20:])
    except OSError:
        detail = "No application log was produced"
    print(f"Photo Drop failed to become ready. Log: {log_file}\n{detail}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
