#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../../.."
python3 docs/features/proactive-coding-workflow/proof/check.py
