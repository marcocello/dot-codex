---
name: coding-feature-queue
description: "Maintain readiness, overlap revalidation, blocking, and completion in docs/features/status.json."
---

# Feature Queue

Purpose: provide a durable progress index for feature work. `FEATURE.md` and `PROOF.md` remain authoritative; the queue never stores behavior, proof details, receipts, or progress calculations.

## File
Use `docs/features/status.json` at the repository root.

Create it only when the repository has multiple tracked features, autonomous queue work, or a durable need to distinguish draft/ready/revalidate/blocked/done. Do not create a queue for one isolated lightweight fix.

## Schema
```json
{
  "features": [
    {
      "id": "short-feature-id",
      "feature_dir": "docs/features/short-feature-id",
      "priority": 1,
      "status": "draft",
      "notes": "",
      "files": ["app/change-boundary"],
      "revalidate_on": ["app/proof-dependency"]
    }
  ]
}
```

Allowed fields only:

- `id`: stable short identifier.
- `feature_dir`: repository-relative directory containing contracts and proof.
- `priority`: numeric; lower number runs first.
- `status`: one of the five values below.
- `notes`: short next-action or blocker context.
- `files`: repository-relative prefixes the active feature may change, including implementation, contract, proof, configuration, documentation, and lifecycle output when applicable.
- `revalidate_on`: repository-relative implementation, contract, proof, configuration, or oracle-input prefixes whose change can invalidate this feature's completed proof. A `done` item must declare a non-empty list. Exclude queue state, retained runs, completion notes, and other administrative output unless their content actually participates in the claimed behavior or proof.

No globs, hashes, evaluator fields, phase counters, dependency graphs, or nested evidence state.

## Status
- `draft`: feature discovery, proof decisions, or executable proof package is incomplete.
- `ready`: `FEATURE.md` and `PROOF.md` are decision-complete, material user-owned questions are resolved, and executable `proof/run.sh` exists; implementation may start.
- `revalidate`: previously completed behavior overlaps newer work; rerun its existing proof and fresh evaluation separately before trusting `done`. This is not implementation or repair work.
- `blocked`: safe local recovery is exhausted and one exact user-owned or external dependency remains.
- `done`: current realistic proof passed, useful gate passed or was proportionately skipped, and fresh managed evaluator returned `PASS`.

There is no `in_progress` or `repairing` status. The active Codex task owns transient execution state; retained attempts and notes preserve history.

## Rules
- Keep contracts authoritative. Queue notes summarize state, not requirements.
- Keep all paths repository-relative and safe: no absolute paths, `..`, or repository root prefix.
- Before implementation, declare likely `files` change prefixes and `revalidate_on` proof dependencies, then run `scripts/invalidate_feature_status --feature <id>`.
- Run the invalidator again whenever the active feature’s prefixes broaden.
- Run it once more immediately before managed evaluation to catch overlapping features that became `done` while the active work was running.
- The invalidator compares active `files` only with each `done` feature's `revalidate_on` prefixes. It has no administrative-filename allowlist or denylist, moves only real change-to-dependency overlaps to `revalidate`, and never marks anything complete.
- One accountable parent per active feature applies that feature's queue transitions. Other feature parents may update the same queue concurrently, so re-read current state before a narrow write and preserve unrelated entries. Evaluator remains read-only.
- Mark `ready` only after both question/challenge/decision rounds and executable proof authoring finish; no separate contract approval is required.
- Mark `blocked` only after available setup, diagnostics, tools, proof repair, and local recovery have been tried.
- Mark `done` only after `coding-feature-execute` receives evaluator `PASS` for the current passing attempt.
- On resumed `done` work, rerun final proof before relying on completion. Do not calculate source freshness.
- Behavior or proof-strength change to a `done` item returns it to `draft` while decisions are revised, then `ready` when the updated package is decision-complete.
- A new feature whose `files` overlap an old completed feature's `revalidate_on` prefixes should add the old item to the separate revalidation backlog before implementation, not place it in the normal build loop.

## Next Item Selection
1. Select the lowest-priority-number `ready` item.
2. Work one item and one `FEATURE_DIR` at a time.
3. Ignore `draft`, `revalidate`, `blocked`, and `done` for autonomous implementation.
4. After one item reaches `done`, select the next `ready` item.
5. Stop when no ready item remains; report drafts and blockers only when they affect next action.

## Explicit Revalidation
1. Enter this mode only when revalidation is explicitly requested; default autonomous implementation never selects it.
2. Select the lowest-priority-number `revalidate` item and keep the pass bounded to that activity.
3. Rerun the existing proof through `proof_run_capture` without changing implementation, setup, `FEATURE.md`, `PROOF.md`, or `proof/run.sh`.
4. Proof `PASS`: run a fresh read-only evaluator. Evaluator `PASS` returns the item to `done`.
5. Proof failure or evaluator `FAIL`: move the item to `ready` for a later normal repair lifecycle.
6. A genuinely external or user-owned proof blocker may move it to `blocked` with the exact reason.
7. Do not repair, consume the newly `ready` item, or recursively select another invalidated feature during the revalidation pass.

## Validation
- Parse JSON before writing.
- Require unique feature ids.
- Require exactly one existing `feature_dir` for the active item.
- Require `files` and `revalidate_on` lists with safe repository-relative prefixes; a `done` item may not have an empty `revalidate_on` list.
- Use `scripts/invalidate_feature_status` for overlap effects; do not reproduce its path logic in prompts or queue prose.

## Handoff
Report only meaningful transitions:

```text
<feature-id>: <old status> -> <new status>
Reason: <one line>
Next: <one action or none>
```

Do not dump the full queue unless asked.
