#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../../.."
printf '%s\n' 'Second-brain acceptance: real CLI processes, isolated temporary state, synthetic provider edge.'
python3 docs/features/secondbrain-cycle/proof/acceptance.py
