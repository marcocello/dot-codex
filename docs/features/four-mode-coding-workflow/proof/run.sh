#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
python="$root/.venv/bin/python"

echo "python=$($python --version 2>&1)"
echo "target=current-installed-dot-codex-checkout; fresh-session discovery not proven"
"$python" -m pytest tests/unit/test_feature_status.py -q -p no:cacheprovider
"$python" -m pytest tests/unit/test_coding_workflow_v2.py -q -p no:cacheprovider
