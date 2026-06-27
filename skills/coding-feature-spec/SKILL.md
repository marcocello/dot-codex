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

## Pipeline
1) Load context
   - Read `docs/APP.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, and
     `docs/TESTING.md` when present.

2) Create or update `FEATURE.md`
   - Use `docs/features/<feature-id-slug>/`; create or update only that directory.
   - Default to the short form: summary, desired behavior, constraints, and routing.
   - Add extended sections only when they remove ambiguity for implementation or proof.
   - Keep behavior observable, product-facing, and testable.
   - Cover the happy path plus material edge, error, permission, and recovery cases.
   - For API, CLI, file, event, provider, or UI-boundary features, capture the
     external contract: inputs, outputs, statuses, states, schemas, or messages that
     consumers observe.
   - Capture defaulting, fallback, precedence, version-resolution, and selection rules
     when more than one behavior could reasonably apply.
   - For semantic behavior such as duplicate prevention, routing, classification,
     extraction, permissions, or intent handling, describe the durable invariant and
     structured decision rule. Do not define correctness as a list of trigger phrases.
   - Capture operational constraints when runtime, deployment target, storage,
     credentials, environment variables, or resource limits affect correctness.
   - When updating an existing feature, preserve existing desired behavior, constraints,
     and non-goals unless the user explicitly changes or removes them.
   - Keep proof commands, fixtures, environment, and evidence out of `FEATURE.md`.
   - If the repo has a local scenario skill, describe the workflow in `FEATURE.md` and let
     `coding-proof-author` choose the executable proof artifact.
   - Use `coding-research` when important assumptions depend on external APIs, domain
     rules, or framework behavior.

3) Add routing
   - Add `Required skills` only when clear: backend, frontend, WordPress, proof, or another
     relevant local skill.
   - Keep framework, starter, and folder details inside the owning domain skills.

4) Create the proof package
   - Use `coding-proof-author` for every non-trivial feature before queue update or final
     handoff.
   - `coding-proof-author` must create or repair `FEATURE_DIR/PROOF.md` and executable
     proof artifacts such as `FEATURE_DIR/proof/run.sh`, `FEATURE_DIR/proof/tests/`,
     `FEATURE_DIR/proof/fixtures/`, or a repo-native E2E/testbed file.
   - Do not accept a prose-only `PROOF.md` as proof authoring.
   - If executable proof cannot be created after readiness scaffolding, report
     `NEED_INPUT` and ask only for the missing product, API, provider, or environment
     detail.

5) Review contract readiness
   - Use `coding-feature-quality` for non-trivial feature specs before queue update or final
     handoff.
   - Repair material ambiguity, missing edge cases, weak testability, architecture conflict,
     or proof gaps before marking the item `ready`.
   - Do not run `coding-feature-evaluator` unless implementation or issue-fix work was also
     completed.

6) Update `status.json`
   - Use `coding-feature-queue` to add or update the item.
   - `draft`: `FEATURE.md`, `PROOF.md`, executable proof artifacts, or contract review are
     incomplete or still being repaired.
   - `ready`: contract package is ready for implementation.
   - `needs_input`: proof authoring or contract review still needs missing input or
     unavailable external state after local recovery attempts.
   - If an existing `done` feature's behavior, proof contract, or executable proof artifacts
     change, reset status to `draft` while authoring, then `ready` after review passes.
   - Preserve `done` only for clearly non-behavioral metadata, typo, or formatting edits.

7) Handoff
   - Use the artifact-authoring receipt from `AGENTS.md`.
   - Lead with the feature behavior now specified, then list only the created/changed
     contract files.
   - Include the primary proof command and queue status only when they help the next
     implementation step.
   - Say `implementation proof: NOT RUN` only when the user might otherwise think
     implementation was completed.

## FEATURE.md Short Template
```md
# <Feature title>

## Summary
<Short description of the change.>

## Desired Behavior
- <Observable behavior that should become true.>

## Constraints
- <Only constraints that materially affect correctness.>

## Implementation Routing
- Required skills: <coding-python-backend | coding-frontend | coding-wordpress |
  coding-proof-author | other relevant skills>
```

## Extended Sections
Add these only when the short template would leave implementation or proof ambiguous:

```md
## Scope
- <Included behavior or surfaces.>

## Non-Goals
- <Explicitly excluded behavior.>

## Scenarios
- <Happy path scenario.>
- <Important edge, error, permission, or recovery scenario.>

## External Contract
- <Endpoints, commands, file formats, events, provider calls, UI states, request/input
  shapes, response/output shapes, and error/status behavior that consumers observe.>

## Resolution Rules
- <Defaults, fallbacks, precedence, version selection, conflict handling, or selection
  rules that remove ambiguity from implementation.>

## Additional Constraints
- <Architecture, data, security, UX, compatibility, runtime, or credential constraint.>
```

## Rules
- Keep `FEATURE.md` concise and human-readable.
- Do not put proof commands in `FEATURE.md`.
- Do not stop after `FEATURE.md` for non-trivial features; create the proof package in the same feature-spec run.
- Do not treat feature-spec authoring as feature implementation.
- Do not make Gherkin mandatory.
- Do not add architecture decisions unless explicitly provided or already authoritative.
- Do not add backward compatibility requirements unless explicitly requested.
