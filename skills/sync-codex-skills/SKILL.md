---
name: sync-codex-skills
description: Reconcile or bootstrap Codex from skills.toml. Use for new-machine setup, pinned external downloads, plugin installation, or desired-state checks; use manage-codex-skills for inventory changes.
---

# Sync Codex Skills

Use the shared inventory engine; do not hand-copy declared dependencies.

1. From the dot-codex checkout, run `"${CODEX_HOME:-$HOME/.codex}/scripts/skill_inventory.py" doctor` to inspect drift when the user asked for an audit only.
2. Run `"${CODEX_HOME:-$HOME/.codex}/scripts/skill_inventory.py" sync` when the user asked to bootstrap or reconcile.
3. Report each installed dependency and any provider prerequisite that failed.
4. Run `doctor` again after a successful sync.
5. Tell the user that newly installed skills or plugins may require a new Codex task or app restart.

`sync` is additive: it never removes undeclared content. Git skills resolve current `HEAD`; user-managed plugins use the configured marketplace; URL skills retain digest verification. Codex system skills and `openai-primary-runtime` plugins are intentionally absent because the runtime owns them. Read `docs/skill-management.md` when source ownership, plugin versus `npx`, or OpenSpace boundaries matter.
