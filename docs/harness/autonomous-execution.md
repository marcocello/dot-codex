# Autonomous Execution

Owner: `coding-autonomous-execute`.

This layer selects queue work and continues it. Per-feature procedure belongs only to `coding-feature-execute`.

- One ready item per autonomous parent. One accountable parent per active feature. The default build loop ignores `revalidate` items.
- Multiple feature parents and supporting agents may edit the same checkout concurrently. They preserve unrelated work, keep ownership prefixes narrow, and do not run competing proofs for one feature.
- Delegate the whole item to feature execution.
- Continue to next ready item after completion.
- Continue local recovery while safe progress exists.
- Block only on an exact user/external dependency.
- Goal runtime owns continuation. Retained attempts own history.

## Separate Revalidation

Revalidation runs only when explicitly requested. Select one `revalidate` item and rerun its existing captured proof without changing implementation, setup, `FEATURE.md`, `PROOF.md`, or `proof/run.sh`. These lane-specific rules override the normal repair loop for that item.

If proof passes, run a fresh managed evaluator. Evaluator `PASS` returns the feature to `done`. Proof or evaluator failure moves it to `ready`, where a later normal build loop may repair it. Revalidation itself does not repair, run the repository gate, consume newly ready work, or recursively revalidate overlapping features.

On resume:

1. Inspect the newest run directory, not merely the newest `result.json`.
2. `attempt-start.json` without `result.json` is incomplete. Check whether the recorded capture or runner process is still active.
3. Active process: wait or diagnose it; do not start a competing proof.
4. Dead process: retain the incomplete attempt, treat it as interrupted, diagnose available output, and create a new captured attempt.
5. Never fall back to an older PASS while the newer attempt is unresolved.
