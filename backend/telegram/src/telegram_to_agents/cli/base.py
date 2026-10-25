"""Minimal interface shared by the native Codex and Claude harnesses."""

from __future__ import annotations

import asyncio
import contextlib
import inspect
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from telegram_to_agents.cli._log_redact import redact_cmd_for_log
from telegram_to_agents.cli.stream_events import StreamEvent
from telegram_to_agents.cli.types import AgentRequest

if TYPE_CHECKING:
    from telegram_to_agents.cli.process_registry import ProcessRegistry


async def feed_stdin_and_close(process: asyncio.subprocess.Process, data: str) -> None:
    writer = process.stdin
    if writer is None:
        return
    with contextlib.suppress(BrokenPipeError, ConnectionResetError, RuntimeError, ValueError):
        writer.write(data.encode())
        result = writer.drain()
        if inspect.isawaitable(result):
            await result
    writer.close()
    with contextlib.suppress(BrokenPipeError, ConnectionResetError, RuntimeError, OSError):
        await writer.wait_closed()


def format_cli_cmd(cmd: list[str]) -> str:
    """Render a redacted command without exposing long argument values."""
    display = redact_cmd_for_log(cmd)
    return " ".join(value[:80] + "..." if len(value) > 80 else value for value in display)


@dataclass(slots=True)
class CLIConfig:
    """Gateway-owned process coordinates; harnesses own agent configuration."""

    working_dir: str | Path = "."
    process_registry: ProcessRegistry | None = None
    chat_id: int = 0
    topic_id: int | None = None


class BaseCLI(ABC):
    """Streaming interface implemented by each retained native harness."""

    @abstractmethod
    def send_streaming(self, request: AgentRequest) -> AsyncGenerator[StreamEvent, None]: ...
