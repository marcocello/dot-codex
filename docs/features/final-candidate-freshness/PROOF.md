# Final-Candidate Freshness Proof

## Done
- The tracked/autonomous lifecycle names the final candidate and checks it before evaluation and completion.
- A relevant edit after proof invalidates proof; a relevant edit after evaluator `PASS` invalidates both proof and verdict.
- The recovery path is always complete proof followed by a fresh evaluator.
- Autonomous execution still selects the next `ready` item after completion and stops only when no `ready` item remains.
- Bookkeeping does not trigger an impossible rerun loop.
- No durable freshness graph or orchestration state is introduced.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/final-candidate-freshness --timeout-seconds 30 --note "verify final-candidate freshness policy"
```

## Scenario: Proof and evaluator apply to one unchanged candidate
- Producer/activation: pytest reads the global completion kernel, feature execution, evaluator, queue, and autonomous execution instructions.
- Consumer: the parent preparing evaluation and the final `ready` to `done` transition.
- Read-back: a relevant implementation, contract, proof, fixture, runtime, configuration, or call-path edit after proof requires a complete proof rerun; an edit after evaluator `PASS` also requires another fresh evaluator.
- Fake: none.
- Catches: completing from evidence that predates the final implementation.

## Scenario: Lean serial enforcement
- Producer/activation: pytest reads the owning lifecycle and actual queue schema.
- Consumer: a single-user serial feature run.
- Read-back: attempt creation and the narrow completion bookkeeping are excluded from candidate changes; after a fresh candidate reaches `done`, autonomous execution selects the next `ready` item until none remains; policy explicitly rejects hashes, manifests, receipts, dependency graphs, commit pins, branches, worktrees, extra queue fields, and parallel coordination.
- Fake: none.
- Catches: a freshness system more complicated than the failure it prevents, or freshness wording that stops serial queue draining after one feature.

## Scope
Proves:
- The authoritative instruction path cannot honestly complete a stale candidate.
- Freshness recovery preserves the existing proof-then-evaluator order.
- Freshness validation preserves autonomous queue continuation.

Does not prove:
- Cryptographic detection of a dishonest or invisible writer.
- That a language model will classify every file's relevance perfectly.

False-green risks:
- Relevance is a semantic judgment. The conservative rule is to include uncertain behavior-affecting files and rerun.

Evidence method:
- deterministic

Known gaps:
- Enforcement is procedural, which is deliberate for a single accountable parent and serial checkout.

## Environment
- Repository-local Python and pytest; no network, credentials, or external mutation.
