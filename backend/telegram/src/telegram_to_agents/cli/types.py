"""Small value objects shared by the Telegram and native-harness boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

CodexTransport = Literal["managed", "embedded"]


@dataclass(frozen=True, slots=True)
class Attachment:
    """One unchanged Telegram attachment available at an absolute local path."""

    path: Path
    media_type: str


@dataclass(frozen=True, slots=True)
class UserTurn:
    """User-authored text plus transport-native attachments."""

    text: str = ""
    attachments: tuple[Attachment, ...] = ()


@dataclass(frozen=True, slots=True)
class AgentRequest:
    """Transport coordinates for one exact provider-native turn."""

    turn: UserTurn
    chat_id: int = 0
    topic_id: int | None = None
    resume_session: str | None = None
    resume_backend: CodexTransport | None = None
    timeout_seconds: float | None = None


@dataclass(frozen=True, slots=True)
class AgentResponse:
    """Terminal result needed by Telegram and session persistence."""

    result: str
    session_id: str | None = None
    session_backend: CodexTransport | None = None
    is_error: bool = False
    timed_out: bool = False


def text_with_attachment_lines(turn: UserTurn) -> str:
    """Serialize attachments for harnesses without native local-file input."""
    lines = [
        f"[Telegram attachment: {item.path.resolve()}; type={item.media_type}]"
        for item in turn.attachments
    ]
    if not lines:
        return turn.text
    attachment_text = "\n".join(lines)
    return f"{turn.text}\n\n{attachment_text}" if turn.text else attachment_text
