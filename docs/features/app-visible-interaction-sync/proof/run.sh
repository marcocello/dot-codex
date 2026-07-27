#!/usr/bin/env bash
set -euo pipefail

feature_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(cd "$feature_dir/../../.." && pwd)"
python_bin="$repo_root/.venv/bin/python"
validator="$repo_root/skills/.system/skill-creator/scripts/quick_validate.py"
skill_dir="$repo_root/skills/second-brain-capture-interactions"

printf 'python=%s\n' "$python_bin"
"$python_bin" --version
printf 'capture=%s\n' "$skill_dir/scripts/capture_interactions.py"
printf 'app_server_boundary=fake_outer_process\n'

"$python_bin" "$validator" "$skill_dir"
"$python_bin" -m pytest tests/unit/test_capture_interactions.py -q -p no:cacheprovider
