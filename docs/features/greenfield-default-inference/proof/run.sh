#!/usr/bin/env bash
set -euo pipefail

feature_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(cd "$feature_dir/../../.." && pwd)"
python_bin="$repo_root/.venv/bin/python"

echo "python=$python_bin"
"$python_bin" --version
echo "policy=AGENTS.md"
echo "app_skill=skills/coding-app-to-features"
echo "feature_skill=skills/coding-feature-spec"
echo "proof_skill=skills/coding-proof-author"

"$python_bin" -m pytest tests/unit/test_greenfield_default_policy.py -q -p no:cacheprovider
