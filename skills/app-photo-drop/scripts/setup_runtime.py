#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import venv

sys.dont_write_bytecode = True

from _runtime import APP_ROOT, RUNTIME_ROOT, VENV_PYTHON


def runtime_ready() -> bool:
    if not VENV_PYTHON.is_file():
        return False
    result = subprocess.run(
        [str(VENV_PYTHON), "-I", "-c", "import fastapi, uvicorn, ngrok"],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare the isolated Photo Drop Python runtime")
    parser.add_argument("--check", action="store_true", help="Only check whether the runtime is ready")
    args = parser.parse_args()
    if sys.version_info < (3, 12):
        print("Photo Drop requires Python 3.12 or newer for the ngrok SDK", file=sys.stderr)
        return 2
    if runtime_ready():
        print(json.dumps({"status": "ready", "python": str(VENV_PYTHON)}))
        return 0
    if args.check:
        print(json.dumps({"status": "missing", "runtime": str(RUNTIME_ROOT)}))
        return 1
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    venv.EnvBuilder(with_pip=True).create(RUNTIME_ROOT / "venv")
    subprocess.check_call(
        [
            str(VENV_PYTHON),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            str(APP_ROOT / "backend" / "requirements.txt"),
        ]
    )
    if not runtime_ready():
        print("Photo Drop runtime setup did not produce an importable application environment", file=sys.stderr)
        return 1
    print(json.dumps({"status": "ready", "python": str(VENV_PYTHON)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
