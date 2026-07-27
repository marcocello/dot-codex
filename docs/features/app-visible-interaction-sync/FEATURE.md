# App-visible interaction synchronization

## Goal
Synchronize the human-visible Codex chats shown for a project into project-owned interaction records so the stored history matches the app after chat updates and archival.

## Behavior
- A normal skill invocation synchronizes every non-archived, interactive Codex chat assigned to the selected project.
- Chats running in the main checkout and Codex-managed Git worktrees assigned to the same saved project are included.
- CLI execution sessions, guardian sessions, spawned subagents, reviewer sessions, archived chats, and worktree chats not assigned to the project are excluded.
- Records are written under `docs/interactions/index.json` and `docs/interactions/threads/<task-id>.json`.
- Synchronization is an exact mirror of the app-visible set:
  - a newly visible chat creates one record;
  - new completed dialogue atomically updates the existing record;
  - an archived or otherwise no-longer-visible chat is removed from both the index and record directory;
  - an unchanged chat does not rewrite its record.
- Only completed user-visible dialogue is persisted. An in-progress turn is reported as incomplete and remains outside completed history until a later synchronization.
- If the authoritative app-visible list cannot be obtained, synchronization fails without changing the store.
- If one visible chat cannot be read, synchronization reports partial coverage and preserves any existing record for that still-visible chat.

## Constraints
- The Codex app-server non-archived interactive thread list is authoritative for visibility.
- Saved-project workspace-root hints establish that a worktree chat belongs to the selected project.
- Writes remain atomic and protected by the interaction-store lock.
- Critical credential values detected in captured dialogue remain redacted.

## Non-Goals
- Capturing archived chats.
- Capturing ChatGPT chats, Codex CLI execution jobs, or internal agent sessions.
- Automatically committing or uploading interaction records.
- Migrating or deleting the legacy top-level `interactions/` directory.
