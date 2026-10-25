#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$ROOT"
"$ROOT/.venv/bin/python" -m pytest -q docs/features/installer-bootstrap/proof/test_bootstrap.py
