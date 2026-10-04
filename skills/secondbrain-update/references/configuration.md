# Configuration

The source of truth is `secondbrain.yaml`, selected explicitly or found at `${CODEX_HOME:-$HOME/.codex}/secondbrain.yaml`. The tracked `secondbrain.template.yaml` is a starting point, not an active account selection. Copy it without overwriting an existing private file. Its defaults are a one-hour initial window, update every 15 minutes and review every 60 minutes, both paused and all sources disabled. Private configuration and default state stay Git-ignored.

Use a Python environment with `PyYAML>=6,<7` from `skills/secondbrain-update/requirements.txt`. The repository `.venv/bin/python` can run the helper when present; otherwise install that requirement in a local environment, not globally. The underlying state CLI still uses only the standard library.

```bash
"${CODEX_HOME:-$HOME/.codex}/.venv/bin/python" \
  "${CODEX_HOME:-$HOME/.codex}/scripts/secondbrain_config.py" show
"${CODEX_HOME:-$HOME/.codex}/.venv/bin/python" \
  "${CODEX_HOME:-$HOME/.codex}/scripts/secondbrain_config.py" sync-sources
```

Pass `--config /absolute/path/secondbrain.yaml` for another config. `show` validates and returns normalized config without writing. `sync-sources` initializes the configured private workspace and atomically reconciles source registrations, preserving cursors/evidence. Disabled empty scopes are placeholders; they never bind a new immutable source. Removing a source disables it in storage. Changing an existing ID's provider or configured scope is rejected; use a new ID, preserving the old evidence. No command here fetches remote data.

Schema `1` requires `workspace`, positive integer `initial_lookback_minutes`, `schedules.update` and `schedules.review` (each `enabled` boolean and positive `every_minutes`), and a `sources` list. Source fields are `id`, `provider`, `enabled`, and object `scope`. IDs are unique. Unknown top-level/source/schedule fields, duplicate YAML keys and unsafe tags fail before reconciliation. Paths expand `~` and resolve relative to the config file. The helper returns structured JSON and nonzero exit on failure; do not continue using a stale successful result.

Supported providers: `whatsapp`, `repos`, `zotero`, `gmail`, `onedrive`, `clickup`, `notion`. Disabled scopes may be `{}`. Enabled scopes must explicitly select their account/resources. WhatsApp requires exactly `adapter: wacli`, `store: PATH`, `chats: [JID, ...]` or the explicit scalar `all`. Repositories require `paths: [PATH, ...]`. Other scopes carry account/library/workspace/folder selections verified by the corresponding connector; a syntactically valid scope does not prove credentials or access.

The initial lookback supplies the first bounded intake window, not a sliding checkpoint reset. Read incoming and outgoing state. Historical imports and unsupported edits/deletions need an explicit coverage decision. Personal goals and delegated authority remain in the workspace's `profile.md`, `priorities.md`, and `rules.md`, backed by actual user instructions. No `auto_send` switch or elapsed-time rule silently grants messaging authority.

`schedule-plan` returns two desired native heartbeat payloads. Apply them through the [scheduler procedure](../../secondbrain-review/references/scheduling.md). Planning does not install a watcher or activate anything. Pause both jobs before changing workspace/config identity, then reconcile explicitly; never migrate private state or create new schedules merely because an old file disappeared.
