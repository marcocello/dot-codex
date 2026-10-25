"""Translate one Telegram Codex turn into native App Server JSON-RPC.

The module intentionally emits the same JSONL events as ``codex exec --json``
so the gateway parser and session persistence remain the single consumer.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import struct
import subprocess
import sys
import threading
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Any, Self

from telegram_to_agents.cli.types import CodexTransport

_WEBSOCKET_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
_MAX_HTTP_HEADER_BYTES = 16_384
_MAX_WEBSOCKET_MESSAGE_BYTES = 64 * 1024 * 1024
_MAX_JSON_LINE_BYTES = 64 * 1024 * 1024


class BridgeError(RuntimeError):
    """A process, protocol, or App Server request failed."""


def _transport_streams(process: subprocess.Popen[bytes]) -> tuple[IO[bytes], IO[bytes]]:
    if process.stdin is None or process.stdout is None:
        raise BridgeError("could not open Codex App Server transport")
    return process.stdin, process.stdout


def _upgrade_headers(raw: bytes) -> dict[str, str]:
    try:
        lines = raw.decode("ascii").split("\r\n")
    except UnicodeDecodeError as exc:
        raise BridgeError("Codex App Server returned an invalid WebSocket upgrade") from exc
    if lines[0] != "HTTP/1.1 101 Switching Protocols":
        raise BridgeError(f"Codex App Server WebSocket upgrade failed: {lines[0]}")
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if not line:
            continue
        try:
            name, value = line.split(":", 1)
        except ValueError as exc:
            raise BridgeError("Codex App Server returned a malformed WebSocket header") from exc
        headers[name.lower()] = value.strip()
    return headers


def _header_tokens(value: str) -> set[str]:
    return {token.strip().lower() for token in value.split(",") if token.strip()}


class AppServer:
    """Small synchronous JSON-RPC client for one Codex App Server transport."""

    def __init__(
        self,
        codex_bin: Path,
        *,
        transport: CodexTransport,
    ) -> None:
        self._transport = transport
        self._next_id = 1
        self._queued: deque[dict[str, Any]] = deque()
        self._stderr: deque[str] = deque(maxlen=80)
        command = (
            ("app-server", "proxy")
            if transport == "managed"
            else ("app-server", "--listen", "stdio://")
        )
        self._process = subprocess.Popen(
            [str(codex_bin), *command],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
        try:
            self._stdin, self._stdout = _transport_streams(self._process)
            threading.Thread(target=self._drain_stderr, daemon=True).start()
            if self._transport == "managed":
                self._upgrade_websocket()
            self.request(
                "initialize",
                {
                    "clientInfo": {
                        "name": "telegram-to-agents",
                        "title": "telegram-to-agents gateway",
                        "version": "1.0.0",
                    },
                    "capabilities": {"experimentalApi": True},
                },
            )
            self.notify("initialized", {})
        except BaseException:
            self.close()
            raise

    def _drain_stderr(self) -> None:
        if self._process.stderr is None:
            return
        for line in self._process.stderr:
            self._stderr.append(line.decode(errors="replace").rstrip())

    def _read_exact(self, size: int) -> bytes:
        data = bytearray()
        while len(data) < size:
            chunk = self._stdout.read(size - len(data))
            if not chunk:
                detail = "\n".join(self._stderr)[-2000:]
                suffix = f": {detail}" if detail else ""
                raise BridgeError(f"Codex App Server closed unexpectedly{suffix}")
            data.extend(chunk)
        return bytes(data)

    def _upgrade_websocket(self) -> None:
        key = base64.b64encode(os.urandom(16)).decode()
        request = (
            "GET / HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self._stdin.write(request.encode())
        self._stdin.flush()

        raw = bytearray()
        while not raw.endswith(b"\r\n\r\n"):
            raw.extend(self._read_exact(1))
            if len(raw) > _MAX_HTTP_HEADER_BYTES:
                raise BridgeError("Codex App Server returned an oversized WebSocket upgrade")
        headers = _upgrade_headers(bytes(raw))
        expected = base64.b64encode(
            hashlib.sha1((key + _WEBSOCKET_GUID).encode(), usedforsecurity=False).digest()
        ).decode()
        if headers.get("upgrade", "").lower() != "websocket":
            raise BridgeError("Codex App Server returned an invalid WebSocket Upgrade header")
        if "upgrade" not in _header_tokens(headers.get("connection", "")):
            raise BridgeError("Codex App Server returned an invalid WebSocket Connection header")
        if headers.get("sec-websocket-accept") != expected:
            raise BridgeError("Codex App Server returned an invalid WebSocket accept value")

    @staticmethod
    def _masked_frame(payload: bytes, *, opcode: int = 1) -> bytes:
        mask = os.urandom(4)
        header = bytearray([0x80 | opcode])
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length <= 0xFFFF:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", length))
        masked = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        return bytes(header) + mask + masked

    def _write_frame(self, payload: bytes, *, opcode: int = 1) -> None:
        try:
            self._stdin.write(self._masked_frame(payload, opcode=opcode))
            self._stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise BridgeError("Codex App Server closed while receiving a request") from exc

    def _read_frame(self) -> tuple[bool, int, bytes]:
        first, second = self._read_exact(2)
        fin = bool(first & 0x80)
        if first & 0x70:
            raise BridgeError("Codex App Server emitted unsupported WebSocket extensions")
        opcode = first & 0x0F
        masked = bool(second & 0x80)
        if masked:
            raise BridgeError("Codex App Server emitted a masked server WebSocket frame")
        length = second & 0x7F
        if opcode >= 8 and (not fin or length >= 126):
            raise BridgeError("Codex App Server emitted an invalid WebSocket control frame")
        if length == 126:
            length = struct.unpack("!H", self._read_exact(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self._read_exact(8))[0]
        if length > _MAX_WEBSOCKET_MESSAGE_BYTES:
            raise BridgeError("Codex App Server emitted an oversized WebSocket message")
        payload = self._read_exact(length)
        return fin, opcode, payload

    def _write(self, message: dict[str, Any]) -> None:
        payload = json.dumps(message, separators=(",", ":")).encode()
        if self._transport == "managed":
            self._write_frame(payload)
            return
        try:
            self._stdin.write(payload + b"\n")
            self._stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise BridgeError("Codex App Server closed while receiving a request") from exc

    def _handle_control_frame(self, opcode: int, payload: bytes) -> None:
        if opcode == 8:
            raise BridgeError("Codex App Server closed the WebSocket connection")
        if opcode == 9:
            self._write_frame(payload, opcode=10)
        elif opcode != 10:
            raise BridgeError(f"Codex App Server emitted unsupported WebSocket opcode {opcode}")

    @staticmethod
    def _append_data_frame(
        fragments: bytearray | None,
        *,
        fin: bool,
        opcode: int,
        payload: bytes,
    ) -> tuple[bytearray | None, bytes | None]:
        if opcode == 1:
            if fragments is not None:
                raise BridgeError(
                    "Codex App Server started a new message before finishing a fragmented one"
                )
            return (None, payload) if fin else (bytearray(payload), None)
        if opcode != 0:
            kind = "binary message" if opcode == 2 else f"WebSocket opcode {opcode}"
            raise BridgeError(f"Codex App Server emitted unsupported {kind}")
        if fragments is None:
            raise BridgeError("Codex App Server emitted a continuation frame without a message")
        fragments.extend(payload)
        if len(fragments) > _MAX_WEBSOCKET_MESSAGE_BYTES:
            raise BridgeError("Codex App Server emitted an oversized WebSocket message")
        return (None, bytes(fragments)) if fin else (fragments, None)

    def _read_message_payload(self) -> bytes:
        fragments: bytearray | None = None
        while True:
            fin, opcode, payload = self._read_frame()
            if opcode >= 8:
                self._handle_control_frame(opcode, payload)
                continue
            fragments, complete = self._append_data_frame(
                fragments,
                fin=fin,
                opcode=opcode,
                payload=payload,
            )
            if complete is not None:
                return complete

    def _read(self) -> dict[str, Any]:
        if self._transport == "managed":
            message_payload = self._read_message_payload()
        else:
            message_payload = self._stdout.readline(_MAX_JSON_LINE_BYTES + 1)
            if not message_payload:
                detail = "\n".join(self._stderr)[-2000:]
                suffix = f": {detail}" if detail else ""
                raise BridgeError(f"Codex App Server closed unexpectedly{suffix}")
            if len(message_payload) > _MAX_JSON_LINE_BYTES:
                raise BridgeError("Codex App Server emitted an oversized JSON message")
        try:
            value = json.loads(message_payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            preview = message_payload[:200].decode(errors="replace")
            raise BridgeError(f"Codex App Server emitted invalid JSON: {preview}") from exc
        if not isinstance(value, dict):
            raise BridgeError("Codex App Server emitted a non-object message")
        return value

    def notify(self, method: str, params: dict[str, Any]) -> None:
        self._write({"method": method, "params": params})

    def request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        request_id = self._next_id
        self._next_id += 1
        self._write({"id": request_id, "method": method, "params": params})
        while True:
            message = self._read()
            if message.get("id") != request_id:
                self._queued.append(message)
                continue
            if "error" in message:
                error = message.get("error")
                detail = error.get("message") if isinstance(error, dict) else str(error)
                raise BridgeError(f"{method} failed: {detail}")
            result = message.get("result", {})
            if not isinstance(result, dict):
                raise BridgeError(f"{method} returned an invalid result")
            return result

    def next_message(self) -> dict[str, Any]:
        return self._queued.popleft() if self._queued else self._read()

    def answer_unsupported_request(self, message: dict[str, Any]) -> None:
        request_id = message.get("id")
        if request_id is None:
            return
        self._write(
            {
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": "telegram-to-agents cannot answer interactive App Server requests",
                },
            }
        )

    def close(self) -> None:
        if self._process.poll() is not None:
            return
        self._process.terminate()
        try:
            self._process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait(timeout=3)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


@dataclass(frozen=True, slots=True)
class Invocation:
    """Validated inputs for a single App Server-backed turn."""

    codex_bin: Path
    cwd: Path
    resume_thread: str | None
    images: tuple[Path, ...] = ()
    transport: CodexTransport = "managed"
    resume_transport: CodexTransport | None = None


@dataclass(slots=True)
class _TurnState:
    """Accumulated response state while one App Server turn is active."""

    text_parts: list[str]
    last_error: str | None = None
    item_phases: dict[str, str] = field(default_factory=dict)
    delta_item_ids: set[str] = field(default_factory=set)


_APP_SERVER_TOOL_TYPES: dict[str, str] = {
    "commandExecution": "command_execution",
    "fileChange": "file_change",
    "webSearch": "web_search",
}


def _thread_id(result: dict[str, Any], method: str) -> str:
    thread = result.get("thread")
    value = thread.get("id") if isinstance(thread, dict) else None
    if not isinstance(value, str) or not value:
        raise BridgeError(f"{method} did not return a thread ID")
    return value


def start_or_resume(server: AppServer, invocation: Invocation) -> str:
    """Start an app-visible project thread or resume the exact stored thread."""
    params: dict[str, Any] = {"cwd": str(invocation.cwd)}
    if invocation.resume_thread and invocation.resume_transport == invocation.transport:
        params["threadId"] = invocation.resume_thread
        return _thread_id(server.request("thread/resume", params), "thread/resume")
    params["threadSource"] = "vscode"
    params["serviceName"] = "telegram-to-agents"
    return _thread_id(server.request("thread/start", params), "thread/start")


def _consume_turn_event(
    message: dict[str, Any],
    *,
    thread_id: str,
    turn_id: str,
    state: _TurnState,
) -> dict[str, Any] | None:
    """Consume one notification and return the matching completed turn."""
    method = message.get("method")
    event = message.get("params", {})
    if not isinstance(event, dict) or event.get("threadId") not in {None, thread_id}:
        return None
    if method in {"item/agentMessage/delta", "item/completed"} and event.get("turnId") != turn_id:
        return None
    if _consume_agent_message_event(method, event, state):
        return None
    if method == "error" and event.get("turnId") == turn_id and not event.get("willRetry"):
        error = event.get("error")
        state.last_error = error.get("message") if isinstance(error, dict) else str(error)
    elif method == "turn/completed":
        completed = event.get("turn")
        if isinstance(completed, dict) and completed.get("id") == turn_id:
            return completed
    return None


def _consume_agent_message_event(
    method: object,
    event: dict[str, Any],
    state: _TurnState,
) -> bool:
    if method == "item/agentMessage/delta" and isinstance(event.get("delta"), str):
        item_id = event.get("itemId")
        if isinstance(item_id, str):
            state.delta_item_ids.add(item_id)
        if isinstance(item_id, str) and state.item_phases.get(item_id) == "final_answer":
            state.text_parts.append(event["delta"])
        return True
    if method == "item/completed":
        item = event.get("item")
        item_id = item.get("id") if isinstance(item, dict) else None
        phase = item.get("phase") if isinstance(item, dict) else None
        already_streamed = isinstance(item_id, str) and item_id in state.delta_item_ids
        if (
            isinstance(item, dict)
            and item.get("type") == "agentMessage"
            and phase == "final_answer"
            and not already_streamed
        ):
            item_text = item.get("text")
            if isinstance(item_text, str) and item_text:
                state.text_parts.append(item_text)
        return True
    return False


def _turn_start_params(thread_id: str, prompt: str, invocation: Invocation) -> dict[str, Any]:
    inputs: list[dict[str, str]] = []
    if prompt:
        inputs.append({"type": "text", "text": prompt})
    inputs.extend({"type": "localImage", "path": str(path)} for path in invocation.images)
    params: dict[str, Any] = {
        "threadId": thread_id,
        "input": inputs,
    }
    return params


def _tool_progress_item(item: dict[str, Any]) -> dict[str, Any] | None:
    item_type = item.get("type")
    item_id = item.get("id")
    if not isinstance(item_id, str):
        return None
    if item_type == "mcpToolCall":
        server = item.get("server")
        tool = item.get("tool")
        if not isinstance(tool, str):
            return None
        name = f"{server}/{tool}" if isinstance(server, str) and server else tool
        progress: dict[str, Any] = {"id": item_id, "type": "mcp_tool_call", "name": name}
        arguments = item.get("arguments")
        if isinstance(arguments, dict):
            progress["arguments"] = arguments
        return progress
    progress_type = _APP_SERVER_TOOL_TYPES.get(str(item_type))
    if progress_type is None:
        return None
    progress = {"id": item_id, "type": progress_type}
    if item_type == "commandExecution":
        parameters = _command_progress_parameters(item)
        if parameters:
            progress["parameters"] = parameters
    elif item_type == "webSearch" and isinstance(item.get("query"), str):
        progress["input"] = {"query": item["query"]}
    return progress


def _command_progress_parameters(item: dict[str, Any]) -> dict[str, Any]:
    parameters: dict[str, Any] = {}
    if isinstance(item.get("command"), str):
        parameters["command"] = item["command"]
    command_actions = item.get("commandActions")
    if isinstance(command_actions, list):
        parameters["command_actions"] = command_actions
    return parameters


def _progress_exec_event(
    message: dict[str, Any],
    *,
    thread_id: str,
    turn_id: str,
    state: _TurnState,
) -> dict[str, Any] | None:
    params = message.get("params")
    if not isinstance(params, dict):
        return None
    if params.get("threadId") != thread_id or params.get("turnId") != turn_id:
        return None
    method = message.get("method")
    if method == "item/reasoning/summaryTextDelta" and isinstance(params.get("delta"), str):
        return {"type": "system", "subtype": "status", "status": "thinking"}
    if method == "item/agentMessage/delta" and isinstance(params.get("delta"), str):
        item_id = params.get("itemId")
        if isinstance(item_id, str) and state.item_phases.get(item_id) == "commentary":
            return {"type": "progress", "text": params["delta"]}
    if method != "item/started":
        return None
    item = params.get("item")
    progress_item = _tool_progress_item(item) if isinstance(item, dict) else None
    return {"type": "item.started", "item": progress_item} if progress_item else None


def _record_agent_message_phase(
    message: dict[str, Any],
    *,
    thread_id: str,
    turn_id: str,
    state: _TurnState,
) -> None:
    if message.get("method") not in {"item/started", "item/completed"}:
        return
    params = message.get("params")
    if not isinstance(params, dict):
        return
    if params.get("threadId") != thread_id or params.get("turnId") != turn_id:
        return
    item = params.get("item")
    if not isinstance(item, dict) or item.get("type") != "agentMessage":
        return
    item_id = item.get("id")
    phase = item.get("phase")
    if isinstance(item_id, str) and isinstance(phase, str):
        state.item_phases[item_id] = phase


def _emit_exec_event(event: dict[str, Any]) -> None:
    print(json.dumps(event), flush=True)


def run_turn(
    server: AppServer,
    thread_id: str,
    prompt: str,
    invocation: Invocation,
) -> tuple[str, dict[str, Any]]:
    """Run one text turn and collect its final assistant message."""
    started = server.request("turn/start", _turn_start_params(thread_id, prompt, invocation))
    turn = started.get("turn")
    turn_id = turn.get("id") if isinstance(turn, dict) else None
    if not isinstance(turn_id, str) or not turn_id:
        raise BridgeError("turn/start did not return a turn ID")

    state = _TurnState(text_parts=[])
    while True:
        message = server.next_message()
        if "method" in message and "id" in message:
            server.answer_unsupported_request(message)
            continue
        _record_agent_message_phase(
            message,
            thread_id=thread_id,
            turn_id=turn_id,
            state=state,
        )
        progress = _progress_exec_event(
            message,
            thread_id=thread_id,
            turn_id=turn_id,
            state=state,
        )
        if progress is not None:
            _emit_exec_event(progress)
        completed = _consume_turn_event(
            message,
            thread_id=thread_id,
            turn_id=turn_id,
            state=state,
        )
        if completed is None:
            continue
        if completed.get("status") != "completed":
            detail = state.last_error or completed.get("error") or completed.get("status")
            raise BridgeError(f"turn failed: {detail}")
        text = "".join(state.text_parts).strip()
        if not text:
            raise BridgeError("Codex completed without an assistant response")
        return text, completed


def emit_final_exec_events(text: str, turn: dict[str, Any]) -> None:
    """Emit the final Codex JSON events consumed by the gateway."""
    _emit_exec_event({"type": "item.completed", "item": {"type": "agent_message", "text": text}})
    usage = turn.get("usage", {})
    _emit_exec_event({"type": "turn.completed", "usage": usage or {}})


def _parse_args(args: list[str]) -> Invocation:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex-bin", required=True, type=Path)
    parser.add_argument("--cwd", required=True, type=Path)
    parser.add_argument("--resume")
    parser.add_argument("--transport", choices=("managed", "embedded"), required=True)
    parser.add_argument("--resume-transport", choices=("managed", "embedded"))
    parser.add_argument("--image", action="append", default=[], type=Path)
    values = parser.parse_args(args)
    cwd = values.cwd.expanduser().resolve()
    if not cwd.is_dir():
        raise BridgeError(f"project directory does not exist: {cwd}")
    images = tuple(path.expanduser().resolve() for path in values.image)
    missing = next((path for path in images if not path.is_file()), None)
    if missing is not None:
        raise BridgeError(f"image does not exist: {missing}")
    return Invocation(
        codex_bin=values.codex_bin,
        cwd=cwd,
        resume_thread=values.resume,
        images=images,
        transport=values.transport,
        resume_transport=values.resume_transport,
    )


def _read_prompt() -> str:
    return sys.stdin.read()


def _validate_turn_input(prompt: str, invocation: Invocation) -> None:
    if not prompt and not invocation.images:
        raise BridgeError("turn has no text or images")


def main(args: list[str] | None = None) -> int:
    """Run one bridge turn, returning non-zero for every failure."""
    try:
        invocation = _parse_args(sys.argv[1:] if args is None else args)
        prompt = _read_prompt()
        _validate_turn_input(prompt, invocation)
        with AppServer(invocation.codex_bin, transport=invocation.transport) as server:
            thread_id = start_or_resume(server, invocation)
            _emit_exec_event(
                {
                    "type": "thread.started",
                    "thread_id": thread_id,
                    "transport": invocation.transport,
                }
            )
            text, turn = run_turn(server, thread_id, prompt, invocation)
        emit_final_exec_events(text, turn)
    except (BridgeError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Codex App Server bridge error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
