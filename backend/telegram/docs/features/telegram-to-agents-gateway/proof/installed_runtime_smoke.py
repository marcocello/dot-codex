"""Start the installed wheel through its real runtime with Telegram mocked at the edge."""

# ruff: noqa: ASYNC240, INP001, S106

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import telegram_to_agents
from telegram_to_agents.__main__ import run_bot
from telegram_to_agents.config import AgentConfig


async def _main() -> None:
    wheel_site = Path(os.environ["GATEWAY_WHEEL_SITE"]).resolve()
    package_file = Path(telegram_to_agents.__file__).resolve()
    assert package_file.is_relative_to(wheel_site), package_file

    smoke_root = Path(os.environ["GATEWAY_SMOKE_TMP"]).resolve()
    project = smoke_root / "project"
    project.mkdir(parents=True)
    config = AgentConfig(
        telegram_token="12345678:abcdefghijklmnopqrstuvwxyzABCDEF123456",
        allowed_user_ids=[100],
        project_root=str(project),
        state_home=str(smoke_root / "home"),
    )
    runtime = MagicMock()
    runtime.run = AsyncMock(return_value=0)
    runtime.shutdown = AsyncMock()
    with (
        patch("telegram_to_agents.messenger.telegram.app.TelegramBot", return_value=runtime),
        patch("telegram_to_agents.infra.pidlock.acquire_lock"),
        patch("telegram_to_agents.infra.pidlock.release_lock"),
    ):
        assert await run_bot(config) == 0
    runtime.run.assert_awaited_once_with()
    runtime.shutdown.assert_awaited_once_with()
    print("installed_artifact_runtime_start=PASS")


if __name__ == "__main__":
    asyncio.run(_main())
