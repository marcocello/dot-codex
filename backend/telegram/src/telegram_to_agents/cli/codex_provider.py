"""Native Codex App Server execution through an automatically selected transport."""

from __future__ import annotations

import logging
import os
import stat
import sys
from collections.abc import AsyncGenerator
from pathlib import Path
from shutil import which

from telegram_to_agents.cli.base import BaseCLI, CLIConfig, format_cli_cmd
from telegram_to_agents.cli.codex_events import CodexThinkingFilter, parse_codex_stream_event
from telegram_to_agents.cli.executor import (
    SubprocessResult,
    SubprocessSpec,
    run_streaming_subprocess,
)
from telegram_to_agents.cli.stream_events import (
    AssistantTextDelta,
    ResultEvent,
    StreamEvent,
    SystemInitEvent,
)
from telegram_to_agents.cli.types import (
    AgentRequest,
    Attachment,
    CodexTransport,
    UserTurn,
    text_with_attachment_lines,
)

logger = logging.getLogger(__name__)
_NO_FINAL_RESPONSE = "Codex failed before producing a final response."


def codex_control_socket() -> Path:
    """Return the canonical native Remote Control socket for this environment."""
    configured_home = os.environ.get("CODEX_HOME", "").strip()
    codex_home = Path(configured_home).expanduser() if configured_home else Path.home() / ".codex"
    return codex_home / "app-server-control" / "app-server-control.sock"


def resolve_codex_transport() -> CodexTransport:
    """Use Remote Control only when its canonical path is an actual Unix socket."""
    try:
        is_socket = stat.S_ISSOCK(codex_control_socket().stat().st_mode)
    except OSError:
        is_socket = False
    return "managed" if is_socket else "embedded"


class _StreamState:
    def __init__(self) -> None:
        self.text: list[str] = []
        self.thread_id: str | None = None
        self.transport: CodexTransport | None = None
        self.error: str | None = None

    def track(self, event: StreamEvent) -> None:
        if isinstance(event, SystemInitEvent) and event.session_id:
            self.thread_id = event.session_id
            self.transport = event.session_backend or self.transport
        elif isinstance(event, AssistantTextDelta) and event.text:
            self.text.append(event.text)
        elif isinstance(event, ResultEvent) and event.is_error and event.result:
            self.error = event.result


class CodexCLI(BaseCLI):
    """Send one exact turn to an app-visible native Codex thread."""

    def __init__(self, config: CLIConfig) -> None:
        self._config = config
        self._working_dir = Path(config.working_dir).expanduser().resolve()
        if not self._working_dir.is_dir():
            raise ValueError(f"project directory does not exist: {self._working_dir}")
        binary = which("codex")
        if not binary:
            raise FileNotFoundError("codex CLI not found on PATH")
        self._cli = binary

    def _build_command(self, request: AgentRequest, images: tuple[Attachment, ...]) -> list[str]:
        transport = resolve_codex_transport()
        command = [
            sys.executable,
            "-m",
            "telegram_to_agents.cli.codex_appserver_bridge",
            "--codex-bin",
            self._cli,
            "--cwd",
            str(self._working_dir),
            "--transport",
            transport,
        ]
        if request.resume_session:
            command.extend(("--resume", request.resume_session))
        if request.resume_backend:
            command.extend(("--resume-transport", request.resume_backend))
        for image in images:
            command.extend(("--image", str(image.path.resolve())))
        return command

    def send_streaming(self, request: AgentRequest) -> AsyncGenerator[StreamEvent, None]:
        return self._stream(request)

    async def _stream(self, request: AgentRequest) -> AsyncGenerator[StreamEvent, None]:
        images, other = _partition_attachments(request.turn.attachments)
        text_turn = UserTurn(text=request.turn.text, attachments=other)
        command = self._build_command(request, images)
        logger.info("Codex stream cmd: %s", format_cli_cmd(command))
        state = _StreamState()
        thinking_filter = CodexThinkingFilter()

        async def line_handler(line: str) -> AsyncGenerator[StreamEvent, None]:
            if not line:
                return
            for raw_event in parse_codex_stream_event(line):
                for event in thinking_filter.process(raw_event):
                    state.track(event)
                    yield event
            for event in thinking_filter.flush():
                state.track(event)
                yield event

        async def post_handler(result: SubprocessResult) -> AsyncGenerator[StreamEvent, None]:
            detail = state.error or "\n".join(state.text)
            if result.process.returncode != 0:
                stderr = result.stderr_bytes.decode(errors="replace")[:2000].strip()
                yield ResultEvent(
                    type="result",
                    result=detail or stderr or _NO_FINAL_RESPONSE,
                    is_error=True,
                    returncode=result.process.returncode,
                    session_id=state.thread_id,
                    session_backend=state.transport,
                )
                return
            yield ResultEvent(
                type="result",
                session_id=state.thread_id,
                session_backend=state.transport,
                result=detail,
                returncode=result.process.returncode,
            )

        async for event in run_streaming_subprocess(
            config=self._config,
            spec=SubprocessSpec(
                exec_cmd=command,
                use_cwd=str(self._working_dir),
                timeout_seconds=request.timeout_seconds,
                stdin_text=text_with_attachment_lines(text_turn),
            ),
            line_handler=line_handler,
            provider_label="Codex App Server",
            post_handler=post_handler,
        ):
            yield event


def _partition_attachments(
    attachments: tuple[Attachment, ...],
) -> tuple[tuple[Attachment, ...], tuple[Attachment, ...]]:
    images = tuple(item for item in attachments if item.media_type.startswith("image/"))
    other = tuple(item for item in attachments if not item.media_type.startswith("image/"))
    return images, other
