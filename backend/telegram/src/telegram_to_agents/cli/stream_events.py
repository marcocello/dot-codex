"""Normalized progress and result events emitted by native harnesses."""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel

from telegram_to_agents.cli.types import CodexTransport

logger = logging.getLogger(__name__)


class StreamEvent(BaseModel):
    """Base event consumed by gateway streaming."""

    type: str
    subtype: str | None = None


class AssistantTextDelta(StreamEvent):
    """Text from an assistant turn."""

    text: str = ""


class SystemInitEvent(StreamEvent):
    """First event of a stream -- contains session_id and tool list."""

    session_id: str | None = None
    session_backend: CodexTransport | None = None


class ResultEvent(StreamEvent):
    """Terminal text and native session identity."""

    session_id: str | None = None
    session_backend: CodexTransport | None = None
    result: str = ""
    is_error: bool = False
    returncode: int | None = None


class ToolUseEvent(StreamEvent):
    """Tool invocation detected during streaming."""

    tool_name: str = ""
    tool_id: str | None = None
    parameters: dict[str, Any] | None = None


class ThinkingEvent(StreamEvent):
    """Extended thinking/reasoning block."""

    text: str = ""


class ProgressUpdateEvent(StreamEvent):
    """Temporary assistant commentary that is not part of the final answer."""

    text: str = ""


class SystemStatusEvent(StreamEvent):
    """System status update (e.g. ``compacting``)."""

    status: str | None = None


def parse_claude_stream_event(line: str) -> list[StreamEvent]:
    """Normalize one Claude Code ``stream-json`` record."""
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        logger.debug("Ignoring malformed Claude stream line: %.200s", line)
        return []
    if not isinstance(data, dict):
        return []
    event_type = data.get("type")
    if event_type == "result":
        events: list[StreamEvent] = [
            ResultEvent(
                type="result",
                subtype=_string(data.get("subtype")),
                session_id=_string(data.get("session_id")),
                result=_string(data.get("result")) or "",
                is_error=bool(data.get("is_error")),
            )
        ]
    elif event_type == "system" and data.get("subtype") == "init":
        events = [
            SystemInitEvent(
                type="system",
                subtype="init",
                session_id=_string(data.get("session_id")),
            )
        ]
    elif event_type == "system" and data.get("subtype") == "status":
        events = [
            SystemStatusEvent(
                type="system",
                subtype="status",
                status=_string(data.get("status")),
            )
        ]
    elif event_type == "assistant":
        message = data.get("message")
        content = message.get("content", []) if isinstance(message, dict) else []
        events = _claude_content_events(content)
    else:
        events = []
    return events


def _claude_content_events(content: object) -> list[StreamEvent]:
    if not isinstance(content, list):
        return []
    events: list[StreamEvent] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type == "text" and isinstance(block.get("text"), str):
            events.append(AssistantTextDelta(type="assistant", text=block["text"]))
        elif block_type == "thinking":
            thinking = block.get("thinking", block.get("text"))
            if isinstance(thinking, str):
                events.append(ThinkingEvent(type="assistant", text=thinking))
        elif block_type == "tool_use" and isinstance(block.get("name"), str):
            parameters = block.get("input")
            events.append(
                ToolUseEvent(
                    type="assistant",
                    tool_name=block["name"],
                    tool_id=_string(block.get("id")),
                    parameters=parameters if isinstance(parameters, dict) else None,
                )
            )
    return events


def _string(value: object) -> str | None:
    return value if isinstance(value, str) else None
