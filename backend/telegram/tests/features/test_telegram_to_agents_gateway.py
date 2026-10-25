"""Black-box feature proof for the native-harness Telegram gateway."""

from __future__ import annotations

import asyncio
import contextlib
import importlib.util
import json
import logging
import os
import shlex
import socket
import subprocess
import sys
import tarfile
import tempfile
import threading
import tomllib
import zipfile
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.exceptions import TelegramNetworkError
from aiogram.types import Update
from openai import AsyncOpenAI as NativeAsyncOpenAI
from pydantic import ValidationError

from telegram_to_agents.__main__ import load_config, run_bot
from telegram_to_agents.cli import codex_provider
from telegram_to_agents.cli.base import CLIConfig
from telegram_to_agents.cli.codex_appserver_bridge import (
    Invocation,
    _turn_start_params,
    start_or_resume,
)
from telegram_to_agents.cli.executor import build_subprocess_env
from telegram_to_agents.cli.process_registry import ProcessRegistry
from telegram_to_agents.cli.service import CLIService, CLIServiceConfig
from telegram_to_agents.cli.stream_events import SystemInitEvent
from telegram_to_agents.cli.types import AgentRequest, AgentResponse, UserTurn
from telegram_to_agents.cli_commands.lifecycle import stop_bot
from telegram_to_agents.cli_commands.status import print_status
from telegram_to_agents.commands import get_bot_commands
from telegram_to_agents.config import AgentConfig, TimeoutConfig, TranscriptionConfig
from telegram_to_agents.files.allowed_roots import resolve_allowed_roots
from telegram_to_agents.infra import service_linux
from telegram_to_agents.messenger.telegram.app import TelegramBot
from telegram_to_agents.messenger.telegram.message_dispatch import MessageDispatch, run_message
from telegram_to_agents.messenger.telegram.sender import send_files_from_text
from telegram_to_agents.messenger.telegram.temporary_progress import TemporaryProgressEditor
from telegram_to_agents.orchestrator.core import Orchestrator, OrchestratorResult
from telegram_to_agents.session.key import SessionKey
from telegram_to_agents.session.manager import SessionManager
from telegram_to_agents.workspace.paths import GatewayPaths, resolve_paths


def _load_fake_daemon() -> type:
    path = Path(__file__).parents[2] / "docs/features/telegram-to-agents-gateway/proof/fake_daemon.py"
    spec = importlib.util.spec_from_file_location("gateway_fake_daemon", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.FakeDaemon


FakeDaemon = _load_fake_daemon()


RETAINED_COMMANDS = {
    "start",
    "new",
    "reset",
    "stop",
    "stop_all",
    "interrupt",
    "status",
    "where",
    "leave",
    "showfiles",
    "info",
    "help",
    "restart",
}
ALLOWED_SOURCE_FILES = {
    "telegram_to_agents/__init__.py",
    "telegram_to_agents/__main__.py",
    "telegram_to_agents/cli/__init__.py",
    "telegram_to_agents/cli/_log_redact.py",
    "telegram_to_agents/cli/auth.py",
    "telegram_to_agents/cli/base.py",
    "telegram_to_agents/cli/claude_provider.py",
    "telegram_to_agents/cli/codex_appserver_bridge.py",
    "telegram_to_agents/cli/codex_events.py",
    "telegram_to_agents/cli/codex_provider.py",
    "telegram_to_agents/cli/executor.py",
    "telegram_to_agents/cli/init_wizard.py",
    "telegram_to_agents/cli/process_registry.py",
    "telegram_to_agents/cli/service.py",
    "telegram_to_agents/cli/stream_events.py",
    "telegram_to_agents/cli/types.py",
    "telegram_to_agents/cli_commands/__init__.py",
    "telegram_to_agents/cli_commands/lifecycle.py",
    "telegram_to_agents/cli_commands/status.py",
    "telegram_to_agents/commands.py",
    "telegram_to_agents/config.py",
    "telegram_to_agents/files/__init__.py",
    "telegram_to_agents/files/allowed_roots.py",
    "telegram_to_agents/files/storage.py",
    "telegram_to_agents/files/tags.py",
    "telegram_to_agents/infra/__init__.py",
    "telegram_to_agents/infra/atomic_io.py",
    "telegram_to_agents/infra/env_secrets.py",
    "telegram_to_agents/infra/json_store.py",
    "telegram_to_agents/infra/pidlock.py",
    "telegram_to_agents/infra/process_tree.py",
    "telegram_to_agents/infra/service.py",
    "telegram_to_agents/infra/service_base.py",
    "telegram_to_agents/infra/service_linux.py",
    "telegram_to_agents/infra/service_logs.py",
    "telegram_to_agents/messenger/__init__.py",
    "telegram_to_agents/messenger/telegram/__init__.py",
    "telegram_to_agents/messenger/telegram/app.py",
    "telegram_to_agents/messenger/telegram/formatting.py",
    "telegram_to_agents/messenger/telegram/media.py",
    "telegram_to_agents/messenger/telegram/message_dispatch.py",
    "telegram_to_agents/messenger/telegram/message_text.py",
    "telegram_to_agents/messenger/telegram/middleware.py",
    "telegram_to_agents/messenger/telegram/sender.py",
    "telegram_to_agents/messenger/telegram/temporary_progress.py",
    "telegram_to_agents/messenger/telegram/topic.py",
    "telegram_to_agents/messenger/telegram/typing.py",
    "telegram_to_agents/orchestrator/__init__.py",
    "telegram_to_agents/orchestrator/core.py",
    "telegram_to_agents/security/__init__.py",
    "telegram_to_agents/security/paths.py",
    "telegram_to_agents/session/__init__.py",
    "telegram_to_agents/session/key.py",
    "telegram_to_agents/session/manager.py",
    "telegram_to_agents/text/__init__.py",
    "telegram_to_agents/text/response_format.py",
    "telegram_to_agents/transcription/__init__.py",
    "telegram_to_agents/transcription/openai_audio.py",
    "telegram_to_agents/workspace/__init__.py",
    "telegram_to_agents/workspace/paths.py",
    "telegram_to_agents/workspace/project_roots.py",
}
ALLOWED_TEST_FILES = {
    "tests/__init__.py",
    "tests/conftest.py",
    "tests/features/__init__.py",
    "tests/features/test_telegram_to_agents_gateway.py",
    "tests/transcription/__init__.py",
    "tests/transcription/test_openai_audio.py",
}
ALLOWED_ROOT_FILES = {
    ".gitignore",
    ".pre-commit-config.yaml",
    "AGENTS.md",
    "LICENSE",
    "README.md",
    "config.example.json",
    "justfile",
    "pyproject.toml",
    "uv.lock",
}
ALLOWED_DOC_FILES = {
    "docs/architecture.md",
    "docs/README.md",
    "docs/config.md",
    "docs/developer_quickstart.md",
    "docs/features/telegram-to-agents-gateway/FEATURE.md",
    "docs/features/telegram-to-agents-gateway/PROOF.md",
    "docs/features/telegram-to-agents-gateway/proof/fake_codex_proxy.py",
    "docs/features/telegram-to-agents-gateway/proof/fake_daemon.py",
    "docs/features/telegram-to-agents-gateway/proof/installed_runtime_smoke.py",
    "docs/features/telegram-to-agents-gateway/proof/run.sh",
    "docs/installation.md",
}
ALLOWED_GITHUB_FILES = {
    ".github/ISSUE_TEMPLATE/1-bug-report.yml",
    ".github/ISSUE_TEMPLATE/2-feature-request.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/scripts/malice-scan.sh",
    ".github/workflows/publish.yml",
    ".github/workflows/security-audit.yml",
}


class _GatewayDaemon(FakeDaemon):
    """Fake managed App Server that returns a distinct ID for every new thread."""

    def _start_thread(
        self,
        client: object,
        message: dict[str, object],
        state: dict[str, object],
    ) -> None:
        threads = state["threads"]
        assert isinstance(threads, dict)
        thread_id = f"thread-shared-{len(threads) + 1}"
        params = message["params"]
        assert isinstance(params, dict)
        threads[thread_id] = {
            "id": thread_id,
            "cwd": params["cwd"],
            "source": params.get("threadSource"),
            "turns": [],
            "busy": False,
        }
        self._save(state)  # type: ignore[arg-type]
        with self._clients_lock:
            for connected in self._clients:
                connected.subscriptions.add(thread_id)
        self._broadcast(
            thread_id,
            [
                {
                    "method": "thread/started",
                    "params": {
                        "thread": {
                            "id": thread_id,
                            "cwd": params["cwd"],
                            "source": params.get("threadSource"),
                        }
                    },
                }
            ],
        )
        self._send(client, {"id": message["id"], "result": {"thread": {"id": thread_id}}})  # type: ignore[arg-type]

    def _start_turn(
        self,
        client: Any,
        message: dict[str, Any],
        state: dict[str, Any],
        mode: str,
    ) -> None:
        params = message["params"]
        assert isinstance(params, dict)
        turn_input = params["input"]
        assert isinstance(turn_input, list)
        first_input = turn_input[0]
        assert isinstance(first_input, dict)
        if first_input.get("text") not in {
            "Cancel this active turn.",
            "Timeout this turn.",
        }:
            super()._start_turn(client, message, state, mode)
            return

        self._save(state)  # type: ignore[arg-type]

        def _finish_delayed_turn() -> None:
            with contextlib.suppress(OSError):
                FakeDaemon._start_turn(self, client, message, state, mode)

        completion = threading.Timer(0.5, _finish_delayed_turn)
        completion.daemon = True
        completion.start()


@pytest.fixture
def fake_codex(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    source = (
        Path(__file__).parents[2] / "docs/features/telegram-to-agents-gateway/proof/fake_codex_proxy.py"
    )
    binary = tmp_path / "codex"
    binary.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    binary.chmod(0o755)
    state = tmp_path / "codex-state.json"
    daemon = _GatewayDaemon(state)
    daemon.start()
    codex_home = tmp_path / "codex-home"
    control_dir = codex_home / "app-server-control"
    control_dir.mkdir(parents=True)
    (control_dir / "app-server-control.sock").symlink_to(daemon.address)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ.get('PATH', '')}")
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv("FAKE_CODEX_STATE", str(state))
    monkeypatch.setenv("FAKE_CODEX_ADDR", daemon.address)
    try:
        yield state
    finally:
        daemon.close()


@pytest.fixture
def fake_claude(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Install a deterministic outer Claude CLI boundary on PATH."""
    binary = tmp_path / "claude"
    binary.write_text(
        """#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

state_path = Path(os.environ["FAKE_CLAUDE_STATE"])
state = json.loads(state_path.read_text()) if state_path.exists() else {"calls": []}
args = sys.argv[1:]
resume = args[args.index("--resume") + 1] if "--resume" in args else None
session_id = resume or f"claude-session-{len(state['calls']) + 1}"
prompt = sys.stdin.read()
state["calls"].append({"args": args, "cwd": os.getcwd(), "prompt": prompt, "session_id": session_id})
state_path.write_text(json.dumps(state))
print(json.dumps({"type": "system", "subtype": "init", "session_id": session_id}), flush=True)
print(json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "tool-1", "name": "Read", "input": {}}]}}), flush=True)
print(json.dumps({"type": "result", "session_id": session_id, "result": f"Claude: {prompt}"}), flush=True)
""",
        encoding="utf-8",
    )
    binary.chmod(0o755)
    state = tmp_path / "claude-state.json"
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ.get('PATH', '')}")
    monkeypatch.setenv("FAKE_CLAUDE_STATE", str(state))
    return state


def _paths(tmp_path: Path) -> GatewayPaths:
    home = tmp_path / "home"
    home.mkdir()
    return GatewayPaths(state_home=home)


def _update(update_id: int, text: str, *, user_id: int = 100) -> Update:
    return Update.model_validate(
        {
            "update_id": update_id,
            "message": {
                "message_id": update_id,
                "date": 1_700_000_000,
                "chat": {"id": 7, "type": "private"},
                "from": {"id": user_id, "is_bot": False, "first_name": "Marco"},
                "text": text,
            },
        }
    )


def _voice_update(update_id: int, *, caption: str = "check this") -> Update:
    return Update.model_validate(
        {
            "update_id": update_id,
            "message": {
                "message_id": update_id,
                "date": 1_700_000_000,
                "chat": {"id": 7, "type": "private"},
                "from": {"id": 100, "is_bot": False, "first_name": "Marco"},
                "caption": caption,
                "voice": {
                    "file_id": "voice-file",
                    "file_unique_id": "voice-unique",
                    "duration": 3,
                    "mime_type": "audio/ogg",
                    "file_size": 5,
                },
            },
        }
    )


def _photo_update(update_id: int, *, caption: str = "inspect pixels") -> Update:
    return Update.model_validate(
        {
            "update_id": update_id,
            "message": {
                "message_id": update_id,
                "date": 1_700_000_000,
                "chat": {"id": 7, "type": "private"},
                "from": {"id": 100, "is_bot": False, "first_name": "Marco"},
                "caption": caption,
                "photo": [
                    {
                        "file_id": "photo-file",
                        "file_unique_id": "photo-unique",
                        "width": 640,
                        "height": 480,
                        "file_size": 8,
                    }
                ],
            },
        }
    )


def _document_update(update_id: int, *, caption: str = "inspect report") -> Update:
    return Update.model_validate(
        {
            "update_id": update_id,
            "message": {
                "message_id": update_id,
                "date": 1_700_000_000,
                "chat": {"id": 7, "type": "private"},
                "from": {"id": 100, "is_bot": False, "first_name": "Marco"},
                "caption": caption,
                "document": {
                    "file_id": "document-file",
                    "file_unique_id": "document-unique",
                    "file_name": "report.pdf",
                    "mime_type": "application/pdf",
                    "file_size": 13,
                },
            },
        }
    )


def _channel_update(update_id: int, channel_id: int, text: str) -> Update:
    return Update.model_validate(
        {
            "update_id": update_id,
            "channel_post": {
                "message_id": update_id,
                "date": 1_700_000_000,
                "chat": {"id": channel_id, "type": "channel", "title": "Builds"},
                "text": text,
            },
        }
    )


def _topic_update(
    update_id: int,
    text: str | None = None,
    *,
    topic_id: int = 42,
    topic_name: str | None = None,
) -> Update:
    message: dict[str, object] = {
        "message_id": update_id,
        "date": 1_700_000_000,
        "chat": {"id": -200, "type": "supergroup", "title": "Projects", "is_forum": True},
        "from": {"id": 100, "is_bot": False, "first_name": "Marco"},
        "message_thread_id": topic_id,
        "is_topic_message": True,
    }
    if text is not None:
        message["text"] = text
    if topic_name is not None:
        message["forum_topic_created"] = {
            "name": topic_name,
            "icon_color": 7_322_096,
        }
    return Update.model_validate({"update_id": update_id, "message": message})


class _TranscriptionHandler(BaseHTTPRequestHandler):
    requests: list[dict[str, object]] = []

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        self.__class__.requests.append(
            {
                "path": self.path,
                "authorization": self.headers.get("Authorization"),
                "content_type": self.headers.get("Content-Type"),
                "body": body,
            }
        )
        payload = b'{"text":"This is the transcript."}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, _format: str, *_args: object) -> None:
        return


@pytest.fixture
def transcription_http() -> Iterator[str]:
    _TranscriptionHandler.requests = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), _TranscriptionHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}/v1"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def _fake_telegram_bot() -> MagicMock:
    bot = AsyncMock()
    bot.id = 999
    bot.return_value = SimpleNamespace(message_id=900)
    bot.send_message = AsyncMock(return_value=SimpleNamespace(message_id=900))
    bot.edit_message_text = AsyncMock(return_value=SimpleNamespace(message_id=900))
    bot.delete_message = AsyncMock()
    bot.send_chat_action = AsyncMock()
    bot.set_message_reaction = AsyncMock()
    bot.send_photo = AsyncMock()
    bot.send_document = AsyncMock()
    bot.send_audio = AsyncMock()
    bot.download = AsyncMock()
    return bot


def _gateway(
    tmp_path: Path,
    *,
    transcription: TranscriptionConfig | None = None,
    allowed_group_ids: list[int] | None = None,
    allowed_channel_ids: list[int] | None = None,
    project_roots: dict[str, str] | None = None,
    file_access: str = "all",
    timeout_seconds: float = 1800.0,
    provider: str = "codex",
) -> tuple[TelegramBot, Orchestrator, MagicMock]:
    project = tmp_path / "project"
    project.mkdir()
    config = AgentConfig(
        provider=provider,  # type: ignore[arg-type]
        telegram_token="12345678:abcdefghijklmnopqrstuvwxyzABCDEF123456",
        allowed_user_ids=[100],
        allowed_group_ids=allowed_group_ids or [],
        allowed_channel_ids=allowed_channel_ids or [],
        project_root=str(project),
        project_roots=project_roots or {},
        file_access=file_access,
        timeouts=TimeoutConfig(normal=timeout_seconds),
        transcription=transcription or TranscriptionConfig(),
    )
    paths = _paths(tmp_path)
    paths.telegram_files_dir.mkdir(parents=True)
    orchestrator = Orchestrator(config, paths)
    telegram = _fake_telegram_bot()
    with patch("telegram_to_agents.messenger.telegram.app.Bot", return_value=telegram):
        app = TelegramBot(config)
    app._bind_orchestrator(orchestrator)
    return app, orchestrator, telegram


async def test_authorized_telegram_text_is_exact_resumable_and_new_resets(
    tmp_path: Path,
    fake_codex: Path,
) -> None:
    app, _orchestrator, telegram = _gateway(tmp_path)

    await app.dispatcher.feed_update(telegram, _update(1, "Inspect the repository exactly."))
    await app.dispatcher.feed_update(telegram, _update(2, "Continue from the first turn."))
    await app.dispatcher.feed_update(telegram, _update(3, "/new"))
    await app.dispatcher.feed_update(telegram, _update(4, "Start clean."))

    state = json.loads(fake_codex.read_text(encoding="utf-8"))
    requests = state["requests"]
    methods = [request["method"] for request in requests]
    assert methods.count("thread/start") == 2
    assert methods.count("thread/resume") == 1
    assert state["invocations"] == [
        ["app-server", "proxy"],
        ["app-server", "proxy"],
        ["app-server", "proxy"],
    ]
    turns = [request["params"] for request in requests if request["method"] == "turn/start"]
    assert [turn["input"][0]["text"] for turn in turns] == [
        "Inspect the repository exactly.",
        "Continue from the first turn.",
        "Start clean.",
    ]
    assert [turn["threadId"] for turn in turns] == [
        "thread-shared-1",
        "thread-shared-1",
        "thread-shared-2",
    ]
    starts = [request["params"] for request in requests if request["method"] == "thread/start"]
    assert [start["cwd"] for start in starts] == [
        str((tmp_path / "project").resolve()),
        str((tmp_path / "project").resolve()),
    ]
    for request in requests:
        for key in ("model", "effort", "developerInstructions", "sandbox", "approvalPolicy"):
            assert key not in request["params"]


def test_codex_transport_resolution_requires_the_canonical_unix_socket(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    codex_home = tmp_path / "explicit-codex-home"
    control = codex_home / "app-server-control" / "app-server-control.sock"
    control.parent.mkdir(parents=True)
    monkeypatch.setenv("CODEX_HOME", str(codex_home))

    assert codex_provider.codex_control_socket() == control
    assert codex_provider.resolve_codex_transport() == "embedded"
    control.write_text("not a socket", encoding="utf-8")
    assert codex_provider.resolve_codex_transport() == "embedded"
    control.unlink()

    with tempfile.TemporaryDirectory(prefix="telegram-to-agents-socket-", dir="/tmp") as socket_dir:
        actual_socket = Path(socket_dir) / "control.sock"
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            server.bind(str(actual_socket))
            control.symlink_to(actual_socket)
            assert codex_provider.resolve_codex_transport() == "managed"
        finally:
            server.close()

    default_home = tmp_path / "default-home"
    monkeypatch.setenv("CODEX_HOME", "")
    monkeypatch.setenv("HOME", str(default_home))
    assert codex_provider.codex_control_socket() == (
        default_home / ".codex/app-server-control/app-server-control.sock"
    )


async def test_codex_transport_switch_starts_a_backend_owned_session(
    tmp_path: Path,
    fake_codex: Path,
) -> None:
    app, orchestrator, telegram = _gateway(tmp_path)

    await app.dispatcher.feed_update(telegram, _update(1, "Use managed transport."))
    control = Path(os.environ["CODEX_HOME"]) / "app-server-control/app-server-control.sock"
    control.unlink()
    await app.dispatcher.feed_update(telegram, _update(2, "Use embedded transport."))

    state = json.loads(fake_codex.read_text(encoding="utf-8"))
    assert state["invocations"] == [
        ["app-server", "proxy"],
        ["app-server", "--listen", "stdio://"],
    ]
    methods = [request["method"] for request in state["requests"]]
    assert methods.count("thread/start") == 2
    assert "thread/resume" not in methods
    turns = [
        request["params"] for request in state["requests"] if request["method"] == "turn/start"
    ]
    assert [turn["input"][0]["text"] for turn in turns] == [
        "Use managed transport.",
        "Use embedded transport.",
    ]
    assert [turn["threadId"] for turn in turns] == ["thread-shared-1", "thread-shared-2"]
    persisted = json.loads(orchestrator.paths.sessions_path.read_text(encoding="utf-8"))
    assert persisted["tg:7"]["session_backend"] == "embedded"


async def test_lost_managed_turn_ack_is_not_retried_on_embedded_transport(
    tmp_path: Path,
    fake_codex: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FAKE_CODEX_MODE", "lost_turn_ack")
    app, _orchestrator, telegram = _gateway(tmp_path)

    await app.dispatcher.feed_update(telegram, _update(1, "Do this exactly once."))

    state = json.loads(fake_codex.read_text(encoding="utf-8"))
    assert state["invocations"] == [["app-server", "proxy"]]
    turns = [request for request in state["requests"] if request["method"] == "turn/start"]
    assert len(turns) == 1
    native_turns = [turn for thread in state["threads"].values() for turn in thread["turns"]]
    assert native_turns == [{"client": "telegram", "text": "Do this exactly once."}]
    assert any(
        "closed unexpectedly" in str(call).lower() for call in telegram.send_message.await_args_list
    )


async def test_authorized_telegram_text_uses_native_claude_config_and_resumes(
    tmp_path: Path,
    fake_claude: Path,
) -> None:
    app, _orchestrator, telegram = _gateway(tmp_path, provider="claude")

    await app.dispatcher.feed_update(telegram, _update(1, "Use Claude exactly."))
    await app.dispatcher.feed_update(telegram, _update(2, "Resume Claude."))

    calls = json.loads(fake_claude.read_text(encoding="utf-8"))["calls"]
    assert [call["prompt"] for call in calls] == ["Use Claude exactly.", "Resume Claude."]
    assert [call["cwd"] for call in calls] == [
        str((tmp_path / "project").resolve()),
        str((tmp_path / "project").resolve()),
    ]
    assert "--resume" not in calls[0]["args"]
    assert calls[1]["args"][-2:] == ["--resume", "claude-session-1"]
    forbidden = {
        "--model",
        "--effort",
        "--system-prompt",
        "--append-system-prompt",
        "--permission-mode",
        "--dangerously-skip-permissions",
        "--allowedTools",
        "--tools",
    }
    assert not forbidden.intersection(calls[0]["args"])
    assert telegram.delete_message.await_count >= 1
    assert any(
        "Claude: Use Claude exactly." in str(call) for call in telegram.send_message.await_args_list
    )


async def test_unauthorized_telegram_update_never_reaches_codex(tmp_path: Path) -> None:
    app, orchestrator, telegram = _gateway(tmp_path)
    execute = AsyncMock()
    object.__setattr__(orchestrator._cli_service, "execute", execute)

    await app.dispatcher.feed_update(telegram, _update(1, "unauthorized", user_id=404))

    execute.assert_not_awaited()


async def test_channel_allowlist_is_enforced_without_a_user_actor(tmp_path: Path) -> None:
    app, orchestrator, telegram = _gateway(tmp_path, allowed_channel_ids=[-300])
    execute = AsyncMock(
        return_value=AgentResponse(
            result="channel answer",
            session_id="channel-thread",
        )
    )
    object.__setattr__(orchestrator._cli_service, "execute", execute)

    await app.dispatcher.feed_update(telegram, _channel_update(1, -301, "blocked"))
    execute.assert_not_awaited()
    await app.dispatcher.feed_update(telegram, _channel_update(2, -300, "allowed"))
    assert execute.await_args.args[0].turn == UserTurn(text="allowed")


async def test_audio_transcript_and_caption_become_the_only_codex_prompt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fake_codex: Path,
    transcription_http: str,
) -> None:
    app, _orchestrator, telegram = _gateway(
        tmp_path,
        transcription=TranscriptionConfig(automatic_audio=True, model="gpt-4o-transcribe"),
    )

    async def _download(_file: object, *, destination: Path) -> None:
        destination.write_bytes(b"audio")

    telegram.download.side_effect = _download
    monkeypatch.setenv("OPENAI_API_KEY", "transcription-secret")

    def _transcription_client(*, api_key: str) -> NativeAsyncOpenAI:
        return NativeAsyncOpenAI(api_key=api_key, base_url=transcription_http)

    monkeypatch.setattr(
        "telegram_to_agents.transcription.openai_audio.AsyncOpenAI",
        _transcription_client,
    )

    await app.dispatcher.feed_update(telegram, _voice_update(1))

    assert len(_TranscriptionHandler.requests) == 1
    transcription_request = _TranscriptionHandler.requests[0]
    assert transcription_request["path"] == "/v1/audio/transcriptions"
    assert transcription_request["authorization"] == "Bearer transcription-secret"
    assert b"gpt-4o-transcribe" in transcription_request["body"]
    state = json.loads(fake_codex.read_text(encoding="utf-8"))
    turns = [request for request in state["requests"] if request["method"] == "turn/start"]
    assert turns[0]["params"]["input"] == [
        {
            "type": "text",
            "text": "This is the transcript.\n\nThe user's caption:\ncheck this",
        }
    ]

    monkeypatch.delenv("OPENAI_API_KEY")
    await app.dispatcher.feed_update(telegram, _voice_update(2))
    state = json.loads(fake_codex.read_text(encoding="utf-8"))
    assert len([item for item in state["requests"] if item["method"] == "turn/start"]) == 1


async def test_original_image_reaches_codex_and_claude_without_conversion(
    tmp_path: Path,
    fake_codex: Path,
    fake_claude: Path,
) -> None:
    async def _download(_file: object, *, destination: Path) -> None:
        destination.write_bytes(b"original-jpeg-bytes")

    codex_root = tmp_path / "codex-case"
    codex_root.mkdir()
    codex_app, _orchestrator, codex_telegram = _gateway(codex_root)
    codex_telegram.download.side_effect = _download
    await codex_app.dispatcher.feed_update(codex_telegram, _photo_update(10))

    codex_state = json.loads(fake_codex.read_text(encoding="utf-8"))
    codex_turn = next(
        item["params"] for item in codex_state["requests"] if item["method"] == "turn/start"
    )
    assert codex_turn["input"][0] == {"type": "text", "text": "inspect pixels"}
    image_item = codex_turn["input"][1]
    image_path = Path(image_item["path"])
    assert image_item["type"] == "localImage"
    assert image_path.suffix == ".jpg"
    assert image_path.read_bytes() == b"original-jpeg-bytes"

    claude_root = tmp_path / "claude-case"
    claude_root.mkdir()
    claude_app, _orchestrator, claude_telegram = _gateway(claude_root, provider="claude")
    claude_telegram.download.side_effect = _download
    await claude_app.dispatcher.feed_update(claude_telegram, _photo_update(11))

    claude_call = json.loads(fake_claude.read_text(encoding="utf-8"))["calls"][0]
    attachment_line = claude_call["prompt"].splitlines()[-1]
    assert claude_call["prompt"].startswith("inspect pixels\n\n")
    assert attachment_line.startswith("[Telegram attachment: ")
    assert attachment_line.endswith("; type=image/jpeg]")
    claude_image = Path(attachment_line.removeprefix("[Telegram attachment: ").split(";", 1)[0])
    assert claude_image.suffix == ".jpg"
    assert claude_image.read_bytes() == b"original-jpeg-bytes"
    assert not list(tmp_path.rglob("*.webp"))


async def test_original_document_reaches_codex_as_the_exact_attachment_line(
    tmp_path: Path,
    fake_codex: Path,
) -> None:
    app, _orchestrator, telegram = _gateway(tmp_path)

    async def _download(_file: object, *, destination: Path) -> None:
        destination.write_bytes(b"%PDF-original")

    telegram.download.side_effect = _download
    await app.dispatcher.feed_update(telegram, _document_update(12))

    state = json.loads(fake_codex.read_text(encoding="utf-8"))
    turn = next(item["params"] for item in state["requests"] if item["method"] == "turn/start")
    assert len(turn["input"]) == 1
    text = turn["input"][0]["text"]
    assert text.startswith("inspect report\n\n[Telegram attachment: ")
    assert text.endswith("; type=application/pdf]")
    document = Path(text.split("[Telegram attachment: ", 1)[1].split(";", 1)[0])
    assert document.suffix == ".pdf"
    assert document.read_bytes() == b"%PDF-original"


def test_harness_environment_excludes_gateway_values_but_preserves_native_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TELEGRAM_TO_AGENTS_HOME", "/gateway/new-state")
    monkeypatch.setenv("UNRELATED_PRODUCT_HOME", "/unrelated/state")
    monkeypatch.setenv("OPENAI_API_KEY", "transcription-secret")
    monkeypatch.setenv("CODEX_HOME", "/native/codex")
    monkeypatch.setenv("PATH", "/native/bin")

    child = build_subprocess_env(CLIConfig())

    assert child["CODEX_HOME"] == "/native/codex"
    assert child["PATH"] == "/native/bin"
    assert "TELEGRAM_TO_AGENTS_HOME" not in child
    assert child["UNRELATED_PRODUCT_HOME"] == "/unrelated/state"
    assert child["OPENAI_API_KEY"] == "transcription-secret"


async def test_authorized_file_delivery_cannot_escape_the_selected_project(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    allowed = project / "report.txt"
    allowed.write_text("ok", encoding="utf-8")
    blocked = tmp_path / "secret.txt"
    blocked.write_text("secret", encoding="utf-8")
    telegram = _fake_telegram_bot()

    await send_files_from_text(
        telegram,
        7,
        f"<file:{allowed}>\n<file:{blocked}>",
        allowed_roots=[project],
    )

    telegram.send_document.assert_awaited_once()
    sent_file = telegram.send_document.await_args.kwargs["document"]
    assert Path(sent_file.path) == allowed


def test_codex_rpc_omits_all_gateway_provider_configuration(tmp_path: Path) -> None:
    calls: list[tuple[str, dict[str, object]]] = []

    class _Server:
        def request(self, method: str, params: dict[str, object]) -> dict[str, object]:
            calls.append((method, params))
            return {"thread": {"id": "native-thread"}}

    invocation = Invocation(
        codex_bin=Path("codex"),
        cwd=tmp_path,
        resume_thread=None,
    )
    assert start_or_resume(_Server(), invocation) == "native-thread"  # type: ignore[arg-type]
    method, params = calls[0]
    assert method == "thread/start"
    assert params["cwd"] == str(tmp_path)
    for key in ("model", "effort", "developerInstructions", "sandbox", "approvalPolicy"):
        assert key not in params

    turn = _turn_start_params("native-thread", "exact input", invocation)
    assert turn["input"] == [{"type": "text", "text": "exact input"}]
    for key in ("model", "effort", "developerInstructions", "sandbox", "approvalPolicy"):
        assert key not in turn


def test_configuration_commands_and_file_policy_are_gateway_only(tmp_path: Path) -> None:
    fields = AgentConfig.model_fields
    assert "state_home" in fields
    assert AgentConfig().provider == "codex"
    assert AgentConfig(provider="claude").provider == "claude"
    for removed in (
        "transport",
        "codex_transport",
        "streaming",
        "model",
        "reasoning_effort",
        "permission_mode",
        "prompt_mode",
        "append_system_prompt_files",
        "docker",
        "memory_flush",
        "memory_reflection",
        "memory_compaction",
        "heartbeat",
        "webhooks",
        "api",
        "tasks",
        "skills",
        "matrix",
        "slack",
        "transports",
        "interagent_port",
        "notifications",
        "language",
        "update_check",
        "idle_timeout_minutes",
        "session_age_warning_hours",
        "daily_reset_enabled",
        "daily_reset_hour",
        "max_session_messages",
    ):
        assert removed not in fields

    with pytest.raises(ValidationError):
        AgentConfig(provider="gemini")  # type: ignore[arg-type]

    assert {name for name, _description in get_bot_commands()} == RETAINED_COMMANDS
    assert "turn" in AgentRequest.__dataclass_fields__
    assert "system_prompt" not in AgentRequest.__dataclass_fields__
    assert "append_system_prompt" not in AgentRequest.__dataclass_fields__
    assert "model_override" not in AgentRequest.__dataclass_fields__
    assert "provider_override" not in AgentRequest.__dataclass_fields__
    assert resolve_allowed_roots("workspace", tmp_path) == [tmp_path.resolve()]
    assert resolve_allowed_roots("none", tmp_path) == []


@pytest.mark.parametrize("container", [None, "timeouts", "transcription", "scene"])
def test_unknown_config_field_is_rejected_without_rewriting_the_file(
    tmp_path: Path,
    container: str | None,
) -> None:
    paths = _paths(tmp_path)
    paths.config_path.parent.mkdir(parents=True, exist_ok=True)
    config: dict[str, object] = {
        "provider": "claude",
        "telegram_token": "12345678:abcdefghijklmnopqrstuvwxyzABCDEF123456",
        "allowed_user_ids": [100],
        "project_root": str(tmp_path),
    }
    if container is None:
        config["unexpected_extension"] = {"enabled": True}
    else:
        config[container] = {"unexpected_extension": True}
    original = json.dumps(config, indent=2).encode()
    paths.config_path.write_bytes(original)

    with (
        patch("telegram_to_agents.__main__.resolve_paths", return_value=paths),
        pytest.raises(ValidationError),
    ):
        load_config()

    assert paths.config_path.read_bytes() == original


def test_default_and_explicit_state_roots_leave_unrelated_state_untouched(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_home = tmp_path / "user"
    user_home.mkdir()
    unrelated = user_home / ".unrelated-product"
    unrelated.mkdir()
    sentinel = unrelated / "state.bin"
    sentinel.write_bytes(b"untouched")
    monkeypatch.setenv("HOME", str(user_home))
    monkeypatch.delenv("TELEGRAM_TO_AGENTS_HOME", raising=False)

    default = user_home / ".telegram-to-agents"
    assert resolve_paths().state_home == default.resolve()
    assert not default.exists()
    assert sentinel.read_bytes() == b"untouched"

    explicit = tmp_path / "explicit-state"
    monkeypatch.setenv("TELEGRAM_TO_AGENTS_HOME", str(explicit))
    assert resolve_paths().state_home == explicit.resolve()
    assert not explicit.exists()
    assert sentinel.read_bytes() == b"untouched"


@pytest.mark.parametrize("selection", ["default", "environment"])
async def test_runtime_status_and_stop_share_the_authoritative_state_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    selection: str,
) -> None:
    user_home = tmp_path / "user"
    project = tmp_path / "project"
    user_home.mkdir()
    project.mkdir()
    monkeypatch.setenv("HOME", str(user_home))
    unrelated = tmp_path / "unrelated-state"
    unrelated.mkdir()
    unrelated_sentinel = unrelated / "pid"
    unrelated_sentinel.write_text("111", encoding="utf-8")
    if selection == "environment":
        active = tmp_path / "environment-state"
        monkeypatch.setenv("TELEGRAM_TO_AGENTS_HOME", str(active))
    else:
        active = user_home / ".telegram-to-agents"
        monkeypatch.delenv("TELEGRAM_TO_AGENTS_HOME", raising=False)
    active.joinpath("config").mkdir(parents=True)
    active.joinpath("config/config.json").write_text(
        json.dumps(
            {
                "telegram_token": "12345678:abcdefghijklmnopqrstuvwxyzABCDEF123456",
                "allowed_user_ids": [100],
                "project_root": str(project),
            }
        ),
        encoding="utf-8",
    )

    paths = resolve_paths()
    config = load_config()
    assert paths.state_home == active.resolve()
    assert config.state_home == str(active.resolve())

    active_pid = paths.state_home / "bot.pid"
    active_pid.write_text("222", encoding="utf-8")
    runtime = MagicMock()
    runtime.run = AsyncMock(return_value=0)
    runtime.shutdown = AsyncMock()
    with (
        patch("telegram_to_agents.messenger.telegram.app.TelegramBot", return_value=runtime),
        patch("telegram_to_agents.infra.pidlock.acquire_lock") as acquire,
        patch("telegram_to_agents.infra.pidlock.release_lock") as release,
    ):
        assert await run_bot(config) == 0
    acquire.assert_called_once_with(pid_file=active_pid, kill_existing=True)
    release.assert_called_once_with(pid_file=active_pid)

    with (
        patch("telegram_to_agents.cli_commands.status._console.print") as show,
        patch("telegram_to_agents.infra.pidlock._is_process_alive", return_value=False),
    ):
        print_status()
    assert str(paths.config_path) in show.call_args.args[0].renderable
    assert str(paths.sessions_path) in show.call_args.args[0].renderable

    with (
        patch("telegram_to_agents.infra.service.is_service_installed", return_value=False),
        patch("telegram_to_agents.infra.pidlock._is_process_alive", return_value=False),
    ):
        stop_bot()
    assert not active_pid.exists()
    assert unrelated_sentinel.read_text(encoding="utf-8") == "111"


def test_service_install_manages_only_the_telegram_to_agents_unit(
    tmp_path: Path,
) -> None:
    service_dir = tmp_path / "systemd"
    service_dir.mkdir()
    unrelated_unit = service_dir / "unrelated.service"
    unrelated_unit.write_text("unrelated", encoding="utf-8")
    calls: list[tuple[str, ...]] = []

    def _systemctl(*args: str, user: bool = True) -> SimpleNamespace:
        del user
        calls.append(args)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    with (
        patch.object(service_linux, "_systemd_user_dir", return_value=service_dir),
        patch.object(service_linux, "_has_systemd", return_value=True),
        patch.object(service_linux, "_has_linger", return_value=True),
        patch.object(service_linux, "resolve_paths", return_value=_paths(tmp_path)),
        patch.object(service_linux, "_run_systemctl", side_effect=_systemctl),
        patch.object(
            service_linux,
            "find_telegram_to_agents_binary",
            return_value="/venv/bin/telegram-to-agents",
        ),
    ):
        assert service_linux.install_service() is True

    unit = service_dir / "telegram-to-agents.service"
    assert unit.is_file()
    assert "ExecStart=/venv/bin/telegram-to-agents" in unit.read_text(encoding="utf-8")
    assert unrelated_unit.read_text(encoding="utf-8") == "unrelated"
    assert calls == [
        ("daemon-reload",),
        ("enable", "telegram-to-agents"),
        ("start", "telegram-to-agents"),
    ]


def test_installed_service_launches_with_the_selected_state_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_home = tmp_path / "user"
    project = tmp_path / "project"
    active = tmp_path / "selected state"
    service_dir = tmp_path / "systemd"
    user_home.mkdir()
    project.mkdir()
    service_dir.mkdir()
    active.joinpath("config").mkdir(parents=True)
    active.joinpath("config/config.json").write_text(
        json.dumps(
            {
                "telegram_token": "12345678:abcdefghijklmnopqrstuvwxyzABCDEF123456",
                "allowed_user_ids": [100],
                "project_root": str(project),
            }
        ),
        encoding="utf-8",
    )
    probe = tmp_path / "telegram-to-agents-probe"
    probe.write_text(
        f"""#!{sys.executable}
import json
from telegram_to_agents.__main__ import load_config
from telegram_to_agents.cli_commands.lifecycle import stop_bot
from telegram_to_agents.cli_commands.status import print_status
from telegram_to_agents.workspace.paths import resolve_paths

paths = resolve_paths()
config = load_config()
pid_file = paths.state_home / "bot.pid"
pid_file.write_text("999999999", encoding="utf-8")
print_status()
stop_bot()
print("PROBE=" + json.dumps({{
    "state_home": str(paths.state_home),
    "config_state_home": config.state_home,
    "pid_exists_after_stop": pid_file.exists(),
}}))
""",
        encoding="utf-8",
    )
    probe.chmod(0o755)
    monkeypatch.setenv("HOME", str(user_home))
    monkeypatch.setenv("TELEGRAM_TO_AGENTS_HOME", str(active))
    with (
        patch.object(service_linux, "_systemd_user_dir", return_value=service_dir),
        patch.object(service_linux, "_has_systemd", return_value=True),
        patch.object(service_linux, "_has_linger", return_value=True),
        patch.object(
            service_linux,
            "_run_systemctl",
            return_value=SimpleNamespace(returncode=0, stdout="", stderr=""),
        ),
        patch.object(
            service_linux,
            "find_telegram_to_agents_binary",
            return_value=str(probe),
        ),
    ):
        assert service_linux.install_service() is True

    unit = service_dir.joinpath("telegram-to-agents.service").read_text(encoding="utf-8")
    clean_environment: dict[str, str] = {}
    command: list[str] = []
    for line in unit.splitlines():
        if line.startswith("Environment="):
            assignment = shlex.split(line.removeprefix("Environment="))[0].replace("%%", "%")
            key, _, value = assignment.partition("=")
            clean_environment[key] = value
        elif line.startswith("ExecStart="):
            command = shlex.split(line.removeprefix("ExecStart="))
    assert clean_environment["TELEGRAM_TO_AGENTS_HOME"] == str(active.resolve())
    assert command == [str(probe)]

    default_home = user_home / ".telegram-to-agents"
    default_home.mkdir()
    default_home.joinpath("bot.pid").write_text("111", encoding="utf-8")
    result = subprocess.run(
        command,
        cwd=project,
        env=clean_environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Config:" in result.stdout
    assert "Sessions:" in result.stdout
    probe_result = json.loads(result.stdout.split("PROBE=", maxsplit=1)[1].splitlines()[0])
    assert probe_result == {
        "state_home": str(active.resolve()),
        "config_state_home": str(active.resolve()),
        "pid_exists_after_stop": False,
    }
    assert default_home.joinpath("bot.pid").read_text(encoding="utf-8") == "111"


def test_onboarding_collects_only_provider_telegram_project_and_transcription(
    tmp_path: Path,
) -> None:
    from rich.console import Console

    from telegram_to_agents.cli import init_wizard
    from telegram_to_agents.cli.auth import AuthResult, AuthStatus

    paths = _paths(tmp_path)
    project = tmp_path / "selected-project"
    project.mkdir()
    provider_check = MagicMock(return_value=AuthResult("claude", AuthStatus.AUTHENTICATED))
    with patch.object(init_wizard, "check_auth", provider_check):
        assert init_wizard._check_provider(Console(), "claude") is True
    provider_check.assert_called_once_with("claude")
    assert hasattr(init_wizard, "_ask_provider")
    assert not hasattr(init_wizard, "_ask_transport")

    wizard_config = init_wizard._WizardConfig(
        provider="claude",
        telegram_token="12345678:abcdefghijklmnopqrstuvwxyzABCDEF123456",
        allowed_user_ids=[100],
        project_root=str(project),
        user_timezone="Europe/Rome",
        automatic_audio=True,
        openai_api_key="test-key",
    )
    with patch.object(init_wizard, "resolve_paths", return_value=paths):
        init_wizard._write_config(wizard_config)

    generated = json.loads(paths.config_path.read_text(encoding="utf-8"))
    assert generated == AgentConfig.model_validate(generated).model_dump(mode="json")
    assert generated["provider"] == "claude"
    assert "transport" not in generated
    assert generated["project_root"] == str(project.resolve())
    assert generated["transcription"]["automatic_audio"] is True
    assert "model" not in generated
    assert "prompt_mode" not in generated
    assert paths.env_file.stat().st_mode & 0o777 == 0o600


async def test_provider_change_never_reuses_an_incompatible_session_id(tmp_path: Path) -> None:
    session_path = tmp_path / "sessions.json"
    key = SessionKey.telegram(7)
    codex = SessionManager(session_path, "codex")
    codex_session, _ = await codex.resolve_session(key)
    await codex.update_session(codex_session, "codex-thread")

    claude = SessionManager(session_path, "claude")
    claude_session, is_new = await claude.resolve_session(key)

    assert is_new is True
    assert claude_session.provider == "claude"
    assert claude_session.session_id == ""
    persisted = json.loads(session_path.read_text(encoding="utf-8"))["tg:7"]
    assert persisted["provider"] == "claude"
    assert persisted["session_id"] == ""


async def test_same_topic_turns_serialize_and_resume_the_first_native_session(
    tmp_path: Path,
) -> None:
    _app, orchestrator, _telegram = _gateway(tmp_path)
    first_started = asyncio.Event()
    release_first = asyncio.Event()
    requests: list[AgentRequest] = []

    async def _execute(request: AgentRequest, **_callbacks: object) -> AgentResponse:
        requests.append(request)
        if len(requests) == 1:
            first_started.set()
            await release_first.wait()
        return AgentResponse(result=request.turn.text, session_id="native-session-1")

    orchestrator._cli_service.execute = _execute  # type: ignore[method-assign]
    key = SessionKey.telegram(7, 42)
    first = asyncio.create_task(orchestrator.handle_message(key, UserTurn(text="first")))
    await first_started.wait()
    second = asyncio.create_task(orchestrator.handle_message(key, UserTurn(text="second")))
    await asyncio.sleep(0.01)

    assert [request.turn.text for request in requests] == ["first"]

    release_first.set()
    await asyncio.gather(first, second)
    assert [request.resume_session for request in requests] == [None, "native-session-1"]


async def test_progress_is_deleted_before_one_clean_final_answer(tmp_path: Path) -> None:
    events: list[str] = []
    telegram = _fake_telegram_bot()
    telegram.delete_message.side_effect = lambda **_kwargs: events.append("delete")
    message = SimpleNamespace(
        message_id=1,
        answer=AsyncMock(return_value=SimpleNamespace(message_id=901)),
    )
    orchestrator = AsyncMock()

    async def _handle(_key: SessionKey, _turn: UserTurn, **callbacks: object) -> OrchestratorResult:
        await callbacks["on_progress_update"]("Checking repository")  # type: ignore[operator]
        await callbacks["on_tool_activity"](SimpleNamespace(tool_name="Read"))  # type: ignore[operator]
        return OrchestratorResult(text="Final answer")

    orchestrator.handle_message.side_effect = _handle

    async def _send_final(*_args: object, **_kwargs: object) -> None:
        events.append("final")

    with patch(
        "telegram_to_agents.messenger.telegram.message_dispatch.send_rich",
        AsyncMock(side_effect=_send_final),
    ) as send_final:
        result = await run_message(
            MessageDispatch(
                bot=telegram,
                orchestrator=orchestrator,
                message=message,
                key=SessionKey.telegram(7),
                turn=UserTurn(text="Do work"),
                allowed_roots=[tmp_path],
            )
        )

    assert result == "Final answer"
    assert events == ["delete", "final"]
    send_final.assert_awaited_once()


async def test_native_codex_progress_is_semantic_grouped_and_safe(
    tmp_path: Path,
    fake_codex: Path,
) -> None:
    assert fake_codex.parent == tmp_path
    app, _orchestrator, telegram = _gateway(tmp_path)

    await app.dispatcher.feed_update(telegram, _update(1, "Show aligned progress."))

    initial_payloads = [
        str(method.text)
        for call in telegram.await_args_list
        if call.args
        for method in call.args[:1]
        if isinstance(getattr(method, "text", None), str)
    ]
    edited_payloads = [
        str(call.kwargs["text"])
        for call in telegram.edit_message_text.await_args_list
        if isinstance(call.kwargs.get("text"), str)
    ]
    temporary_payloads = [*initial_payloads, *edited_payloads]

    assert temporary_payloads
    assert any("a deliberately long" in payload for payload in temporary_payloads)
    for payload in temporary_payloads:
        assert "[TOOL:" not in payload
        assert "RAW_REASONING_SENTINEL" not in payload
        assert "SAFE_SUMMARY_SENTINEL" not in payload
        assert "fake assistant response" not in payload
        assert "SHOULD_NOT_APPEAR" not in payload
        assert "progress-secret" not in payload

    final_progress = temporary_payloads[-1]
    assert "Read files" in final_progress
    assert "Read SKILL.md" in final_progress
    assert "Ran command" in final_progress
    assert "Searched the web · 3 searches" in final_progress
    assert final_progress.count("Searched the web") == 1
    assert final_progress.count("Codex App Server") == 1
    assert "rename chat Codex app" in final_progress


async def test_progress_delete_retries_a_transient_network_failure() -> None:
    telegram = _fake_telegram_bot()
    telegram.delete_message.side_effect = [
        TelegramNetworkError(method=MagicMock(), message="temporary network failure"),
        None,
    ]
    message = SimpleNamespace(
        message_id=1,
        answer=AsyncMock(return_value=SimpleNamespace(message_id=901)),
    )
    progress = TemporaryProgressEditor(telegram, 7, reply_to=message)

    await progress.append_tool("Read")

    assert await progress.clear() is True
    assert telegram.delete_message.await_count == 2


async def test_progress_cleanup_failure_withholds_the_final_answer(tmp_path: Path) -> None:
    telegram = _fake_telegram_bot()
    message = SimpleNamespace(message_id=1, answer=AsyncMock())
    orchestrator = AsyncMock()
    orchestrator.handle_message.return_value = OrchestratorResult(text="Do not send")
    with (
        patch(
            "telegram_to_agents.messenger.telegram.message_dispatch.TemporaryProgressEditor.clear",
            AsyncMock(return_value=False),
        ),
        patch(
            "telegram_to_agents.messenger.telegram.message_dispatch.send_rich",
            AsyncMock(),
        ) as send_final,
        pytest.raises(RuntimeError, match="Could not remove temporary"),
    ):
        await run_message(
            MessageDispatch(
                bot=telegram,
                orchestrator=orchestrator,
                message=message,
                key=SessionKey.telegram(7),
                turn=UserTurn(text="Do work"),
                allowed_roots=[tmp_path],
            )
        )
    send_final.assert_not_awaited()


async def test_provider_stream_failure_is_not_replayed(tmp_path: Path) -> None:
    service = CLIService(
        config=CLIServiceConfig(provider="codex", working_dir=str(tmp_path)),
        process_registry=ProcessRegistry(),
    )
    calls = 0

    class _FailingCLI:
        async def send_streaming(self, _request: AgentRequest) -> Any:
            nonlocal calls
            calls += 1
            yield SystemInitEvent(type="system", session_id="accepted-session")
            raise RuntimeError("stream broke")

    with patch.object(service, "_make_cli", return_value=_FailingCLI()):
        response = await service.execute(AgentRequest(turn=UserTurn(text="run once"), chat_id=7))

    assert calls == 1
    assert response.is_error is True
    assert response.session_id == "accepted-session"
    assert "stream broke" in response.result


async def test_provider_stream_without_a_terminal_result_is_not_replayed(tmp_path: Path) -> None:
    service = CLIService(
        config=CLIServiceConfig(provider="codex", working_dir=str(tmp_path)),
        process_registry=ProcessRegistry(),
    )
    calls = 0

    class _IncompleteCLI:
        async def send_streaming(self, _request: AgentRequest) -> Any:
            nonlocal calls
            calls += 1
            yield SystemInitEvent(type="system", session_id="incomplete-session")

    with patch.object(service, "_make_cli", return_value=_IncompleteCLI()):
        response = await service.execute(AgentRequest(turn=UserTurn(text="run once"), chat_id=7))

    assert calls == 1
    assert response.is_error is True
    assert response.session_id == "incomplete-session"
    assert response.result == "The codex turn ended without a final response."


async def test_streaming_and_cancellation_stay_on_the_telegram_boundary(
    tmp_path: Path,
    fake_codex: Path,
) -> None:
    app, orchestrator, telegram = _gateway(tmp_path)
    active_turn = asyncio.create_task(
        app.dispatcher.feed_update(telegram, _update(1, "Cancel this active turn."))
    )
    for _ in range(100):
        try:
            state = json.loads(fake_codex.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            await asyncio.sleep(0.01)
            continue
        turns = [request for request in state["requests"] if request["method"] == "turn/start"]
        if turns:
            break
        await asyncio.sleep(0.01)
    else:
        pytest.fail("active Codex bridge turn did not start")
    assert orchestrator.is_chat_busy(7)

    await app.dispatcher.feed_update(telegram, _update(2, "/stop"))
    assert any(
        "Stopped 1 active turn(s)." in str(call) for call in telegram.send_message.await_args_list
    )
    await asyncio.wait_for(active_turn, timeout=3)

    state = json.loads(fake_codex.read_text(encoding="utf-8"))
    turns = [request for request in state["requests"] if request["method"] == "turn/start"]
    assert [turn["params"]["input"][0]["text"] for turn in turns] == ["Cancel this active turn."]
    persisted = json.loads(orchestrator.paths.sessions_path.read_text(encoding="utf-8"))
    assert persisted["tg:7"]["session_id"] == "thread-shared-1"

    interrupted_turn = asyncio.create_task(
        app.dispatcher.feed_update(telegram, _update(3, "Cancel this active turn."))
    )
    for _ in range(100):
        try:
            current = json.loads(fake_codex.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            await asyncio.sleep(0.01)
            continue
        current_turns = [
            request for request in current["requests"] if request["method"] == "turn/start"
        ]
        if len(current_turns) == 2:
            break
        await asyncio.sleep(0.01)
    else:
        pytest.fail("interrupt target did not reach the provider")
    await app.dispatcher.feed_update(telegram, _update(4, "/interrupt"))
    await asyncio.wait_for(interrupted_turn, timeout=3)
    assert any(
        "Interrupted 1 active turn(s)." in str(call)
        for call in telegram.send_message.await_args_list
    )
    await app.dispatcher.feed_update(telegram, _update(5, "/stop_all"))

    await app.dispatcher.feed_update(telegram, _update(6, "Stream after stop."))
    state = json.loads(fake_codex.read_text(encoding="utf-8"))
    turns = [request for request in state["requests"] if request["method"] == "turn/start"]
    assert [turn["params"]["input"][0]["text"] for turn in turns] == [
        "Cancel this active turn.",
        "Cancel this active turn.",
        "Stream after stop.",
    ]
    assert telegram.delete_message.await_count >= 1


async def test_fixed_timeout_stops_once_and_the_topic_recovers(
    tmp_path: Path,
    fake_codex: Path,
) -> None:
    app, _orchestrator, telegram = _gateway(tmp_path, timeout_seconds=0.05)

    await asyncio.wait_for(
        app.dispatcher.feed_update(telegram, _update(1, "Timeout this turn.")),
        timeout=3,
    )
    await app.dispatcher.feed_update(telegram, _update(2, "Turn after timeout."))

    state = json.loads(fake_codex.read_text(encoding="utf-8"))
    turns = [request for request in state["requests"] if request["method"] == "turn/start"]
    assert [turn["params"]["input"][0]["text"] for turn in turns] == [
        "Timeout this turn.",
        "Turn after timeout.",
    ]
    assert any("timed out after" in str(call) for call in telegram.send_message.await_args_list)
    assert not any("__TIMEOUT__" in str(call) for call in telegram.send_message.await_args_list)


async def test_forum_topic_uses_one_mapped_project_for_codex_where_and_files(
    tmp_path: Path,
    fake_codex: Path,
) -> None:
    mapped = tmp_path / "mapped-project"
    mapped.mkdir()
    allowed = mapped / "topic-report.txt"
    allowed.write_text("ok", encoding="utf-8")
    blocked = tmp_path / "outside.txt"
    blocked.write_text("secret", encoding="utf-8")
    app, _orchestrator, telegram = _gateway(
        tmp_path,
        allowed_group_ids=[-200],
        project_roots={"Builds": str(mapped)},
        file_access="workspace",
    )

    await app.dispatcher.feed_update(telegram, _topic_update(1, topic_name="Builds"))
    await app.dispatcher.feed_update(telegram, _topic_update(2, "Inspect this topic project."))
    await app.dispatcher.feed_update(telegram, _topic_update(3, "/where"))
    key = SessionKey.telegram(-200, 42)
    roots = app.file_roots(key)
    await send_files_from_text(
        telegram,
        -200,
        f"<file:{allowed}>\n<file:{blocked}>",
        allowed_roots=roots,
        thread_id=42,
    )

    state = json.loads(fake_codex.read_text(encoding="utf-8"))
    starts = [
        request["params"] for request in state["requests"] if request["method"] == "thread/start"
    ]
    assert starts[0]["cwd"] == str(mapped.resolve())
    assert roots == [mapped.resolve()]
    assert any(str(mapped.resolve()) in str(call) for call in telegram.send_message.await_args_list)
    telegram.send_document.assert_awaited_once()
    sent_file = telegram.send_document.await_args.kwargs["document"]
    assert Path(sent_file.path) == allowed

    restarted_orchestrator = Orchestrator(app._config, _orchestrator.paths)
    restarted_telegram = _fake_telegram_bot()
    with patch("telegram_to_agents.messenger.telegram.app.Bot", return_value=restarted_telegram):
        restarted_app = TelegramBot(app._config)
    restarted_app._bind_orchestrator(restarted_orchestrator)
    await restarted_app.dispatcher.feed_update(
        restarted_telegram,
        _topic_update(4, "/new"),
    )
    await restarted_app.dispatcher.feed_update(
        restarted_telegram,
        _topic_update(5, "Inspect after gateway restart."),
    )

    state = json.loads(fake_codex.read_text(encoding="utf-8"))
    starts = [
        request["params"] for request in state["requests"] if request["method"] == "thread/start"
    ]
    assert starts[-1]["cwd"] == str(mapped.resolve())
    assert restarted_app.file_roots(key) == [mapped.resolve()]


async def test_invalid_matching_topic_project_fails_without_using_default_or_codex(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing-project"
    app, _orchestrator, telegram = _gateway(
        tmp_path,
        allowed_group_ids=[-200],
        project_roots={"Builds": str(missing)},
    )

    with patch("telegram_to_agents.cli.service.CodexCLI") as codex_cli:
        await app.dispatcher.feed_update(telegram, _topic_update(1, topic_name="Builds"))
        await app.dispatcher.feed_update(telegram, _topic_update(2, "Do not run elsewhere."))

    codex_cli.assert_not_called()
    assert any(
        "configured topic project does not exist" in str(call).lower() and str(missing) in str(call)
        for call in telegram.send_message.await_args_list
    )


async def test_runtime_starts_one_telegram_gateway_without_agent_supervision(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()
    config = AgentConfig(
        telegram_token="12345678:abcdefghijklmnopqrstuvwxyzABCDEF123456",
        allowed_user_ids=[100],
        project_root=str(project),
        log_level="DEBUG",
    )
    runtime = MagicMock()
    runtime.run = AsyncMock(return_value=0)
    runtime.shutdown = AsyncMock()
    with (
        patch("telegram_to_agents.messenger.telegram.app.TelegramBot", return_value=runtime) as create,
        patch("telegram_to_agents.infra.pidlock.acquire_lock"),
        patch("telegram_to_agents.infra.pidlock.release_lock"),
        patch("telegram_to_agents.__main__.logging.basicConfig") as configure_logging,
    ):
        assert await run_bot(config) == 0

    create.assert_called_once_with(config)
    runtime.run.assert_awaited_once_with()
    runtime.shutdown.assert_awaited_once_with()
    configure_logging.assert_called_once()
    assert configure_logging.call_args.kwargs["level"] == logging.DEBUG


def test_built_distributions_use_the_current_gateway_identity() -> None:
    if "GATEWAY_WHEEL" not in os.environ or "GATEWAY_SDIST" not in os.environ:
        pytest.skip("the feature proof builds and supplies both distributions")
    wheel_path = Path(os.environ["GATEWAY_WHEEL"])
    sdist_path = Path(os.environ["GATEWAY_SDIST"])
    assert wheel_path.is_file()
    assert sdist_path.is_file()
    assert wheel_path.name == "telegram_to_agents-0.1.0-py3-none-any.whl"
    assert sdist_path.name == "telegram_to_agents-0.1.0.tar.gz"
    with zipfile.ZipFile(wheel_path) as wheel:
        names = set(wheel.namelist())
        metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
        metadata = wheel.read(metadata_name).decode("utf-8")
        entry_points_name = next(
            name for name in names if name.endswith(".dist-info/entry_points.txt")
        )
        entry_points = wheel.read(entry_points_name).decode("utf-8")

    assert "telegram_to_agents/transcription/openai_audio.py" in names
    assert "telegram_to_agents/cli/codex_provider.py" in names
    assert "telegram_to_agents/cli/claude_provider.py" in names
    assert "telegram_to_agents/cli/codex_appserver_bridge.py" in names
    package_python = {
        name for name in names if name.startswith("telegram_to_agents/") and name.endswith(".py")
    }
    assert package_python <= ALLOWED_SOURCE_FILES
    lowered_metadata = metadata.lower()
    assert "Name: telegram-to-agents" in metadata
    assert "Version: 0.1.0" in metadata
    assert "https://github.com/marcocello/telegram-to-agents" in metadata
    assert "telegram-to-agents = telegram_to_agents.__main__:main" in entry_points
    console_scripts = [
        line for line in entry_points.splitlines() if line and not line.startswith("[")
    ]
    assert console_scripts == ["telegram-to-agents = telegram_to_agents.__main__:main"]
    assert "native codex and claude harnesses" in lowered_metadata
    for removed in ("gemini", "grok", "antigravity", "matrix", "slack"):
        assert removed not in lowered_metadata
    assert "Provides-Extra: matrix" not in metadata
    assert "Provides-Extra: slack" not in metadata

    with tarfile.open(sdist_path, "r:gz") as archive:
        sdist_names = {name.split("/", 1)[-1] for name in archive.getnames() if "/" in name}
        pyproject_member = next(
            member for member in archive.getmembers() if member.name.endswith("/pyproject.toml")
        )
        extracted = archive.extractfile(pyproject_member)
        assert extracted is not None
        sdist_pyproject = extracted.read().decode("utf-8")
    assert "src/telegram_to_agents/__main__.py" in sdist_names
    assert 'name = "telegram-to-agents"' in sdist_pyproject
    assert 'packages = ["src/telegram_to_agents"]' in sdist_pyproject


def test_source_checkout_contains_only_the_gateway() -> None:
    repo_root = Path(__file__).parents[2]

    def _files_under(relative_root: str) -> set[str]:
        root = repo_root / relative_root
        return {
            path.relative_to(repo_root).as_posix()
            for path in root.rglob("*")
            if path.is_file()
            and "__pycache__" not in path.parts
            and "runs" not in path.parts
            and path.suffix not in {".pyc", ".pyo"}
        }

    expected_source_files = {f"src/{path}" for path in ALLOWED_SOURCE_FILES}
    assert _files_under("src") == expected_source_files
    assert not (repo_root / "telegram_to_agents").exists()
    assert _files_under("tests") <= ALLOWED_TEST_FILES
    assert _files_under("docs") <= ALLOWED_DOC_FILES
    assert _files_under(".github") <= ALLOWED_GITHUB_FILES
    assert {path.name for path in repo_root.iterdir() if path.is_file()} <= ALLOWED_ROOT_FILES

    active_docs = "\n".join(
        (repo_root / path).read_text(encoding="utf-8")
        for path in ("README.md", "docs/installation.md", "docs/architecture.md")
    )
    for expected in (
        "codex app-server proxy",
        "codex app-server --listen stdio://",
        "Remote Control is optional",
        "macOS",
        "Linux systemd",
    ):
        assert expected in active_docs

    project = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["name"] == "telegram-to-agents"
    assert project["project"]["version"] == "0.1.0"
    assert project["project"]["urls"]["Repository"] == (
        "https://github.com/marcocello/telegram-to-agents"
    )
    assert project["project"]["scripts"] == {
        "telegram-to-agents": "telegram_to_agents.__main__:main"
    }
    dependencies = "\n".join(project["project"]["dependencies"]).lower()
    assert "pillow" not in dependencies
    assert "pyyaml" not in dependencies
    hatch_build = project.get("tool", {}).get("hatch", {}).get("build", {})
    assert not hatch_build.get("exclude")
    assert hatch_build["targets"]["wheel"]["packages"] == ["src/telegram_to_agents"]
    assert "src/telegram_to_agents/" in hatch_build["targets"]["sdist"]["include"]

    developer_paths = "\n".join(
        (repo_root / path).read_text(encoding="utf-8")
        for path in ("docs/developer_quickstart.md",)
    )
    assert "mypy src/telegram_to_agents" in developer_paths
    assert "mypy telegram_to_agents" not in developer_paths

    license_text = repo_root.joinpath("LICENSE").read_text(encoding="utf-8")
    assert "Copyright (c) 2025-2026 PleasePrompto" in license_text
    assert "Copyright (c) 2026 Marco Cello" in license_text
    assert (
        "telegram-to-agents is a derived version of Ductor by PleasePrompto"
        in license_text
    )
    readme = repo_root.joinpath("README.md").read_text(encoding="utf-8")
    assert "based on Ductor by PleasePrompto" in readme
