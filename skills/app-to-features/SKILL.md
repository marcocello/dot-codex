---
name: app-to-features
description: Turn an overall app description into a sharper app brief, bootstrap repo-level docs, and create a series of features through discovery-first feature specs. Use for greenfield work when the user has an app idea and wants Codex to initialize the project before returning to normal single-feature execution. Use the `research` skill when assumptions need external evidence.
metadata:
  short-description: Greenfield app idea to feature series
---

# App To Features

Purpose: take an overall app description, improve it into a sharper app brief, bootstrap repo-level
docs, and create a series of features before returning to the normal single-`FEATURE_DIR`
workflow.

## Inputs
- overall app description
- optional constraints, stack preferences, target users, or scope cuts

If key details are missing, make reasonable assumptions and state them briefly instead of blocking.
If important product, domain, or technical assumptions are uncertain, use `research` before locking
them into repo docs.

## Workflow
1) Improve the app brief
   - Rewrite the raw idea into a concise, sharper app description.
   - Focus on target user, core outcome, product shape, and obvious scope cuts.
   - Create or update `docs/APP.md`.

2) Bootstrap repo-level architecture context
   - Create or update `docs/ARCHITECTURE.md` only when the architecture is explicit, requested, or
     stable enough to be treated as authoritative guidance.
   - If useful, also create or update `docs/CONVENTIONS.md` and `docs/TESTING.md`.

3) Research before guessing when needed
   - Use `research` for framework choices, domain uncertainty, external APIs, or comparable product
     expectations that would otherwise become speculative assumptions.
   - Fold durable findings back into `docs/APP.md` or repo docs instead of leaving them as loose
     notes.

4) Derive a small feature series
   - Split the app into 3 to 7 implementable features.
   - Order features from foundation to highest user-visible value.
   - Keep each feature independently specifiable and testable.

5) Materialize features through `feature`
   - This skill is the explicit exception to the single FEATURE_DIR rule during greenfield
     bootstrap.
   - For each selected feature, use the `feature` skill to create
     `docs/features/<slug>/FEATURE.md`.
   - After bootstrap completes, return to the normal single-`FEATURE_DIR` workflow.

6) Keep the series pragmatic
   - Prefer a shippable first slice over exhaustive roadmap coverage.
   - Merge overlapping ideas instead of producing thin or redundant features.
   - Leave clearly out-of-scope ideas out of the first series.

7) Handoff cleanly
   - Return the improved app brief summary.
   - List the generated feature directories in recommended implementation order.

## Rules
- Do not add an in-repo orchestration layer.
- Do not create a planning daemon, router, or local workflow engine.
- Reuse the repo's `feature` skill for final feature specs rather than inventing a new spec
  format.
- Keep outputs concise and implementation-agnostic.
