#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../../.."
printf 'Target: local dot-codex fresh-discovery files and declared inventory\n'
python3 docs/features/skill-portfolio-consolidation/proof/acceptance.py
