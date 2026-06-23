---
name: coding-autonomous-execute
description: "Execute a feature queue, one feature, or a stubborn issue fix through a Codex Goal with explicit PROOF.md verification, evaluator judgment, bounded repair, and queue progress updates. Use when the user asks for autonomous execution, keep-going-until-done behavior, queue completion, or repeated repair after coding-feature-execute or coding-repair."
---

# Autonomous Execute

Purpose: use Codex Goals as the only runtime continuation mechanism for autonomous feature work. Do not introduce scheduler, daemon, or repo-local workflow-engine behavior.

## Runtime Contract
A Codex Goal is thread-scoped runtime continuation. It does not replace the durable
contracts, queue, checks, evaluator, or handoff rules in `AGENTS.md`.

Budget limit is not completion. Mark a Goal complete only by the universal lifecycle in
`AGENTS.md`.

## Goal Quality Checklist
Before starting or rewriting a Goal, make sure it includes:
- concrete outcome state;
- proof source, gate, evaluator, and queue expectations from `AGENTS.md`;
- starting context or suspected area when known;
- realistic environment requirements when relevant;
- anti-gaming constraints;
- queue or progress artifact for long-running work;
- final cleanup/review before marking complete.

## Goal Templates
Queue:

```text
/goal Complete all ready or repairing items in docs/features/status.json one feature at a time.
For each feature, ensure FEATURE.md and PROOF.md exist, run coding-feature-execute, apply the
AGENTS.md Universal Lifecycle, repair bounded failures, and mark the item done only after that
lifecycle passes. Skip draft and blocked items. Stop when no ready or repairing items remain, and
report any draft or blocked items with concrete reasons. Do not weaken proof, reduce scope, or
substitute assistant/tool claims for observable evidence.
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
2. Select the next repairing or ready item with `coding-feature-queue`.
3. Preflight the selected item's `FEATURE.md`, `PROOF.md`, primary proof command, and
   executable proof artifact before marking it `in_progress`.
4. If the contract or proof is missing, stale, weak, or blocked, use `coding-proof-author`
   and mark the item `draft` or `blocked`; do not mark it `in_progress`.
5. Mark the item `in_progress` only after the preflight shows it is implementable.
6. Work on exactly one `FEATURE_DIR`.
7. Use `coding-feature-execute` for implementation.
8. Apply the `AGENTS.md` Universal Lifecycle.
9. Continue only while the Goal remains active and the next item is clear.

## Bounded Repair
Use bounded repair when proof, gate, or evaluator judgment fails.

1. Repair one concrete failure at a time with `coding-repair`.
2. Rerun the narrowest failing check first.
3. Rerun the checks required by the `AGENTS.md` Universal Lifecycle.
4. Stop as `BLOCKED` when the same blocker repeats three times.

## Green-But-Broken Handling
Use this when the primary proof, gate, and evaluator pass but observed product behavior still fails.

1. Treat the result as a proof-system failure, not as completed work.
2. Read the relevant run output, browser/runtime evidence, or agent trace to identify what the proof missed.
3. Use `coding-proof-author` to add or strengthen a failing proof for the observed broken behavior.
4. Repair implementation only after the strengthened proof fails for the right reason.
5. Rerun the checks required by the `AGENTS.md` Universal Lifecycle before marking the item done.

## Boundaries
- Do not use Goals for one-line edits, simple explanations, vague improvement requests, or work without an auditable finish line.
- Do not run multiple autonomous Codex sessions against the same checkout.
- Use an isolated `codex/` branch or worktree for independent background tasks.
- Do not auto-approve destructive commands, force pushes, deploy actions, or secret edits.
- Use the proof and handoff terminology from `AGENTS.md`.
- Do not continue treating an item as done after credible green-but-broken evidence.

## Handoff
Report using the `AGENTS.md` handoff format for completed feature or issue work.
