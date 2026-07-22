#!/usr/bin/env python3
"""Provision a managed ggmcp server when needed and scan one checkout."""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path


DOT_CODEX_ROOT = Path(__file__).resolve().parents[3]
SCANNER = Path(__file__).resolve().with_name("scan_current_checkout.py")
GGMCP_SOURCE = "git+https://github.com/GitGuardian/ggmcp.git"
TOKEN_ENV = "GITGUARDIAN_PERSONAL_ACCESS_TOKEN"
DEFAULT_START_TIMEOUT = 180.0
START_PROGRESS_INTERVAL = 15.0


def arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Git checkout to scan")
    return parser.parse_args(argv)


def resolve_uvx() -> str:
    configured = os.environ.get("GITGUARDIAN_UVX", "").strip()
    executable = shutil.which(configured or "uvx")
    if executable is None:
        raise RuntimeError("uvx is unavailable; install uv or set GITGUARDIAN_UVX")
    return executable


def reserve_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def wait_for_server(process: subprocess.Popen[bytes], port: int, timeout: float) -> None:
    started = time.monotonic()
    deadline = started + timeout
    next_progress = started + START_PROGRESS_INTERVAL
    while time.monotonic() < deadline:
        returncode = process.poll()
        if returncode is not None:
            raise RuntimeError(
                f"managed ggmcp exited before readiness with status {returncode}"
            )
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return
        except OSError:
            now = time.monotonic()
            if now >= next_progress:
                elapsed = int(now - started)
                print(
                    "GITGUARDIAN setup: still waiting for managed ggmcp "
                    f"({elapsed}s elapsed)",
                    flush=True,
                )
                next_progress = now + START_PROGRESS_INTERVAL
            time.sleep(0.1)
    raise RuntimeError(f"managed ggmcp was not ready within {timeout:g} seconds")


def stop_server(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def load_scanner() -> Callable[[list[str]], int]:
    if not SCANNER.is_file():
        raise RuntimeError(f"checkout scanner is missing: {SCANNER}")
    spec = importlib.util.spec_from_file_location(
        "coding_critical_secret_audit_scanner", SCANNER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"checkout scanner could not be loaded: {SCANNER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    scanner_main = getattr(module, "main", None)
    if not callable(scanner_main):
        raise RuntimeError(f"checkout scanner has no callable main: {SCANNER}")
    return scanner_main


def run_scanner(root: Path, url: str, token: str) -> int:
    scanner_main = load_scanner()
    return scanner_main(
        [
            "--root",
            str(root.resolve()),
            "--url",
            url,
            "--token",
            token,
        ]
    )


def managed_scan(root: Path, token: str) -> int:
    uvx = resolve_uvx()
    runtime = Path(
        os.environ.get(
            "GITGUARDIAN_RUNTIME_DIR", DOT_CODEX_ROOT / ".gitguardian-runtime"
        )
    ).resolve()
    runtime.mkdir(parents=True, exist_ok=True)
    port = reserve_loopback_port()
    server_env = {
        **os.environ,
        "ENABLE_LOCAL_OAUTH": "false",
        "MULTI_TENANCY_ENABLED": "true",
        "MCP_HOST": "127.0.0.1",
        "MCP_PORT": str(port),
        "UV_CACHE_DIR": str(runtime / "uv-cache"),
        "UV_TOOL_DIR": str(runtime / "uv-tools"),
        "UV_TOOL_BIN_DIR": str(runtime / "uv-bin"),
        "UV_PYTHON_INSTALL_DIR": str(runtime / "uv-python"),
    }
    server_env.pop(TOKEN_ENV, None)
    server_env.pop("GGMCP_TOKEN", None)
    command = [uvx, "--from", GGMCP_SOURCE, "gg-mcp-server"]
    print(
        "GITGUARDIAN setup: provisioning ggmcp via uvx "
        "(first run may download/install; later runs reuse the local cache)",
        flush=True,
    )
    with tempfile.TemporaryFile() as server_output:
        try:
            process = subprocess.Popen(
                command,
                cwd=DOT_CODEX_ROOT,
                env=server_env,
                stdout=server_output,
                stderr=subprocess.STDOUT,
            )
        except OSError as exc:
            raise RuntimeError(f"could not start managed ggmcp: {exc}") from exc
        try:
            timeout = float(
                os.environ.get(
                    "GITGUARDIAN_SERVER_START_TIMEOUT", DEFAULT_START_TIMEOUT
                )
            )
            wait_for_server(process, port, timeout)
            print("GITGUARDIAN runtime: READY (managed uvx)", flush=True)
            return run_scanner(root, f"http://127.0.0.1:{port}", token)
        finally:
            stop_server(process)


def report_result(result: int) -> int:
    if result == 0:
        print("GITGUARDIAN audit: PASS")
    return result


def main(argv: list[str]) -> int:
    args = arguments(argv)
    token = os.environ.get(TOKEN_ENV, "").strip()
    if not token:
        print("GITGUARDIAN audit failed: token not configured", file=sys.stderr)
        return 1
    try:
        configured_url = os.environ.get("GGMCP_URL", "").strip()
        if configured_url:
            print("GITGUARDIAN runtime: READY (configured URL)", flush=True)
            return report_result(run_scanner(args.root, configured_url, token))
        return report_result(managed_scan(args.root, token))
    except (RuntimeError, ValueError) as exc:
        print(f"GITGUARDIAN setup failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
