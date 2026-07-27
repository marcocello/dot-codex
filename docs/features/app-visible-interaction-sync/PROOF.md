# Proof

## Done
- The real capture CLI mirrors app-visible main-checkout and assigned-worktree chats under `docs/interactions`.
- A completed chat update rewrites its existing record, while an archived chat and a pre-existing stale record are removed.

## Command
```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/app-visible-interaction-sync --timeout-seconds 60 --note "verify app-visible interaction synchronization"
```

## Scenario: Mirror app-visible project chats
- Producer/activation: a pytest scenario creates a temporary Git repository and worktree, realistic Codex JSONL sessions, saved-project workspace hints, and invokes the production capture CLI in project mode.
- Consumer: the normal app-server client, visibility filter, dialogue parser, atomic writer, index writer, and stale-record reconciliation run unchanged.
- Read-back: the scenario reads `docs/interactions/index.json` and every managed thread record after initial capture, chat update, and archive removal.
- Fake: a deterministic outer Codex app-server executable supplies paginated `thread/list` responses and rejects requests that do not ask for non-archived interactive app chats.
- Catches: raw session-folder enumeration, exact-main-cwd filtering that misses worktrees, subagent inclusion, merge-only indexes, stale record files, writes to top-level `interactions/`, and failure to update completed dialogue.

## Scope
Proves:
- Main-checkout and assigned-worktree app chats are captured.
- App-server requests exclude archived and non-interactive sources.
- Index and record files exactly mirror the successful visible set.
- Completed dialogue updates and incomplete-turn exclusion are persisted correctly.
- Removed app-visible entries and orphan records are deleted.

Does not prove:
- Compatibility with future Codex app-server protocol changes.
- Cross-host capture.
- Migration of the legacy top-level interaction store.

False-green risks:
- A fake that silently accepts the wrong app-server request could hide source-filter regressions; the fixture validates request parameters.
- Inner-function-only assertions could miss CLI wiring; the scenario invokes the production script as a subprocess.

Evidence method:
- deterministic

Known gaps:
- live: the proof replaces the outer Codex app server and does not mutate or archive real user chats.

## Environment
- Repository-local Python and pytest.
- Temporary Git repository, worktree, session files, app state, and interaction store.
- Runner stdout prints the Python executable/version, capture entrypoint, and fake boundary.
