# Autonomous Execution

Autonomous work is proof-satisfaction work. The loop exists to finish one feature or issue
honestly, not to keep generating code.

## Runtime State

A Codex Goal is runtime continuation state. It does not replace:

- `FEATURE.md`
- `PROOF.md`
- `docs/features/status.json`
- the primary proof command
- the target repo gate
- `coding-feature-evaluator`

## Execution Loop

1. Select exactly one ready or repairing feature.
2. Preflight `FEATURE.md`, `PROOF.md`, and the executable proof artifact.
3. Mark the item `in_progress` only when the contract is implementable.
4. Freeze contract files after implementation begins.
5. Run the primary proof.
6. Repair the narrowest concrete failure.
7. Rerun the failed check, then lifecycle checks.
8. Use the evaluator before marking done.

Failed proof, gate, or evaluator output is the next work item. It is not a reason to call the
feature done.

When a queue exists, `done` entries should include a `completion` object with:

```json
{
  "primary_proof": "PASS",
  "gate": "PASS",
  "evaluator": "PASS",
  "latest_evidence": "docs/features/<feature>/proof/runs/<timestamp>"
}
```

`scripts/validate_feature_queue` checks this shape.

## Recovery Before NEED_INPUT

Before reporting `NEED_INPUT`, Codex should inspect available local paths:

- proof artifacts and recent run output
- setup docs, package scripts, Makefiles, Docker files, and repo scripts
- browser/app automation and local app state
- MCP/app connectors and local CLIs
- readiness checks and diagnostics

Use `NEED_INPUT` only when the remaining requirement is user-owned or external: credentials,
safe external target, approval, unavailable service, or product decision.

## Green But Broken

If proof, gate, and evaluator pass but observed behavior is still broken, treat that as a
proof-system failure.

Do not keep repairing code against a weak proof. Return to contract repair, strengthen the
proof to catch the observed broken behavior, then restart implementation.
