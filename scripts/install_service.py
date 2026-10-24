#!/usr/bin/env python3
"""Small persistent service runner, independent of the activated harness checkout."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def connected(value: dict) -> bool:
    return (isinstance(value, dict) and value.get("status") == "connected"
            and value.get("timedOut") is False
            and isinstance(value.get("environmentId"), str) and bool(value["environmentId"])
            and isinstance(value.get("daemon"), dict) and bool(value["daemon"].get("status")))


def check(binary: str, env: dict[str, str]) -> bool:
    try:
        response = subprocess.run([binary, "remote-control", "start", "--json"], env=env,
                                  capture_output=True, text=True, timeout=90)
        return response.returncode == 0 and connected(json.loads(response.stdout))
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-bin", required=True)
    parser.add_argument("--codex-home", required=True)
    parser.add_argument("--user-home", required=True)
    parser.add_argument("--bootstrap", action="store_true")
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()
    binary = Path(args.codex_bin)
    if not binary.is_file() or not os.access(binary, os.X_OK):
        print("Codex executable missing; rerun ./install.sh cli, then service.", file=sys.stderr)
        return 1
    native = Path(args.codex_home) / "packages/standalone/current/codex"
    if not native.is_file() or native.resolve() != binary.resolve():
        print("Native daemon package publication is missing or uses another CLI; rerun ./install.sh cli, then service.", file=sys.stderr)
        return 1
    env = dict(os.environ, HOME=args.user_home, CODEX_HOME=args.codex_home)
    if args.bootstrap or args.watch:
        try:
            result = subprocess.run([str(binary), "app-server", "daemon", "bootstrap", "--remote-control"],
                                    env=env, capture_output=True, timeout=120)
            if result.returncode:
                print("Managed daemon bootstrap failed; rerun ./install.sh service.", file=sys.stderr)
                return 1
        except (OSError, subprocess.TimeoutExpired):
            return 1
    while True:
        healthy = check(str(binary), env)
        print("Remote Control connected." if healthy else
              "Remote Control is not ready; check login and network access.", flush=True)
        if not args.watch:
            return 0 if healthy else 1
        # Relay outages do not tear down or repeatedly restart a healthy local daemon.
        time.sleep(60)


if __name__ == "__main__":
    raise SystemExit(main())
