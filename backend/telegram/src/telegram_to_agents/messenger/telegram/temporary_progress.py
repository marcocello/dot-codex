"""Temporary Telegram progress messages removed when a turn finishes."""

from __future__ import annotations

import asyncio
import html
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError, TelegramRetryAfter

from telegram_to_agents.messenger.telegram.formatting import TELEGRAM_MSG_LIMIT
from telegram_to_agents.text.response_format import normalize_tool_name

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import Message

logger = logging.getLogger(__name__)

_COMMENTARY_PREFIX = "⚙️ "
_COMMENTARY_VISIBLE_LIMIT = 240
_DEFAULT_HEADING = "<i>⚙️ Working…</i>"
_OMITTED_PROGRESS = "<i>…</i>"
_ENTRY_SEPARATOR = "\n\n"
_DETAIL_LIMIT = 120
_MAX_DETAILS = 3


@dataclass(frozen=True, slots=True)
class _ActivitySpec:
    key: str
    singular: str
    plural: str
    unit_singular: str
    unit_plural: str
    detail: str | None = None


@dataclass(slots=True)
class _Activity:
    singular: str
    plural: str
    unit_singular: str
    unit_plural: str
    count: int = 0
    details: list[str] = field(default_factory=list)

    def add(self, detail: str | None) -> None:
        self.count += 1
        if detail and detail not in self.details and len(self.details) < _MAX_DETAILS:
            self.details.append(detail)

    def render(self) -> str:
        label = self.singular if self.count == 1 else self.plural
        unit = self.unit_singular if self.count == 1 else self.unit_plural
        count = "" if self.count == 1 else f" · {self.count} {unit}"
        heading = f"<b>{html.escape(label + count)}</b>"
        details = [f"• {html.escape(detail)}" for detail in self.details]
        return "\n".join([heading, *details])


_ACTIVITY_LABELS: dict[str, tuple[str, str, str, str]] = {
    "read": ("📖 Read files", "📖 Read files", "read", "reads"),
    "file_search": ("🔎 Searched files", "🔎 Searched files", "search", "searches"),
    "web_search": ("🌐 Searched the web", "🌐 Searched the web", "search", "searches"),
    "change": ("✍️ Changed files", "✍️ Changed files", "change", "changes"),
    "command": ("💻 Ran command", "💻 Ran commands", "command", "commands"),
}

_EXPLICIT_TOOL_KINDS = {
    "read": "read",
    "read_file": "read",
    "ls": "read",
    "glob": "file_search",
    "grep": "file_search",
    "search": "file_search",
    "searchtool": "file_search",
    "toolsearch": "file_search",
    "websearch": "web_search",
    "web_search": "web_search",
    "webfetch": "web_search",
    "edit": "change",
    "write": "change",
    "multiedit": "change",
    "file_change": "change",
    "bash": "command",
    "powershell": "command",
    "cmd": "command",
    "sh": "command",
    "zsh": "command",
    "shell": "command",
}


def _activity_specs(
    tool_name: str,
    parameters: dict[str, Any] | None,
) -> list[_ActivitySpec]:
    lower = tool_name.strip().lower()
    leaf = lower.rsplit("/", 1)[-1]
    if lower in {"bash", "powershell", "cmd", "sh", "zsh", "shell"}:
        return _command_activity_specs(parameters)
    kind = _EXPLICIT_TOOL_KINDS.get(lower) or _EXPLICIT_TOOL_KINDS.get(leaf)
    if kind is not None:
        return [_known_activity_spec(kind, _parameter_detail(kind, parameters))]
    label = normalize_tool_name(tool_name).strip() or "tool"
    return [
        _ActivitySpec(
            key=f"tool:{lower}",
            singular=f"🔌 Used {label}",
            plural=f"🔌 Used {label}",
            unit_singular="call",
            unit_plural="calls",
        )
    ]


def _command_activity_specs(parameters: dict[str, Any] | None) -> list[_ActivitySpec]:
    actions = parameters.get("command_actions") if parameters else None
    if not isinstance(actions, list) or not actions:
        return [_known_activity_spec("command")]
    specs: list[_ActivitySpec] = []
    for action in actions:
        if not isinstance(action, dict):
            specs.append(_known_activity_spec("command"))
            continue
        action_type = action.get("type")
        if action_type in {"read", "listFiles"}:
            specs.append(_known_activity_spec("read", _command_action_detail(action)))
        elif action_type == "search":
            specs.append(_known_activity_spec("file_search", _command_action_detail(action)))
        else:
            specs.append(_known_activity_spec("command"))
    return specs


def _known_activity_spec(kind: str, detail: str | None = None) -> _ActivitySpec:
    singular, plural, unit_singular, unit_plural = _ACTIVITY_LABELS[kind]
    return _ActivitySpec(kind, singular, plural, unit_singular, unit_plural, detail)


def _command_action_detail(action: dict[str, Any]) -> str | None:
    action_type = action.get("type")
    if action_type == "read":
        name = _safe_detail(action.get("name")) or _path_detail(action.get("path"))
        return f"Read {name}" if name else None
    if action_type == "listFiles":
        path = _path_detail(action.get("path"))
        return f"Listed {path}" if path else None
    if action_type == "search":
        return _safe_detail(action.get("query")) or _path_detail(action.get("path"))
    return None


def _parameter_detail(kind: str, parameters: dict[str, Any] | None) -> str | None:
    if not parameters:
        return None
    if kind == "web_search":
        return _safe_detail(parameters.get("query"))
    if kind == "file_search":
        return _safe_detail(parameters.get("query") or parameters.get("pattern"))
    if kind in {"read", "change"}:
        path = parameters.get("file_path") or parameters.get("path")
        name = _path_detail(path)
        if not name:
            return None
        return f"Read {name}" if kind == "read" else name
    return None


def _path_detail(value: object) -> str | None:
    normalized = _safe_detail(value)
    if not normalized:
        return None
    name = Path(normalized).name
    return name or normalized


def _safe_detail(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = " ".join(value.split())
    if not normalized:
        return None
    return normalized if len(normalized) <= _DETAIL_LIMIT else f"{normalized[: _DETAIL_LIMIT - 1]}…"


class TemporaryProgressEditor:
    """Render progress separately and retain every message ID for final deletion."""

    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        *,
        reply_to: Message | None = None,
        thread_id: int | None = None,
    ) -> None:
        self._bot = bot
        self._chat_id = chat_id
        self._reply_to = reply_to
        self._thread_id = thread_id
        self._activities: dict[str, _Activity] = {}
        self._system_steps: list[str] = []
        self._active: Message | None = None
        self._known_ids: set[int] = set()
        self._commentary_text = ""
        self._commentary_entry: str | None = None
        self._rendered_text: str | None = None

    @property
    def has_content(self) -> bool:
        return bool(self._known_ids)

    async def append_commentary(self, text: str) -> None:
        if not text:
            return
        self._commentary_text += text
        normalized = " ".join(self._commentary_text.split())
        if not normalized:
            return
        visible = f"{_COMMENTARY_PREFIX}{normalized}"
        if len(visible) > _COMMENTARY_VISIBLE_LIMIT:
            visible = f"{visible[: _COMMENTARY_VISIBLE_LIMIT - 1]}…"
        self._commentary_entry = f"<i>{html.escape(visible)}</i>"
        await self._render()

    async def append_tool(
        self,
        tool_name: str,
        parameters: dict[str, Any] | None = None,
    ) -> None:
        for spec in _activity_specs(tool_name, parameters):
            activity = self._activities.get(spec.key)
            if activity is None:
                activity = _Activity(
                    spec.singular,
                    spec.plural,
                    spec.unit_singular,
                    spec.unit_plural,
                )
                self._activities[spec.key] = activity
            activity.add(spec.detail)
        await self._render()

    async def append_system(self, text: str) -> None:
        if text.strip():
            entry = f"<i>[{html.escape(text.strip())}]</i>"
            if entry not in self._system_steps:
                self._system_steps.append(entry)
            await self._render()

    async def clear(self) -> bool:
        for attempt in range(2):
            for message_id in list(self._known_ids):
                await self._delete(message_id)
            if not self._known_ids:
                break
            if attempt == 0:
                await asyncio.sleep(0)
        if self._known_ids:
            return False
        self._active = None
        self._activities.clear()
        self._system_steps.clear()
        self._commentary_text = ""
        self._commentary_entry = None
        self._rendered_text = None
        return True

    async def _render(self) -> None:
        text = self._bounded_render()
        if self._active is None:
            message = await self._create(text, allow_reply=True)
            if message is not None:
                self._active = message
                self._rendered_text = text
            return
        if text == self._rendered_text:
            return
        await self._edit_or_replace(text)

    def _bounded_render(self) -> str:
        heading = self._commentary_entry or _DEFAULT_HEADING
        steps = [*self._system_steps, *(item.render() for item in self._activities.values())]
        full = _ENTRY_SEPARATOR.join([heading, *steps])
        if len(full) <= TELEGRAM_MSG_LIMIT:
            return full

        selected: list[str] = []
        for step in reversed(steps):
            if len(_ENTRY_SEPARATOR.join([heading, step])) > TELEGRAM_MSG_LIMIT:
                continue
            candidate = _ENTRY_SEPARATOR.join([heading, step, *selected])
            if len(candidate) > TELEGRAM_MSG_LIMIT:
                break
            selected.insert(0, step)
        while selected:
            rolled = _ENTRY_SEPARATOR.join([heading, _OMITTED_PROGRESS, *selected])
            if len(rolled) <= TELEGRAM_MSG_LIMIT:
                return rolled
            selected.pop(0)
        return _ENTRY_SEPARATOR.join([heading, _OMITTED_PROGRESS])

    async def _edit_or_replace(self, text: str) -> None:
        message = self._active
        if message is None:
            return
        try:
            await self._bot.edit_message_text(
                text=text,
                chat_id=self._chat_id,
                message_id=message.message_id,
                parse_mode=ParseMode.HTML,
            )
        except TelegramBadRequest as exc:
            if "message is not modified" in str(exc).lower():
                self._rendered_text = text
                return
            await self._replace_after_delete(message, text)
            return
        except TelegramRetryAfter as exc:
            await asyncio.sleep(exc.retry_after)
            try:
                await self._bot.edit_message_text(
                    text=text,
                    chat_id=self._chat_id,
                    message_id=message.message_id,
                    parse_mode=ParseMode.HTML,
                )
            except TelegramBadRequest as retry_exc:
                if "message is not modified" in str(retry_exc).lower():
                    self._rendered_text = text
                    return
                await self._replace_after_delete(message, text)
                return
            except TelegramRetryAfter:
                return
        self._rendered_text = text

    async def _replace_after_delete(self, message: Message, text: str) -> None:
        if not await self._delete(message.message_id):
            return
        self._active = None
        self._rendered_text = None
        replacement = await self._create(text, allow_reply=False)
        if replacement is not None:
            self._active = replacement
            self._rendered_text = text

    async def _create(self, text: str, *, allow_reply: bool) -> Message | None:
        try:
            if allow_reply and not self._known_ids and self._reply_to is not None:
                message = await self._reply_to.answer(text, parse_mode=ParseMode.HTML)
            else:
                message = await self._bot.send_message(
                    chat_id=self._chat_id,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    message_thread_id=self._thread_id,
                )
        except TelegramBadRequest:
            logger.warning("Failed to create temporary Telegram progress message")
            return None
        self._known_ids.add(message.message_id)
        return message

    async def _delete(self, message_id: int) -> bool:
        try:
            await self._bot.delete_message(chat_id=self._chat_id, message_id=message_id)
        except TelegramRetryAfter as exc:
            await asyncio.sleep(exc.retry_after)
            try:
                await self._bot.delete_message(chat_id=self._chat_id, message_id=message_id)
            except (TelegramBadRequest, TelegramNetworkError, TelegramRetryAfter):
                logger.warning(
                    "Failed to delete temporary Telegram progress message %d", message_id
                )
                return False
        except (TelegramBadRequest, TelegramNetworkError):
            logger.warning("Failed to delete temporary Telegram progress message %d", message_id)
            return False
        self._known_ids.discard(message_id)
        return True
