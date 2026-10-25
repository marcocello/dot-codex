"""Thin Telegram-to-native-harness orchestration."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from telegram_to_agents.cli.process_registry import ProcessRegistry
from telegram_to_agents.cli.service import CLIService, CLIServiceConfig
from telegram_to_agents.cli.stream_events import ToolUseEvent
from telegram_to_agents.cli.types import AgentRequest, AgentResponse, UserTurn
from telegram_to_agents.config import AgentConfig
from telegram_to_agents.session.key import SessionKey
from telegram_to_agents.session.manager import SessionData, SessionManager
from telegram_to_agents.workspace.paths import GatewayPaths, resolve_paths
from telegram_to_agents.workspace.project_roots import (
    resolve_default_project_root,
    resolve_project_root,
)

TextCallback = Callable[[str], Awaitable[None]]
ToolCallback = Callable[[ToolUseEvent], Awaitable[None]]
StatusCallback = Callable[[str | None], Awaitable[None]]


@dataclass(frozen=True, slots=True)
class OrchestratorResult:
    """Final text consumed by Telegram delivery."""

    text: str


class Orchestrator:
    """Preserve transport/session state while the harness owns agent behavior."""

    def __init__(self, config: AgentConfig, paths: GatewayPaths) -> None:
        self._config = config
        self._paths = paths
        self._sessions = SessionManager(paths.sessions_path, config.provider)
        self._process_registry = ProcessRegistry()
        self._turn_locks: dict[tuple[int, int | None], asyncio.Lock] = {}
        fallback = resolve_default_project_root(config.project_root)
        if fallback is None:
            raise ValueError(f"Project directory does not exist: {config.project_root!r}")
        self._default_project_root = fallback
        self._cli_service = CLIService(
            config=CLIServiceConfig(provider=config.provider, working_dir=fallback),
            process_registry=self._process_registry,
        )
        self._cli_service.set_working_dir_resolver(self._resolve_request_working_dir)

    @classmethod
    async def create(cls, config: AgentConfig, **kwargs: object) -> Orchestrator:
        paths = resolve_paths(state_home=config.state_home)
        paths.state_home.mkdir(parents=True, exist_ok=True)
        paths.telegram_files_dir.mkdir(parents=True, exist_ok=True)
        return cls(config, paths, **kwargs)

    @property
    def paths(self) -> GatewayPaths:
        return self._paths

    def set_topic_name_resolver(self, resolver: Callable[[int, int], str | None]) -> None:
        self._sessions.set_topic_name_resolver(resolver)

    def project_root(self, key: SessionKey) -> str:
        topic_name = self._sessions.resolve_topic_name(key.chat_id, key.topic_id)
        return (
            resolve_project_root(
                self._config.project_roots,
                chat_id=key.chat_id,
                topic_id=key.topic_id,
                topic_name=topic_name,
            )
            or self._default_project_root
        )

    def _resolve_request_working_dir(self, request: AgentRequest) -> str:
        return self.project_root(SessionKey.telegram(request.chat_id, request.topic_id))

    async def handle_message(
        self,
        key: SessionKey,
        turn: UserTurn,
        *,
        on_tool_activity: ToolCallback | None = None,
        on_system_status: StatusCallback | None = None,
        on_progress_update: TextCallback | None = None,
    ) -> OrchestratorResult:
        async with self._turn_locks.setdefault(key.lock_key, asyncio.Lock()):
            session, _ = await self._sessions.resolve_session(key)
            response = await self._cli_service.execute(
                self._request(key, turn, session),
                on_tool_activity=on_tool_activity,
                on_system_status=on_system_status,
                on_progress_update=on_progress_update,
            )
            await self._persist_response(session, response)
            return OrchestratorResult(text=response.result)

    def _request(self, key: SessionKey, turn: UserTurn, session: SessionData) -> AgentRequest:
        return AgentRequest(
            turn=turn,
            chat_id=key.chat_id,
            topic_id=key.topic_id,
            resume_session=session.session_id or None,
            resume_backend=session.session_backend,
            timeout_seconds=self._config.timeouts.normal,
        )

    async def _persist_response(self, session: SessionData, response: AgentResponse) -> None:
        await self._sessions.update_session(
            session,
            response.session_id,
            response.session_backend,
        )

    async def reset_session(self, key: SessionKey) -> None:
        await self.abort(key.chat_id, key.topic_id)
        async with self._turn_locks.setdefault(key.lock_key, asyncio.Lock()):
            await self._sessions.reset_session(key)

    async def abort(self, chat_id: int, topic_id: int | None = None) -> int:
        return await self._process_registry.kill_by_chat_topic(chat_id, topic_id)

    def interrupt(self, chat_id: int) -> int:
        return self._process_registry.interrupt_all(chat_id)

    async def abort_all(self) -> int:
        return await self._process_registry.kill_all_active()

    def is_chat_busy(self, chat_id: int, topic_id: int | None = None) -> bool:
        return self._process_registry.has_active(chat_id, topic_id)

    async def status_text(self, key: SessionKey) -> str:
        session = await self._sessions.get_active(key)
        native_id = session.session_id if session and session.session_id else "new"
        provider = self._config.provider.capitalize()
        return f"{provider} session: {native_id}\nProject: {self.project_root(key)}"

    async def shutdown(self) -> None:
        await self.abort_all()
