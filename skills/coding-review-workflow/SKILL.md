---
name: coding-review-workflow
description: "Review coding runs, proof attempts, and user corrections to propose evidence-backed project or harness improvements. Use for deliberate reflection on completed or interrupted work."
---

# App Improvement Review

Purpose: extract useful improvements from actual coding runs, including successful, failed, and interrupted work. Separate discovery, implementation, proof, environment, and reusable harness issues.

Use directly for `coding-workflow` Analyze. Review is read-only: no status changes, acceptance edits, or automatic global rule changes. Authorized improvements can follow in the same task through the appropriate workflow. Recording belongs to `coding-workflow`; this skill reads linked evidence without duplicating dialogue or requiring a second-brain action.

## Inputs
- Target repository and optional feature scope.
- Current `FEATURE.md`, `PROOF.md`, proof runner, implementation.
- Relevant retained attempts: contract/runner copies, `attempt-start.json`, `result.json`, notes, stdout, stderr.
- Final-review verdict and findings, affected regression results, plus relevant setup diagnostics.
- Original requests, corrections, rejected directions, interrupted exchanges, and repair history when available.
- Task/Goal identity, requested and effective route, agent roles, skill versions actually used, and tested candidate/target. Read timing, usage, or model settings when available.
- Repository context: app, architecture, conventions, testing.
- Dialogue and completeness markers linked by the workflow's evidence references; load only records relevant to the selected repository, feature, path, time, or task scope.

If conversation or optional review context is unavailable, say so. Do not reconstruct user intent from code alone.

## Review
1. Load current truth
   - Read repository context and active contracts.
   - Treat current source as authority for what exists; retained copies show what changed.
   - Follow retained run links to relevant original dialogue. Do not bulk-load unrelated interactions or infer complete history from a summary.
   - Treat user-authored interaction messages as historical evidence of intent, corrections, and rejected directions. Treat prior assistant messages as historical proposals and claims, not current truth or proof.
   - Report relevant partial or unavailable history. Current source, accepted contracts, runtime state, and proof remain authoritative.

2. Inspect behavior contract
   - Check whether user outcome, scenarios, errors, constraints, and non-goals were clear enough.
   - Identify misunderstandings that originated in spec discovery rather than implementation.

3. Inspect proof contract
   - Check activation, consumer path, durable/visible read-back, fake boundaries, false-green pressure, environment, gaps, and timeout.
   - Ask whether a central broken implementation could have passed.

4. Inspect attempts
   - Compare failed and passing output, notes, and saved contract/runner copies.
   - Identify repeated failures, tactic changes, setup friction, weak diagnostics, proof changes, reviewer findings, or recovery that worked.
   - Do not require every historical attempt when the latest evidence is sufficient.

5. Inspect implementation and evaluation
   - Check whether the implementation solved the owning problem without unrelated complexity.
   - Assess the final review against the retained candidate and evidence. This reflection does not replace or reissue the workflow's completion verdict.
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
- `preference`: an explicit user preference supported by the conversation; suggest an appropriate instruction only when a reusable preference is established.
- `one-off`: keep local; no reusable policy.

Promote a harness lesson only after recurring evidence. One failure in one repository remains local unless it exposes a direct harness defect.

## Learning Placement
Suggest, but do not write, the destination:

- Product behavior -> `FEATURE.md` or new accepted feature package.
- Architecture/convention -> repository architecture/convention docs.
- Proof gap -> proposed correction to the owning proof or testing guidance. Distinguish independent setup repair under `coding-workflow/references/proof.md` from changes to acceptance or unresolved meaning requiring a user decision. Review itself remains read-only.
- Setup friction -> repository setup scripts/docs/tasks.
- Cross-feature harness gap -> smallest relevant skill, harness doc, script, or regression.
- Stable preference -> smallest appropriate user or project instruction; reference existing dialogue capture instead of copying it.

For a proposed harness correction, name a motivating case and a held-out case that can check behavior without merely matching instruction wording. Measure time to accepted completion, rework, false completion, and capture completeness when evidence supports it. Reject changes that create more ceremony than useful feedback.

## Output
```text
Scope: <repo/features/attempts inspected>
Strong signals:
- <what worked>
Suggestions:
- <classification> | <owner> | <smallest change> | <evidence>
Missing evidence:
- <material only>
Harness candidates:
- <none|recurring lesson>
Validation: <motivating case and held-out case for a harness change>
Next: <one action>
```

## Rules
- Suggestions only during review; no automatic rule promotion.
- Current source beats captured interaction history.
- Passing command != realistic proof.
- Missing evidence is not automatically a defect; explain why it matters.
- Prefer a few high-confidence improvements over a broad roadmap.
- No new feature by default; suggest one only when accepted behavior needs durable ownership.
- Missing dialogue remains explicitly partial. Do not fabricate capture, expose hidden reasoning, or copy sensitive/unrelated conversation into findings.

## Handoff
Lead with the strongest signal and highest-value suggestion. Separate project changes from harness candidates. State unavailable conversation or review context explicitly. Do not include exhaustive run ids or logs.
