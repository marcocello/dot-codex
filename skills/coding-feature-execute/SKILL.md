---
name: coding-feature-execute
description: "Implement one decision-ready feature through realistic proof, fresh evaluation, and queue completion."
---

# Feature Execute

Purpose: deliver one accepted feature through realistic executable proof and fresh semantic evaluation. One accountable parent owns decisions, implementation, proof repair, evaluator follow-up, queue transition, and completion.

## Entry
Require one `FEATURE_DIR` containing:

- decision-complete `FEATURE.md`;
- decision-complete `PROOF.md`;
- executable `proof/run.sh`;
- `ready` queue item when `docs/features/status.json` exists.

Contract readiness alone is not implementation authorization. Enter only when the original or a later separate explicit request asks to build, implement, or execute the product behavior.

If behavior is vague or a material choice remains, return to `coding-feature-spec`. If proof is prose-only, proxy-only, gameable, or decision-incomplete, return to `coding-proof-author`.

## Workflow
1. Load current authority
   - Read `FEATURE.md`, `PROOF.md`, `proof/run.sh`, the queue item, required domain skills, and only relevant current sections of app, architecture, conventions, and testing docs.
   - Preserve unrelated dirty-tree work and do not load superseded history unless the active feature owns its migration.

2. Confirm ownership and environment
   - Work on one feature and one `FEATURE_DIR` only. The parent owns contracts, implementation, queue state, official proof, evaluation, and completion.
   - Maintain a transient active-feature surface in parent context: files changed for this feature plus directly relevant call paths. Do not persist it as queue fields, intermediate reports, receipts, hashes, commits, branches, or worktrees, and do not turn it into another agent or another completion stage.
   - Reuse repository-native runtimes and tasks. Use `coding-prepare-environment` only for missing dependencies, services, local configuration, or runtime readiness.
   - On resume, inspect the newest run directory and resolve an incomplete attempt before starting another.

3. Establish red evidence
   - Before substantial implementation, capture the decision-complete proof failing for the intended reason when safe and meaningful.
   - If it passes, determine whether the behavior already exists or the proof is weak. An older `PASS` is not red evidence.
   - If useful red cannot be produced, preserve the exact reason in the first implementation attempt note.

4. Implement
   - Use the owning stack/domain skill and make the smallest coherent change satisfying `FEATURE.md`.
   - Reuse existing paths and abstractions; fix semantic behavior at its durable decision boundary.
   - Add lower-level tests only when they reduce risk or localize a concrete defect.

5. Capture proof
   - Run `"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir FEATURE_DIR --timeout-seconds N --note "reason"` from the target repository.
   - Read the new `result.json` and relevant output.
   - Retain meaningful red, materially distinct failures, evaluator-driven strengthened-proof failures when practical, and the final passing attempt. Narrow debugging checks are not official attempts.

6. Repair proof failures
   - Use `coding-repair` for the latest concrete failure.
   - Run the narrow failing check while repairing, then capture the complete feature proof when a materially different failure or final pass is expected.
   - Same failure twice: change tactic or widen only the owning inspection boundary.
   - If behavior or proof meaning is wrong, use Contract Repair below before continuing.

7. Run fresh evaluator
   - After the current proof passes, start a fresh read-only `coding-feature-evaluator` with isolated context.
   - Before starting the evaluator, confirm that the final candidate has no relevant edit after the passing attempt. If it changed, that proof is stale: rerun the complete official proof before starting a fresh evaluator.
   - Require one evidence-first, implementation-second review by the same evaluator, with no intermediate report or second evaluation stage.
   - Provide the original goal and material corrections, accepted feature and proof contracts, latest passing attempt, paths in the transient active-feature surface, and only relevant current app/architecture context. Do not send parent implementation summaries as evaluation evidence and do not substitute the checkout's accumulated dirty diff for the feature surface. The evaluator opens implementation paths only after its evidence pass.
   - Wait for `PASS`, `FINDINGS`, or `NEED_INPUT`. The evaluator never edits or mutates queue state.

8. Handle evaluator result
   - `PASS`: continue to queue completion.
   - `FINDINGS`: preserve the material finding in the next proof attempt note. If it identifies contract mismatch or a central false-green path, strengthen proof and demonstrate the missed failure when practical, repair the owning behavior, rerun the complete proof, and invoke another fresh evaluator.
   - Reject evaluator scope expansion or unsupported preferences with a concise evidence-based reason, but still invoke another fresh evaluator because completion requires `PASS`.
   - `NEED_INPUT`: ask only when the evaluator identifies an exact user-owned or external dependency that local recovery cannot resolve.
   - Repeat until a fresh evaluator returns `PASS`.

9. Finalize queue
   - Before marking the item `done`, confirm again that the final candidate has no relevant edit after the proof or evaluator `PASS`.
   - A relevant edit after evaluator `PASS` makes both the proof and verdict stale. Rerun the complete official proof, then obtain another fresh evaluator `PASS`.
   - The parent marks the item `done` only after the current realistic proof passes and a fresh evaluator returns `PASS` for that unchanged proof and implementation.
   - Re-read the queue before the narrow update and preserve unrelated entries.

## Final Candidate Freshness
The final candidate is the implementation, contracts, proof runner and fixtures, and relevant runtime, configuration, and call paths that produced the latest passing official proof. Relevant edits include changes to any of those surfaces. When relevance is uncertain, include the file and rerun rather than assuming it cannot affect behavior or evidence.

Freshness is a serial parent judgment, not another artifact or stage. Retained attempt generation and the narrow queue transition to `done` are bookkeeping, not candidate changes. Do not add hashes, manifests, receipts, dependency graphs, commit pins, branches, worktrees, or queue fields to enforce it.

## Contract Repair
When accepted behavior or proof meaning is wrong or incomplete after implementation begins:

1. Stop coding against the wrong contract.
2. Explain the defect and its behavior/proof consequence.
3. State the revised decision and continue when it remains within the user goal; ask only for a material unresolved user-owned choice.
4. Strengthen proof and demonstrate the missed failure when practical.
5. Rerun the complete official proof with a note explaining the change and why scope was not weakened.

Mechanical runner, fixture, or setup repairs with unchanged proof meaning need an attempt note and full rerun, not another product discussion.

## Green-But-Broken
Observed failure after green proof is proof-system failure. Identify the missed activation, read-back, fake boundary, or scenario; strengthen proof; demonstrate the missed failure when practical; repair; rerun the complete proof; and obtain a fresh evaluator `PASS`.

## Handoff
Report outcome, changed surface, realistic proof, final evaluator verdict, known gaps, and blockers. Keep internal prompts, exhaustive logs, and complete file lists out unless audit/debug is requested.
