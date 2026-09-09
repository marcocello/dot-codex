#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
python="$repo_root/.venv/bin/python"
skill_dir="$repo_root/skills/keep-or-cringe"
validator="$repo_root/skills/.system/skill-creator/scripts/quick_validate.py"

echo "python=$($python --version 2>&1)"
echo "target=$skill_dir"
"$python" "$validator" "$skill_dir"
"$python" "$repo_root/docs/features/linkedin-post-filter/proof/validate_filter_skill.py"
"$repo_root/scripts/gate" --root "$repo_root"
