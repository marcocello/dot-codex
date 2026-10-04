#!/usr/bin/env bash
set -euo pipefail
proof_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$proof_dir/../../../../scripts/tests/test_completion_attribution.py"
