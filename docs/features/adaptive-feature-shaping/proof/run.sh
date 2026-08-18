#!/usr/bin/env bash
set -euo pipefail

feature_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(cd "$feature_dir/../../.." && pwd)"
python_bin="$repo_root/.venv/bin/python"

echo "python=$python_bin"
"$python_bin" --version
echo "harness_boundary=adaptive-product-and-feature-shaping"
echo "artifacts=conditional-and-decision-owned"
echo "adjacency=classify-before-expanding-scope"
echo "proof=feature-specific-risk-pressure"

"$python_bin" -m pytest \
  tests/unit/test_adaptive_feature_shaping.py \
  tests/unit/test_app_planning_artifact_authority.py \
  tests/unit/test_greenfield_default_policy.py \
  tests/unit/test_lean_completion_lifecycle.py \
  tests/unit/test_ready_feature_size_guard.py \
  -q -p no:cacheprovider
