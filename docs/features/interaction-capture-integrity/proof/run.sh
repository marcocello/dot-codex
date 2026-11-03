#!/usr/bin/env bash
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
python="$root/.venv/bin/python"

echo "python=$($python --version 2>&1)"
echo "target=candidate-dot-codex-interaction-capture-source"
"$python" docs/features/interaction-capture-integrity/proof/acceptance.py
