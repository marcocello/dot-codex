#!/usr/bin/env bash
set -euo pipefail

feature_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(cd "$feature_dir/../../.." && pwd)"
python_bin="$repo_root/.venv/bin/python"

echo "python=$python_bin"
"$python_bin" --version
echo "ui-proof=real-actions-visible-resources-real-domain-api"

"$python_bin" -m pytest tests/unit/test_ui_proof_realism.py -q -p no:cacheprovider

