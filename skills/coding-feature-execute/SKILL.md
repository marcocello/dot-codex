---
name: coding-feature-execute
description: "Implement one decision-ready feature through proportional assurance, realistic proof, fresh final review, repair, and truthful completion."
---

# Feature Execute

Deliver one accepted material feature. One accountable parent owns contracts, implementation, proof, review follow-up, queue transition, and completion while invoking separate skills for their focused responsibilities.

## Entry

Require one `FEATURE_DIR` with decision-complete `FEATURE.md`, `PROOF.md`, executable `proof/run.sh`, and a `ready` item when a feature queue exists. Enter only when the user has explicitly authorized implementation.

If expected behavior or a material product choice remains unclear, return to `coding-product-partner`. If evidence is proxy-only or decision-incomplete, return to `coding-proof-author`. A clear isolated defect that does not need a material feature contract belongs to `coding-repair` rather than this lifecycle.

## Assurance

Classify the feature at the implementation boundary:

- `standard`: material new or changed product behavior; requires realistic executable proof and fresh final review;
- `sensitive`: standard assurance plus fresh preflight before red evidence because the change affects data or migration semantics, authorization or security, destructive or paid external effects, durable cross-component ownership, or has a material proof-target ambiguity.

`focused` work does not enter feature execution; standalone `coding-repair` owns it. Repair inside a standard or sensitive feature inherits the active assurance and returns here.

Explicit user, repository, or accepted-contract sensitivity is the minimum floor. Never downgrade it. Execution-time discovery may escalate standard work to sensitive before implementation. On resume, reclassify from current contracts and repository evidence, preserve the explicit floor, and resolve any incomplete proof attempt before continuing.

Autonomous execution is a continuation mode, not an assurance tier. `coding-autonomous-execute` applies this classification separately to each selected feature.

## Preflight

For sensitive work only, before red evidence or implementation, start one fresh separate read-only `coding-feature-review` invocation with `mode: preflight`.

Provide verbatim goal and corrections, current feature/proof contracts, the named consumption target, and relevant repository paths as discovery entry points. Do not provide a candidate implementation or parent rationale as evidence.

- `CLEAR`: continue.
- `FINDINGS`: repair supported contract or proof defects once; reject unsupported scope expansion with evidence; do not repeat preflight as an approval gate.
- `NEED_INPUT`: block before red evidence and implementation, update the queue when present, and ask the exact user-owned question.

Standard work skips preflight and proceeds directly to red evidence.

## Establish Red Evidence

Capture the decision-complete proof failing for the intended reason before substantial implementation when safe and meaningful. A passing attempt means the behavior may already exist or the proof may be weak. If useful red is impossible, retain the exact reason in the first attempt note.

## Implement And Repair

Use the owning stack/domain skill and make the smallest coherent change satisfying `FEATURE.md`. Reuse existing ownership boundaries and add lower-level tests only when they reduce a concrete risk.

Use `coding-repair` for the latest implementation, setup, proof, or review failure. Run narrow diagnostics while repairing, then return to the full feature proof. The repair inherits standard or sensitive assurance; it cannot reset the feature to focused.

If accepted behavior or proof meaning is wrong, stop coding against it, explain the consequence, repair the contract within the user goal, strengthen proof, demonstrate the missed failure when practical, and rerun the complete proof. Ask only for a new material user-owned choice.

## Capture Proof

Run:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir FEATURE_DIR --timeout-seconds N --note "reason"
```

Inspect the new `result.json` and retained output. Keep meaningful red, materially distinct failures, review-driven strengthened-proof failures when practical, and the final passing attempt.

Compare the proof environment with the named consumption target. Source proof is intermediate when the user consumes an existing local or deployed runtime. Continue safe local rebuild, restart, readiness, and exact-runtime verification. If an approval or external dependency remains after recovery, mark the item blocked with the exact action.

## Final Review

After target-valid realistic proof passes, confirm no relevant candidate edit occurred after the attempt. Then start a fresh separate read-only `coding-feature-review` invocation with `mode: final`.

Provide verbatim goal and corrections, current contracts, latest passing attempt, named target, and the transient active-feature surface as a discovery entry point. Do not substitute an implementation summary or accumulated dirty diff for evidence.

- `PASS`: continue to completion.
- `FINDINGS`: preserve the finding in the next attempt note, strengthen proof when practical, repair through `coding-repair`, rerun the complete proof, and request another fresh final review.
- `NEED_INPUT`: stop only for an exact user-owned decision or external dependency that safe local recovery cannot resolve.

## Completion

The final candidate includes implementation, contracts, proof runner and fixtures, relevant configuration, runtime, and call paths. Any relevant edit after proof makes that evidence stale; any relevant edit after final review also voids the verdict. Rerun the complete proof and obtain a fresh final `PASS`.

Mark the queue item `done` only when target-valid realistic proof and fresh final review `PASS` apply to the unchanged candidate. Re-read the queue and preserve unrelated entries.

Observed broken behavior after green proof is proof-system failure. Strengthen the missed activation, state, read-back, consumer, fake, or runtime boundary; demonstrate the miss when practical; repair; rerun; and obtain a fresh final review.

## Handoff

Report outcome, changed surface, realistic proof, final review verdict, and one runtime state: `active runtime proven`, `source proven; activation required`, or `not applicable`. Include known gaps and exact blockers; never report source-only evidence as completed work for a named active-runtime target.
