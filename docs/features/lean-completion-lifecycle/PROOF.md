# Lean Completion Lifecycle Proof

## Done
- Active owners define serial one-feature execution with no batch, parallel feature, or coordinator policy.
- Tracked and autonomous completion requires current realistic proof plus a fresh evaluator `PASS`, with no repository fast-check stage.
- Evaluator findings strengthen proof and drive repair before another fresh evaluator is required.
- Lightweight fixes remain outside the managed proof/evaluator lifecycle.
- App preparation creates the complete lean feature set and routes every decided feature through normal feature-spec and executable proof authoring.
- The queue keeps only four statuses and serial priority selection.
- Meaningful failing and passing proof attempts remain retained.
- Harness policy is stated by its smallest owner rather than requiring repeated lifecycle prose across several files.
- Graphify remains absent from the global harness instruction surface.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/lean-completion-lifecycle --timeout-seconds 60 --note "verify serial proof-evaluator completion lifecycle"
```

## Scenario: Completion is proof plus fresh evaluator PASS
- Producer/activation: pytest reads the global completion invariant, one-feature execution owner, evaluator owner, queue owner, prompt metadata, and handoff contract.
- Consumer: tracked and autonomous feature completion.
- Read-back: assertions require a passing realistic proof followed by a fresh read-only evaluator `PASS`, with evaluator findings routed through proof strengthening, repair, proof rerun, and another fresh evaluation.
- Fake: none.
- Catches: optional evaluation, high-risk-only evaluation, one-shot findings without confirming reevaluation, evaluator queue mutation, or a repository fast-check completion stage.

## Scenario: Autonomous execution is serial
- Producer/activation: pytest reads the autonomous owner, queue owner, app preparation owner, and global routing.
- Consumer: a queue containing several ready features.
- Read-back: assertions require only the lowest-priority ready feature to run through the complete lifecycle before the next is selected.
- Fake: none.
- Catches: batches, compatible-pair selection, parallel feature writers, coordinators, write barriers, worktrees, or branch orchestration.

## Scenario: Queue state remains small
- Producer/activation: pytest parses the real `docs/features/status.json` and reads the queue schema owner.
- Consumer: queue selection and mutation policy.
- Read-back: every item uses only the allowed fields and one of `draft`, `ready`, `blocked`, or `done`; `done` requires proof plus evaluator `PASS`.
- Fake: none.
- Catches: legacy revalidation/dependency state or completion authority stored in queue prose.

## Scenario: App preparation produces the complete lean feature set
- Producer/activation: pytest reads app preparation, feature-spec, proof-author, queue, and their routing prompts.
- Consumer: greenfield or app-level brownfield preparation before implementation.
- Read-back: assertions require concise app architecture/testing context, the complete non-speculative feature list, lean observable feature boundaries, and normal executable proof packages for every decided feature.
- Fake: none.
- Catches: preparing only one runnable feature, speculative backlog, god features, or bypassing normal spec/proof skills.

## Scenario: Proof evidence and evaluator corrections remain durable
- Producer/activation: pytest reads proof lifecycle, feature execution, evaluator, and autonomous repair policy.
- Consumer: initial red, proof repair, evaluator findings, and final completion.
- Read-back: assertions require meaningful red evidence when practical, retained materially distinct failures, evaluator findings preserved in the next attempt note, a final passing proof, and a fresh evaluator `PASS`.
- Fake: none.
- Catches: fixing evaluator prose without executable pressure, weakening proof, treating narrow debugging as official evidence, or losing the correction across context compaction.

## Scenario: Harness validation still checks owned content
- Producer/activation: pytest executes the real gate against a temporary harness repository containing one ignored external skill and a deliberately failing unit test.
- Consumer: dot-codex's own lint and unit-test validation.
- Read-back: the ignored external skill produces no lint finding, while the owned unit failure is still reported even when another owned lint issue exists.
- Fake: temporary repository only; the real gate and Git ignore semantics are used unchanged.
- Catches: scanning managed external copies or suppressing unit tests after lint failures.

## Scope
Proves:
- The active harness exposes the accepted serial proof-evaluator lifecycle.
- Repository fast checks, batching, invalidation, revalidation, completion notes, and pre-implementation evaluator routing are absent from active completion policy.
- Evaluator findings cannot be completion by prose; they must become proof pressure and receive fresh reevaluation.
- App preparation still creates the complete lean feature and proof set.
- Repository-specific Graphify policy is not promoted into the global harness.

Does not prove:
- Deterministic compliance by every future model.
- Product-specific proof quality in a target repository.
- Semantic quality of a future evaluator verdict.

False-green risks:
- Static policy checks cannot guarantee future model adherence. They can demonstrate that active repository-owned instructions no longer expose the rejected lifecycle.
- An evaluator can miss a defect. The harness preserves executable proof and requires a fresh evaluator after every supported correction, but neither is a formal correctness proof.

Evidence method:
- deterministic

Known gaps:
- Live adherence and evaluator judgment remain probabilistic.

## Environment
- Repository-local Python and pytest.
- No network, credentials, external mutation, or evaluator invocation inside the proof runner.
