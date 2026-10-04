#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../../.."
python3 docs/features/secondbrain-cycle/tests/test_regressions.py
python3 skills/.system/skill-creator/scripts/quick_validate.py skills/secondbrain-update
python3 skills/.system/skill-creator/scripts/quick_validate.py skills/secondbrain-review
python3 -m unittest discover -s skills/knowledge-tool-connect/tests -p 'test_*.py'
