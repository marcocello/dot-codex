"""Authenticated Telegram frontend for the native-harness gateway."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import BotCommand

from telegram_to_agents.cli.types import UserTurn
from telegram_to_agents.commands import get_bot_commands
from telegram_to_agents.config import AgentConfig
from telegram_to_agents.files.allowed_roots import resolve_allowed_roots
from telegram_to_agents.messenger.telegram.media import (
    AutomaticTranscription,
    has_media,
    resolve_media_turn,
    should_drop_in_group,
)
from telegram_to_agents.messenger.telegram.message_dispatch import MessageDispatch, run_message
from telegram_to_agents.messenger.telegram.message_text import (
    build_reply_prompt,
    prepend_reply_to_media,
    strip_mention,
)
from telegram_to_agents.messenger.telegram.middleware import AuthMiddleware
from telegram_to_agents.messenger.telegram.sender import SendRichOpts, send_rich
from telegram_to_agents.messenger.telegram.topic import (
    TopicNameCache,
    get_session_key,
    get_thread_id,
    get_topic_name_from_message,
)
from telegram_to_agents.orchestrator.core import Orchestrator
from telegram_to_agents.session.key import SessionKey

if TYPE_CHECKING:
    from aiogram.types import Message

logger = logging.getLogger(__name__)


class TelegramBot:
    """The only public transport: Telegram messages into one native harness."""

    def __init__(self, config: AgentConfig) -> None:
        self._config = config
        self._bot = Bot(
            token=config.telegram_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self._dp = Dispatcher()
        self._router = Router(name="native-harness-gateway")
        self._orchestrator: Orchestrator | None = None
        self._topic_names = TopicNameCache()
        self._exit_code = 0
        self._bot_id: int | None = None
        self._bot_username: str | None = None

        auth = AuthMiddleware(
            set(config.allowed_user_ids),
            allowed_group_ids=set(config.allowed_group_ids),
            allowed_channel_ids=set(config.allowed_channel_ids),
        )
        self._router.message.outer_middleware(auth)
        self._router.channel_post.outer_middleware(auth)
        self._register_handlers()
        self._dp.include_router(self._router)
        self._dp.startup.register(self._on_startup)

    @property
    def _orch(self) -> Orchestrator:
        if self._orchestrator is None:
            raise RuntimeError("Orchestrator not initialized -- call after startup")
        return self._orchestrator

    @property
    def dispatcher(self) -> Dispatcher:
        return self._dp

    def file_roots(self, key: SessionKey) -> list[Path] | None:
        return resolve_allowed_roots(
            self._config.file_access,
            Path(self._orch.project_root(key)),
        )

    def _bind_orchestrator(self, orchestrator: Orchestrator) -> None:
        self._orchestrator = orchestrator
        orchestrator.set_topic_name_resolver(self._topic_names.get)

    def _register_handlers(self) -> None:
        router = self._router
        router.message(CommandStart(ignore_case=True))(self._on_start)
        router.message(Command("help", ignore_case=True))(self._on_help)
        router.message(Command("info", ignore_case=True))(self._on_info)
        router.message(Command("status", ignore_case=True))(self._on_status)
        router.message(Command("new", ignore_case=True))(self._on_new)
        router.message(Command("reset", ignore_case=True))(self._on_new)
        router.message(Command("stop", ignore_case=True))(self._on_stop)
        router.message(Command("stop_all", ignore_case=True))(self._on_stop_all)
        router.message(Command("interrupt", ignore_case=True))(self._on_interrupt)
        router.message(Command("restart", ignore_case=True))(self._on_restart)
        router.message(Command("where", ignore_case=True))(self._on_where)
        router.message(Command("leave", ignore_case=True))(self._on_leave)
        router.message(Command("showfiles", ignore_case=True))(self._on_showfiles)
        router.message()(self._on_message)
        router.channel_post()(self._on_message)

    async def _on_startup(self) -> None:
        if self._orchestrator is None:
            self._bind_orchestrator(await Orchestrator.create(self._config))
        else:
            self._bind_orchestrator(self._orchestrator)
        me = await self._bot.get_me()
        self._bot_id = me.id
        self._bot_username = (me.username or "").lower()
        await self._bot.set_my_commands(
            [
                BotCommand(command=name, description=description)
                for name, description in get_bot_commands()
            ]
        )

    async def run(self) -> int:
        await self._bot.delete_webhook(drop_pending_updates=True)
        await self._dp.start_polling(
            self._bot,
            allowed_updates=self._dp.resolve_used_update_types(),
            close_bot_session=True,
            handle_signals=False,
        )
        return self._exit_code

    async def shutdown(self) -> None:
        if self._orchestrator is not None:
            await self._orchestrator.shutdown()

    async def _reply(self, message: Message, text: str) -> None:
        await send_rich(
            self._bot,
            message.chat.id,
            text,
            SendRichOpts(
                reply_to_message_id=message.message_id,
                thread_id=get_thread_id(message),
            ),
        )

    async def _on_start(self, message: Message) -> None:
        await self._reply(
            message,
            f"{self._config.provider.capitalize()} gateway is ready. Send text, files, voice notes, or audio. Use /new for a fresh session.",
        )

    async def _on_help(self, message: Message) -> None:
        lines = [f"/{name} — {description}" for name, description in get_bot_commands()]
        await self._reply(message, "Native-harness Telegram gateway\n\n" + "\n".join(lines))

    async def _on_info(self, message: Message) -> None:
        await self._reply(message, f"Telegram → native {self._config.provider.capitalize()}")

    async def _on_status(self, message: Message) -> None:
        await self._reply(message, await self._orch.status_text(get_session_key(message)))

    async def _on_new(self, message: Message) -> None:
        await self._orch.reset_session(get_session_key(message))
        await self._reply(message, f"Started a new {self._config.provider.capitalize()} session.")

    async def _on_stop(self, message: Message) -> None:
        count = await self._orch.abort(message.chat.id, get_thread_id(message))
        await self._reply(message, f"Stopped {count} active turn(s).")

    async def _on_stop_all(self, message: Message) -> None:
        count = await self._orch.abort_all()
        await self._reply(message, f"Stopped {count} active turn(s).")

    async def _on_interrupt(self, message: Message) -> None:
        count = self._orch.interrupt(message.chat.id)
        await self._reply(message, f"Interrupted {count} active turn(s).")

    async def _on_restart(self, message: Message) -> None:
        self._exit_code = 42
        await self._reply(message, "Restart requested.")
        await self._dp.stop_polling()

    async def _on_where(self, message: Message) -> None:
        key = get_session_key(message)
        await self._reply(
            message,
            f"Chat: {message.chat.id}\nTopic: {get_thread_id(message) or '-'}\nProject: {self._orch.project_root(key)}",
        )

    async def _on_leave(self, message: Message) -> None:
        if message.chat.type == "private":
            await self._reply(message, "/leave is only available inside a group or channel.")
            return
        await self._bot.leave_chat(message.chat.id)

    async def _on_showfiles(self, message: Message) -> None:
        directory = self._orch.paths.telegram_files_dir
        files = sorted(
            (path for path in directory.rglob("*") if path.is_file()),
            key=lambda path: path.stat().st_mtime,
        )[-20:]
        text = (
            "Recent Telegram files:\n" + "\n".join(path.name for path in files)
            if files
            else "No Telegram files."
        )
        await self._reply(message, text)

    async def _on_message(self, message: Message) -> None:
        topic_id = get_thread_id(message)
        topic_name = get_topic_name_from_message(message)
        if topic_id is not None and topic_name:
            self._topic_names.set(message.chat.id, topic_id, topic_name)
        turn = await self._resolve_turn(message)
        if turn is None:
            return
        key = get_session_key(message)
        thread_id = get_thread_id(message)
        await self._handle_message(message, key, turn, thread_id=thread_id)

    async def _resolve_turn(self, message: Message) -> UserTurn | None:
        if should_drop_in_group(
            message,
            bot_id=self._bot_id,
            bot_username=self._bot_username,
            group_mention_only=self._config.group_mention_only,
        ):
            return None
        if has_media(message):
            turn = await resolve_media_turn(
                self._bot,
                message,
                self._orch.paths.telegram_files_dir,
                automatic_transcription=AutomaticTranscription(
                    config=self._config.transcription,
                    env_file=self._orch.paths.env_file,
                ),
            )
            if turn is None:
                return None
            if (message.voice or message.audio) and self._config.transcription.automatic_audio:
                return UserTurn(text=build_reply_prompt(message, turn.text))
            return UserTurn(
                text=prepend_reply_to_media(message, turn.text),
                attachments=turn.attachments,
            )
        if not message.text:
            return None
        return UserTurn(
            text=build_reply_prompt(message, strip_mention(message.text, self._bot_username))
        )

    async def _handle_message(
        self,
        message: Message,
        key: SessionKey,
        turn: UserTurn,
        *,
        thread_id: int | None = None,
    ) -> None:
        try:
            allowed_roots = self.file_roots(key)
        except ValueError as exc:
            await self._reply(message, str(exc))
            return
        await run_message(
            MessageDispatch(
                bot=self._bot,
                orchestrator=self._orch,
                message=message,
                key=key,
                turn=turn,
                allowed_roots=allowed_roots,
                thread_id=thread_id,
                scene_config=self._config.scene,
            )
        )
