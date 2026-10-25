#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$ROOT"
"$ROOT/.venv/bin/python" -c 'import platform, importlib.metadata as m; print(platform.platform(), platform.python_version()); print({name:m.version(name) for name in ("pinecone", "mcp", "fastembed", "qdrant-client")})'
"$ROOT/.venv/bin/python" -m pytest -q docs/features/comprehensive-setup/proof/test_setup.py
