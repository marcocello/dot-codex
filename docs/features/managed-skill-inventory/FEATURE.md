# Managed Skill Inventory

## Goal
Make `skills.toml` the portable desired-state inventory for authored skills, user-managed plugins, and third-party skill sources, so a fresh dot-codex checkout can reconcile the same skill set without committing downloaded third-party content or recording Git revisions and plugin versions.

## Decisions
- Keep authored skill content in this repository and describe it with `kind = "owned"` entries.
- Exclude Codex system skills and plugins selected from `openai-primary-runtime`; those capabilities are supplied and managed by the Codex runtime rather than this repository.
- Delegate plugin installation and removal to `codex plugin`; a plugin entry represents the package that contributes one or more skills.
- Git skill entries follow the source repository's current `HEAD`; the resolved commit is recorded only in derived local installer metadata.
- Plugin entries follow the configured Codex marketplace and do not record or compare package versions.
- URL skill entries retain SHA-256 verification because a URL does not provide a repository revision.
- Bundle skill entries follow a provider-supplied JSON version and safely materialize its declared multi-file payload.
- Keep downloaded content out of Git. The manifest is authoritative; installer metadata and a marked generated `.gitignore` block are derived state.
- Reconciliation is additive. It installs or refreshes declared dependencies but never prunes undeclared directories or plugins.
- `update` refreshes a Git skill from current `HEAD` or reinstalls a plugin from its configured marketplace. URL updates remain explicit URL/digest changes.
- Keep OpenSpace outside the bootstrap path. It is an optional retrieval, evaluation, sharing, and evolution layer, not the authority for this machine's installed skill set.

## Behavior
- `scripts/skill_inventory.py` reads `skills.toml` by default and exposes `list`, `doctor`, `sync`, `add`, `remove`, and `update` commands.
- `list` prints the declared desired state without requiring providers to be available.
- `doctor` validates the manifest, checks each local skill's `SKILL.md`, checks derived installer metadata, and compares declared plugins with `codex plugin list --json` without comparing versions.
- `sync` verifies owned entries, resolves Git sources at current `HEAD`, reads provider bundle versions, materializes missing or stale third-party skills, installs missing declared plugins with `codex plugin add`, and fails on unavailable providers or enablement drift.
- Manifest validation rejects `kind = "system"` and plugin selectors ending in `@openai-primary-runtime`; `add` cannot introduce either form.
- Third-party materialization is atomic and refuses to overwrite a destination that does not carry matching manager metadata.
- `add` validates and writes one entry, then reconciles it unless `--no-sync` is supplied.
- `update NAME` refreshes Git or plugin dependencies from their provider. URL updates require an explicitly supplied URL or SHA-256; plugin enablement remains an explicit expectation.
- `remove` uninstalls a managed raw skill or declared plugin before deleting its manifest entry. `--keep-installed` removes desired state only.
- Removing owned content is never attempted; removal only changes its manifest membership.
- Managed third-party paths are added to a marked generated block in the repository's `.gitignore` when the manifest and skill root belong to a Git checkout. This is required because the repository's whitelist negations take precedence over `.git/info/exclude`.
- The two user-facing skills, `sync-codex-skills` and `manage-codex-skills`, route bootstrap/reconciliation and inventory mutation to the shared script.

## Constraints
- The implementation uses Python's standard library and explicit subprocess argument arrays; the manifest cannot execute arbitrary shell commands.
- Third-party destinations and source subpaths must be safe relative paths beneath the selected skill root or checkout after filesystem resolution. Symlinked path components and symlinked Git payloads are rejected.
- URL sources may materialize one `SKILL.md`; Git sources and validated provider bundles may materialize one skill directory.
- `skills.toml` rejects `revision` and `version` fields; resolved Git commits and installed plugin versions may appear only in provider or derived local state.
- `skills.toml` contains no Codex system skills or `openai-primary-runtime` plugins.
- Provider credentials, private repositories, and unavailable marketplaces remain external prerequisites.

## Non-Goals
- Managing MCP servers declared directly in `config.toml`, including servers launched with `npx`.
- Replacing Codex plugin cache, marketplace, enablement, or authentication semantics.
- Automatically discovering every skill visible through remote app connectors.
- Automatically publishing, evaluating, evolving, or sharing skills through OpenSpace.
- Deleting undeclared skills or plugins during `sync`.
