#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 check.py "${1:-../evidence/trials}"
