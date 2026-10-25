"""Native Claude execution with no gateway agent-policy overrides."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from pathlib import Path
from shutil import which

from telegram_to_agents.cli.base import BaseCLI, CLIConfig, format_cli_cmd
from telegram_to_agents.cli.executor import SubprocessSpec, run_streaming_subprocess
from telegram_to_agents.cli.stream_events import StreamEvent, parse_claude_stream_event
from telegram_to_agents.cli.types import AgentRequest, text_with_attachment_lines

logger = logging.getLogger(__name__)


class ClaudeCLI(BaseCLI):
    """Send one exact turn through Claude Code's native configuration."""

    def __init__(self, config: CLIConfig) -> None:
        self._config = config
        self._working_dir = Path(config.working_dir).expanduser().resolve()
        if not self._working_dir.is_dir():
            raise ValueError(f"project directory does not exist: {self._working_dir}")
        binary = which("claude")
        if not binary:
            raise FileNotFoundError("claude CLI not found on PATH")
        self._cli = binary

    def _build_command(self, resume_session: str | None) -> list[str]:
        command = [self._cli, "--verbose", "-p", "--output-format", "stream-json"]
        if resume_session:
            command.extend(("--resume", resume_session))
        return command

    def send_streaming(self, request: AgentRequest) -> AsyncGenerator[StreamEvent, None]:
        return self._stream(request)

    async def _stream(self, request: AgentRequest) -> AsyncGenerator[StreamEvent, None]:
        command = self._build_command(request.resume_session)
        logger.info("Claude stream cmd: %s", format_cli_cmd(command))

        async def line_handler(line: str) -> AsyncGenerator[StreamEvent, None]:
            for event in parse_claude_stream_event(line):
                yield event

        async for event in run_streaming_subprocess(
            config=self._config,
            spec=SubprocessSpec(
                exec_cmd=command,
                use_cwd=str(self._working_dir),
                timeout_seconds=request.timeout_seconds,
                stdin_text=text_with_attachment_lines(request.turn),
            ),
            line_handler=line_handler,
            provider_label="Claude",
        ):
            yield event
