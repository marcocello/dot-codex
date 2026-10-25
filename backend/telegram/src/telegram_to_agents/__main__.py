"""Entry point for the native-harness Telegram gateway."""

from __future__ import annotations

import asyncio
import json
import logging
import signal
import sys
from collections.abc import Callable
from pathlib import Path

from rich.console import Console

from telegram_to_agents.config import AgentConfig
from telegram_to_agents.workspace.paths import resolve_paths

_console = Console()


def _is_configured() -> bool:
    paths = resolve_paths()
    if not paths.config_path.is_file():
        return False
    try:
        data = json.loads(paths.config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    return (
        bool(data.get("telegram_token"))
        and bool(data.get("allowed_user_ids"))
        and bool(data.get("project_root"))
    )


def load_config() -> AgentConfig:
    """Load the strict telegram-to-agents configuration."""
    paths = resolve_paths()
    paths.config_path.parent.mkdir(parents=True, exist_ok=True)
    if paths.config_path.is_file():
        try:
            raw = json.loads(paths.config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise RuntimeError(f"Could not read {paths.config_path}: {exc}") from exc
        if not isinstance(raw, dict):
            raise RuntimeError(f"Configuration must be a JSON object: {paths.config_path}")
    else:
        raw = {}
    config = AgentConfig.model_validate(raw).model_copy(
        update={"state_home": str(paths.state_home)}
    )
    paths.state_home.mkdir(parents=True, exist_ok=True)
    paths.telegram_files_dir.mkdir(parents=True, exist_ok=True)
    return config


def _validate_config(config: AgentConfig) -> None:
    if not config.telegram_token or not config.allowed_user_ids:
        raise ValueError("Telegram token and at least one allowed user are required")
    project = config.project_root.strip()
    if not project or not Path(project).expanduser().is_dir():
        raise ValueError(f"Project directory does not exist: {project!r}")


def _configure_logging(config: AgentConfig) -> None:
    level = getattr(logging, config.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


async def run_bot(config: AgentConfig) -> int:
    """Run exactly one Telegram gateway, with no gateway agent supervisor."""
    from telegram_to_agents.infra.pidlock import acquire_lock, release_lock
    from telegram_to_agents.messenger.telegram.app import TelegramBot

    _validate_config(config)
    _configure_logging(config)
    paths = resolve_paths(state_home=config.state_home)
    acquire_lock(pid_file=paths.state_home / "bot.pid", kill_existing=True)
    runtime = TelegramBot(config)
    current = asyncio.current_task()
    loop = asyncio.get_running_loop()
    installed: list[signal.Signals] = []

    def _cancel() -> None:
        if current and not current.done():
            current.cancel()

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, _cancel)
        except (NotImplementedError, RuntimeError, ValueError):
            continue
        installed.append(sig)
    try:
        return await runtime.run()
    except asyncio.CancelledError:
        return 0
    finally:
        for sig in installed:
            loop.remove_signal_handler(sig)
        await runtime.shutdown()
        release_lock(pid_file=paths.state_home / "bot.pid")


def _run_gateway() -> None:
    from telegram_to_agents.cli.init_wizard import run_onboarding

    if not _is_configured() and run_onboarding():
        return
    raise SystemExit(asyncio.run(run_bot(load_config())))


def main() -> None:
    """Dispatch focused lifecycle commands or run the gateway."""
    args = sys.argv[1:]
    if "--version" in args or "-V" in args:
        from telegram_to_agents import __version__

        _console.print(f"telegram-to-agents {__version__}")
        return
    if "help" in args or "-h" in args or "--help" in args:
        _console.print(
            "telegram-to-agents [onboarding|reset|status|stop|restart]\n"
            "With no command, run the native-harness Telegram gateway.",
            markup=False,
        )
        return
    command = next((arg for arg in args if not arg.startswith("-")), "")
    handlers: dict[str, Callable[[], None]] = {
        "onboarding": lambda: __import__(
            "telegram_to_agents.cli.init_wizard", fromlist=["run_onboarding"]
        ).run_onboarding(),
        "reset": lambda: __import__(
            "telegram_to_agents.cli.init_wizard", fromlist=["run_onboarding"]
        ).run_onboarding(),
        "status": lambda: __import__(
            "telegram_to_agents.cli_commands.status", fromlist=["print_status"]
        ).print_status(),
        "stop": lambda: __import__(
            "telegram_to_agents.cli_commands.lifecycle", fromlist=["stop_bot"]
        ).stop_bot(),
        "restart": lambda: __import__(
            "telegram_to_agents.cli_commands.lifecycle", fromlist=["cmd_restart"]
        ).cmd_restart(),
    }
    handler = handlers.get(command)
    if handler:
        handler()
        return
    _run_gateway()


if __name__ == "__main__":
    main()
