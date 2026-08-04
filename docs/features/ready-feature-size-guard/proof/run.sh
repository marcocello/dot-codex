#!/usr/bin/env bash
set -euo pipefail

feature_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(cd "$feature_dir/../../.." && pwd)"
python_bin="$repo_root/.venv/bin/python"

echo "python=$python_bin"
"$python_bin" --version
echo "ready-guard=one-observable-outcome-and-proof-boundary"
echo "queue-schema=id,feature_dir,priority,status,notes"

"$python_bin" -m pytest tests/unit/test_ready_feature_size_guard.py -q -p no:cacheprovider

