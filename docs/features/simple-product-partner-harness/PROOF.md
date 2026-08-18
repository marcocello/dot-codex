# Simple Product Partner Harness Proof

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/simple-product-partner-harness --timeout-seconds 60 --note "verify compact ownership and truthful runtime completion"
```

## Scenarios

1. Compact authority: pytest checks that `AGENTS.md` stays a small router and does not duplicate shaping or reviewer procedures owned elsewhere.
2. Seven pillars: pytest checks the README and design document expose the same distilled product-partner model without a larger pillar inventory.
3. Existing-state read-back: pytest checks proof authoring requires relevant pre-change state and save/reopen/remount read-back rather than trusting a successful write.
4. Runtime truth: pytest checks proof, execution, evaluation, queue completion, autonomous continuation, durable design, and handoff distinguish isolated source proof from validation of the exact active runtime. When an active runtime is the named target, source proof remains intermediate and cannot produce `done`; retained source-only completion authority makes the scenario fail.
5. Activation recovery: pytest checks safe local activation continues autonomously, while approval-gated deployment or an exhausted external dependency produces `blocked` with the exact required action rather than source-only completion.
6. Compatibility: existing adaptive shaping, preflight, completion, freshness, greenfield, and gate-policy tests remain green.

## Scope

Proves:
- The active instruction surface encodes compact ownership, the seven pillars, existing-state proof pressure, and completion against the accepted consumption target.

Does not prove:
- Deterministic compliance by every future model.
- Product-specific proof quality or deployment correctness in another repository.

False-green risks:
- Static text checks can prove active policy ownership but not future judgment quality.

Evidence method:
- deterministic

Known gaps:
- Live behavior continues to depend on model judgment and project-specific proof.

## Environment

- Repository-local Python and pytest; no network, credentials, deployment, or external mutation.
