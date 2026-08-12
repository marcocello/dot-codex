#!/usr/bin/env bash
set -euo pipefail

feature_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(cd "$feature_dir/../../.." && pwd)"
python_bin="$repo_root/.venv/bin/python"

echo "python=$python_bin"
"$python_bin" --version
echo "policy=serial-proof-evaluator-completion"
echo "queue_statuses=draft,ready,blocked,done"
echo "evaluator=fresh-final-pass-required-after-every-repair"
echo "invalidation=disabled"
echo "completion=feature-proof-plus-evaluator-pass"
echo "feature-preparation=complete-lean-set-with-proof"
echo "contract-preflight=fresh-separate-read-only-before-red"
echo "feature-execution=serial-one-at-a-time"
echo "graphify=repository-owned"

"$python_bin" -m pytest \
  tests/unit/test_feature_contract_preflight.py \
  tests/unit/test_lean_completion_lifecycle.py \
  tests/unit/test_gate_policy.py::test_harness_gate_ignores_external_skills_and_runs_tests_after_lint_failure \
  -q -p no:cacheprovider
