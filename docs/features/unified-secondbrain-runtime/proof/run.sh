#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$ROOT"
python3 docs/features/unified-secondbrain-runtime/proof/test_runtime.py
PACKAGE_TMP="$(mktemp -d)"
trap 'rm -rf "$PACKAGE_TMP"' EXIT
uv build --project "$ROOT/backend/telegram" --sdist --wheel --out-dir "$PACKAGE_TMP"
export GATEWAY_WHEEL="$PACKAGE_TMP/telegram_to_agents-0.1.0-py3-none-any.whl"
export GATEWAY_SDIST="$PACKAGE_TMP/telegram_to_agents-0.1.0.tar.gz"
"$ROOT/.venv/bin/python" -m pytest -q backend/telegram/tests
node backend/whatsapp/tests/acceptance.mjs
