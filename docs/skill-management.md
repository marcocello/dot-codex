# Skill Management

`skills.toml` is the desired-state authority for this dot-codex installation. It records what should exist and where it comes from; it does not make all skill content repository-owned.

## Ownership model

| Kind | Content authority | Reconciliation |
| --- | --- | --- |
| `owned` | This Git repository | Verify `SKILL.md`; edit and commit normally |
| `git` | External Git repository | Resolve current `HEAD`, copy one skill directory, and record the resolved commit only in derived metadata |
| `url` | External single-file endpoint at an exact SHA-256 | Download one `SKILL.md` and verify bytes |
| `plugin` | Configured Codex marketplace snapshot | Install/remove through `codex plugin`; verify membership and enablement, not version |

Downloaded Git and URL skills remain uncommitted. The manager derives a marked block in `.gitignore` from the manifest. This repository uses whitelist negations that override `.git/info/exclude`, so the tracked generated block is required to keep the same clean behavior on every clone. The block and each `.codex-skill-source.json` are derived state, not authorities; edit the manifest, never the block.

Codex system skills and plugins from `openai-primary-runtime` are runtime-owned. They stay out of `skills.toml`, are neither installed nor verified by this manager, and must not be added through `manage-codex-skills`.

## Commands

Run the manager through `"${CODEX_HOME:-$HOME/.codex}/scripts/skill_inventory.py"`.

- `list`: read desired state without contacting providers.
- `doctor`: report invalid sources, missing local skills, metadata drift, or plugin membership/enablement drift.
- `sync`: install or refresh declared dependencies; never prune undeclared content.
- `add`: add one validated entry and reconcile it.
- `update`: refresh a Git skill from current `HEAD`, reinstall a plugin from its marketplace, or explicitly change a URL skill's digest.
- `remove`: uninstall manager-owned external content or a plugin, then remove the entry. Owned files are retained.

Use `--no-sync` on `add` or `update` only when recording desired state before an external prerequisite is available. Use `remove --keep-installed` only when undeclared content should deliberately remain.

## Plugin marketplace versus `npx`

A Codex plugin is a first-class bundle. Codex reads its plugin manifest, installs it from a configured marketplace snapshot, caches it, exposes bundled skills/MCP/apps, and tracks enabled state. Use `codex plugin add PLUGIN@MARKETPLACE` directly or a `kind = "plugin"` inventory entry.

`npx PACKAGE@VERSION ...` downloads and runs an npm package binary. It is an execution mechanism, not a Codex package lifecycle: the binary decides what files or configuration it changes, and Codex does not automatically know its provenance, version, removal procedure, or contributed capabilities. The existing `npx` MCP launchers in `config.toml` therefore remain outside `skills.toml`; npm version policy stays with that configuration rather than this inventory.

For Impeccable, this inventory tracks the actual Codex skill directory from the upstream Git repository's current `HEAD`. Its optional npm installer and project hooks remain a separate, explicit workflow.

## Why OpenSpace is optional

[OpenSpace](https://github.com/HKUDS/OpenSpace) is a broader skill-management and agent harness layer: local/cloud retrieval, evidence and quality records, sharing, controlled evolution, task execution, and an MCP integration. Its Codex setup adds an OpenSpace runtime plus host skills and configuration.

That solves a different problem from repeatable machine membership bootstrap. Adding OpenSpace as the authority here would introduce another runtime, index, evidence store, optional cloud identity, and evolution policy before the smaller dependency problem requires them. Keep `skills.toml` as the installed-set authority. Add OpenSpace later if cross-agent retrieval, measured skill quality, sharing, or evidence-driven evolution becomes valuable; imported OpenSpace skills should still be promoted into this inventory with an explicit source before they become permanent dependencies.

## Update policy

- Owned skills change through normal Git review.
- Git skills follow current repository `HEAD`; `sync` detects and installs a changed resolved commit.
- URL skills move only after reviewing new content and recording its SHA-256.
- Plugin versions are intentionally absent. `update NAME` removes and reinstalls a plugin from the configured marketplace.
- Codex system skills and `openai-primary-runtime` plugins move with the runtime and remain outside inventory drift checks.
- `sync` refreshes Git dependencies but never deletes undeclared content. Plugins update only when explicitly refreshed.
