---
name: coding-autonomous-execute
description: "Continue ready queue work or bounded revalidation until fresh evaluation decides the outcome."
---

# Autonomous Execute

Purpose: provide runtime continuation around `coding-feature-execute`. No scheduler, daemon, or repository workflow engine.

## Contract
- The Goal or keep-going instruction does not replace `FEATURE.md`, `PROOF.md`, queue state, proof capture, safety rules, or evaluator judgment.
- Budget pressure, difficulty, repetition, or elapsed time is not completion and is not automatically a blocker.
- Failed proof, gate, or evaluator output becomes the next work item during `ready` implementation. Explicit revalidation instead moves a failure to `ready` and stops without repair.
- Multiple feature parents and supporting agents may edit the same checkout concurrently. Each active feature keeps one accountable parent for decisions, integration, queue transitions, and completion judgment.
- Every official proof command has an explicit timeout.

Concurrent agents preserve unrelated work, declare narrow `files` change prefixes and `revalidate_on` proof dependencies, and re-read shared files before narrow edits. Do not start a competing proof for the same feature while its newest attempt is unresolved.

## Recovery Ladder
Before marking `blocked` or asking `NEED_INPUT`:

1. Inspect the newest run directory, not merely the newest available `result.json`.
2. When it has `attempt-start.json` but no `result.json`, read the recorded capture/runner PID and check whether that process is still active. Wait or diagnose an active run; do not start a competing proof. Treat a dead process as an interrupted retained attempt and inspect available stdout/stderr.
3. Never fall back to an older PASS while a newer attempt is incomplete or unresolved.
4. Read the active contracts, queue note, and repository setup/testing docs when needed.
5. Discover available repository scripts, tasks, Makefiles, package commands, containers, local services, browser/app state, and configured connectors.
6. Use `coding-prepare-environment` for local runtime/dependency/setup problems.
7. Use `coding-repair` for implementation, proof runner, gate, or evaluator failures.
8. Use `coding-architecture-deep-dive` when repeated failure or evaluator evidence identifies a structural boundary problem; implement only the smallest correction tied to the active goal.
9. Use `coding-proof-author` when the proof boundary, readiness, fake, or gap is insufficient; record the revised proof decision and continue unless a material user-owned choice remains.
10. Request approval for exact destructive/external actions when approval can unblock realistic proof.
11. Retry the narrow failing check after each focused repair.
12. Same failure twice: change tactic, add a diagnostic, or widen only the owning inspection boundary.
13. Ask the user only when the remaining decision, credential, safe target, approval, or external state cannot be supplied locally.

## Queue Execution
1. Read `docs/features/status.json` using `coding-feature-queue` rules.
2. Select the lowest-priority-number `ready` item.
3. Confirm decision-complete `FEATURE.md`, `PROOF.md`, executable `proof/run.sh`, declared `files` change prefixes, and `revalidate_on` proof dependencies.
4. Run the overlap invalidator before implementation.
5. Work exactly one `FEATURE_DIR` through `coding-feature-execute`.
6. On `done`, select the next ready item.
7. Skip `draft`, `revalidate`, `blocked`, and `done` items.
8. Stop when no ready item remains; report only material drafts/blockers.

## Explicit Revalidation
Use this mode only when the user or active Goal explicitly requests revalidation. It is separate from default autonomous implementation.

This section overrides the Recovery Ladder, Persistent Repair Loop, and `coding-feature-execute` for the selected `revalidate` item.

1. Read the queue through `coding-feature-queue` and select one `revalidate` item.
2. Read its existing `FEATURE.md`, `PROOF.md`, and `proof/run.sh`. Do not change implementation, setup, contracts, proof, fixtures, or queue ownership paths.
3. Capture the unchanged proof with `"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir FEATURE_DIR --timeout-seconds N --note "revalidation reason"`.
4. Proof failure: write the result and reason into that attempt's plain `completion.md`, move the item to `ready`, and stop processing that item.
5. Proof pass: skip the repository gate because revalidation owns no new implementation, then automatically spawn a fresh read-only `coding-feature-evaluator` using the passing attempt.
6. Evaluator `PASS`: preserve its output in `completion.md` and return the item to `done`.
7. Evaluator `FAIL`: preserve its output in `completion.md`, move the item to `ready`, and stop processing that item.
8. Evaluator `NEED_INPUT` or a proof blocker may move the item to `blocked` only when the remaining dependency is genuinely user-owned or external.

Never repair during revalidation. Never call `coding-feature-execute`, consume an item just moved to `ready`, or recursively process another invalidated feature as an effect of the current item. A later normal autonomous run owns any repair.

## Persistent Repair Loop
Use when proof, an executed gate, or evaluator judgment fails:

1. Read the newest failure first.
2. Repair one owning problem with `coding-repair`.
3. Run the narrow check when useful.
4. Capture the complete proof again.
5. After proof `PASS`, initialize that attempt’s plain `completion.md` before gate/evaluation, then keep it current with stage outcomes and material correction or repair context. It is not a receipt and is never parsed for status.
6. Run the useful repository gate or retain the justified skip.
7. Spawn a fresh evaluator after the new passing attempt.
8. Evaluator `FAIL`: repeat with its concrete finding.
9. Evaluator `PASS`: parent marks `done`.
10. Evaluator `NEED_INPUT`: confirm the dependency is genuinely external/user-owned before asking.

Do not calculate progress scores or deterministic non-convergence. The LLM judges whether evidence changed and must change tactic when it did not.

## Green-But-Broken
When observed product behavior fails despite green proof/evaluation:

1. Treat it as proof-system failure.
2. Identify the missed activation, read-back, fake boundary, or scenario.
3. Stop implementation, state the strengthened proof decision, and ask only if a material user-owned choice remains.
4. Demonstrate the missed failure when practical.
5. Repair implementation and rerun the complete lifecycle with a fresh evaluator.

## Subagents
- Bounded support: discovery, diagnosis, implementation assistance, final evaluation.
- The accountable feature parent verifies and integrates support work; support agents may edit the checkout without becoming competing decision owners.
- Final evaluator is always fresh and read-only.
- Concurrent work on other features is allowed in the same checkout. Preserve unrelated changes and do not run competing proof attempts for one feature.

## Terminal Conditions
- Normal queue execution stops when no `ready` item remains.
- Explicit revalidation stops after the selected item's proof/evaluator result updates its status; it never enters repair.
- A genuine user-owned or external dependency stops work only after the Recovery Ladder is exhausted.
- One-line edits, explanations, vague improvement requests, and work without a finish line do not enter autonomous execution.
- Capture cannot recover from hard kill, host crash, or deliberately detached descendants; runners may not detach.

## Handoff
Lead with `Goal complete`, `Done`, or `Needs input`. Report outcome, current feature/queue state, realistic proof, gate or skip reason, evaluator, known gaps, and exact blocker. Omit token counts, task ids, prompts, and exhaustive attempt transcripts unless asked.
