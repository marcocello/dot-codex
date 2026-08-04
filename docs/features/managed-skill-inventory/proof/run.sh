#!/usr/bin/env bash
set -euo pipefail

feature_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(cd "$feature_dir/../../.." && pwd)"
python_bin="$repo_root/.venv/bin/python"
validator="$repo_root/skills/.system/skill-creator/scripts/quick_validate.py"

printf 'repo_root=%s\n' "$repo_root"
printf 'python=%s\n' "$python_bin"
"$python_bin" --version
printf 'manager=%s\n' "$repo_root/scripts/skill_inventory.py"
printf 'manifest=%s\n' "$repo_root/skills.toml"

"$python_bin" -m pytest tests/unit/test_skill_inventory.py -q -p no:cacheprovider
"$python_bin" "$validator" "$repo_root/skills/sync-codex-skills"
"$python_bin" "$validator" "$repo_root/skills/manage-codex-skills"

