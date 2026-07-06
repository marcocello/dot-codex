---
name: coding-app-to-features
description: "Turn an overall app description into a sharper app brief, bootstrap repo-level docs, create a series of features, executable proof packages, and the feature queue. Use for greenfield work when the user has an app idea and wants Codex to initialize the project before returning to feature execution. Use the `research` skill when assumptions need external evidence."
metadata:
  short-description: Greenfield app idea to feature series
---

# App To Features

Purpose: take an overall app description, improve it into a sharper app brief, bootstrap repo-level docs, and create a series of features with executable proof packages before returning to the normal single-`FEATURE_DIR` workflow.

## Inputs
- overall app description
- optional constraints, stack preferences, target users, or scope cuts

If key details are missing, make reasonable assumptions and state them briefly instead of blocking. If important product, domain, or technical assumptions are uncertain, use `research` before locking them into repo docs.

## Workflow
1) Initialize the software project baseline
   - For greenfield software projects, initialize a Git repository with `git init` when the current project directory is not already inside a Git worktree.
   - Do not overwrite existing Git history or reinitialize a repository that already has `.git`.
   - Use `coding-prepare-environment` to create or update `.vscode/tasks.json` for the standard backend/frontend/fullstack local run workflow.

2) Improve the app brief
   - Rewrite the raw idea into a concise, sharper app description.
   - Focus on target user, core outcome, product shape, and obvious scope cuts.
   - Create or update `docs/APP.md`.

3) Bootstrap repo-level architecture context
   - Create or update `docs/ARCHITECTURE.md` only when the architecture is explicit, requested, stable enough to be treated as authoritative guidance, or covered by the default greenfield architecture below.
   - Default greenfield architecture: when a new app has no explicit architecture, make `docs/ARCHITECTURE.md` authoritative with backend APIs, a React frontend, and frontend communication with the backend through APIs.
   - Do not define the application folder tree in this skill. Architecture docs may name the selected stack and boundaries, but stack/domain skills own concrete directories and bootstrap structure.
   - For backend framework, service layering, API implementation details, and backend tree structure, delegate to the `coding-python-backend` skill.
   - For frontend starter, component system, UI baseline choices, and frontend tree structure, delegate to the `coding-frontend` skill.
   - For WordPress plugin, theme, full-site, or Bedrock-style app structure, delegate to the `coding-wordpress` skill.
   - If useful, also create or update `docs/CONVENTIONS.md` and `docs/TESTING.md`.

4) Research before guessing when needed
   - Use `research` for framework choices, domain uncertainty, external APIs, or comparable product expectations that would otherwise become speculative assumptions.
   - Fold durable findings back into `docs/APP.md` or repo docs instead of leaving them as loose notes.

5) Derive a small feature series
   - Split the app into 3 to 7 implementable features.
   - Order features from foundation to highest user-visible value.
   - Keep each feature independently specifiable and provable.
   - For greenfield apps with no user-specified implementation order, make the first generated features technical foundation features based on the selected stack. For the default React/API architecture, use this order:
     1. `Build API layer` - use the `coding-python-backend` skill for backend framework and API implementation specifics.
     2. `Build frontend skeleton` - use the `coding-frontend` skill for starter and UI baseline specifics.
     3. `Build data model` - create the SQLite database model, migrations/schema, and persistence boundary.
   - For WordPress apps, start with a foundation feature routed to `coding-wordpress` before product-facing WordPress behavior.
   - After those foundations, add the smallest product-facing features needed for a shippable first slice.

6) Materialize features and proof packages
   - This skill is the explicit exception to the single FEATURE_DIR rule during greenfield bootstrap.
   - For each selected feature, use `coding-feature-spec` to create `docs/features/<slug>/FEATURE.md`.
   - Ensure `coding-feature-spec` invokes `coding-proof-author` for each non-trivial feature.
   - Require `docs/features/<slug>/PROOF.md` plus executable proof artifacts for each non-trivial feature.
   - Require each non-trivial primary proof command to call `scripts/proof_run_capture`.
   - Do not count a feature as materialized when it only has `FEATURE.md` and a prose `PROOF.md`.
   - After bootstrap completes, return to the normal feature execution workflow.

7) Initialize the feature queue
   - Use `coding-feature-queue` to create or update `docs/features/status.json`.
   - Add every generated feature directory to the queue.
   - Use `draft` while feature/proof authoring is incomplete or contract review still
     needs repair.
   - Set initial statuses to `ready` only for features with `FEATURE.md`, `PROOF.md`, an
     executable proof artifact, a primary proof command wrapped with `scripts/proof_run_capture`,
     and a passing contract review.
   - Set initial status to `needs_input` only after proof authoring or contract review has
     exhausted local recovery and still needs missing product input, unavailable external
     state, or an unreproducible requirement.
   - Preserve implementation order with numeric priorities.
   - `FEATURE.md` and `PROOF.md` remain the feature contracts; `docs/features/status.json` is only the machine-readable progress queue.

8) Keep the series pragmatic
   - Prefer a shippable first slice over exhaustive roadmap coverage.
   - Merge overlapping ideas instead of producing thin or redundant features.
   - Leave clearly out-of-scope ideas out of the first series.

9) Handoff cleanly
   - Return the improved app brief summary.
   - List generated feature ids in recommended implementation order.
   - Point to `docs/features/status.json` as the queue for autonomous execution.
   - Do not list every proof path or executable artifact by default; include the next
     primary proof command only when it is immediately actionable.

## Rules
- Do not add an in-repo orchestration layer.
- Do not create a planning daemon, router, or local workflow engine.
- Reuse `coding-feature-spec` for final feature descriptions and `coding-proof-author` for proof packages rather than inventing another format.
- Keep outputs concise. Avoid unnecessary implementation commitments and leave concrete folder structure to the owning stack/domain skill.
