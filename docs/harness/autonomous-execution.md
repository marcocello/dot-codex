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
   `PROOF.md` must define a primary proof command that calls `scripts/proof_run_capture`.
3. Mark the item `in_progress` only when the contract is implementable.
4. Freeze contract files after implementation begins.
5. Run the primary proof.
6. Repair the narrowest concrete failure.
7. Rerun the failed check, then lifecycle checks.
8. Use the evaluator before marking done.

Failed proof, gate, or evaluator output is the next work item. It is not a reason to call the
feature done.

## Target Repo Autofix And Suggestions

For another software repo, the autonomous loop provides repo-facing behavior:

- Autofix is the normal repair loop for a concrete failing proof, gate, runtime check, or evaluator result.
- Autosuggestions are proposed next steps from captured evidence when immediate repair is not the right move.
- Auto-improve means turning an accepted suggestion into normal repo work with its own proof lifecycle.

Prefer target-repo autofix over harness changes. Prefer target-repo autosuggestions when the evidence shows a broader improvement but not a single safe code patch. Use harness evolution only when repeated evidence shows the harness itself caused or allowed the failure pattern.

Use `$coding-app-improvement-review` for target-repo suggestions. `scripts/harness_review` can summarize proof bundles first, but suggestions are planning artifacts, not permission to silently broaden scope or skip proof.

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

The referenced `latest_evidence` must be a serious proof bundle created by `scripts/proof_run_capture`. Bare `result.json` evidence is not enough for `done`; repeated repair attempts must include attempt metadata and `attempts.json`.

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
