#!/usr/bin/env bash
set -euo pipefail
proof_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
printf '%s\n' 'Target: local knowledge-profile CLI; isolated temporary configuration; no live provider calls.'
python3 "$proof_dir/acceptance.py"
