---
name: coding-app-improvement-review
description: "Review completed feature evidence and corrections to propose grounded project or harness improvements."
---

# App Improvement Review

Purpose: extract high-confidence improvement suggestions from actual feature history. Keep project-specific fixes, proof improvements, harness lessons, and personal preferences separate.

Read-only. Do not apply suggestions, mutate queue state, rewrite contracts, or persist additional interaction history.

## Inputs
- Target repository and optional feature scope.
- Current `FEATURE.md`, `PROOF.md`, proof runner, implementation.
- Relevant retained attempts: contract/runner copies, `attempt-start.json`, `result.json`, notes, stdout, stderr.
- Plain per-attempt `completion.md` with gate outcome, evaluator output, and material correction or repair context when that stage was reached.
- Gate result or skip reason.
- Evaluator findings when available in the current conversation or supplied material.
- User corrections, rejected directions, or repair history when available.
- Repository context: app, architecture, conventions, testing.
- Optional `interactions/index.json` and only the interaction records relevant to the explicit repository, feature, path, time, or task scope.

If conversation/evaluator context is unavailable, say so. Do not reconstruct user intent from code alone.

## Review
1. Load current truth
   - Read repository context and active contracts.
   - Treat current source as authority for what exists; retained copies show what changed.
   - When `interactions/index.json` exists, establish relevance before loading a record. Do not bulk-load unrelated project interactions.
   - Treat user-authored interaction messages as historical evidence of intent, corrections, and rejected directions. Treat prior assistant messages as historical proposals and claims, not current truth or proof.
   - Report relevant partial or unavailable history. Current source, accepted contracts, runtime state, and proof remain authoritative.

2. Inspect behavior contract
   - Check whether user outcome, scenarios, errors, constraints, and non-goals were clear enough.
   - Identify misunderstandings that originated in spec discovery rather than implementation.

3. Inspect proof contract
   - Check activation, consumer path, durable/visible read-back, fake boundaries, false-green pressure, environment, gaps, and timeout.
   - Ask whether a central broken implementation could have passed.

4. Inspect attempts
   - Compare failed and passing output, notes, saved contracts, runner copies, and `completion.md` when present.
   - Identify repeated failures, tactic changes, setup friction, weak diagnostics, proof changes, or recovery that worked.
   - Do not require every historical attempt when the latest evidence is sufficient.

5. Inspect implementation and evaluation
   - Check whether the implementation solved the owning problem without unrelated complexity.
   - Use evaluator findings as semantic feedback, not a recorded mechanical authority.
   - Distinguish a product defect from proof weakness or harness friction.

6. Inspect user corrections
   - Capture accepted behavior, rejected direction, and why the previous path failed.
   - Prefer correction patterns with reusable value over one-off wording differences.

7. Classify each lesson
   - Use Classification below.
   - Suggest the smallest owner and next action.

## Classification
- `project`: behavior, architecture, implementation, setup, convention, or testing owned by the target repository.
- `proof`: scenario, activation, fake, fixture, readiness, read-back, false-green risk, or known gap owned by one feature/repository.
- `harness`: repeated cross-feature or cross-repository evidence that a reusable skill, harness doc, script, or regression should change.
- `preference`: stable user preference; suggest explicit `second-brain-capture-interactions` only when the user asks to preserve the relevant dialogue.
- `one-off`: keep local; no reusable policy.

Promote a harness lesson only after recurring evidence. One failure in one repository remains local unless it exposes a direct harness defect.

## Learning Placement
Suggest, but do not write, the destination:

- Product behavior -> `FEATURE.md` or new accepted feature package.
- Architecture/convention -> repository architecture/convention docs.
- Proof gap -> owning `PROOF.md`, runner, fixture, readiness check, or testing doc.
- Setup friction -> repository setup scripts/docs/tasks.
- Cross-feature harness gap -> smallest relevant skill, harness doc, script, or regression.
- Stable preference -> explicit `second-brain-capture-interactions` only when the user asks to save the relevant dialogue.

Reject changes that create more ceremony than useful feedback.

## Output
```text
Review: PASS|SUGGESTIONS|NEED_INPUT
Scope: <repo/features/attempts inspected>
Strong signals:
- <what worked>
Suggestions:
- <classification> | <owner> | <smallest change> | <evidence>
Missing evidence:
- <material only>
Harness candidates:
- <none|recurring lesson>
Next: <one action>
```

## Rules
- Suggestions only; no auto-apply.
- Current source beats captured interaction history.
- Passing command != realistic proof.
- Missing evidence is not automatically a defect; explain why it matters.
- Prefer a few high-confidence improvements over a broad roadmap.
- No new feature by default; suggest one only when accepted behavior needs durable ownership.
- No evaluator receipt, progress score, or evidence schema recommendation unless the user changes the threat model.

## Handoff
Lead with the strongest signal and highest-value suggestion. Separate project changes from harness candidates. State unavailable conversation/evaluator context explicitly. Do not include exhaustive run ids or logs.
