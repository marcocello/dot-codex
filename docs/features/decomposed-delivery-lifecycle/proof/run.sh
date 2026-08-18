#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
python="$root/.venv/bin/python"

echo "python=$($python --version 2>&1)"
echo "target=active-dot-codex-delivery-surface"
"$python" -m pytest tests/unit/test_decomposed_delivery_lifecycle.py -q -p no:cacheprovider
"$python" -m pytest tests/unit/test_proof_run_capture.py -q -p no:cacheprovider
"$root/scripts/gate" --root "$root"
