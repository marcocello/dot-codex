#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else "Install Python 3.11+ before running dot-codex installation.")'
exec python3 "$repo_root/scripts/install.py" "$@"
