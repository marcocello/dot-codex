#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import json
import os
import signal
import socket
import struct
import sys
import threading
import time
from typing import BinaryIO

_WEBSOCKET_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def _read_exact(stream: BinaryIO, size: int) -> bytes:
    data = bytearray()
    while len(data) < size:
        chunk = stream.read(size - len(data))
        if not chunk:
            raise EOFError
        data.extend(chunk)
    return bytes(data)


def _read_http_upgrade(stream: BinaryIO) -> dict[str, str]:
    raw = bytearray()
    while not raw.endswith(b"\r\n\r\n"):
        raw.extend(_read_exact(stream, 1))
        if len(raw) > 16_384:
            raise ValueError("oversized WebSocket upgrade")
    lines = raw.decode("ascii").split("\r\n")
    if lines[0] != "GET / HTTP/1.1":
        raise ValueError("missing WebSocket GET upgrade")
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if not line:
            continue
        name, value = line.split(":", 1)
        headers[name.lower()] = value.strip()
    if headers.get("upgrade", "").lower() != "websocket":
        raise ValueError("missing WebSocket Upgrade header")
    if "upgrade" not in headers.get("connection", "").lower():
        raise ValueError("missing WebSocket Connection header")
    return headers


def _frame(
    payload: bytes,
    *,
    opcode: int = 1,
    fin: bool = True,
    masked: bool = False,
) -> bytes:
    header = bytearray([(0x80 if fin else 0) | opcode])
    length = len(payload)
    if length < 126:
        header.append((0x80 if masked else 0) | length)
    elif length <= 0xFFFF:
        header.append((0x80 if masked else 0) | 126)
        header.extend(struct.pack("!H", length))
    else:
        header.append((0x80 if masked else 0) | 127)
        header.extend(struct.pack("!Q", length))
    if not masked:
        return bytes(header) + payload
    mask = b"mask"
    masked_payload = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
    return bytes(header) + mask + masked_payload


def _read_client_frame(stream: BinaryIO) -> tuple[int, bytes]:
    first, second = _read_exact(stream, 2)
    if not first & 0x80:
        raise ValueError("fragmented client frame")
    opcode = first & 0x0F
    if not second & 0x80:
        raise ValueError("unmasked client frame")
    length = second & 0x7F
    if length == 126:
        length = struct.unpack("!H", _read_exact(stream, 2))[0]
    elif length == 127:
        length = struct.unpack("!Q", _read_exact(stream, 8))[0]
    mask = _read_exact(stream, 4)
    payload = _read_exact(stream, length)
    return opcode, bytes(value ^ mask[index % 4] for index, value in enumerate(payload))


mode = os.environ.get("FAKE_CODEX_MODE", "normal")
command = sys.argv[1:]
if command not in (["app-server", "proxy"], ["app-server", "--listen", "stdio://"]):
    print("expected a managed or embedded app-server command", file=sys.stderr)
    raise SystemExit(2)

daemon = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
daemon.settimeout(3)
daemon.connect(os.environ["FAKE_CODEX_ADDR"])
daemon.sendall((json.dumps({"_proxy": command}) + "\n").encode())
if mode == "startup_exit":
    raise SystemExit(3)

if command == ["app-server", "--listen", "stdio://"]:

    def _copy_embedded_output() -> None:
        with daemon.makefile("rb") as source:
            for line in source:
                sys.stdout.buffer.write(line)
                sys.stdout.buffer.flush()
        if mode == "lost_turn_ack":
            os._exit(12)

    threading.Thread(target=_copy_embedded_output, daemon=True).start()
    for line in sys.stdin.buffer:
        daemon.sendall(line)
    raise SystemExit(0)

try:
    headers = _read_http_upgrade(sys.stdin.buffer)
except (EOFError, ValueError) as exc:
    print(f"invalid WebSocket upgrade: {exc}", file=sys.stderr)
    raise SystemExit(7) from exc

if mode == "handshake_error":
    sys.stdout.buffer.write(b"HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\n\r\n")
    sys.stdout.buffer.flush()
    raise SystemExit(8)

key = headers.get("sec-websocket-key", "")
accept = base64.b64encode(
    hashlib.sha1((key + _WEBSOCKET_GUID).encode(), usedforsecurity=False).digest()
).decode()
upgrade_header = (
    "Upgrade: not-websocket\r\n" if mode == "bad_upgrade_headers" else "Upgrade: websocket\r\n"
)
connection_header = (
    "Connection: notupgrade\r\n"
    if mode == "bad_connection_headers"
    else "Connection: keep-alive, Upgrade\r\n"
)
sys.stdout.buffer.write(
    (
        "HTTP/1.1 101 Switching Protocols\r\n"
        f"{upgrade_header}"
        f"{connection_header}"
        f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
    ).encode()
)
sys.stdout.buffer.flush()
if mode in {"bad_upgrade_headers", "bad_connection_headers"}:
    time.sleep(30)
    raise SystemExit(10)

stdout_lock = threading.Lock()


def _write_split(wire: bytes) -> None:
    split = min(2, len(wire))
    sys.stdout.buffer.write(wire[:split])
    sys.stdout.buffer.flush()
    sys.stdout.buffer.write(wire[split:])
    sys.stdout.buffer.flush()


def _send_frame(payload: bytes, *, opcode: int = 1, masked: bool = False) -> None:
    with stdout_lock:
        if opcode == 1 and not masked:
            pivot = max(1, len(payload) // 2)
            _write_split(_frame(payload[:pivot], opcode=1, fin=False))
            _write_split(_frame(b"telegram-to-agents-ping", opcode=9))
            _write_split(_frame(payload[pivot:], opcode=0))
            return
        _write_split(_frame(payload, opcode=opcode, masked=masked))


def _copy_output() -> None:
    with daemon.makefile("rb") as source:
        for line in source:
            _send_frame(line.rstrip(b"\n"), masked=mode == "masked_server_frame")
    if mode == "lost_turn_ack":
        os._exit(12)


threading.Thread(target=_copy_output, daemon=True).start()
while True:
    try:
        opcode, payload = _read_client_frame(sys.stdin.buffer)
    except EOFError:
        break
    if opcode == 8:
        _send_frame(payload, opcode=8)
        break
    if opcode == 9:
        _send_frame(payload, opcode=10)
        continue
    if opcode == 10:
        if payload != b"telegram-to-agents-ping":
            print("unexpected WebSocket pong payload", file=sys.stderr)
            raise SystemExit(11)
        continue
    if opcode != 1:
        print(f"unexpected WebSocket opcode: {opcode}", file=sys.stderr)
        raise SystemExit(9)
    message = json.loads(payload)
    if mode == "malformed":
        _send_frame(b"{not-json")
        raise SystemExit(4)
    if mode == "initialize_error" and message.get("method") == "initialize":
        _send_frame(
            json.dumps(
                {"id": message["id"], "error": {"code": -32000, "message": "init failed"}}
            ).encode()
        )
        raise SystemExit(5)
    if mode == "bridge_sigkill" and message.get("method") == "turn/start":
        os.kill(os.getppid(), signal.SIGKILL)
        raise SystemExit(6)
    daemon.sendall(payload + b"\n")
