#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
active_config="/Users/marcocello/.codex/config.toml"
template_config="$repo_root/config.template.toml"
doctor_output="$(mktemp)"
trap 'rm -f "$doctor_output"' EXIT

printf 'codex_path=%s\n' "$(command -v codex)"
printf 'codex_version=%s\n' "$(codex --version)"
printf 'active_config=%s\n' "$active_config"
printf 'template_config=%s\n' "$template_config"

python3 - "$active_config" "$template_config" <<'PY'
import pathlib
import sys
import tomllib

active_path = pathlib.Path(sys.argv[1])
template_path = pathlib.Path(sys.argv[2])
active = tomllib.loads(active_path.read_text(encoding="utf-8"))
template = tomllib.loads(template_path.read_text(encoding="utf-8"))

expected_roots = {
    active_path: {
        "/Users/marcocello/software",
        "/Users/marcocello/Documents",
        "/Users/marcocello/.azure",
    },
    template_path: {
        "/path/to/your/workspace/example-project",
        "/path/to/your/local/state",
    },
}

for path, config in ((active_path, active), (template_path, template)):
    assert config.get("default_permissions") == "projects-write", path
    assert "sandbox_mode" not in config, path
    assert "sandbox_workspace_write" not in config, path
    profile = config["permissions"]["projects-write"]
    assert profile.get("extends") == ":workspace", path
    assert profile.get("network", {}).get("enabled") is True, path
    roots = {root for root, enabled in profile.get("workspace_roots", {}).items() if enabled}
    assert roots == expected_roots[path], (path, roots)
    features = config.get("features", {})
    assert features.get("multi_agent") is False, path
    assert "js_repl" not in features, path

print("permission_profile_artifacts=PASS")
PY

codex --strict-config app-server --stdio </dev/null

doctor_exit=0
codex doctor --json >"$doctor_output" || doctor_exit=$?
if [[ "$doctor_exit" -gt 1 ]]; then
    printf 'codex_doctor_unexpected_exit=%s\n' "$doctor_exit" >&2
    exit "$doctor_exit"
fi

python3 - "$doctor_output" <<'PY'
import json
import pathlib
import sys

report = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
checks = report["checks"]
config_load = checks["config.load"]
sandbox = checks["sandbox.helpers"]

assert config_load["status"] == "ok", config_load
assert config_load["details"]["config.toml parse"] == "ok", config_load
assert sandbox["status"] == "ok", sandbox
assert sandbox["details"]["filesystem sandbox"] == "restricted", sandbox
assert sandbox["details"]["network sandbox"] == "enabled", sandbox

print("codex_config_load=PASS")
print("filesystem_sandbox=restricted")
print("network_sandbox=enabled")
PY

printf 'named_permission_profile_proof=PASS\n'
