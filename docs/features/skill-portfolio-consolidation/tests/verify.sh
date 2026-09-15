#!/usr/bin/env bash
set -euo pipefail
for skill in coding-ui-toolkit writing-technical-content codex-manage-skills second-brain-review coding-workflow; do
  python3 skills/.system/skill-creator/scripts/quick_validate.py "skills/$skill"
done
"${CODEX_HOME:-$HOME/.codex}/scripts/skill_inventory.py" doctor
"${CODEX_HOME:-$HOME/.codex}/scripts/gate" --root "$PWD"
