# Bounded Consolidated Evaluation Proof

## Done
- Evaluation uses a transient active-feature surface rather than the accumulated dirty diff.
- One evaluator performs an ordered evidence-first pass and implementation-second pass.
- The evidence pass reads the accepted goal, contracts, retained result, and actual output before implementation files or parent implementation summaries can bias its claim map.
- The implementation pass traces the active surface and relevant call paths against that evidence map.
- One verdict contains all material findings from the completed bounded review.
- No second agent, durable intermediate report, or orchestration state is introduced.
- Autonomous execution still drains every ready feature serially.
- Relevant outside-surface call paths and proof-backed fresh reevaluation remain required for assurance.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/bounded-consolidated-evaluation --timeout-seconds 30 --note "verify bounded consolidated evaluation"
```

## Scenario: Ordered evidence and implementation challenge
- Producer/activation: pytest reads feature execution, evaluator, its agent prompt, and durable harness rationale.
- Consumer: fresh evaluation after a passing feature proof in an accumulated same-checkout run.
- Read-back: evaluator instructions require an evidence pass before implementation inspection, prohibit parent implementation summaries from substituting for evidence, then require an implementation pass that traces the changed surface and relevant call paths against the evidence-pass claim map.
- Fake: none.
- Catches: implementation-first review that rationalizes a green result without first challenging what the retained runtime evidence proves.

## Scenario: One bounded comprehensive verdict
- Producer/activation: pytest reads feature execution, evaluator, its agent prompt, and durable harness rationale.
- Consumer: completion of both ordered reasoning passes.
- Read-back: policy completes review after the first blocker, returns all material findings while excluding preferences, and preserves proof-backed repair plus fresh reevaluation.
- Fake: none.
- Catches: repeated one-finding evaluator cycles.

## Scenario: Transient scope does not become orchestration state
- Producer/activation: pytest reads feature and autonomous execution owners.
- Consumer: the transition between two ready features.
- Read-back: the parent resets transient scope for the next item; instructions and real queue prohibit new fields, intermediate reports, receipts, hashes, commits, branches, worktrees, another agent, and another completion stage; one feature completes before selection continues until no ready item remains.
- Fake: none.
- Catches: durable scope bookkeeping or one-feature-per-run regression.

## Scope
Proves:
- The active evaluator lifecycle is feature-local, evidence-first, implementation-challenging, comprehensive, transient, and still drains the queue.

Does not prove:
- Deterministic evaluator quality or runtime.
- Deterministic context isolation between reasoning passes.
- That every future parent supplies a perfect call-path surface.

False-green risks:
- A parent can omit a relevant call path. The evaluator may follow outside the supplied surface when required by the accepted behavior or architecture.

Evidence method:
- deterministic

Known gaps:
- Live evaluator adherence and judgment remain probabilistic.

## Environment
- Repository-local Python and pytest; no network, credentials, or external mutation.
