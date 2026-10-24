#!/usr/bin/env python3
"""Run the public installer journeys in a temporary Linux tree over explicit SSH."""

import argparse
import io
from pathlib import Path
import shlex
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[4]
REMOTE = '''
import io, pathlib, subprocess, sys, tarfile, tempfile
with tempfile.TemporaryDirectory(prefix="dot-codex-proof-") as temporary:
    root = pathlib.Path(temporary)
    with tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()), mode="r:gz") as archive:
        archive.extractall(root, filter="data")
    command = (["bash", "docs/features/guided-installer/proof/native-package.sh"] if sys.argv[1] == "native"
               else ["python3", "-B", "docs/features/guided-installer/tests/test_guided_install.py"])
    result = subprocess.run(command, cwd=root)
    raise SystemExit(result.returncode)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True)
    parser.add_argument("--native-package", action="store_true", help="Download and run the official CLI in a disposable HOME instead of the fixture journeys")
    args = parser.parse_args()
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode="w:gz") as stream:
        for name in ["install.sh", ".gitignore", "config.template.toml", "skills.toml", "integrations",
                     "scripts/install.py", "scripts/install_runtime.py", "scripts/install_state.py",
                     "scripts/install_service.py", "scripts/skill_inventory.py",
                     "docs/features/guided-installer/tests/test_guided_install.py",
                     "docs/features/guided-installer/proof/native-package.sh"]:
            stream.add(ROOT / name, arcname=name)
    result = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", args.host,
                             "python3 -c " + shlex.quote(REMOTE) + (" native" if args.native_package else " journeys")],
                            input=archive.getvalue(), timeout=240)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
