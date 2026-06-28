---
name: coding-feature-spec
description: "Create or update docs/features/{feature-id-slug}/FEATURE.md from a rough or incomplete idea, then use coding-proof-author to create PROOF.md and executable proof artifacts for non-trivial features. Use when the task is feature-spec authoring or refinement."
metadata:
  short-description: Define product-facing FEATURE.md
---

# Feature Spec

Purpose: concise product-facing `FEATURE.md`, then provable package via
`coding-proof-author`.

`FEATURE.md` describes what to build. It does not own proof commands or executable proof.
For non-trivial features, this skill must call `coding-proof-author` after `FEATURE.md` is written
so the same run produces `PROOF.md` plus executable proof artifacts.

## Inputs
Ask only for blockers:
- title
- persona/job
- desired behavior/workflow
- constraints/must-avoid behavior

No architecture questions unless required.

## Pipeline
1. Load context
   - Read `docs/APP.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, `docs/TESTING.md`
     when present.

2. Write `FEATURE.md`
   - Use only `docs/features/<feature-id-slug>/`.
   - Default to the short form: summary, desired behavior, constraints, and routing.
   - Add extended sections only when they remove ambiguity for implementation or proof.
   - Keep behavior observable, product-facing, testable.
   - Cover happy path plus material edge/error/permission/recovery cases.
   - For API, CLI, file, event, provider, or UI-boundary features, capture the external
     contract: inputs, outputs, statuses, states, schemas, messages.
   - Capture defaulting, fallback, precedence, version-resolution, selection rules when
     multiple behaviors could apply.
   - For semantic behavior such as duplicate prevention, routing, classification,
     extraction, permissions, or intent handling, describe durable invariant and structured
     decision rule. Do not define correctness as a list of trigger phrases.
   - Capture operational constraints when runtime, deployment target, storage, credentials,
     env vars, or resource limits affect correctness.
   - When updating, preserve existing desired behavior, constraints, non-goals unless user
     changes them.
   - Keep proof commands, fixtures, environment, evidence out of `FEATURE.md`.
   - If the repo has a local scenario skill, describe the workflow in `FEATURE.md` and let
     `coding-proof-author` choose the executable proof artifact.
   - Use `coding-research` when assumptions depend on external APIs/domain/framework rules.

3. Add routing
   - Add `Required skills` only when clear.
   - Keep framework/starter/folder detail inside owning domain skills.

4. Create proof package
   - Use `coding-proof-author` for every non-trivial feature before queue update or handoff.
   - It must create/repair `FEATURE_DIR/PROOF.md` plus executable proof artifacts:
     `FEATURE_DIR/proof/run.sh`, `proof/tests/`, `proof/fixtures/`, or repo-native E2E.
   - Do not accept a prose-only `PROOF.md` as proof authoring.
   - If executable proof cannot be created after readiness scaffolding, report `NEED_INPUT`
     with only missing product/API/provider/environment detail.

5. Review readiness
   - Use `coding-feature-quality` for non-trivial feature specs before queue update/handoff.
   - Repair material ambiguity, missing edges, weak testability, architecture conflict, proof
     gaps before `ready`.
   - Do not run `coding-feature-evaluator` unless implementation or issue-fix work was also
     completed.

6. Update queue
   - Use `coding-feature-queue`.
   - `draft`: `FEATURE.md`, `PROOF.md`, executable proof artifacts, or contract review are
     incomplete or still being repaired.
   - `ready`: contract package is ready for implementation.
   - `needs_input`: proof authoring or contract review still needs missing input/external
     state after recovery.
   - Behavior/proof changes to existing `done`: reset status to `draft` while authoring, then `ready` after review.
   - Preserve `done` only for clearly non-behavioral metadata, typo, formatting edits.

7. Handoff
   - Artifact-authoring receipt from `AGENTS.md`.
   - Feature behavior first; only created/changed contract files.
   - Include primary proof command and queue status only when useful next.
   - Say `implementation proof: NOT RUN` only if confusion likely.

## FEATURE.md Short Template
```md
# <Feature title>

## Summary
<Short description.>

## Desired Behavior
- <Observable behavior.>

## Constraints
- <Correctness-affecting constraints.>

## Implementation Routing
- Required skills: <coding-python-backend | coding-frontend | coding-wordpress |
  coding-proof-author | other relevant skills>
```

## Extended Sections
Add only when short template leaves implementation/proof ambiguous:

```md
## Scope
- <Included behavior/surfaces.>

## Non-Goals
- <Excluded behavior.>

## Scenarios
- <Happy path.>
- <Important edge/error/permission/recovery case.>

## External Contract
- <Endpoints, commands, file formats, events, provider calls, UI states, input/output
  shapes, statuses, errors.>

## Resolution Rules
- <Defaults, fallbacks, precedence, version selection, conflict handling.>

## Additional Constraints
- <Architecture, data, security, UX, runtime, credential constraint.>
```

## Rules
- Concise human-readable `FEATURE.md`.
- No proof commands in `FEATURE.md`.
- Do not stop after `FEATURE.md` for non-trivial features; create proof package same run.
- Non-trivial feature: create proof package same run.
- Feature-spec authoring is not implementation.
- No mandatory Gherkin.
- No new architecture/backward compatibility unless explicit or authoritative.
