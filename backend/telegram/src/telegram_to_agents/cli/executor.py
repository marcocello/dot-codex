"""Native-harness subprocess lifecycle and fixed-timeout execution."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import AsyncGenerator, Callable
from dataclasses import dataclass

from telegram_to_agents.cli.base import CLIConfig, feed_stdin_and_close
from telegram_to_agents.cli.stream_events import ResultEvent, StreamEvent
from telegram_to_agents.infra.process_tree import force_kill_process_tree

logger = logging.getLogger(__name__)


def build_subprocess_env(_config: CLIConfig) -> dict[str, str]:
    """Return a clean native-harness environment.

    Gateway variables are removed. The inherited service environment remains
    native harness configuration; the gateway's private ``.env`` is never merged.
    """
    import os

    private_prefixes = ("TELEGRAM_TO_AGENTS_",)
    return {
        key: value for key, value in os.environ.items() if not key.startswith(private_prefixes)
    }


@dataclass(slots=True)
class SubprocessSpec:
    """Command, working directory, timeout, and exact stdin payload."""

    exec_cmd: list[str]
    use_cwd: str
    timeout_seconds: float | None = None
    stdin_text: str = ""


@dataclass(slots=True)
class SubprocessResult:
    """Outcome of a completed streaming subprocess."""

    process: asyncio.subprocess.Process
    stderr_bytes: bytes


# ---------------------------------------------------------------------------
# Streaming subprocess
# ---------------------------------------------------------------------------

LineHandler = Callable[[str], AsyncGenerator[StreamEvent, None]]
"""Async generator that receives a decoded stdout line and yields events."""

PostHandler = Callable[[SubprocessResult], AsyncGenerator[StreamEvent, None]]
"""Async generator that receives the subprocess result after stream ends."""


async def _default_post_handler(result: SubprocessResult) -> AsyncGenerator[StreamEvent, None]:
    """Yield an error ``ResultEvent`` when the process exited non-zero."""
    if result.process.returncode != 0:
        stderr_text = (
            result.stderr_bytes.decode(errors="replace")[:2000] if result.stderr_bytes else ""
        )
        yield ResultEvent(
            type="result",
            result=stderr_text[:500],
            is_error=True,
            returncode=result.process.returncode,
        )


async def run_streaming_subprocess(
    config: CLIConfig,
    spec: SubprocessSpec,
    line_handler: LineHandler,
    *,
    provider_label: str = "CLI",
    post_handler: PostHandler | None = None,
) -> AsyncGenerator[StreamEvent, None]:
    """Spawn a subprocess and stream stdout lines through *line_handler*.

    Lifecycle:
    1. Create subprocess with stdout/stderr pipes
    2. Feed stdin when requested
    3. Register in process registry
    4. Drain stderr in background task
    5. Stream stdout lines through *line_handler* with timeout
    6. On timeout: kill, yield error, return
    7. Cleanup: cancel drain, unregister tracked process
    8. Post-loop: delegate to *post_handler* (default: yield error on non-zero exit)
    """
    subprocess_env = build_subprocess_env(config) if spec.use_cwd else None
    process = await asyncio.create_subprocess_exec(
        *spec.exec_cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=spec.use_cwd,
        env=subprocess_env,
        limit=4 * 1024 * 1024,
    )
    if process.stdout is None or process.stderr is None:
        msg = "Subprocess created without stdout/stderr pipes"
        raise RuntimeError(msg)
    # Feed stdin concurrently with the stdout read loop: a prompt larger than
    # the OS pipe buffer (~64 KiB) would otherwise deadlock against a child
    # that starts emitting stdout before draining stdin.
    stdin_feed = asyncio.create_task(_feed_streaming_stdin(process, spec))
    logger.info("%s subprocess starting pid=%s", provider_label, process.pid)

    reg = config.process_registry
    tracked = reg.register(config.chat_id, process, topic_id=config.topic_id) if reg else None
    stderr_drain = asyncio.create_task(process.stderr.read())

    try:
        async for event in _stream_with_timeout(process, spec, line_handler):
            yield event
        stderr_bytes = await stderr_drain
    except TimeoutError:
        force_kill_process_tree(process.pid)
        await process.wait()
        timeout_s = spec.timeout_seconds or 0
        logger.warning("%s stream timed out after %.0fs", provider_label, timeout_s)
        yield ResultEvent(
            type="result",
            result=f"__TIMEOUT__{int(timeout_s)}",
            is_error=True,
        )
        return
    finally:
        if not stdin_feed.done():
            stdin_feed.cancel()
        with contextlib.suppress(BaseException):
            await stdin_feed
        await _cancel_drain(stderr_drain)
        if tracked and reg:
            reg.unregister(tracked)

    await process.wait()

    handler = post_handler or _default_post_handler
    async for event in handler(SubprocessResult(process=process, stderr_bytes=stderr_bytes)):
        yield event


# ---------------------------------------------------------------------------
# Streaming timeout
# ---------------------------------------------------------------------------


async def _stream_with_timeout(
    process: asyncio.subprocess.Process,
    spec: SubprocessSpec,
    line_handler: LineHandler,
) -> AsyncGenerator[StreamEvent, None]:
    """Read stdout lines until EOF or the fixed deadline."""
    async with asyncio.timeout(spec.timeout_seconds):
        while True:
            line_bytes = await process.stdout.readline()  # type: ignore[union-attr]
            if not line_bytes:
                break
            line = line_bytes.decode(errors="replace").rstrip()
            logger.debug("Stream line: %s", line[:120])
            async for event in line_handler(line):
                yield event


async def _feed_streaming_stdin(
    process: asyncio.subprocess.Process,
    spec: SubprocessSpec,
) -> None:
    """Feed the exact user payload without placing it in process arguments."""
    await feed_stdin_and_close(process, spec.stdin_text)


async def _cancel_drain(drain: asyncio.Task[bytes]) -> None:
    """Cancel a stderr drain task and silently absorb any resulting exception."""
    if not drain.done():
        drain.cancel()
        with contextlib.suppress(BaseException):
            await drain
