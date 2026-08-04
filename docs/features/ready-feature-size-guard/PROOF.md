# Ready Feature Size Guard Proof

## Done
- The actual queue owner rejects oversized packages before `ready`.
- App decomposition and feature specification use the same boundary.
- The queue schema remains unchanged.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/ready-feature-size-guard --timeout-seconds 30 --note "verify oversized packages cannot enter ready"
```

## Scenario: Ready transition owns the size guard
- Producer/activation: pytest reads app decomposition, feature specification, and the queue status owner.
- Consumer: a parent preparing to transition a decision-complete package to `ready`.
- Read-back: each owner requires splitting multiple independently valuable outcomes or independently runnable proof boundaries while permitting one outcome to span files or layers.
- Fake: none.
- Catches: authoring guidance that the queue transition can bypass.

## Scenario: Queue remains lean
- Producer/activation: pytest parses the real queue.
- Consumer: queue readers and autonomous selection.
- Read-back: every item still has exactly `id`, `feature_dir`, `priority`, `status`, and `notes`.
- Fake: none.
- Catches: implementing the guard with new state or metadata.

## Scope
Proves:
- Active owners expose the same pre-ready size boundary.
- Queue schema does not grow.

Does not prove:
- Deterministic semantic sizing by future models.

False-green risks:
- Static policy assertions cannot guarantee future model judgment; final evaluation challenges the current packages semantically.

Evidence method:
- deterministic

Known gaps:
- Live model sizing remains probabilistic.

## Environment
- Repository-local Python and pytest; no network or external mutation.

