"""Persistent Telegram-to-native-harness session mappings."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from telegram_to_agents.cli.types import CodexTransport
from telegram_to_agents.infra.json_store import atomic_json_save, load_json
from telegram_to_agents.session.key import SessionKey

Provider = Literal["codex", "claude"]
TopicNameResolver = Callable[[int, int], str | None]


@dataclass(slots=True)
class SessionData:
    """The one provider-native session owned by a Telegram chat/topic."""

    chat_id: int
    provider: Provider
    topic_id: int | None = None
    topic_name: str | None = None
    session_id: str = ""
    session_backend: CodexTransport | None = None

    @property
    def session_key(self) -> SessionKey:
        return SessionKey.telegram(self.chat_id, self.topic_id)


class SessionManager:
    """Atomically manage provider-safe native sessions."""

    def __init__(self, sessions_path: Path, provider: Provider) -> None:
        self._path = sessions_path
        self._provider = provider
        self._lock = asyncio.Lock()
        self._topic_name_resolver: TopicNameResolver | None = None

    def set_topic_name_resolver(self, resolver: TopicNameResolver) -> None:
        self._topic_name_resolver = resolver

    def resolve_topic_name(self, chat_id: int, topic_id: int | None) -> str | None:
        if topic_id is None:
            return None
        if self._topic_name_resolver:
            current = self._topic_name_resolver(chat_id, topic_id)
            if current:
                return current
        sessions = self._load()
        persisted = sessions.get(SessionKey.telegram(chat_id, topic_id).storage_key)
        return persisted.topic_name if persisted else None

    async def resolve_session(self, key: SessionKey) -> tuple[SessionData, bool]:
        async with self._lock:
            sessions = self._load()
            changed = False
            session = sessions.get(key.storage_key)
            if session is None or session.provider != self._provider:
                session = SessionData(
                    chat_id=key.chat_id,
                    topic_id=key.topic_id,
                    topic_name=session.topic_name if session else None,
                    provider=self._provider,
                )
                sessions[key.storage_key] = session
                changed = True
            current_name = self._resolved_name(key, session.topic_name)
            if current_name != session.topic_name:
                session.topic_name = current_name
                changed = True
            if changed:
                self._save(sessions)
            return session, not bool(session.session_id)

    async def get_active(self, key: SessionKey) -> SessionData | None:
        sessions = self._load()
        session = sessions.get(key.storage_key)
        if session is not None and session.provider != self._provider:
            session = None
        return session

    async def reset_session(self, key: SessionKey) -> SessionData:
        async with self._lock:
            sessions = self._load()
            previous = sessions.get(key.storage_key)
            session = SessionData(
                chat_id=key.chat_id,
                topic_id=key.topic_id,
                topic_name=self._resolved_name(key, previous.topic_name if previous else None),
                provider=self._provider,
            )
            sessions[key.storage_key] = session
            self._save(sessions)
            return session

    async def update_session(
        self,
        session: SessionData,
        session_id: str | None,
        session_backend: CodexTransport | None = None,
    ) -> None:
        if not session_id:
            return
        async with self._lock:
            sessions = self._load()
            current = sessions.get(session.session_key.storage_key, session)
            current.provider = self._provider
            current.session_id = session_id
            current.session_backend = (
                session_backend or current.session_backend or "managed"
                if self._provider == "codex"
                else None
            )
            sessions[current.session_key.storage_key] = current
            self._save(sessions)
            session.provider = current.provider
            session.session_id = current.session_id
            session.session_backend = current.session_backend

    def _resolved_name(self, key: SessionKey, fallback: str | None) -> str | None:
        if key.topic_id is not None and self._topic_name_resolver:
            return self._topic_name_resolver(key.chat_id, key.topic_id) or fallback
        return fallback

    def _load(self) -> dict[str, SessionData]:
        raw = load_json(self._path)
        if raw is None:
            return {}
        if not isinstance(raw, dict):
            raise TypeError(f"Session store must be a JSON object: {self._path}")
        sessions: dict[str, SessionData] = {}
        for storage_key, value in raw.items():
            if not isinstance(storage_key, str) or not isinstance(value, dict):
                raise TypeError(f"Invalid session record at {storage_key!r}")
            key = SessionKey.parse(storage_key)
            session = self._from_raw(key, value)
            if storage_key != key.storage_key:
                raise ValueError(f"Non-canonical session key: {storage_key!r}")
            sessions[storage_key] = session
        return sessions

    def _from_raw(self, key: SessionKey, raw: dict[str, object]) -> SessionData:
        expected_fields = set(SessionData.__dataclass_fields__)
        if set(raw) != expected_fields:
            raise ValueError(f"Session record must contain exactly {sorted(expected_fields)}")
        chat_id = raw["chat_id"]
        topic_id = raw["topic_id"]
        topic_name = raw["topic_name"]
        provider = raw["provider"]
        session_id = raw["session_id"]
        session_backend = raw["session_backend"]
        if type(chat_id) is not int or chat_id != key.chat_id:
            raise ValueError("Session chat_id does not match its key")
        if topic_id is not None and type(topic_id) is not int:
            raise ValueError("Session topic_id must be an integer or null")
        if topic_id != key.topic_id:
            raise ValueError("Session topic_id does not match its key")
        if topic_name is not None and not isinstance(topic_name, str):
            raise ValueError("Session topic_name must be a string or null")
        if provider not in {"codex", "claude"}:
            raise ValueError("Session provider must be codex or claude")
        if not isinstance(session_id, str):
            raise TypeError("Session session_id must be a string")
        if session_backend not in {None, "managed", "embedded"}:
            raise ValueError("Session backend must be managed, embedded, or null")
        if provider != "codex" and session_backend is not None:
            raise ValueError("Only Codex sessions may have a transport backend")
        return SessionData(
            chat_id=chat_id,
            topic_id=topic_id,
            topic_name=topic_name,
            provider=provider,  # type: ignore[arg-type]
            session_id=session_id,
            session_backend=session_backend,  # type: ignore[arg-type]
        )

    def _save(self, sessions: dict[str, SessionData]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        atomic_json_save(self._path, {key: asdict(value) for key, value in sessions.items()})
