---
name: codex-manage-skills
description: Inspect, add, remove, refresh, or reconcile skills.toml dependencies. Use for skill inventory changes, audits, synchronization, and machine bootstrap.
---

# Manage Codex Skills

Use `"${CODEX_HOME:-$HOME/.codex}/scripts/skill_inventory.py"` for every inventory mutation so `skills.toml` remains authoritative. Read `docs/harness/skill-management.md` when ownership or plugin versus npm boundaries matter.

## Choose the operation

- Inspect, list, audit, or diagnose: run `list` or `doctor`. Audit-only requests never install, refresh, remove, or synchronize dependencies.
- Bootstrap or reconcile declared dependencies: run `sync`, report per-dependency results and unavailable prerequisites, then run `doctor`. Sync is additive and never prunes undeclared content. Git dependencies resolve current HEAD, bundles follow the provider version, URL skills retain digest verification, and plugins follow their configured marketplace lifecycle. Explicit plugin refresh uses `update NAME`.
- Change inventory membership or refresh one dependency: use the commands below, then run `doctor`.

## Membership and refresh

- Repository-owned skill: `add NAME --kind owned --path PATH`.
- Raw Git skill: `add NAME --kind git --repository URL --source-path PATH --path DESTINATION`.
- Single-file skill: `add NAME --kind url --url HTTPS_URL --sha256 FULL_SHA256 --path DESTINATION`.
- Provider multi-file bundle: `add NAME --kind bundle --url HTTPS_JSON_URL --path DESTINATION`.
- Native plugin: `add NAME --kind plugin --selector PLUGIN@MARKETPLACE --enabled true`.
- Refresh Git, bundle, or plugin from its provider: `update NAME`.
- Change a URL skill's verified content: `update NAME --sha256 DIGEST`, optionally with `--url URL`.
- Remove desired state and managed installation: `remove NAME`. Owned source files are retained by the engine; retire them separately only when the requested removal includes their content. Use `--keep-installed` only when the user explicitly wants undeclared content retained.

Before adding external content, inspect licensing and provenance. Never add Codex system skills or plugin selectors from `openai-primary-runtime`; the runtime owns them. Resolved revisions and installed versions are derived state and never belong in `skills.toml`. Native plugins use their marketplace lifecycle; npm launchers and MCP entries in `config.toml` remain outside this inventory.

After changes, report doctor results, provider failures, and whether a new task or app restart may be needed for discovery. Do not claim successful installation or reconciliation when prerequisites failed.
