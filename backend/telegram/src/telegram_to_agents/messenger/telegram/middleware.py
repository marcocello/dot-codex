"""Telegram authorization middleware."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

logger = logging.getLogger(__name__)
RejectedCallback = Callable[[int, str, str], None]


class AuthMiddleware(BaseMiddleware):
    """Reject Telegram actors and chats that are not explicitly allowed."""

    def __init__(
        self,
        allowed_user_ids: set[int],
        *,
        allowed_group_ids: set[int] | None = None,
        allowed_channel_ids: set[int] | None = None,
        on_rejected: RejectedCallback | None = None,
    ) -> None:
        self.allowed_user_ids = allowed_user_ids
        self.allowed_group_ids = allowed_group_ids or set()
        self.allowed_channel_ids = allowed_channel_ids or set()
        self.on_rejected = on_rejected

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        message = event.message if isinstance(event, CallbackQuery) else event
        if not isinstance(message, Message):
            return await handler(event, data)
        chat = message.chat
        if chat.type == "channel":
            if chat.id not in self.allowed_channel_ids:
                if self.on_rejected:
                    self.on_rejected(chat.id, chat.type, chat.title or "")
                return None
            return await handler(event, data)
        actor = event.from_user if isinstance(event, CallbackQuery) else message.from_user
        if actor is None or actor.id not in self.allowed_user_ids:
            logger.warning("Rejected unauthorized Telegram user=%s", getattr(actor, "id", None))
            return None
        if chat.type in {"group", "supergroup"} and chat.id not in self.allowed_group_ids:
            if self.on_rejected:
                self.on_rejected(chat.id, chat.type, chat.title or "")
            return None
        return await handler(event, data)
