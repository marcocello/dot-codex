"""Normalize Telegram-native reply and mention structure into user text."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiogram.types import Message


def strip_mention(text: str, bot_username: str | None) -> str:
    if not bot_username:
        return text
    tag = f"@{bot_username}".lower()
    index = text.lower().find(tag)
    if index < 0:
        return text
    stripped = (text[:index] + text[index + len(tag) :]).strip()
    return stripped or text


def build_reply_prompt(message: Message, user_text: str) -> str:
    cited = _cited_reply_text(message)
    if cited is None:
        return user_text
    quoted = "\n".join(f"> {line}" for line in cited.splitlines())
    return (
        f"The user is replying to this quoted message:\n{quoted}\n\n"
        f"The user's message:\n{user_text}"
    )


def prepend_reply_to_media(message: Message, media_prompt: str) -> str:
    cited = _cited_reply_text(message)
    if cited is None:
        return media_prompt
    quoted = "\n".join(f"> {line}" for line in cited.splitlines())
    return (
        f"The user is replying to this quoted message:\n{quoted}\n\n"
        f"Their reply is {_reply_attachment_label(message)} (the attached file below).\n\n"
        f"{media_prompt}"
    )


def _cited_reply_text(message: Message) -> str | None:
    cited: str | None
    if message.quote is not None and message.quote.text:
        cited = message.quote.text
    elif message.reply_to_message is not None:
        cited = message.reply_to_message.text or message.reply_to_message.caption
    else:
        cited = None
    return cited.strip() if cited and cited.strip() else None


def _reply_attachment_label(message: Message) -> str:
    labels = (
        (message.photo, "an image"),
        (message.document, "a document"),
        (message.voice, "a voice message"),
        (message.audio, "an audio file"),
        (message.video, "a video"),
        (message.video_note, "a video note"),
        (message.sticker, "a sticker"),
    )
    return next((label for value, label in labels if value), "a file")
