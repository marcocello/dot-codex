---
name: coding-feature-spec
description: "Create or refine one FEATURE.md from an idea, resolve contract-changing ambiguity, then route non-trivial work to executable proof authoring."
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
Derive these from the request and repo context first. Ask only for unresolved blockers:
- title
- persona/job
- desired behavior/workflow
- constraints/must-avoid behavior
- ambiguity or decision boundary only when multiple implementation strategies, exact files/paths/sources, auth/secrets/deployment/runtime/data, or a prior user correction makes intent materially uncertain

Before writing, identify unanswered choices that could materially change observable behavior, scope, non-goals, external contracts, data handling, permissions, runtime ownership, or proof strategy. Ask at most two high-leverage questions in one message. Each question must name the decision and briefly explain the materially different outcomes; do not ask broad discovery questions such as "anything else?"

Stop and wait for the answers instead of drafting one branch as fact. If more than two blockers remain, ask the two that collapse the most downstream ambiguity first, then ask a later follow-up only if still necessary.

Do not ask when authoritative repo context already answers the choice, when the choice is implementation-only and reversible without changing the feature contract, or when a clearly stated assumption preserves rather than narrows the requested behavior. No architecture questions unless architecture changes the product contract.

## Pipeline
1. Load context
   - Read `docs/APP.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, `docs/TESTING.md`
     when present.
   - Read an existing `FEATURE.md` and `PROOF.md` before refining that feature.
   - If the request has multiple plausible meanings or a high-risk tradeoff, make a lightweight ambiguity checkpoint before writing: intended behavior, plausible alternative, and material consequence.
   - When local context cannot resolve a contract-changing decision, ask up to two focused questions and pause artifact changes until answered. If the request is clear, proceed without ceremony.
   - After a user correction, restate the accepted behavior and rejected prior direction before asking only about any ambiguity that still remains.

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
   - The primary proof command in `PROOF.md` must call `scripts/proof_run_capture`.
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

## Ambiguity Check
- <Only when useful: selected interpretation, rejected alternatives, and known tradeoff.>
```

## Rules
- Concise human-readable `FEATURE.md`.
- Resolve material ambiguity before authoring; never invent product behavior merely to keep the workflow moving.
- Ask at most two focused clarification questions per turn, and only when their answers can change the contract.
- No proof commands in `FEATURE.md`.
- Do not stop after `FEATURE.md` for non-trivial features; create proof package same run.
- Non-trivial feature: create proof package same run.
- Feature-spec authoring is not implementation.
- No mandatory Gherkin.
- No new architecture/backward compatibility unless explicit or authoritative.
