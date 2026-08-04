#!/usr/bin/env bash
set -euo pipefail

feature_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(cd "$feature_dir/../../.." && pwd)"
python_bin="$repo_root/.venv/bin/python"
validator="$repo_root/skills/.system/skill-creator/scripts/quick_validate.py"
skill_dir="$repo_root/skills/coding-ui-improvement"
test_path="tests/unit/test_ui_improvement_skill_contract.py"

printf 'python=%s\n' "$python_bin"
"$python_bin" --version
printf 'skill=%s\n' "$skill_dir"
printf 'validator=%s\n' "$validator"
printf 'test=%s\n' "$test_path"

"$python_bin" "$validator" "$skill_dir"
"$python_bin" -m pytest "$test_path" -q -p no:cacheprovider
