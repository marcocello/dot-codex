---
name: coding-feature-spec
description: "Define one non-trivial behavior contract from repository context, focused questions, and explicit decisions."
---

# Feature Spec

Purpose: learn the real user goal, challenge incomplete assumptions, state the resulting behavior decisions, then write one `FEATURE.md` without a contract-approval gate.

`FEATURE.md` owns what should be built. It does not own proof commands, fixtures, execution output, or implementation details.

For every non-trivial feature, this skill must invoke `coding-proof-author` after writing `FEATURE.md` and before handoff in the same parent run. Load and apply the proof-author skill as the next workflow phase so it produces decision-complete `PROOF.md` and executable `proof/run.sh`. A separate proof-decision round is not a separate task or a reason to return control to the user.

## Inputs
Derive from the request and repository before asking:

- target user or actor;
- trigger and workflow;
- desired observable outcome;
- inputs, outputs, states, errors;
- permissions, concurrency, recovery, external effects;
- constraints, non-goals, compatibility needs;
- success criteria and material corner cases.

Read `docs/APP.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, `docs/TESTING.md`, related feature contracts, and existing behavior when present. Do not ask the user for facts the repository already establishes.

## User Discovery
1. Identify choices that can change observable behavior, scope, external contracts, data handling, permissions, runtime ownership, or proof cost.
2. Ask focused grouped questions. Prefer a small coherent set over one question per turn; avoid broad prompts such as “anything else?”
3. Challenge the happy path. Include relevant empty, invalid, duplicate, unauthorized, concurrent, partial-failure, retry, cancellation, restart, and recovery cases.
4. Offer recommended defaults for smaller choices. Explain the material consequence of alternatives.
5. Stop asking when remaining answers would only change reversible implementation details.

When the user corrects a prior direction, first restate:

- accepted behavior;
- rejected previous interpretation;
- remaining uncertainty, if any.

## Decision Summary
Before writing the artifact, show the decided contract in chat:

- goal and user outcome;
- observable behavior and main scenarios;
- external interface or data contract when relevant;
- constraints and assumptions;
- non-goals;
- unresolved decisions, if any.

The summary is not an approval request. After the user answers material discovery questions, write `FEATURE.md` and continue. When repository context and the request already resolve the material choices, summarize decisions and proceed directly. Ask and wait only when an unresolved user-owned choice would materially change observable behavior, scope, safety, cost, data handling, permissions, or external effects and no safe recommended default exists.

## Workflow
1. Inspect request, repository context, existing features, and implementation boundary.
2. Run User Discovery.
3. Show Decision Summary.
4. Create or update `docs/features/<feature-id>/FEATURE.md`.
5. Preserve existing accepted behavior unless the user changes it.
6. Add implementation routing only when a stack/domain skill clearly owns the work.
7. Invoke and apply `coding-proof-author` for non-trivial decided behavior in the same parent run. Complete its separate proof-decision round before handoff.
8. Keep the queue item `draft` until `PROOF.md` and executable proof are decision-complete; `ready` belongs to the completed contract package.

## FEATURE.md Shape
Start small:

```md
# <Feature title>

## Goal
<Actor and outcome.>

## Behavior
- <Observable behavior.>

## Constraints
- <Correctness-affecting boundary.>

## Non-Goals
- <Explicit exclusion.>
```

Add only sections that remove implementation or proof ambiguity:

- scenarios;
- external contract;
- states and error behavior;
- resolution/default/precedence rules;
- data, security, runtime, compatibility, or architecture constraints;
- required skills.

For semantic behavior, define the durable invariant and decision boundary. Do not define correctness as a list of natural-language trigger phrases unless the vocabulary is an explicit closed set.

## Rules
- One feature and one owning `FEATURE_DIR`.
- Product-facing behavior, not implementation diary.
- No silent invented product decisions; label inferred defaults in the decision summary.
- No proof commands or evidence in `FEATURE.md`.
- No mandatory Gherkin.
- No architecture or backward-compatibility commitment unless requested or authoritative.
- Material ambiguity unresolved: ask and wait.
- Non-trivial feature incomplete until `coding-proof-author` produces a decision-complete executable proof package.

## Handoff
For a non-trivial feature, hand off only after `coding-proof-author` has produced decision-complete `PROOF.md` and executable `proof/run.sh`, or after it returns `NEED_INPUT` for an exact user-owned dependency. Report the decided behavior, feature and proof paths, remaining product or proof decisions, and queue readiness. Do not claim implementation proof was run during contract-authoring work.
