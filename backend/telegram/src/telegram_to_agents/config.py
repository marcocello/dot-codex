"""Focused configuration for the native-harness Telegram gateway."""

from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class TimeoutConfig(BaseModel):
    """Fixed timeout for one foreground native-harness turn."""

    model_config = ConfigDict(extra="forbid")

    normal: float = Field(default=1800.0, gt=0)


class TranscriptionConfig(BaseModel):
    """Optional automatic transcription for Telegram voice and audio."""

    model_config = ConfigDict(extra="forbid")

    automatic_audio: bool = False
    model: str = "gpt-4o-transcribe"
    timeout_seconds: float = Field(default=120.0, gt=0)


class SceneConfig(BaseModel):
    """Telegram-only progress presentation settings."""

    model_config = ConfigDict(extra="forbid")

    status_reaction: bool = True


class AgentConfig(BaseModel):
    """The complete public gateway configuration."""

    model_config = ConfigDict(extra="forbid")

    provider: Literal["codex", "claude"] = "codex"
    telegram_token: str = ""
    allowed_user_ids: list[int] = Field(default_factory=list)
    allowed_group_ids: list[int] = Field(default_factory=list)
    allowed_channel_ids: list[int] = Field(default_factory=list)
    group_mention_only: bool = False
    file_access: Literal["all", "workspace", "none"] = "all"
    project_root: str = ""
    project_roots: dict[str, str] = Field(default_factory=dict)
    timeouts: TimeoutConfig = Field(default_factory=TimeoutConfig)
    transcription: TranscriptionConfig = Field(default_factory=TranscriptionConfig)
    scene: SceneConfig = Field(default_factory=SceneConfig)
    state_home: str = "~/.telegram-to-agents"
    log_level: str = "INFO"
