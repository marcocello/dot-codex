---
name: coding-feature-queue
description: "Maintain docs/features/status.json as a lightweight machine-readable feature queue for greenfield and brownfield autonomy. Use when creating multiple features, selecting the next feature, marking feature progress, or running coding-autonomous-execute across all features."
metadata:
  short-description: Feature status queue for autonomous runs
---

# Feature Queue

Purpose: provide durable progress for autonomous feature execution without creating a workflow engine. `FEATURE.md` and `PROOF.md` remain the authoritative feature contracts.

## File
Use `docs/features/status.json`.

Do not use the queue as a workflow engine. It is only a progress index that points to authoritative feature directories.

## Schema
```json
{
  "features": [
    {
      "id": "short-feature-id",
      "feature_dir": "docs/features/short-feature-id",
      "proof": "docs/features/short-feature-id/PROOF.md",
      "priority": 1,
      "status": "pending",
      "notes": ""
    }
  ]
}
```

Allowed `status` values:
- `pending`: specified but not started.
- `in_progress`: currently being implemented.
- `failing`: attempted, but proof, gate, or evaluator failed.
- `blocked`: cannot proceed without user input or external state.
- `passing`: primary proof, gate, and evaluator passed.

## Rules
- Keep `FEATURE.md` and `PROOF.md` authoritative; never move behavior or proof details into `status.json`.
- Keep `feature_dir` and `proof` relative to the repo root.
- Keep `priority` numeric; lower numbers run first.
- Update the queue whenever `coding-app-to-features` creates a feature series.
- Update the queue whenever `coding-feature-spec` or `coding-proof-author` materially changes a feature or proof.
- Mark one item `in_progress` at a time during autonomous execution.
- Mark `passing` only after primary proof, gate, and `coding-feature-evaluator` pass.
- Mark `failing` when proof, gate, or evaluator fail but bounded repair can continue.
- Mark `blocked` only when the same blocker repeats or required input is missing.

## Next Item Selection
1. Choose the lowest-priority `failing` item first.
2. Then choose the lowest-priority `pending` item.
3. Ignore `passing` items.
4. Stop when all features are `passing` or all remaining items are `blocked`.

## Handoff
When updating the queue, report:
- selected feature id
- old status -> new status
- proof path
- primary proof command if known
- reason for `failing` or `blocked`
