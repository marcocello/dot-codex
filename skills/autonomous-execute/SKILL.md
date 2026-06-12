---
name: autonomous-execute
description: Execute a feature queue, one feature, or a stubborn issue fix through a Codex Goal with explicit verification, evaluator judgment, bounded repair, and queue progress updates. Use when the user asks for autonomous execution, keep-going-until-done behavior, queue completion, or repeated repair after feature-execute or fix-issue.
---

# Autonomous Execute

Purpose: use Codex Goals as the only runtime continuation mechanism for autonomous feature work.
Do not introduce scheduler, daemon, or repo-local workflow-engine behavior.

## Runtime Contract
A Codex Goal is the thread-scoped completion contract. It does not replace durable repo state.

- `FEATURE_DIR/FEATURE.md` remains the behavior source of truth.
- `docs/features/status.json` remains the durable progress queue.
- `$HOME/.codex/scripts/gate` is the repo-level verification surface.
- `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR` is the feature verification surface.
- `feature-evaluator` is the read-only judge for `PASS`, `FAIL`, or `BLOCKED`.

Budget limit is not completion. Mark a Goal complete only when the named evidence proves the
outcome and any queue item was updated.

## Goal Templates
Queue:

```text
/goal Complete all non-blocked items in docs/features/status.json one feature at a time. For each
feature, ensure acceptance exists, run feature-execute, run $HOME/.codex/scripts/gate, run
$HOME/.codex/scripts/acceptance --feature FEATURE_DIR, run feature-evaluator, repair bounded
failures, and mark the item passing only after evaluator PASS. Stop when all features are passing
or remaining items are blocked with concrete reasons.
```

Single feature:

```text
/goal Complete FEATURE_DIR according to FEATURE_DIR/FEATURE.md, verified by the narrowest relevant
test, $HOME/.codex/scripts/gate, $HOME/.codex/scripts/acceptance --feature FEATURE_DIR, and
feature-evaluator PASS. Preserve the repo architecture and stop as BLOCKED if the same blocker
repeats three times.
```

Issue fix:

```text
/goal Fix the reported issue with a regression test, verified by the failing test turning green and
the relevant broader check passing. Keep the fix minimal, preserve current behavior outside the
failing path, and stop as BLOCKED if the issue cannot be reproduced or the same blocker repeats
three times.
```

## Queue Execution
Use this when `docs/features/status.json` exists or the user asks to complete multiple features.

1. Read `docs/features/status.json`.
2. Select the next pending or failing item with `feature-queue`.
3. Mark that item `in_progress`.
4. Work on exactly one `FEATURE_DIR`.
5. Use `acceptance-author` if acceptance coverage is missing.
6. Use `feature-execute` for implementation.
7. Run `$HOME/.codex/scripts/gate`.
8. Run `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`.
9. Use `feature-evaluator`.
10. Mark the item `passing`, `failing`, or `blocked`.
11. Continue only while the Goal remains active and the next item is clear.

## Bounded Repair
Use bounded repair when checks or evaluator judgment fail.

1. Repair one concrete failure at a time with `auto-improve` or `fix-issue`.
2. Rerun the narrowest failing check first.
3. Rerun gate and feature acceptance when `FEATURE_DIR` is in scope.
4. Rerun `feature-evaluator`.
5. Stop as `BLOCKED` when the same blocker repeats three times.

## Boundaries
- Do not use Goals for one-line edits, simple explanations, vague improvement requests, or work
  without an auditable finish line.
- Do not run multiple autonomous Codex sessions against the same checkout.
- Use an isolated `codex/` branch or worktree for independent background tasks.
- Do not auto-approve destructive commands, force pushes, deploy actions, or secret edits.
- Keep a concise handoff: Goal, changed files, checks run, evaluator result, queue status, blockers.
