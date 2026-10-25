"""Focused gateway lifecycle commands."""

from __future__ import annotations

import contextlib
import subprocess
import sys
from typing import NoReturn

from rich.console import Console

from telegram_to_agents.workspace.paths import resolve_paths

_console = Console()


def _re_exec_gateway() -> NoReturn:
    subprocess.Popen([sys.executable, "-m", "telegram_to_agents"])
    raise SystemExit(0)


def stop_bot() -> None:
    """Stop the installed service or the PID-file gateway process."""
    with contextlib.suppress(Exception):
        from telegram_to_agents.infra.service import (
            is_service_installed,
            is_service_running,
            stop_service,
        )

        if is_service_installed() and is_service_running():
            stop_service(_console)

    from telegram_to_agents.infra.pidlock import _is_process_alive, _kill_and_wait

    pid_file = resolve_paths().state_home / "bot.pid"
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
    except (FileNotFoundError, OSError, ValueError):
        pid = None
    if pid is not None and _is_process_alive(pid):
        _kill_and_wait(pid)
        _console.print(f"Stopped telegram-to-agents (PID {pid}).")
    else:
        _console.print("telegram-to-agents is not running.")
    pid_file.unlink(missing_ok=True)


def cmd_restart() -> None:
    """Restart the installed service, or re-exec a foreground gateway."""
    with contextlib.suppress(Exception):
        from telegram_to_agents.infra.service import (
            is_service_installed,
            start_service,
            stop_service,
        )

        if is_service_installed():
            stop_service(_console)
            start_service(_console)
            return
    stop_bot()
    _re_exec_gateway()
