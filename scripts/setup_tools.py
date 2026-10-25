"""Discover enabled plugin MCP declarations and retain separate connection readiness."""
import getpass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib

from setup_support import SetupError, atomic_write, command, save_json


def load_secrets(state):
    path = state / "tool-secrets.json"
    if not path.exists():
        return {}
    if path.is_symlink() or path.stat().st_mode & 0o077:
        raise SetupError("Tool credentials must be an owner-only regular file")
    values = json.loads(path.read_text())
    if not isinstance(values, dict) or any(not re.fullmatch(r"[A-Z_][A-Z0-9_]*", key) or not isinstance(value, str) or any(c in value for c in "\n\r\x00") for key,value in values.items()):
        raise SetupError("Invalid private tool credential format")
    return values


def declarations(root, env):
    entries = tomllib.loads((root / "skills.toml").read_text())["skills"]
    result = command([Path.home() / ".local/bin/codex", "plugin", "list", "--json"], env=env, capture=True)
    installed = {entry["pluginId"]:entry for entry in json.loads(result.stdout).get("installed", []) if entry.get("installed")}
    for entry in entries:
        if entry["kind"] != "plugin" or not entry["enabled"]:
            continue
        plugin, marketplace = entry["selector"].split("@")
        local = root / "integrations/packages" / plugin / ".mcp.json"
        cache = root / "plugins/cache" / marketplace / plugin
        version = installed.get(entry["selector"], {}).get("version")
        if not isinstance(version, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+-]{0,127}", version):
            version = None
        resolved = cache / str(version) / ".mcp.json"
        paths = [resolved] if version and resolved.is_file() else ([local] if marketplace == "dot-codex" and local.is_file() else list(cache.glob("*/.mcp.json")))
        if len(paths) > 1:
            yield entry["name"], plugin, {"_error":"Installed plugin version did not resolve an unambiguous MCP declaration; inspect its native plugin state"}
            continue
        if not paths:
            yield entry["name"], None, None
        for path in paths:
            for name, server in json.loads(path.read_text()).get("mcpServers", {}).items():
                yield entry["name"], name, server


def reconcile(root, state, env, interactive, *, review=False):
    secrets = load_secrets(state)
    report = []
    asked = set()
    for plugin, name, server in declarations(root, env):
        if server is None:
            report.append({"plugin":plugin, "server":None, "status":"runtime-managed", "detail":"Installed by inventory; no portable MCP declaration was exposed by this runtime"})
            continue
        if "_error" in server:
            report.append({"plugin":plugin, "server":name, "status":"connection-pending", "detail":server["_error"]})
            continue
        required = set(server.get("env_vars", []))
        mandatory = set()
        if token := server.get("bearer_token_env_var"):
            required.add(token)
            mandatory.add(token)
        for field in ("env", "http_headers", "headers"):
            for value in server.get(field, {}).values():
                variables = re.findall(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", str(value))
                required.update(variables)
                mandatory.update(variables)
        missing = []
        for key in sorted(required):
            if not re.fullmatch(r"[A-Z_][A-Z0-9_]*", key):
                raise SetupError("MCP credential variable names must be uppercase environment identifiers")
            if env.get(key):
                secrets[key] = env[key]
            if interactive and key not in asked and (review or not secrets.get(key)):
                asked.add(key)
                fallback = "keeps the saved value" if secrets.get(key) else "leaves this value unset"
                value = getpass.getpass(f"{name}: {key} (empty {fallback}): ").strip()
                if value:
                    secrets[key] = value
            if not secrets.get(key):
                missing.append(key)
        if any(any(character in value for character in "\n\r\x00") for value in secrets.values()):
            raise SetupError("MCP credential values must not contain control characters")
        env.update(secrets)
        save_json(state / "tool-secrets.json", secrets)
        # systemd reads credentials without embedding them in public unit files or argv.
        atomic_write(state / "tool-secrets.env", "".join(key + '="' + value.replace('\\', '\\\\').replace('"', '\\"') + '"\n' for key,value in secrets.items()))
        if mandatory.intersection(missing):
            row = {"plugin":plugin, "server":name, "status":"authentication-pending", "missing":missing}
        else:
            print(f"  Checking MCP transport: {plugin}/{name}", flush=True)
            if server.get("command") in {"uv", "uvx"} and not shutil.which(server["command"], path=env["PATH"]):
                command([root / ".venv/bin/python", "-m", "pip", "install", "uv==0.13.5"], env=env)
            with tempfile.TemporaryDirectory(prefix="secondbrain-mcp-") as tmp:
                candidate = Path(tmp) / "server.json"
                save_json(candidate, server)
                try:
                    result = command([root / ".venv/bin/python", root / "scripts/setup_mcp.py", candidate], env=env, capture=True, check=False, timeout=110)
                    observed = json.loads(result.stdout) if result.stdout.strip() else {"ok":False}
                    ready = not result.returncode and observed.get("ok")
                except (OSError, ValueError, subprocess.SubprocessError):
                    observed, ready = {}, False
            row = {"plugin":plugin, "server":name, "status":"transport-verified" if ready else "connection-pending",
                   "detail":observed.get("boundary", "Check provider authentication, required desktop application and network")}
            if missing:
                row["unset_forwarded_environment"] = missing
        report.append(row)
        print(f"  MCP {name}: {row['status']}", flush=True)
    save_json(state / "mcp-readiness.json", {"servers":report, "notice":"Transport verification does not establish provider application access or authorize tool actions"})
    pending = [row for row in report if row["status"] in {"authentication-pending", "connection-pending"}]
    if pending:
        raise SetupError("Some installed MCPs need credentials, application startup or provider login; see mcp-readiness.json and repeat setup")
    return "All exposed MCP transports verified; runtime-managed plugin connections remain visible in the readiness report"
