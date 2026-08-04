#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
python="$root/.venv/bin/python"

printf 'python=%s\n' "$python"
"$python" --version
"$python" - <<'PY'
import platform
print(f"platform={platform.system()} {platform.release()}")
PY

"$python" -m pytest tests/unit/test_proof_run_capture.py -q -p no:cacheprovider
