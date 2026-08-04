---
name: coding-feature-queue
description: "Maintain draft, ready, blocked, and done state in docs/features/status.json."
---

# Feature Queue

Purpose: provide a small durable progress index. `FEATURE.md` and `PROOF.md` remain authoritative; the queue never stores behavior, proof details, dependencies, receipts, or progress calculations.

## File
Use `docs/features/status.json` only when the repository has multiple tracked features or explicit autonomous queue work.

```json
{
  "features": [
    {
      "id": "short-feature-id",
      "feature_dir": "docs/features/short-feature-id",
      "priority": 1,
      "status": "draft",
      "notes": ""
    }
  ]
}
```

Allowed fields only:

- `id`: stable short identifier.
- `feature_dir`: safe repository-relative feature directory.
- `priority`: numeric; lower number runs first.
- `status`: `draft`, `ready`, `blocked`, or `done`.
- `notes`: short next-action, completion, or blocker context.

No globs, hashes, change prefixes, dependency graph, evaluator output, evidence state, or phase counters.

## Status
- `draft`: discovery, proof decisions, or executable proof package is incomplete.
- `ready`: contracts are decision-complete, material user-owned questions are resolved, executable `proof/run.sh` exists, and the package owns one coherent observable outcome and one proof boundary.
- `blocked`: safe local recovery is exhausted and one exact user-owned or external dependency remains.
- `done`: the current realistic feature proof passed, a fresh evaluator `PASS` judged the candidate it inspected, and no relevant edit later made that proof or verdict void.

The active Codex task owns transient execution state. Retained attempts and the short note preserve useful history.

## Rules
- Keep contracts authoritative; notes summarize state rather than requirements.
- Keep `feature_dir` repository-relative with no absolute path, `..`, or repository-root prefix.
- App preparation makes every feature in the accepted non-speculative set decision-ready through normal feature-spec and proof authoring.
- Before `ready`, reject a package with multiple independently valuable observable outcomes or independently runnable proof boundaries and split it into separate feature packages. Multiple files or layers alone do not make a feature oversized.
- Mark `ready` only after the size check, feature and proof decisions, and executable proof authoring finish.
- Mark `blocked` only after setup, diagnostics, proof repair, evaluator follow-up, and local recovery are exhausted.
- Mark `done` only after `coding-feature-execute` records current realistic proof `PASS` and fresh evaluator `PASS` for the unchanged final candidate. A relevant edit returns to proof and evaluation; queue state never overrides stale evidence.
- Behavior or proof-strength change to a completed item returns it to `draft` while decisions change, then `ready` when the package is current.
- One accountable parent applies the active feature's transitions. Re-read current state before each narrow write and preserve unrelated entries.

## Next Item
1. Select the lowest-priority-number `ready` item.
2. Work one item and one `FEATURE_DIR` through completion.
3. Ignore `draft`, `blocked`, and `done` during implementation selection.
4. After it reaches `done`, select the next `ready` item.
5. Stop when no ready item remains.

## Validation
- Parse JSON before writing.
- Require unique feature ids, numeric priorities, exactly the five allowed fields, and one of the four statuses.
- Require an existing `feature_dir`; `ready` and `done` require `FEATURE.md`, `PROOF.md`, executable `proof/run.sh`, and one coherent observable outcome with one proof boundary.

## Handoff
Report only meaningful transitions: `<feature-id>: <old> -> <new>; reason; next`.
