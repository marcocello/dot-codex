"""Telegram chat/topic session coordinates."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SessionKey:
    """Identify one Telegram chat and optional forum topic."""

    chat_id: int
    topic_id: int | None = None

    @property
    def storage_key(self) -> str:
        if self.topic_id is None:
            return f"tg:{self.chat_id}"
        return f"tg:{self.chat_id}:{self.topic_id}"

    @property
    def lock_key(self) -> tuple[int, int | None]:
        return (self.chat_id, self.topic_id)

    @classmethod
    def telegram(cls, chat_id: int, topic_id: int | None = None) -> SessionKey:
        return cls(chat_id=chat_id, topic_id=topic_id)

    @classmethod
    def parse(cls, raw: str) -> SessionKey:
        """Parse a canonical Telegram session key."""
        parts = raw.split(":")
        try:
            if len(parts) == 2 and parts[0] == "tg":
                return cls(chat_id=int(parts[1]))
            if len(parts) == 3 and parts[0] == "tg":
                return cls(chat_id=int(parts[1]), topic_id=int(parts[2]))
        except ValueError as exc:
            raise ValueError(f"Invalid Telegram session key: {raw!r}") from exc
        raise ValueError(f"Invalid Telegram session key: {raw!r}")
