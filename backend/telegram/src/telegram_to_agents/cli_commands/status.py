"""Focused gateway status command."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from rich.console import Console
from rich.panel import Panel

from telegram_to_agents.workspace.paths import resolve_paths

_console = Console()


def print_status() -> None:
    """Show process, project, and persisted-state coordinates."""
    from telegram_to_agents.infra.pidlock import _is_process_alive

    paths = resolve_paths()
    try:
        config = json.loads(paths.config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        config = {}
    pid_file = paths.state_home / "bot.pid"
    try:
        pid = int(pid_file.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        pid = None
    running = pid is not None and _is_process_alive(pid)
    uptime = ""
    if running:
        started = datetime.fromtimestamp(pid_file.stat().st_mtime, tz=UTC)
        minutes = int((datetime.now(UTC) - started).total_seconds() // 60)
        uptime = f" · {minutes // 60}h {minutes % 60}m"
    lines = [
        f"Status: {'running' if running else 'stopped'}{uptime}",
        f"PID: {pid or '-'}",
        f"Provider: native {str(config.get('provider', 'codex')).capitalize()}",
        "Transport: Telegram",
        f"Project: {config.get('project_root', '-')}",
        f"Config: {paths.config_path}",
        f"Sessions: {paths.sessions_path}",
    ]
    _console.print(Panel("\n".join(lines), title="telegram-to-agents"))
