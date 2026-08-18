#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-$ROOT/.venv/bin/python}"
"$PYTHON_BIN" --version
printf 'python=%s\n' "$PYTHON_BIN"
printf 'proof_target=dot-codex instruction surface\n'

"$PYTHON_BIN" -m pytest -q \
  tests/unit/test_simple_product_partner_harness.py \
  tests/unit/test_adaptive_feature_shaping.py \
  tests/unit/test_greenfield_default_policy.py \
  tests/unit/test_feature_contract_preflight.py \
  tests/unit/test_independent_feature_risk_review.py \
  tests/unit/test_lean_completion_lifecycle.py \
  tests/unit/test_final_candidate_freshness.py \
  tests/unit/test_gate_policy.py
