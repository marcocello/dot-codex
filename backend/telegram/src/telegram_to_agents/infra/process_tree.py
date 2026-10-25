"""POSIX process-tree termination for the Linux gateway service."""

from __future__ import annotations

import contextlib
import logging
import os
import signal
import subprocess

logger = logging.getLogger(__name__)
_PS_TIMEOUT_SECONDS = 5.0


def list_process_descendants(pid: int) -> list[int]:
    """Return recursive child PIDs for a positive process ID."""
    if pid <= 0:
        return []
    snapshot = _read_process_snapshot()
    children: dict[int, list[int]] = {}
    for line in snapshot.splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        with contextlib.suppress(ValueError):
            child_pid, parent_pid = map(int, parts)
            children.setdefault(parent_pid, []).append(child_pid)

    descendants: list[int] = []
    seen: set[int] = set()
    stack = list(children.get(pid, []))
    while stack:
        child = stack.pop()
        if child in seen:
            continue
        seen.add(child)
        descendants.append(child)
        stack.extend(children.get(child, []))
    return descendants


def terminate_process_tree(pid: int) -> None:
    """Send SIGTERM to the lead process and its descendants."""
    _send_signal([pid, *list_process_descendants(pid)], signal.SIGTERM)


def force_kill_process_tree(pid: int) -> None:
    """Send SIGKILL to descendants first, then the lead process."""
    _send_signal([*list_process_descendants(pid), pid], signal.SIGKILL)


def interrupt_process(pid: int) -> None:
    """Send SIGINT to the lead provider process."""
    _send_signal([pid], signal.SIGINT)


def _send_signal(targets: list[int], sig: signal.Signals) -> None:
    current = os.getpid()
    for target in targets:
        if target <= 0 or target == current:
            continue
        with contextlib.suppress(ProcessLookupError, PermissionError, OSError):
            os.kill(target, sig)


def _read_process_snapshot() -> str:
    with contextlib.suppress(OSError, subprocess.TimeoutExpired):
        result = subprocess.run(
            ["ps", "-axo", "pid=,ppid="],
            capture_output=True,
            text=True,
            check=False,
            timeout=_PS_TIMEOUT_SECONDS,
        )
        if result.returncode == 0:
            return result.stdout
    logger.debug("Failed to read process snapshot via ps")
    return ""
