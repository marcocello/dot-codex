# Managed Skill Inventory Proof

## Proves
- The real manager CLI can bootstrap a Git skill from current `HEAD`, a digest-verified URL skill, and a Codex plugin into an isolated skill root without manifest revision/version fields.
- The same CLI can add, refresh, remove, list, and diagnose dependencies while persisting `skills.toml` as the desired-state authority.
- Provider operations use argument arrays and an isolated fake `codex` executable; network and plugin provider behavior are the only fakes.
- A second synchronization is idempotent and undeclared directories are not pruned.
- Forbidden manifest `revision`/`version` fields, `kind = "system"`, `@openai-primary-runtime` selectors, unsafe paths, missing owned skills, plugin enablement drift, and unmanaged destination collisions fail visibly.
- Symlinked destination parents and Git source paths cannot escape their selected roots.
- The repository manifest covers every authored skill and the migrated Bento, Impeccable, and Remotion dependencies, contains no runtime-owned system or primary-runtime entries, and Git-ignores raw external paths with generated rules.
- Both routing skills pass the native skill validator.

## Evidence Method
- Build a temporary local Git repository containing a real `SKILL.md`, install its current `HEAD`, advance the repository, then require `update` to refresh to the new `HEAD`.
- Serve a real `SKILL.md` from an in-process loopback HTTP server and pin its SHA-256 digest.
- Use a fake `codex` executable that implements the documented `plugin list --json`, `plugin add`, and `plugin remove` boundary with persistent JSON state.
- Invoke the actual CLI through subprocesses, then read back the manifest, installed content, installer metadata, plugin state, and preserved extra directory.
- Initialize the temporary inventory root as a real Git checkout, then read back the manager-generated `.gitignore` block after two synchronizations.
- Mutate the fake provider's persisted plugin version and require `doctor` to ignore it; mutate enablement and require `doctor` to reject the drift.
- Create temporary destination-parent and Git-source symlink escapes and require reconciliation to fail without materializing content outside either root.
- Run focused pytest coverage against failure and mutation paths.
- Parse the repository's real manifest, compare owned entries with Git-tracked skill directories, require exactly 52 managed entries, and reject any system kind or primary-runtime selector.
- Run `quick_validate.py` against both new skill directories.

## False-Green Risks
- A mocked network or marketplace cannot prove public provider availability; the proof limits the fake to those external boundaries and exercises the real reconciliation, filesystem, hashing, Git, TOML, and subprocess logic.
- Static manifest coverage cannot prove future provider availability or marketplace contents; `doctor` checks only the dependencies this repository intentionally manages.
- Plugin installation success alone could hide a broken native refresh; the proof requires provider-state read-back across add and update remove/add operations.
- A first successful install could hide non-idempotent behavior; the proof runs synchronization twice and checks unchanged content and state.

## Does Not Prove
- Access to private Git repositories, future marketplace snapshots, or external URLs on another machine.
- That a running Codex task reloads newly installed skills without restart.
- OpenSpace cloud, quality scoring, skill evolution, or task execution.
- MCP servers installed or launched through npm or `npx`.

## Execution
- Runner: `docs/features/managed-skill-inventory/proof/run.sh`
- Official timeout: 120 seconds.
- The runner uses isolated temporary homes and provider state; it does not mutate the live Codex installation.
