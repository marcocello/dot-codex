#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../../../.." && pwd)"
cd "$repo_root"

python_bin="$repo_root/.venv/bin/python"
if [[ ! -x "$python_bin" ]]; then
  python_bin="$(command -v python3)"
fi

echo "python=$python_bin"
"$python_bin" --version
"$python_bin" -m pytest --version
uv --version
echo "repo_root=$repo_root"
echo "proof_tests=tests/features/test_telegram_to_agents_gateway.py"
echo "providers=codex,claude"

proof_tmp="$(mktemp -d)"
trap 'rm -rf "$proof_tmp"' EXIT
uv build --sdist --out-dir "$proof_tmp"
uv build --wheel --out-dir "$proof_tmp"
wheel_path="$(find "$proof_tmp" -maxdepth 1 -name 'telegram_to_agents-*.whl' -print -quit)"
sdist_path="$(find "$proof_tmp" -maxdepth 1 -name 'telegram_to_agents-*.tar.gz' -print -quit)"
test -n "$wheel_path"
test -n "$sdist_path"
echo "wheel=$(basename "$wheel_path")"
echo "sdist=$(basename "$sdist_path")"

wheel_site="$proof_tmp/wheel-site"
uv pip install --python "$python_bin" --no-deps --target "$wheel_site" "$wheel_path"
(
  cd "$proof_tmp"
  PYTHONPATH="$wheel_site" "$python_bin" -m telegram_to_agents --help
  PYTHONPATH="$wheel_site" "$python_bin" -c \
    "from pathlib import Path; import telegram_to_agents; from telegram_to_agents.cli.claude_provider import ClaudeCLI; from telegram_to_agents.cli.codex_provider import CodexCLI; from telegram_to_agents.messenger.telegram.app import TelegramBot; from telegram_to_agents.transcription import transcribe_openai_audio; assert Path(telegram_to_agents.__file__).is_relative_to(Path('$wheel_site')); print('installed_wheel_import=PASS')"
  GATEWAY_WHEEL_SITE="$wheel_site" GATEWAY_SMOKE_TMP="$proof_tmp/smoke" \
    PYTHONPATH="$wheel_site" "$python_bin" \
    "$repo_root/docs/features/telegram-to-agents-gateway/proof/installed_runtime_smoke.py"
)

sdist_site="$proof_tmp/sdist-site"
uv pip install --python "$python_bin" --no-deps --target "$sdist_site" "$sdist_path"
(
  cd "$proof_tmp"
  PYTHONPATH="$sdist_site" "$python_bin" -m telegram_to_agents --help
  PYTHONPATH="$sdist_site" "$python_bin" -c \
    "from pathlib import Path; import telegram_to_agents; assert Path(telegram_to_agents.__file__).is_relative_to(Path('$sdist_site')); print('installed_sdist_import=PASS')"
  GATEWAY_WHEEL_SITE="$sdist_site" GATEWAY_SMOKE_TMP="$proof_tmp/sdist-smoke" \
    PYTHONPATH="$sdist_site" "$python_bin" \
    "$repo_root/docs/features/telegram-to-agents-gateway/proof/installed_runtime_smoke.py"
)

GATEWAY_WHEEL="$wheel_path" GATEWAY_SDIST="$sdist_path" "$python_bin" -m pytest -q \
  tests/features/test_telegram_to_agents_gateway.py::test_configuration_commands_and_file_policy_are_gateway_only
GATEWAY_WHEEL="$wheel_path" GATEWAY_SDIST="$sdist_path" "$python_bin" -m pytest -q \
  tests/features/test_telegram_to_agents_gateway.py
"$python_bin" -m pytest -q tests/transcription/test_openai_audio.py
