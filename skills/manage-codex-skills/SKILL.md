---
name: manage-codex-skills
description: Manage skills.toml membership and sources. Use to add, remove, refresh, list, or diagnose authored, external, and user-managed plugin dependencies; use sync-codex-skills for bootstrap-only requests.
---

# Manage Codex Skills

Use `"${CODEX_HOME:-$HOME/.codex}/scripts/skill_inventory.py"` for every mutation so `skills.toml` remains authoritative.

- Inspect: `list` or `doctor`.
- Add repository-owned membership: `add NAME --kind owned --path PATH`.
- Add a raw Git skill: `add NAME --kind git --repository URL --source-path PATH --path DESTINATION`.
- Add a single-file skill: `add NAME --kind url --url HTTPS_URL --sha256 FULL_SHA256 --path DESTINATION`.
- Add a native plugin: `add NAME --kind plugin --selector PLUGIN@MARKETPLACE --enabled true`.
- Refresh a Git skill or plugin from its provider: `update NAME`.
- Change a URL skill's verified content: `update NAME --sha256 DIGEST` and optionally `--url URL`.
- Remove desired state and managed installation: `remove NAME`. Use `--keep-installed` only when the user explicitly wants undeclared content retained.

Before adding external content, inspect its licensing and provenance. Never add Codex system skills or plugin selectors from `openai-primary-runtime`; the Codex runtime owns both. Git skills follow current repository `HEAD`; user-managed plugins follow their configured marketplace. Resolved revisions and installed versions are derived state and never belong in `skills.toml`. Plugin packages belong to the native marketplace lifecycle; `npx` commands and MCP entries in `config.toml` remain outside this inventory. After mutation, run `doctor` and report any restart requirement. Read `docs/skill-management.md` for the ownership and OpenSpace model.
