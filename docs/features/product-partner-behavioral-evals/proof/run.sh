#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
python="$root/.venv/bin/python"

echo "python=$($python --version 2>&1)"
echo "target=active-dot-codex-product-partner-evals"
"$python" -m pytest tests/unit/test_product_partner_behavioral_evals.py -q -p no:cacheprovider
"$root/scripts/gate" --root "$root"
