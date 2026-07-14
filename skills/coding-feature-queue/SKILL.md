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
- `needs_input`: active recovery has been exhausted and the remaining prerequisite is
  user-owned or external.
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
  an executable proof artifact, a primary proof command wrapped with `scripts/proof_run_capture`,
  and a passing contract review, or after a minor non-behavior edit to an already-ready item.
- Mark one item `in_progress` at a time during autonomous execution.
- Mark `repairing` when proof, gate, or evaluator fail but bounded repair can continue.
- Mark `needs_input` only after autonomous recovery attempts have inspected available
  proof, logs, setup commands, diagnostics, and repair paths.
- Use `needs_input` for credentials, safe external target, approval, or product decision
  requirements that cannot be satisfied honestly from local tools.
- Mark `done` only after primary proof, gate, and `coding-feature-evaluator` pass.
- For `done` items, record only `completion.latest_evidence`, pointing to the latest serious proof evidence bundle with command, result, notes, run metadata, proof scope, contract snapshots, declared source identity, `gate.json`, and `evaluation.json`. Proof, gate, and evaluator status are derived from those artifacts, not mirrored into queue fields. Repeated repair evidence must include `attempts.json`. Validate the active item with `scripts/validate_feature_queue --feature <id>` when available; legacy or prose-only evidence cannot authorize that item's `done` state. Use `--all` only for a strict whole-queue audit.
- If a `done` item's `FEATURE.md`, `PROOF.md`, or executable proof artifacts change in a
  behaviorally meaningful way, reset it to `draft` while authoring, then `ready` after the
  updated contract package passes review. Preserve `done` only for clearly non-behavioral
  metadata, typo, or formatting edits.

## Next Item Selection
1. Choose the lowest-priority `repairing` item first.
2. Then choose the lowest-priority `ready` item.
3. Ignore `draft`, `needs_input`, and `done` items.
4. Stop when all executable items are `done` or all remaining items are `draft` or
   `needs_input`.

## Handoff
When updating the queue, report only what changes the next action:
- `<feature-id>: <old status> -> <new status>`
- one-line reason for `draft`, `repairing`, or `needs_input`
- primary proof command only when it is the next command to run

Do not dump the whole queue, proof paths, or priority list unless the user asks.
