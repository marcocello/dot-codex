# Proof Scope

Proof Scope describes what a proof can honestly prove.

It exists because executable feedback can create false confidence. A passing command is useful only when the proof check matches the behavior being claimed.

The bundle file is still named `oracle-scope.md` for compatibility with existing scripts and evidence validation. In human-facing docs, read that file as the proof scope.

## Required Shape

Every non-trivial `PROOF.md` should include:

```text
Proves:
- <specific behavior, state transition, side effect, or invariant the proof observes>

Does not prove:
- <important live, scale, timing, provider, UI, concurrency, or edge-case path outside this proof>

False-green risks:
- <how a shallow, proxy, mocked, stale, or incomplete implementation could still pass>

Evidence strength:
- deterministic | probabilistic | live gap | manual gap
```

## Evidence Strength

- `deterministic`: repeatable local or live check with clear pass/fail evidence.
- `probabilistic`: repeated or sampled check where the signal is useful but not absolute.
- `live gap`: realistic local proof exists, but live provider/user/environment read-back remains unavailable.
- `manual gap`: proof depends on a user-owned product decision, credential, approval, or external state.

## Green But Weak

If the primary proof passes but the proof scope is obviously too narrow for the behavior being claimed, the work is green but weak. Route it to proof repair before marking done.

Examples:

- A file-exists check stands in for generated report correctness.
- A mocked service return stands in for a real route, worker, or provider boundary.
- Final assistant text stands in for persisted state, provider read-back, or rendered UI.
- A unit test calls an inner helper while the product behavior is triggered by a webhook, queue row, browser flow, CLI, or scheduler.

## Evaluator Rule

The evaluator judges whether the proof and proof scope are sufficient. It must not replace missing executable evidence with model confidence.
