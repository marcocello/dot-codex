"""Paths owned by the Telegram gateway."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_STATE_HOME_ENV = "TELEGRAM_TO_AGENTS_HOME"
_STATE_HOME_NAME = ".telegram-to-agents"


@dataclass(frozen=True, slots=True)
class GatewayPaths:
    """Persistent gateway state rooted at ``state_home``."""

    state_home: Path

    @property
    def config_path(self) -> Path:
        return self.state_home / "config" / "config.json"

    @property
    def sessions_path(self) -> Path:
        return self.state_home / "sessions.json"

    @property
    def telegram_files_dir(self) -> Path:
        return self.state_home / "telegram_files"

    @property
    def env_file(self) -> Path:
        return self.state_home / ".env"

    @property
    def logs_dir(self) -> Path:
        return self.state_home / "logs"


def resolve_paths(
    state_home: str | Path | None = None,
) -> GatewayPaths:
    """Resolve state paths from explicit inputs or the service environment."""
    raw_home = state_home or os.environ.get(_STATE_HOME_ENV)
    if raw_home is None:
        raw_home = Path.home() / _STATE_HOME_NAME
    home = Path(raw_home).expanduser().resolve()
    return GatewayPaths(home)
