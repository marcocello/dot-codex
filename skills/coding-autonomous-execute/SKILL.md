---
name: coding-autonomous-execute
description: "Continue ready queue work serially through proof, repair, fresh evaluation, and completion."
---

# Autonomous Execute

Purpose: provide a continuation mode around `coding-feature-execute`, completing ready queue work one feature at a time without becoming an assurance tier.

## Contract
- A Goal or keep-going instruction does not replace `FEATURE.md`, `PROOF.md`, queue state, proof capture, final review, or safety rules.
- Autonomous execution is a continuation mode, not an assurance tier. Each selected feature is classified independently by `coding-feature-execute` as standard or sensitive.
- Work on one feature and one `FEATURE_DIR` at a time. One accountable parent owns its complete lifecycle.
- Budget pressure, difficulty, repetition, or elapsed time is not completion and is not automatically a blocker.
- Every official proof command has an explicit timeout. Narrow debugging checks are not official proof attempts.

## Queue Execution
1. Read `docs/features/status.json` using `coding-feature-queue` rules.
2. Select the lowest-priority-number `ready` item.
3. Reset the transient active-feature surface for the selected item; do not carry the previous feature's changed-file list into the next feature's review scope.
4. Confirm decision-complete `FEATURE.md`, `PROOF.md`, and executable `proof/run.sh`.
5. Work that feature through the complete `coding-feature-execute` lifecycle.
6. Apply `coding-feature-execute` consumption-target completion: source proof is intermediate and cannot produce `done` when an existing runtime is the named consumption target. After target-valid proof and fresh `coding-feature-review` final `PASS`, confirm the final candidate stayed unchanged. Any relevant edit requires the complete official proof and another fresh final review before moving it to `done`; then select the next `ready` item.
7. Ignore `draft`, `blocked`, and `done` during implementation selection.
8. Stop when no `ready` item remains; report material drafts or blockers only when they affect the next action.

## Recovery Ladder
Before marking `blocked` or asking `NEED_INPUT`:

1. Inspect the newest run directory, not merely the newest available `result.json`.
2. If `attempt-start.json` exists without `result.json`, check the recorded capture/runner process. Wait or diagnose an active process; treat a dead process as an interrupted retained attempt.
3. Never use an older `PASS` while a newer attempt is incomplete or unresolved.
4. Read the active contracts, queue note, and relevant setup context.
5. Discover available repository tasks, services, browser state, and configured connectors.
6. Use `coding-prepare-environment` for local runtime or dependency problems.
7. Continue safe local rebuild, restart, readiness, and exact-runtime verification when an existing local runtime is the target.
8. Use `coding-repair` for implementation, proof, setup, test, lint, typecheck, or build failures; repair inherits the active feature assurance.
9. Use `coding-proof-author` when the proof boundary, fake, activation, or read-back is insufficient.
10. Retry the narrow failure after each focused repair; after the same failure twice, change tactic or widen only the owning inspection boundary.
11. Mark `blocked` and ask the exact question only when deployment approval or an external dependency remains after recovery.

## Review Findings
Final review findings remain inside the active feature lifecycle. Strengthen proof, repair, rerun full proof, and obtain another fresh final review. Do not select another queue item until the current feature reaches `done` or a genuine blocker.

## Terminal Conditions
- Queue work is complete when no `ready` item remains.
- A genuine user-owned or external dependency stops a feature only after the Recovery Ladder is exhausted.
- One-line edits, explanations, vague improvement requests, and work without a finish line do not enter autonomous execution.

## Handoff
Lead with `Goal complete`, `Done`, or `Needs input`. Report the current feature/queue state, realistic proof, final review verdict, known gaps, and exact blocker.
