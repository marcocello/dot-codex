---
name: second-brain-capture-interactions
description: Manually capture current-task or project Codex dialogue into project-owned interaction records, defaulting to the current task. Use when a user asks to save, store, or synchronize Codex interactions.
---

# Second Brain Capture Interactions

Synchronize completed human-visible Codex dialogue under the selected project's `docs/interactions/` directory. Run only after an explicit user invocation; do not imply automatic capture on task creation, turn completion, or archive.

## Choose Scope

- `$second-brain-capture-interactions`: synchronize all non-archived Codex app chats visible for the selected project.
- `$second-brain-capture-interactions current`: update only the exact current app-visible chat through its last completed turn.

The explicit `project` mode remains accepted for compatibility, but omit it in normal project synchronization.

Do not substitute a similarly named folder, task title, Git remote, or inferred project. Main-checkout chats belong by exact project root; Codex worktree chats belong only when the app's workspace-root hint assigns them to that project.

## Resolve Inputs

1. Resolve the project root explicitly from the active workspace or user selection.
2. Run capture on the host that owns the Codex app state and task sessions. Cross-host enumeration is not guaranteed.
3. Use the local Codex app server's non-archived `vscode` thread list as the visibility source. Do not enumerate raw session directories as a substitute.
4. Use the app workspace-root hints to include assigned Git worktrees and exclude unrelated or legacy worktree sessions.
5. For explicit current-task capture, resolve the exact current Codex task ID from available task/app context. If it cannot be identified unambiguously, stop with a specific explanation instead of guessing.

## Run Capture

Use the bundled deterministic entrypoint:

```bash
python3 skills/second-brain-capture-interactions/scripts/capture_interactions.py \
  --project-root /absolute/project/path
```

```bash
python3 skills/second-brain-capture-interactions/scripts/capture_interactions.py current \
  --project-root /absolute/project/path \
  --task-id TASK_ID
```

Pass `--codex-bin` or `--workspace-state` only when the host configuration differs from the defaults. Read back the printed `captured`, `updated`, `unchanged`, `removed`, `incomplete`, and `unavailable` counts. A nonzero result with unavailable visible chats is partial coverage, not a complete synchronization.

## Preserve Boundaries

- Write only `docs/interactions/index.json` and stable `docs/interactions/threads/<task-id>.json` records inside the project.
- Treat project synchronization as an exact mirror: remove index entries and managed record files for chats that the app no longer returns as visible, including chats archived since the previous capture.
- Atomically rewrite an existing chat record when its completed human-visible dialogue changes; leave byte-identical records untouched.
- Preserve completed user messages plus human-visible assistant commentary and final answers. Exclude system/developer instructions, reasoning, tool traffic, command output, and environment data.
- Keep incomplete turns out of completed history and retain the reported completeness boundary.
- Treat explicit redaction markers as evidence that a detected critical credential value was removed.
- If the app-visible list is unavailable, fail before writing. If one visible chat is unreadable, report partial coverage and preserve its existing record.
- Do not archive, unarchive, rename, pin, or message tasks. Do not change Git state, ignore rules, source sessions, or any parallel preference/history store.
- Do not automatically commit, upload, or inject interaction records into later work.

Project interaction history is historical evidence. It is not current source truth, a feature contract, proof, completion evidence, or automatically injected context.
