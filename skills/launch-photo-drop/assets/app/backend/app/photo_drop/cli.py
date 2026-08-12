import argparse
import asyncio
import json
import os
import signal
import socket
import sys
from contextlib import suppress
from datetime import UTC, datetime, timedelta
from pathlib import Path

import uvicorn

from .event_names import DEFAULT_EVENT_NAME, normalize_event_name
from .process_lock import AlreadyRunningError, ProcessLock
from .runtime import PhotoDropRuntime
from .session_store import SessionStore
from .tunnel import NgrokTunnel
from .upload_service import UploadService
from .upload_store import UploadStore
from .web import create_admin_app, create_guest_app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="photo-drop")
    subparsers = parser.add_subparsers(dest="command", required=True)
    start = subparsers.add_parser("start")
    start.add_argument("--destination", type=Path, required=True)
    start.add_argument("--event-name", default=DEFAULT_EVENT_NAME)
    start.add_argument("--state-dir", type=Path, default=Path.home() / ".photo-drop")
    start.add_argument("--ttl-seconds", type=int, default=43_200)
    start.add_argument("--guest-port", type=int, default=8_443)
    start.add_argument("--admin-port", type=int, default=8_444)
    start.add_argument("--max-session-bytes", type=int, default=50 * 1024**3)
    start.add_argument("--free-space-reserve-bytes", type=int, default=512 * 1024**2)
    start.add_argument("--upload-grace-seconds", type=float, default=30)
    start.add_argument("--no-open", action="store_true")
    return parser.parse_args()


def validate_inputs(args: argparse.Namespace, frontend_dist: Path) -> None:
    args.event_name = normalize_event_name(args.event_name)
    if not args.destination.is_dir():
        raise ValueError(f"Destination is not a directory: {args.destination}")
    if not os.access(args.destination, os.W_OK):
        raise ValueError(f"Destination is not writable: {args.destination}")
    if args.ttl_seconds <= 0:
        raise ValueError("Expiry must be greater than zero seconds")
    if args.max_session_bytes <= 0:
        raise ValueError("Event quota must be greater than zero bytes")
    if args.free_space_reserve_bytes < 0:
        raise ValueError("Free-space reserve cannot be negative")
    if args.upload_grace_seconds < 0:
        raise ValueError("Upload grace cannot be negative")
    if not (frontend_dist / "index.html").is_file():
        raise ValueError(f"Frontend build is missing: {frontend_dist}")


def bound_socket(port: int) -> socket.socket:
    result = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    result.bind(("127.0.0.1", port))
    result.listen(2048)
    result.setblocking(False)
    return result


async def serve(args: argparse.Namespace, repo_root: Path, lock: ProcessLock) -> None:
    frontend_dist = repo_root / "frontend" / "app" / "dist"
    validate_inputs(args, frontend_dist)
    store = SessionStore(args.state_dir)
    store.recover_interrupted()
    guest_socket = bound_socket(args.guest_port)
    try:
        admin_socket = bound_socket(args.admin_port)
    except Exception:
        guest_socket.close()
        raise

    tunnel = NgrokTunnel(args.guest_port)
    runtime = PhotoDropRuntime(store, tunnel, args.upload_grace_seconds)
    upload_store = UploadStore(store.database)
    upload_store.recover_interrupted()
    uploads = UploadService(
        runtime,
        upload_store,
        args.max_session_bytes,
        args.free_space_reserve_bytes,
    )
    guest_server = uvicorn.Server(
        uvicorn.Config(create_guest_app(runtime, frontend_dist, uploads), log_level="warning")
    )
    admin_server = uvicorn.Server(
        uvicorn.Config(create_admin_app(runtime, frontend_dist, upload_store), log_level="warning")
    )
    tasks = [
        asyncio.create_task(guest_server.serve(sockets=[guest_socket])),
        asyncio.create_task(admin_server.serve(sockets=[admin_socket])),
    ]
    try:
        await _wait_until_started(guest_server, admin_server)
        public_origin = await tunnel.start()
        expires_at = datetime.now(UTC) + timedelta(seconds=args.ttl_seconds)
        session = store.start_session(args.destination, expires_at, public_origin, args.event_name)
        runtime.activate(session)
        admin_url = f"http://127.0.0.1:{args.admin_port}"
        lock.publish(admin_url)
        print(
            json.dumps(
                {
                    "event": "ready",
                    "admin_url": admin_url,
                    "guest_listener_url": f"http://127.0.0.1:{args.guest_port}",
                    "guest_url": session.guest_url,
                    "event_name": session.event_name,
                    "provider": "ngrok",
                    "app_root": str(repo_root),
                }
            ),
            flush=True,
        )
        expiry_task = asyncio.create_task(runtime.expire_at_deadline())
        await _wait_for_shutdown()
        expiry_task.cancel()
        with suppress(asyncio.CancelledError):
            await expiry_task
        await runtime.stop_session("shutdown")
    finally:
        try:
            await tunnel.stop()
        except Exception as error:
            print(f"Photo Drop tunnel cleanup failed: {error}", file=sys.stderr, flush=True)
        guest_server.should_exit = True
        admin_server.should_exit = True
        await asyncio.gather(*tasks, return_exceptions=True)
        guest_socket.close()
        admin_socket.close()


async def _wait_until_started(*servers: uvicorn.Server) -> None:
    for _ in range(200):
        if all(server.started for server in servers):
            return
        if any(server.should_exit for server in servers):
            raise RuntimeError("HTTP listener failed during startup")
        await asyncio.sleep(0.01)
    raise RuntimeError("HTTP listeners did not become ready")


async def _wait_for_shutdown() -> None:
    event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signum in (signal.SIGINT, signal.SIGTERM):
        with suppress(NotImplementedError):
            loop.add_signal_handler(signum, event.set)
    await event.wait()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[3]
    lock = ProcessLock(args.state_dir)
    try:
        lock.acquire()
        asyncio.run(serve(args, repo_root, lock))
        return 0
    except AlreadyRunningError as error:
        print(str(error), file=sys.stderr, flush=True)
        return 2
    except Exception as error:
        print(f"Photo Drop could not start: {error}", file=sys.stderr, flush=True)
        return 1
    finally:
        lock.release()


if __name__ == "__main__":
    raise SystemExit(main())
