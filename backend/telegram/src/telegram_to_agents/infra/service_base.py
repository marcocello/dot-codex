"""Shared presentation and binary helpers for the Linux systemd service."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from rich.panel import Panel

if TYPE_CHECKING:
    from rich.console import Console

_SERVICE_TEXT = {
    "service.not_installed": "[dim]Service not installed.[/dim]",
    "service.not_running": "[dim]Service is not running.[/dim]",
    "service.no_binary": (
        "[bold red]Could not find the telegram-to-agents binary in PATH.[/bold red]"
    ),
    "service.removed": "[green]Service removed.[/green]",
    "service.started": "[green]Service started.[/green]",
    "service.stopped": "[green]Service stopped.[/green]",
    "service.start_failed": "[red]Failed to start: {error}[/red]",
    "service.install.title": "telegram-to-agents background service",
    "service.install.body": (
        "[bold green]telegram-to-agents is now running as a background service.[/bold green]\n\n"
        "{detail}\n\n[bold]Useful commands:[/bold]\n"
        "  [cyan]telegram-to-agents status[/cyan]   Check if it is running\n"
        "  [cyan]telegram-to-agents stop[/cyan]     Stop the service\n"
        "  [cyan]telegram-to-agents restart[/cyan]  Restart the service\n"
        "  {logs_hint}"
    ),
    "service.linux.no_systemd": (
        "[bold red]systemd not found. Service install requires Linux with systemd.[/bold red]"
    ),
    "service.linux.linger_warning": (
        "[bold yellow]Linger must be enabled so telegram-to-agents keeps running after logout.[/bold yellow]"
    ),
    "service.linux.linger_enabled": "[green]Linger enabled.[/green]",
    "service.linux.linger_manual": (
        "[yellow]Could not enable linger automatically.[/yellow]\n"
        "Run manually: [bold]sudo loginctl enable-linger {user}[/bold]"
    ),
    "service.linux.start_failed": "[bold red]Failed to start service:[/bold red] {error}",
    "service.linux.detail": "It starts on boot and restarts on crash.",
    "service.logs.no_logs": "[dim]No log files found.[/dim]",
    "service.logs.showing": "[dim]Showing last {count} lines from {name}[/dim]",
    "service.logs.read_error": "[red]Could not read log file: {error}[/red]",
    "service.logs.full_path": "[dim]Full log: {path}[/dim]",
    "service.logs.not_installed": "[dim]Service not installed.[/dim]",
    "service.logs.streaming": "[dim]Showing logs (Ctrl+C to stop)...[/dim]",
    "service.logs.no_journalctl": "[bold red]journalctl not found.[/bold red]",
}


def service_text(key: str, **values: object) -> str:
    return _SERVICE_TEXT[key].format_map(values)


def ensure_console(console: Console | None) -> Console:
    if console is not None:
        return console
    from rich.console import Console as RichConsole

    return RichConsole()


def find_telegram_to_agents_binary() -> str | None:
    return shutil.which("telegram-to-agents")


def collect_nvm_bin_dirs(home: Path) -> list[str]:
    nvm_dir = home / ".nvm"
    if not nvm_dir.is_dir():
        return []
    return [
        node_dir.as_posix()
        for node_dir in sorted(nvm_dir.glob("versions/node/*/bin"), reverse=True)
    ]


def print_not_installed(console: Console) -> None:
    console.print(service_text("service.not_installed"))


def print_not_running(console: Console) -> None:
    console.print(service_text("service.not_running"))


def print_binary_not_found(console: Console) -> None:
    console.print(service_text("service.no_binary"))


def print_removed(console: Console) -> None:
    console.print(service_text("service.removed"))


def print_started(console: Console) -> None:
    console.print(service_text("service.started"))


def print_stopped(console: Console) -> None:
    console.print(service_text("service.stopped"))


def print_start_failed(console: Console, stderr: str) -> None:
    console.print(service_text("service.start_failed", error=stderr))


def print_install_success(console: Console, *, detail: str, logs_hint: str) -> None:
    console.print(
        Panel(
            service_text("service.install.body", detail=detail, logs_hint=logs_hint),
            title=service_text("service.install.title"),
            border_style="green",
            padding=(1, 2),
        )
    )
