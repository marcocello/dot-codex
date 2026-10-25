"""At-most-once execution through the selected native harness."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Literal

from telegram_to_agents.cli.base import BaseCLI, CLIConfig
from telegram_to_agents.cli.claude_provider import ClaudeCLI
from telegram_to_agents.cli.codex_provider import CodexCLI
from telegram_to_agents.cli.process_registry import ProcessRegistry
from telegram_to_agents.cli.stream_events import (
    ProgressUpdateEvent,
    ResultEvent,
    StreamEvent,
    SystemInitEvent,
    SystemStatusEvent,
    ThinkingEvent,
    ToolUseEvent,
)
from telegram_to_agents.cli.types import AgentRequest, AgentResponse, CodexTransport

logger = logging.getLogger(__name__)
Provider = Literal["codex", "claude"]
ToolCallback = Callable[[ToolUseEvent], Awaitable[None]]
StatusCallback = Callable[[str | None], Awaitable[None]]
TextCallback = Callable[[str], Awaitable[None]]


@dataclass(frozen=True, slots=True)
class CLIServiceConfig:
    """Only provider selection and project location are gateway-owned."""

    provider: Provider
    working_dir: str


class _StreamState:
    def __init__(self) -> None:
        self.session_id: str | None = None
        self.session_backend: CodexTransport | None = None
        self.result: ResultEvent | None = None

    async def consume(
        self,
        event: StreamEvent,
        *,
        on_tool: ToolCallback | None,
        on_status: StatusCallback | None,
        on_progress: TextCallback | None,
    ) -> None:
        if isinstance(event, SystemInitEvent):
            self.session_id = event.session_id or self.session_id
            self.session_backend = event.session_backend or self.session_backend
        elif isinstance(event, ResultEvent):
            self.result = event
            self.session_id = event.session_id or self.session_id
            self.session_backend = event.session_backend or self.session_backend
        elif isinstance(event, ToolUseEvent) and on_tool:
            await on_tool(event)
        elif isinstance(event, ProgressUpdateEvent) and on_progress and event.text:
            await on_progress(event.text)
        elif isinstance(event, SystemStatusEvent) and on_status:
            await on_status(event.status)
        elif isinstance(event, ThinkingEvent) and on_status:
            await on_status("thinking")


class CLIService:
    """Execute each Telegram update exactly once through Codex or Claude."""

    def __init__(self, *, config: CLIServiceConfig, process_registry: ProcessRegistry) -> None:
        self._config = config
        self._process_registry = process_registry
        self._working_dir_resolver: Callable[[AgentRequest], str | None] | None = None

    def set_working_dir_resolver(self, resolver: Callable[[AgentRequest], str | None]) -> None:
        self._working_dir_resolver = resolver

    def _make_cli(self, request: AgentRequest) -> BaseCLI:
        working_dir = self._config.working_dir
        if self._working_dir_resolver:
            working_dir = self._working_dir_resolver(request) or working_dir
        cli_config = CLIConfig(
            working_dir=working_dir,
            process_registry=self._process_registry,
            chat_id=request.chat_id,
            topic_id=request.topic_id,
        )
        return CodexCLI(cli_config) if self._config.provider == "codex" else ClaudeCLI(cli_config)

    async def execute(
        self,
        request: AgentRequest,
        *,
        on_tool_activity: ToolCallback | None = None,
        on_system_status: StatusCallback | None = None,
        on_progress_update: TextCallback | None = None,
    ) -> AgentResponse:
        self._process_registry.clear_topic_abort(request.chat_id, request.topic_id)
        state = _StreamState()
        try:
            async for event in self._make_cli(request).send_streaming(request):
                if self._process_registry.was_aborted_topic(request.chat_id, request.topic_id):
                    return AgentResponse(
                        result="",
                        session_id=state.session_id,
                        session_backend=state.session_backend,
                    )
                await state.consume(
                    event,
                    on_tool=on_tool_activity,
                    on_status=on_system_status,
                    on_progress=on_progress_update,
                )
        except asyncio.CancelledError:
            raise
        except (OSError, RuntimeError, ValueError, UnicodeDecodeError) as exc:
            logger.exception("%s stream failed", self._config.provider)
            return AgentResponse(
                result=f"The {self._config.provider} turn failed: {exc}",
                session_id=state.session_id,
                session_backend=state.session_backend,
                is_error=True,
            )
        finally:
            aborted = self._process_registry.was_aborted_topic(request.chat_id, request.topic_id)
            self._process_registry.clear_topic_abort(request.chat_id, request.topic_id)

        if aborted:
            return AgentResponse(
                result="",
                session_id=state.session_id,
                session_backend=state.session_backend,
            )
        if state.result is None:
            return AgentResponse(
                result=f"The {self._config.provider} turn ended without a final response.",
                session_id=state.session_id,
                session_backend=state.session_backend,
                is_error=True,
            )
        if state.result.result.startswith("__TIMEOUT__"):
            seconds = state.result.result.removeprefix("__TIMEOUT__") or "the configured limit"
            return AgentResponse(
                result=f"The {self._config.provider} turn timed out after {seconds} seconds.",
                session_id=state.session_id,
                session_backend=state.session_backend,
                is_error=True,
                timed_out=True,
            )
        return AgentResponse(
            result=state.result.result,
            session_id=state.session_id,
            session_backend=state.session_backend,
            is_error=state.result.is_error,
        )
