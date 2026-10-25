"""Focused onboarding for Telegram, a native harness, and transcription."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal, NoReturn, TypedDict, cast

import questionary
from rich.console import Console
from rich.panel import Panel

from telegram_to_agents.cli.auth import AuthStatus, check_auth
from telegram_to_agents.config import AgentConfig, TranscriptionConfig
from telegram_to_agents.infra.atomic_io import atomic_text_save
from telegram_to_agents.infra.json_store import atomic_json_save
from telegram_to_agents.workspace.paths import resolve_paths

_TOKEN_PATTERN = re.compile(r"^\d{8,}:[A-Za-z0-9_-]{30,}$")


class _WizardConfig(TypedDict, total=False):
    provider: Literal["codex", "claude"]
    telegram_token: str
    allowed_user_ids: list[int]
    project_root: str
    automatic_audio: bool
    openai_api_key: str


def _abort() -> NoReturn:
    raise SystemExit(0)


def _ask_provider() -> Literal["codex", "claude"]:
    value = questionary.select(
        "Native harness",
        choices=[
            questionary.Choice("Codex", value="codex"),
            questionary.Choice("Claude", value="claude"),
        ],
    ).ask()
    if value is None:
        _abort()
    if value not in {"codex", "claude"}:
        raise ValueError(f"Unsupported provider: {value}")
    return cast("Literal['codex', 'claude']", value)


def _check_provider(console: Console, provider: Literal["codex", "claude"]) -> bool:
    """Require the selected authenticated native CLI."""
    result = check_auth(provider)
    label = provider.capitalize()
    if result.status == AuthStatus.AUTHENTICATED:
        console.print(f"[green]Native {label} is authenticated.[/green]")
        return True
    if result.status == AuthStatus.INSTALLED:
        login = "codex login" if provider == "codex" else "claude auth login"
        console.print(f"[red]{label} is installed but not logged in. Run `{login}`.[/red]")
    else:
        console.print(f"[red]{label} CLI was not found.[/red]")
    return False


def _ask_telegram_token(console: Console) -> str:
    while True:
        value = questionary.password("Telegram bot token").ask()
        if value is None:
            _abort()
        token = cast("str", value).strip()
        if _TOKEN_PATTERN.match(token):
            return token
        console.print("[red]That Telegram bot token is not valid.[/red]")


def _ask_user_id(console: Console) -> list[int]:
    while True:
        value = questionary.text("Your numeric Telegram user ID").ask()
        if value is None:
            _abort()
        try:
            return [int(value.strip())]
        except ValueError:
            console.print("[red]Enter a numeric Telegram user ID.[/red]")


def _ask_project_folder(console: Console) -> str:
    while True:
        value = questionary.path("Existing project directory").ask()
        if value is None:
            _abort()
        path = Path(value).expanduser()
        if path.is_dir():
            return str(path.resolve())
        console.print("[red]Choose an existing project directory.[/red]")


def _ask_audio_transcription() -> tuple[bool, str]:
    enabled = questionary.confirm(
        "Automatically transcribe Telegram voice notes and audio?",
        default=True,
    ).ask()
    if enabled is None:
        _abort()
    if not enabled:
        return False, ""
    key = questionary.password(
        "OpenAI API key for transcription (leave blank to use OPENAI_API_KEY)"
    ).ask()
    if key is None:
        _abort()
    return True, key.strip()


def _write_env_value(path: Path, key: str, value: str) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        lines = []
    pattern = re.compile(rf"^(?:export\s+)?{re.escape(key)}\s*=")
    kept = [line for line in lines if not pattern.match(line.strip())]
    kept.append(f"{key}={value}")
    atomic_text_save(path, "\n".join(kept) + "\n")
    path.chmod(0o600)


def _write_config(cfg: _WizardConfig) -> Path:
    paths = resolve_paths()
    project = Path(cfg.get("project_root", "")).expanduser()
    if not project.is_dir():
        raise ValueError(f"Project directory does not exist: {project}")
    config = AgentConfig(
        provider=cfg.get("provider", "codex"),
        telegram_token=cfg.get("telegram_token", ""),
        allowed_user_ids=cfg.get("allowed_user_ids", []),
        project_root=str(project.resolve()),
        transcription=TranscriptionConfig(
            automatic_audio=cfg.get("automatic_audio", False),
        ),
    )
    paths.config_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_json_save(paths.config_path, config.model_dump(mode="json"))
    if key := cfg.get("openai_api_key", "").strip():
        _write_env_value(paths.env_file, "OPENAI_API_KEY", key)
    return paths.config_path


def _offer_service_install() -> bool:
    from telegram_to_agents.infra.service import install_service, is_service_available

    if not is_service_available():
        return False
    choice = questionary.confirm("Install and start as a background service?", default=True).ask()
    if choice:
        install_service()
        return True
    return False


def run_onboarding() -> bool:
    """Collect only settings owned by the focused gateway."""
    console = Console()
    console.print(
        Panel(
            "Telegram transports messages; the native harness owns prompts, tools, permissions, and configuration.",
            title="Native-harness Telegram gateway",
        )
    )
    provider = _ask_provider()
    if not _check_provider(console, provider):
        raise SystemExit(1)
    token = _ask_telegram_token(console)
    users = _ask_user_id(console)
    project = _ask_project_folder(console)
    automatic_audio, api_key = _ask_audio_transcription()
    _write_config(
        _WizardConfig(
            provider=provider,
            telegram_token=token,
            allowed_user_ids=users,
            project_root=project,
            automatic_audio=automatic_audio,
            openai_api_key=api_key,
        )
    )
    return _offer_service_install()
