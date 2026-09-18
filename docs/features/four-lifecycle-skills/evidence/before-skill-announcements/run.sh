#!/usr/bin/env bash
set -euo pipefail
PROOF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$PROOF_DIR/check_split.py"
