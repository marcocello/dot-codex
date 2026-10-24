#!/usr/bin/env bash
set -euo pipefail
task_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
task_native="$(mktemp -d)"
trap 'rm -rf "$task_native"' EXIT
mkdir "$task_native/home"
export HOME="$task_native/home"
unset CODEX_HOME
"$task_root/install.sh" cli --yes
test "$("$HOME/.local/bin/codex" --version)" = 'codex-cli 0.151.0'
task_before="$(readlink "$HOME/.local/share/dot-codex/cli/current")"
"$task_root/install.sh" cli --yes
test "$(readlink "$HOME/.local/share/dot-codex/cli/current")" = "$task_before"
test "$("$HOME/.local/bin/codex" --version)" = 'codex-cli 0.151.0'
printf 'Official package installation and repeat publication passed in disposable HOME.\n'
