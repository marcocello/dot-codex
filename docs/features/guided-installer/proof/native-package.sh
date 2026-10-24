#!/usr/bin/env bash
set -euo pipefail
task_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
task_native="$(mktemp -d /tmp/dot-codex-native.XXXXXX)"
cleanup() {
  if [ -x "$task_native/home/.local/bin/codex" ]; then
    "$task_native/home/.local/bin/codex" app-server daemon stop >/dev/null 2>&1 || true
  fi
  rm -rf "$task_native"
}
trap cleanup EXIT
mkdir "$task_native/home"
export HOME="$task_native/home"
unset CODEX_HOME
"$task_root/install.sh" cli --yes
test "$("$HOME/.local/bin/codex" --version)" = 'codex-cli 0.151.0'
task_before="$(readlink "$HOME/.local/share/dot-codex/cli/current")"
"$task_root/install.sh" cli --yes
test "$(readlink "$HOME/.local/share/dot-codex/cli/current")" = "$task_before"
test "$("$HOME/.local/bin/codex" --version)" = 'codex-cli 0.151.0'
export CODEX_HOME="$HOME/.codex"
mkdir -p "$CODEX_HOME"
python3 - "$task_root" <<'PY'
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / "scripts"))
from install_runtime import prepare_service_package
from install_state import installation_lock
home = Path.home().resolve()
with installation_lock(home) as state:
    prepare_service_package(home, state, home / ".local/bin/codex", home / ".codex", dict(os.environ))
assert (home / ".codex/packages/standalone/current/codex").resolve() == (home / ".local/bin/codex").resolve()
PY
"$HOME/.local/bin/codex" app-server daemon start
"$HOME/.local/bin/codex" app-server daemon version
"$HOME/.local/bin/codex" app-server daemon stop
printf 'Official package installation, repeat publication, native managed layout and app-server start/version/stop passed in disposable HOME.\n'
