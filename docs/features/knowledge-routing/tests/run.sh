#!/usr/bin/env bash
set -euo pipefail
python3 docs/features/knowledge-routing/tests/check_setup_recipe.py
bash docs/features/knowledge-connect/tests/run.sh
python3 skills/.system/skill-creator/scripts/quick_validate.py skills/knowledge-capture
python3 skills/.system/skill-creator/scripts/quick_validate.py skills/knowledge-review
