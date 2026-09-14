#!/usr/bin/env bash
set -euo pipefail
proof_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$proof_dir/acceptance.py" run
