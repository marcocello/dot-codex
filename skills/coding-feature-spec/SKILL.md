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
   - Keep implementation details out unless they are real constraints.
   - Put verification commands, fixtures, environment, and evidence in `PROOF.md`, not `FEATURE.md`.

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

7) Keep optional notes local
   - For larger brownfield changes, optionally create `FEATURE_DIR/notes.md` for intent, non-goals, design notes, or task checklist details.
   - `FEATURE.md` remains the behavior description.

8) Update the feature queue
   - Use `coding-feature-queue` to create or update `docs/features/status.json`.
   - Add the feature if it is new.
   - Preserve existing status when refining a feature unless behavior materially changes; then set status to `pending` or `failing` and explain why.
   - Include the `proof` path in queue entries when the queue schema supports it.

9) Handoff
   - State whether `FEATURE_DIR/PROOF.md` exists.
   - List the executable proof files `coding-proof-author` created or changed.
   - Include the primary proof command from `PROOF.md`.
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
- Do not make Gherkin mandatory.
- Do not add architecture decisions unless explicitly provided or already authoritative.
- Do not add backward compatibility requirements unless explicitly requested.
