# Feature Proof Isolation Proof

## Done
- Proof authoring prohibits complete cross-feature proof reuse.
- Prerequisite setup and the smallest integration canary remain allowed.
- Current feature runners do not invoke complete feature proof runners.
- The selection oracle rejects a complete external pytest module, accepts an owned module, and accepts an explicit external test-node canary.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/feature-proof-isolation --timeout-seconds 30 --note "verify feature-local executable proof"
```

## Scenario: Active proof stays feature-local
- Producer/activation: pytest reads the proof-author invariant and every current feature runner.
- Consumer: a feature proof with completed prerequisites.
- Read-back: policy permits prerequisite setup and the smallest integration canary but forbids importing or executing another feature's complete proof; the oracle rejects a representative complete external pytest module, accepts an explicit node canary, and verifies current shared gate consumers name only their owned test nodes.
- Fake: none.
- Catches: stale unrelated feature proof runners or whole external test modules extending or blocking the active feature.

## Scope
Proves:
- The current proof-author policy and feature runners preserve complete-proof isolation.

Does not prove:
- That every selected integration canary is minimal.
- Future model compliance.

False-green risks:
- Ownership of arbitrary future shared test modules remains semantic; the executable oracle pressures the known whole-module form and evaluator review judges new selections.

Evidence method:
- deterministic

Known gaps:
- Semantic canary size remains evaluator judgment.

## Environment
- Repository-local Python and pytest; no network or external mutation.
