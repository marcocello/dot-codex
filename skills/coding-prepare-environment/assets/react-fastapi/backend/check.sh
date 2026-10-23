#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$project_root/backend"
"$project_root/.venv/bin/python" -m ruff check .
"$project_root/.venv/bin/python" -m pytest
