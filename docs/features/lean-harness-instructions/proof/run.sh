#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../../.."
printf '%s\n' 'Target: current instruction files and navigable ownership/call graph; no live application compliance claim.'
python3 docs/features/lean-harness-instructions/proof/check.py
