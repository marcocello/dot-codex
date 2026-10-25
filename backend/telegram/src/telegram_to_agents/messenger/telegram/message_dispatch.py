"""One Telegram delivery flow: temporary progress, then a clean final answer."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from telegram_to_agents.cli.types import UserTurn
from telegram_to_agents.messenger.telegram.sender import SendRichOpts, send_rich
from telegram_to_agents.messenger.telegram.temporary_progress import TemporaryProgressEditor
from telegram_to_agents.messenger.telegram.typing import TypingContext
from telegram_to_agents.session.key import SessionKey

if TYPE_CHECKING:
    from aiogram import Bot
    from aiogram.types import Message

    from telegram_to_agents.config import SceneConfig
    from telegram_to_agents.orchestrator.core import Orchestrator

logger = logging.getLogger(__name__)
_REACTION_THINKING = "🤔"
_REACTION_SYSTEM = "💯"
_REACTION_TOOL_MAP: tuple[tuple[tuple[str, ...], str], ...] = (
    (("read", "grep", "glob", "ls"), "👀"),
    (("edit", "write", "multiedit", "str_replace"), "✍️"),
    (("bash", "shell", "run", "exec"), "👨‍💻"),
)


class ReactionTracker:
    """Best-effort, deduplicated stage reaction on the triggering message."""

    def __init__(self, bot: Bot, chat_id: int, message_id: int, *, enabled: bool) -> None:
        self._bot = bot
        self._chat_id = chat_id
        self._message_id = message_id
        self._enabled = enabled
        self._current: str | None = None

    async def set_thinking(self) -> None:
        await self._apply(_REACTION_THINKING)

    async def set_system(self) -> None:
        await self._apply(_REACTION_SYSTEM)

    async def set_tool(self, tool_name: str) -> None:
        lower = tool_name.lower()
        emoji = next(
            (value for prefixes, value in _REACTION_TOOL_MAP if lower.startswith(prefixes)),
            _REACTION_THINKING,
        )
        await self._apply(emoji)

    async def clear(self) -> None:
        await self._apply(None)

    async def _apply(self, emoji: str | None) -> None:
        if not self._enabled or emoji == self._current:
            return
        self._current = emoji
        try:
            from aiogram.types import (
                ReactionTypeCustomEmoji,
                ReactionTypeEmoji,
                ReactionTypePaid,
            )

            reaction: list[ReactionTypeEmoji | ReactionTypeCustomEmoji | ReactionTypePaid] = (
                [ReactionTypeEmoji(emoji=emoji)] if emoji is not None else []
            )
            await self._bot.set_message_reaction(
                chat_id=self._chat_id,
                message_id=self._message_id,
                reaction=reaction,
            )
        except Exception:
            logger.debug("Could not update Telegram reaction", exc_info=True)


@dataclass(slots=True)
class MessageDispatch:
    """Inputs for one authenticated Telegram user turn."""

    bot: Bot
    orchestrator: Orchestrator
    message: Message
    key: SessionKey
    turn: UserTurn
    allowed_roots: list[Path] | None
    thread_id: int | None = None
    scene_config: SceneConfig | None = None


async def run_message(dispatch: MessageDispatch) -> str:
    """Execute once, delete progress, then deliver the final answer once."""
    tracker = ReactionTracker(
        dispatch.bot,
        dispatch.key.chat_id,
        dispatch.message.message_id,
        enabled=bool(dispatch.scene_config and dispatch.scene_config.status_reaction),
    )
    progress = TemporaryProgressEditor(
        dispatch.bot,
        dispatch.key.chat_id,
        reply_to=dispatch.message,
        thread_id=dispatch.thread_id,
    )
    progress_cleared = False

    async def on_tool(tool: object) -> None:
        name = str(getattr(tool, "tool_name", tool))
        raw_parameters = getattr(tool, "parameters", None)
        parameters = raw_parameters if isinstance(raw_parameters, dict) else None
        await tracker.set_tool(name)
        await progress.append_tool(name, parameters)

    async def on_system(status: str | None) -> None:
        label = {
            "thinking": "THINKING",
            "compacting": "COMPACTING",
            "recovering": "RECOVERING",
        }.get(status or "")
        if label:
            await tracker.set_system()
            await progress.append_system(label)

    async def on_progress(text: str) -> None:
        if text.strip():
            await tracker.set_thinking()
            await progress.append_commentary(text)

    try:
        await tracker.set_thinking()
        async with TypingContext(dispatch.bot, dispatch.key.chat_id, thread_id=dispatch.thread_id):
            result = await dispatch.orchestrator.handle_message(
                dispatch.key,
                dispatch.turn,
                on_tool_activity=on_tool,
                on_system_status=on_system,
                on_progress_update=on_progress,
            )
        progress_cleared = await progress.clear()
        if not progress_cleared:
            raise RuntimeError("Could not remove temporary Telegram progress before final answer")
        if result.text:
            await send_rich(
                dispatch.bot,
                dispatch.key.chat_id,
                result.text,
                SendRichOpts(
                    reply_to_message_id=dispatch.message.message_id,
                    allowed_roots=dispatch.allowed_roots,
                    thread_id=dispatch.thread_id,
                ),
            )
        return result.text
    finally:
        if not progress_cleared:
            await progress.clear()
        await tracker.clear()
