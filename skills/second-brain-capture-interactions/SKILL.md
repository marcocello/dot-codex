---
name: second-brain-capture-interactions
description: Manually capture current-task or project Codex dialogue into project-owned interaction records, defaulting to the current task. Use when a user asks to save, store, or synchronize Codex interactions.
---

# Second Brain Capture Interactions

Preserve completed human-visible Codex dialogue under the selected project's `interactions/` directory. Run only after an explicit user invocation; do not imply automatic capture on task creation, turn completion, or archive.

## Choose Scope

- `$second-brain-capture-interactions`: capture the exact current task through its last completed turn by default.
- `$second-brain-capture-interactions project`: synchronize accessible active and archived tasks whose normalized workspace exactly matches the selected project root.

The explicit `$second-brain-capture-interactions current` form remains accepted for compatibility, but omit `current` in normal current-task use.

Do not substitute a similarly named folder, task title, Git remote, or inferred project. This skill works for any project directory and does not require Git or `docs/`.

## Resolve Inputs

1. Resolve the project root explicitly from the active workspace or user selection.
2. For current-task capture, resolve the exact current Codex task ID from available task/app context. If it cannot be identified unambiguously, stop with a specific explanation instead of guessing.
3. Run capture on the host that owns the task session store. Cross-host enumeration is not guaranteed.
4. Default to `~/.codex/sessions` and `~/.codex/archived_sessions`; pass alternate roots only when the host configuration establishes them.

## Run Capture

Use the bundled deterministic entrypoint:

```bash
python3 skills/second-brain-capture-interactions/scripts/capture_interactions.py \
  --project-root /absolute/project/path \
  --task-id TASK_ID
```

```bash
python3 skills/second-brain-capture-interactions/scripts/capture_interactions.py project \
  --project-root /absolute/project/path
```

Pass `--sessions-root` and `--archived-sessions-root` when their locations differ from the defaults. Read back the printed `captured`, `updated`, `unchanged`, `incomplete`, and `unavailable` counts. A nonzero result with unavailable sources is partial coverage, not a complete synchronization.

## Preserve Boundaries

- Write only `interactions/index.json` and stable `interactions/threads/<task-id>.json` records inside the project.
- Preserve completed user messages plus human-visible assistant commentary and final answers. Exclude system/developer instructions, reasoning, tool traffic, command output, and environment data.
- Keep incomplete turns out of completed history and retain the reported completeness boundary.
- Treat explicit redaction markers as evidence that a detected critical credential value was removed.
- Do not archive, unarchive, rename, pin, or message tasks. Do not change Git state, ignore rules, source sessions, or any parallel preference/history store.
- Do not automatically commit, upload, or inject interaction records into later work.

Project interaction history is historical evidence. It is not current source truth, a feature contract, proof, completion evidence, or automatically injected context.
