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
      "status": "draft",
      "notes": ""
    }
  ]
}
```

Allowed `status` values:
- `draft`: feature/proof authoring is incomplete, under review, or being repaired.
  Autonomous execution must not select this item.
- `ready`: `FEATURE.md`, `PROOF.md`, an executable proof artifact, and contract review
  are ready for implementation.
- `in_progress`: currently being implemented.
- `repairing`: implementation was attempted, but proof, gate, or evaluator failed and
  bounded repair can continue.
- `blocked`: cannot proceed without user input or external state.
- `done`: primary proof, gate, and evaluator passed.

## Rules
- Keep `FEATURE.md` and `PROOF.md` authoritative; never move behavior or proof details into `status.json`.
- Keep `feature_dir` and `proof` relative to the repo root.
- Keep `priority` numeric; lower numbers run first.
- Update the queue whenever `coding-app-to-features` creates a feature series.
- Update the queue whenever `coding-feature-spec` or `coding-proof-author` materially changes a feature or proof.
- Mark `draft` while feature/proof authoring is incomplete or contract review is failing
  but repair can continue.
- Mark `ready` only after feature/proof authoring has produced `FEATURE.md`, `PROOF.md`,
  an executable proof artifact, and a passing contract review, or after a minor non-behavior
  edit to an already-ready item.
- Mark one item `in_progress` at a time during autonomous execution.
- Mark `repairing` when proof, gate, or evaluator fail but bounded repair can continue.
- Mark `blocked` when required input, unavailable external state, unreproducible behavior,
  or a repeated blocker prevents progress.
- Mark `done` only after primary proof, gate, and `coding-feature-evaluator` pass.
- If a `done` item's `FEATURE.md`, `PROOF.md`, or executable proof artifacts change in a
  behaviorally meaningful way, reset it to `draft` while authoring, then `ready` after the
  updated contract package passes review. Preserve `done` only for clearly non-behavioral
  metadata, typo, or formatting edits.

## Next Item Selection
1. Choose the lowest-priority `repairing` item first.
2. Then choose the lowest-priority `ready` item.
3. Ignore `draft`, `blocked`, and `done` items.
4. Stop when all executable items are `done` or all remaining items are `draft` or
   `blocked`.

## Handoff
When updating the queue, report:
- selected feature id
- old status -> new status
- proof path
- primary proof command if known
- reason for `draft`, `repairing`, or `blocked`
