#!/usr/bin/env bash
set -euo pipefail

feature_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(cd "$feature_dir/../../.." && pwd)"
python_bin="$repo_root/.venv/bin/python"

echo "python=$python_bin"
"$python_bin" --version
echo "proof-isolation=no-cross-feature-complete-proof"

"$python_bin" -m pytest tests/unit/test_feature_proof_isolation.py -q -p no:cacheprovider

