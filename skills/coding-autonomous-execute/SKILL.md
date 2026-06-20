---
name: coding-autonomous-execute
description: "Execute a feature queue, one feature, or a stubborn issue fix through a Codex Goal with explicit PROOF.md verification, evaluator judgment, bounded repair, and queue progress updates. Use when the user asks for autonomous execution, keep-going-until-done behavior, queue completion, or repeated repair after coding-feature-execute or coding-fix-issue."
---

# Autonomous Execute

Purpose: use Codex Goals as the only runtime continuation mechanism for autonomous feature work. Do not introduce scheduler, daemon, or repo-local workflow-engine behavior.

## Runtime Contract
A Codex Goal is the thread-scoped completion contract. It does not replace durable repo state.

- `FEATURE_DIR/FEATURE.md` describes what to build.
- `FEATURE_DIR/PROOF.md` defines the primary proof command and done evidence.
- `docs/features/status.json` remains the durable progress queue.
- `$HOME/.codex/scripts/gate` is the repo-health guard.
- `coding-feature-evaluator` is the read-only judge for `PASS`, `FAIL`, or `BLOCKED`.

Budget limit is not completion. Mark a Goal complete only when the named proof evidence passes, gate passes, evaluator passes, and any queue item was updated.

## Goal Quality Checklist
Before starting or rewriting a Goal, make sure it includes:
- concrete outcome state;
- primary proof command or `FEATURE_DIR/PROOF.md` as the proof source;
- repo-health gate;
- evaluator `PASS`;
- starting context or suspected area when known;
- realistic environment requirements when relevant;
- anti-gaming constraints;
- queue or progress artifact for long-running work;
- final cleanup/review before marking complete.

## Goal Templates
Queue:

```text
/goal Complete all non-blocked items in docs/features/status.json one feature at a time. For each
feature, ensure FEATURE.md and PROOF.md exist, run coding-feature-execute, run the primary proof
command from PROOF.md, run $HOME/.codex/scripts/gate, run coding-feature-evaluator, repair bounded
failures, and mark the item passing only after proof, gate, and evaluator PASS. Stop when all
features are passing or remaining items are blocked with concrete reasons. Do not weaken proof,
reduce scope, or substitute assistant/tool claims for observable evidence.
```

Single feature:

```text
/goal Complete FEATURE_DIR according to FEATURE_DIR/FEATURE.md and FEATURE_DIR/PROOF.md. Completion
requires the primary proof command in PROOF.md, $HOME/.codex/scripts/gate, and
coding-feature-evaluator PASS. Preserve repo architecture, use the most realistic available
environment, clean up abandoned attempts before completion, and stop as BLOCKED if the same blocker
repeats three times.
```

Issue fix:

```text
/goal Fix the reported issue with a regression proof, verified by the failing proof turning green
and the relevant broader check passing. Keep the fix minimal, preserve current behavior outside the
failing path, do not weaken proof, and stop as BLOCKED if the issue cannot be reproduced or the same
blocker repeats three times.
```

## Queue Execution
Use this when `docs/features/status.json` exists or the user asks to complete multiple features.

1. Read `docs/features/status.json`.
2. Select the next pending or failing item with `coding-feature-queue`.
3. Mark that item `in_progress`.
4. Work on exactly one `FEATURE_DIR`.
5. Use `coding-proof-author` if `PROOF.md` or executable proof is missing or weak.
6. Use `coding-feature-execute` for implementation.
7. Run the primary proof command from `PROOF.md`.
8. Run `$HOME/.codex/scripts/gate`.
9. Use `coding-feature-evaluator`.
10. Mark the item `passing`, `failing`, or `blocked`.
11. Continue only while the Goal remains active and the next item is clear.

## Bounded Repair
Use bounded repair when proof, gate, or evaluator judgment fails.

1. Repair one concrete failure at a time with `coding-auto-improve` or `coding-fix-issue`.
2. Rerun the narrowest failing check first.
3. Rerun the primary proof command and gate when `FEATURE_DIR` is in scope.
4. Rerun `coding-feature-evaluator`.
5. Stop as `BLOCKED` when the same blocker repeats three times.

## Boundaries
- Do not use Goals for one-line edits, simple explanations, vague improvement requests, or work without an auditable finish line.
- Do not run multiple autonomous Codex sessions against the same checkout.
- Use an isolated `codex/` branch or worktree for independent background tasks.
- Do not auto-approve destructive commands, force pushes, deploy actions, or secret edits.
- Use one primary proof in the handoff. Do not label gate, evaluator, or secondary checks as proof.
- If secondary feature checks were run, report them under `Safety checks`, not under `Proof`.
- Do not report legacy feature-check wrappers as proof; name them as secondary checks only.

## Handoff Format
Use this order:

1. Outcome: completed, blocked, or left failing.
2. Changed files: only material paths.
3. Primary proof: command from `PROOF.md`, red result, green result.
4. Safety checks: `Gate: PASS` or `Gate: FAIL`; add failure detail only when failing. Do not include full passing gate/test counts unless the user asks.
5. Evaluator: `PASS`, `FAIL`, or `BLOCKED`.
6. Queue: status update when applicable.
7. Blockers: concrete blocker or `None`.
8. Skills used.
9. Goal status and usage when a Goal was completed.
