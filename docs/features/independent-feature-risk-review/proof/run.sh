#!/usr/bin/env bash
set -euo pipefail

feature_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(cd "$feature_dir/../../.." && pwd)"
python_bin="$repo_root/.venv/bin/python"

echo "python=$python_bin"
"$python_bin" --version
echo "review_scope=independent-relevance-bounded-discovery"
echo "parent_surface=entry-point-not-scope-ceiling"
echo "preflight_findings=all-supported-material"
echo "review_state=transient-read-only"

"$python_bin" -m pytest \
  tests/unit/test_independent_feature_risk_review.py \
  tests/unit/test_feature_contract_preflight.py \
  tests/unit/test_bounded_consolidated_evaluation.py \
  tests/unit/test_lean_completion_lifecycle.py \
  -q -p no:cacheprovider
