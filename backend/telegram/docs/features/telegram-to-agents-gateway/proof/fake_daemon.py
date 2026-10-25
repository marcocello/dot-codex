# ruff: noqa: INP001

from __future__ import annotations

import json
import os
import socket
import socketserver
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(eq=False)
class _Client:
    socket: socket.socket
    name: str = "unknown"
    subscriptions: set[str] = field(default_factory=set)
    write_lock: threading.Lock = field(default_factory=threading.Lock)


class FakeDaemon:
    """Long-lived multi-client App Server boundary used by the gateway proof."""

    def __init__(self, state_path: Path) -> None:
        self.state_path = state_path
        self._state_lock = threading.RLock()
        self._clients_lock = threading.Lock()
        self._clients: set[_Client] = set()
        daemon = self

        class Handler(socketserver.StreamRequestHandler):
            def handle(self) -> None:
                daemon._handle(self)

        self._temp_dir = Path(tempfile.mkdtemp(prefix="telegram-to-agents-proof-", dir="/tmp"))
        self._socket_path = self._temp_dir / "app-server.sock"
        self._server = socketserver.ThreadingUnixStreamServer(str(self._socket_path), Handler)
        self._server.daemon_threads = True
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def address(self) -> str:
        return str(self._socket_path)

    def start(self) -> None:
        self._save({"threads": {}, "requests": [], "invocations": []})
        self._thread.start()

    def close(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=3)
        self._socket_path.unlink(missing_ok=True)
        self._temp_dir.rmdir()

    def _load(self) -> dict[str, Any]:
        with self._state_lock:
            return json.loads(self.state_path.read_text())

    def _save(self, state: dict[str, Any]) -> None:
        with self._state_lock:
            self.state_path.write_text(json.dumps(state))

    @staticmethod
    def _send(client: _Client, value: dict[str, Any]) -> None:
        payload = (json.dumps(value) + "\n").encode()
        with client.write_lock:
            client.socket.sendall(payload)

    def _broadcast(self, thread_id: str, values: list[dict[str, Any]]) -> None:
        with self._clients_lock:
            recipients = [c for c in self._clients if thread_id in c.subscriptions]
        for value in values:
            for client in recipients:
                self._send(client, value)

    def _handle(self, handler: socketserver.StreamRequestHandler) -> None:
        client = _Client(handler.connection)
        with self._clients_lock:
            self._clients.add(client)
        try:
            for raw in handler.rfile:
                message = json.loads(raw)
                if "_proxy" in message:
                    state = self._load()
                    state["invocations"].append(message["_proxy"])
                    self._save(state)
                    continue
                self._handle_message(client, message)
        finally:
            with self._clients_lock:
                self._clients.discard(client)

    def _handle_message(self, client: _Client, message: dict[str, Any]) -> None:
        method = message.get("method")
        request_id = message.get("id")
        if method == "initialized":
            return
        if method == "initialize":
            info = message.get("params", {}).get("clientInfo", {})
            client.name = str(info.get("name", "unknown"))
            self._send(client, {"id": request_id, "result": {}})
            return

        state = self._load()
        state["requests"].append({"method": method, "params": message.get("params", {})})
        mode = os.environ.get("FAKE_CODEX_MODE", "normal")
        if method == "thread/start":
            if mode == "thread_start_error":
                self._send_error(client, request_id, "start failed")
                return
            self._start_thread(client, message, state)
        elif method == "thread/resume":
            self._resume_thread(client, message, state)
        elif method == "turn/start":
            self._start_turn(client, message, state, mode)
        else:
            self._send_error(client, request_id, f"unsupported {method}", code=-32601)

    def _start_thread(
        self,
        client: _Client,
        message: dict[str, Any],
        state: dict[str, Any],
    ) -> None:
        thread_id = "thread-shared-1"
        params = message["params"]
        state["threads"][thread_id] = {
            "id": thread_id,
            "cwd": params["cwd"],
            "source": params.get("threadSource"),
            "turns": [],
            "busy": False,
        }
        self._save(state)
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
        self._send(client, {"id": message["id"], "result": {"thread": {"id": thread_id}}})

    def _resume_thread(
        self,
        client: _Client,
        message: dict[str, Any],
        state: dict[str, Any],
    ) -> None:
        thread_id = message["params"]["threadId"]
        if thread_id not in state["threads"]:
            self._save(state)
            self._send_error(client, message["id"], "thread not found")
            return
        self._save(state)
        client.subscriptions.add(thread_id)
        self._send(client, {"id": message["id"], "result": {"thread": {"id": thread_id}}})

    def _start_turn(
        self,
        client: _Client,
        message: dict[str, Any],
        state: dict[str, Any],
        mode: str,
    ) -> None:
        if mode == "premature_exit":
            client.socket.shutdown(socket.SHUT_RDWR)
            return
        thread_id = message["params"]["threadId"]
        thread = state["threads"][thread_id]
        if thread.get("busy"):
            self._send_error(client, message["id"], "thread busy")
            return
        text = message["params"]["input"][0]["text"]
        label = "app" if client.name == "codex_app" else "telegram"
        thread["turns"].append({"client": label, "text": text})
        turn_id = f"turn-{len(thread['turns'])}"
        self._save(state)
        if mode == "lost_turn_ack":
            client.socket.shutdown(socket.SHUT_RDWR)
            return
        self._send(client, {"id": message["id"], "result": {"turn": {"id": turn_id}}})
        events = [
            {
                "method": "item/started",
                "params": {
                    "threadId": thread_id,
                    "turnId": "foreign-turn",
                    "startedAtMs": 0,
                    "item": {
                        "id": "foreign-final",
                        "type": "agentMessage",
                        "text": "",
                        "phase": "final_answer",
                    },
                },
            },
            {
                "method": "item/agentMessage/delta",
                "params": {
                    "threadId": thread_id,
                    "turnId": "foreign-turn",
                    "itemId": "foreign-final",
                    "delta": "FOREIGN_TURN_SENTINEL",
                },
            },
            {
                "method": "item/started",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "startedAtMs": 0,
                    "item": {
                        "id": "unknown-phase",
                        "type": "agentMessage",
                        "text": "",
                    },
                },
            },
            {
                "method": "item/agentMessage/delta",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "itemId": "unknown-phase",
                    "delta": "UNKNOWN_PHASE_SENTINEL",
                },
            },
            {
                "method": "item/started",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "startedAtMs": 0,
                    "item": {
                        "id": "commentary-1",
                        "type": "agentMessage",
                        "text": "",
                        "phase": "commentary",
                    },
                },
            },
            {
                "method": "item/agentMessage/delta",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "itemId": "commentary-1",
                    "delta": "Checking\t<selected>  project\nand preparing ",
                },
            },
            {
                "method": "item/agentMessage/delta",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "itemId": "commentary-1",
                    "delta": "a deliberately long & compact commentary preview",
                },
            },
            {
                "method": "item/agentMessage/delta",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "itemId": "commentary-1",
                    "delta": " with more detail that cannot change the capped preview",
                },
            },
            {
                "method": "item/agentMessage/delta",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "itemId": "commentary-1",
                    "delta": " and must not create another Telegram bubble",
                },
            },
            {
                "method": "item/reasoning/summaryTextDelta",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "itemId": "reasoning-1",
                    "summaryIndex": 0,
                    "delta": "SAFE_SUMMARY_SENTINEL",
                },
            },
            {
                "method": "item/reasoning/textDelta",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "itemId": "reasoning-1",
                    "contentIndex": 0,
                    "delta": "RAW_REASONING_SENTINEL",
                },
            },
            {
                "method": "item/started",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "startedAtMs": 1,
                    "item": {
                        "id": "command-1",
                        "type": "commandExecution",
                        "command": "cat /workspace/SKILL.md",
                        "commandActions": [
                            {
                                "type": "read",
                                "command": "cat /workspace/SKILL.md",
                                "name": "SKILL.md",
                                "path": "/workspace/SKILL.md",
                            }
                        ],
                        "cwd": thread["cwd"],
                        "status": "inProgress",
                    },
                },
            },
            {
                "method": "item/started",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "startedAtMs": 2,
                    "item": {
                        "id": "command-2",
                        "type": "commandExecution",
                        "command": "cat /tmp/SHOULD_NOT_APPEAR secret-token=progress-secret",
                        "commandActions": [
                            {
                                "type": "unknown",
                                "command": (
                                    "cat /tmp/SHOULD_NOT_APPEAR "
                                    "secret-token=progress-secret"
                                ),
                            }
                        ],
                        "cwd": thread["cwd"],
                        "status": "inProgress",
                    },
                },
            },
            {
                "method": "item/started",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "startedAtMs": 3,
                    "item": {
                        "id": "file-1",
                        "type": "fileChange",
                        "changes": [],
                        "status": "inProgress",
                    },
                },
            },
            {
                "method": "item/started",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "startedAtMs": 4,
                    "item": {
                        "id": "mcp-1",
                        "type": "mcpToolCall",
                        "server": "filesystem",
                        "tool": "read_file",
                        "arguments": {"path": "README.md"},
                        "status": "inProgress",
                    },
                },
            },
            {
                "method": "item/started",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "startedAtMs": 5,
                    "item": {
                        "id": "search-1",
                        "type": "webSearch",
                        "query": "Codex App Server",
                    },
                },
            },
            {
                "method": "item/started",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "startedAtMs": 6,
                    "item": {
                        "id": "search-2",
                        "type": "webSearch",
                        "query": "Codex App Server",
                    },
                },
            },
            {
                "method": "item/started",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "startedAtMs": 7,
                    "item": {
                        "id": "search-3",
                        "type": "webSearch",
                        "query": "rename chat Codex app",
                    },
                },
            },
            {
                "method": "item/started",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "startedAtMs": 8,
                    "item": {
                        "id": "final-1",
                        "type": "agentMessage",
                        "text": "",
                        "phase": "final_answer",
                    },
                },
            },
            {
                "method": "item/agentMessage/delta",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "itemId": "final-1",
                    "delta": "fake assistant response",
                },
            },
            {
                "method": "item/completed",
                "params": {
                    "threadId": thread_id,
                    "turnId": turn_id,
                    "item": {
                        "id": "final-1",
                        "type": "agentMessage",
                        "text": "fake assistant response",
                        "phase": "final_answer",
                    },
                },
            },
            {
                "method": "turn/completed",
                "params": {
                    "threadId": thread_id,
                    "turn": {"id": turn_id, "status": "completed"},
                },
            },
        ]
        self._broadcast(thread_id, events)

    def _send_error(
        self,
        client: _Client,
        request_id: object,
        message: str,
        *,
        code: int = -32000,
    ) -> None:
        self._send(client, {"id": request_id, "error": {"code": code, "message": message}})


class ObserverClient:
    """Second already-connected client used to verify live notifications."""

    def __init__(self, address: str) -> None:
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._socket.settimeout(3)
        self._socket.connect(address)
        self._stream = self._socket.makefile("rwb")
        self._next_id = 1
        self._queued: list[dict[str, Any]] = []
        self.request(
            "initialize",
            {"clientInfo": {"name": "codex_app", "title": "Proof observer", "version": "1"}},
        )
        self.notify("initialized", {})

    def close(self) -> None:
        self._stream.close()
        self._socket.close()

    def _write(self, value: dict[str, Any]) -> None:
        self._stream.write((json.dumps(value) + "\n").encode())
        self._stream.flush()

    def _read(self) -> dict[str, Any]:
        self._socket.settimeout(3)
        line = self._stream.readline()
        if not line:
            raise AssertionError("observer connection closed")
        return json.loads(line)

    def notify(self, method: str, params: dict[str, Any]) -> None:
        self._write({"method": method, "params": params})

    def request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        request_id = self._next_id
        self._next_id += 1
        self._write({"id": request_id, "method": method, "params": params})
        while True:
            message = self._read()
            if message.get("id") == request_id:
                return message.get("result", {})
            self._queued.append(message)

    def wait_for(self, method: str, *, timeout: float = 3) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            for index, message in enumerate(self._queued):
                if message.get("method") == method:
                    return self._queued.pop(index)
            message = self._read()
            if message.get("method") == method:
                return message
            self._queued.append(message)
        raise AssertionError(f"observer did not receive {method}")
