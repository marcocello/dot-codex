---
name: coding-feature-spec
description: "Create or update docs/features/{feature-id-slug}/FEATURE.md from a rough or incomplete idea, then use coding-proof-author to create PROOF.md and executable proof artifacts for non-trivial features. Use when the task is feature-spec authoring or refinement."
metadata:
  short-description: Define product-facing FEATURE.md
---

# Feature Spec

Purpose: produce a concise, product-facing `FEATURE.md` inside `docs/features/<feature-id-slug>/`, then make the feature provable through `coding-proof-author`.

`FEATURE.md` describes what to build. It does not own verification commands or executable proof. For non-trivial features, this skill must call `coding-proof-author` after `FEATURE.md` is written so the same feature-spec run produces `PROOF.md` plus executable proof artifacts.

## Inputs
If missing, ask only for blocking details:
- short title
- user persona or core job-to-be-done
- desired behavior or core workflow
- key constraints or must-avoid behavior

Do not ask architecture questions unless strictly required.

## Workflow
1) Load repo-level context when present
   - Read `docs/APP.md` if it exists.
   - Read `docs/ARCHITECTURE.md` if it exists.
   - Read `docs/CONVENTIONS.md` if it exists.
   - Read `docs/TESTING.md` if it exists.

2) Determine feature directory
   - Use `docs/features/<feature-id-slug>/`.
   - Slug format: lowercase words separated by hyphens.
   - If it exists, update `FEATURE.md`.
   - If not, create the directory and `FEATURE.md`.
   - No numbering or date prefixes.

3) Run discovery when the idea is incomplete
   - Write one JTBD statement when useful.
   - Map the user journey or internal workflow in key steps only.
   - Cover happy path, important variants, edge cases, and failure/recovery cases.
   - Identify user roles and external integrations involved.
   - Record assumptions that materially affect behavior.
   - Use `coding-research` when assumptions depend on external APIs, domain rules, or framework behavior.

4) Write behavior, not proof
   - Keep behavior observable and testable.
   - Use bullets or scenarios; Gherkin is optional, not mandatory.
   - When updating an existing feature, preserve existing desired behavior, constraints,
     and non-goals unless the user explicitly changes or removes them.
   - Keep implementation details out unless they are real constraints.
   - Put verification commands, fixtures, environment, and evidence in `PROOF.md`, not `FEATURE.md`.
   - If the repo has a local scenario skill, state the intended user workflow in
     `FEATURE.md` and let `coding-proof-author` choose the executable proof artifact.
   - Do not put generated scenario or fixture data in `FEATURE.md`; proof data belongs in
     `FEATURE_DIR/proof/` unless the user explicitly asked for reusable demo data.

5) Add implementation routing when clear
   - If backend Python application code is in scope, include `- Required skills: coding-python-backend`.
   - If React or Next.js UI code is in scope, include `- Required skills: coding-frontend`.
   - If WordPress code is in scope, include `- Required skills: coding-wordpress`.
   - If a proof or testbed is clearly needed, include `- Required skills: coding-proof-author`.
   - Keep framework, starter, and folder details inside the owning domain skills.

6) Create the proof package
   - Use `coding-proof-author` for every non-trivial feature before queue update or final handoff.
   - `coding-proof-author` must create or repair `FEATURE_DIR/PROOF.md`.
   - `coding-proof-author` must create or repair executable proof artifacts such as `FEATURE_DIR/proof/run.sh`, `FEATURE_DIR/proof/tests/`, `FEATURE_DIR/proof/fixtures/`, or a repo-native E2E/testbed file.
   - Do not accept a prose-only `PROOF.md` as proof authoring.
   - If executable proof cannot be created because required product/API/provider details are missing, mark the proof blocked and ask only for the missing information.

7) Review the contract package
   - Use `coding-feature-quality` for non-trivial feature specs before queue update or final
     handoff.
   - Treat `coding-feature-quality` as the evaluator for spec/proof readiness, not as proof
     that the feature is implemented.
   - Repair material ambiguity, missing edge cases, weak testability, architecture conflict,
     or proof gaps before handoff.
   - Do not run `coding-feature-evaluator` unless implementation or issue-fix work was also
     completed.

8) Keep optional notes local
   - For larger brownfield changes, optionally create `FEATURE_DIR/notes.md` for intent, non-goals, design notes, or task checklist details.
   - `FEATURE.md` remains the behavior description.

9) Update the feature queue
   - Use `coding-feature-queue` to create or update `docs/features/status.json`.
   - Add the feature if it is new.
   - Use `draft` while `FEATURE.md`, `PROOF.md`, executable proof artifacts, or contract
     review are incomplete or still being repaired.
   - Set status to `ready` only when `FEATURE.md`, `PROOF.md`, executable proof artifacts,
     and contract review are ready for implementation.
   - Set status to `blocked` when proof authoring or contract review is blocked by missing
     product input, unavailable external state, or an unreproducible requirement.
   - If an existing `done` feature's behavior, proof contract, or executable proof artifacts
     change, reset status to `draft` while authoring, then `ready` after the updated contract
     package passes review.
   - Preserve `done` only for clearly non-behavioral metadata, typo, or formatting edits.
   - Include the `proof` path in queue entries when the queue schema supports it.

10) Handoff
   - State whether `FEATURE_DIR/PROOF.md` exists.
   - List the executable proof files `coding-proof-author` created or changed.
   - Include the primary proof command from `PROOF.md`.
   - Report `Contract review: PASS`, `FAIL`, or `BLOCKED` from `coding-feature-quality`
     for non-trivial specs.
   - Report implementation proof as `NOT RUN` unless implementation was also in scope.
   - Do not call proof authoring complete when only a prose `PROOF.md` was created.
   - Do not report a primary proof command that only runs the repo safety gate or a legacy feature-check wrapper.

## FEATURE.md Template
```md
# <Feature title>

## Summary
<Short description of the change.>

## Desired Behavior
- <Observable behavior that should become true.>

## Scope
- <Included behavior or surfaces.>

## Non-Goals
- <Explicitly excluded behavior.>

## Scenarios
- <Happy path scenario.>
- <Important edge, error, permission, or recovery scenario.>

## Constraints
- <Architecture, data, security, UX, compatibility, or operational constraint.>

## Implementation Routing
- Required skills: <coding-python-backend | coding-frontend | coding-wordpress |
  coding-proof-author | other relevant skills>
```

## Rules
- Keep `FEATURE.md` concise and human-readable.
- Do not put proof commands in `FEATURE.md`.
- Do not stop after `FEATURE.md` for non-trivial features; create the proof package in the same feature-spec run.
- Do not treat feature-spec authoring as feature implementation.
- Do not make Gherkin mandatory.
- Do not add architecture decisions unless explicitly provided or already authoritative.
- Do not add backward compatibility requirements unless explicitly requested.
