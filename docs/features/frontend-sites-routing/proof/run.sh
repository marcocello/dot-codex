#!/usr/bin/env bash
set -euo pipefail

feature_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repo_root="$(cd "$feature_dir/../../.." && pwd)"
python_bin="$repo_root/.venv/bin/python"

echo "python=$python_bin"
"$python_bin" --version
echo "gate=$repo_root/scripts/gate"
"$python_bin" - <<'PY'
from pathlib import Path
import tomllib

root = Path.cwd()
config = tomllib.loads((root / "config.toml").read_text(encoding="utf-8"))
enabled = config["plugins"]["sites@openai-bundled"]["enabled"]
print(f"sites_enabled={str(enabled).lower()}")
PY

"$python_bin" -m pytest tests/unit/test_gate_policy.py -q -p no:cacheprovider
