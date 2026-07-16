---
name: coding-proof-author
description: "Create or repair PROOF.md and executable behavioral proof artifacts when feature evidence is missing, weak, static-only, stale, or gameable."
metadata:
  short-description: Feature proof authoring
---

# Proof Author

Purpose: turn one `FEATURE_DIR/FEATURE.md` into a proof contract plus executable evidence.

`FEATURE.md` says what to build. `PROOF.md` says how completion is proven. Proof authoring is not complete when only `PROOF.md` exists.

## Invariants
- Every non-trivial feature gets at least one executable proof artifact.
- The primary proof must run a behavioral artifact through the public boundary that owns the claim.
- The primary proof is not a unit test, source assertion, serializer assertion, mocked service return, or assistant-text assertion unless that surface is itself the claimed public boundary.
- Static source/file/term checks are not valid as the primary proof for user-visible, API, provider, messaging, frontend, worker, or workflow features.
- The primary proof command must call `scripts/proof_run_capture` and declare every completion-authorizing input with repeatable `--source-path` arguments.
- Successful tool calls or assistant claims are not proof when durable or user-visible state can be read back.

## Boundary Discovery
Name these before choosing a proof profile:
- Producer: what creates the production input.
- Activation path: route, listener, browser flow, worker pickup, command, scheduler, or callback the proof drives.
- Consumer: the normal app path that must run unchanged.
- Durable state: database row, provider object, file, runtime state, artifact, or visible UI that changes.
- Read-back: query, provider GET, screenshot, artifact extraction, received message, trace, log, or API response proving the effect.
- Unsafe edge: external state that must be live, guarded, or replaced only at the outer boundary.

The proof boundary must match the behavior boundary. For persisted rows, queue items, scheduled polls, webhooks, CLI commands, and API requests, drive the real activation path and verify the durable result. Direct inner-service calls are secondary unless the feature explicitly claims only that inner boundary.

## Profile Routing
Choose one primary behavioral proof using the smallest profile that catches a fake implementation or high-risk behavior.

Read only the relevant sections of [proof-profiles.md](references/proof-profiles.md):
- bug fix or internal invariant -> Bug Fix And Internal;
- API, OAuth, or provider -> API And Provider;
- UI or rendered artifact -> UI And Artifact;
- worker, scheduler, webhook, messaging, queue, or CLI -> Reactive And Process Boundaries;
- semantic or natural-language behavior -> Semantic Pressure.

Use [proof-contract-template.md](references/proof-contract-template.md) only when creating or materially restructuring `PROOF.md` or its evidence layout.

## Workflow
1. Read `FEATURE_DIR/FEATURE.md`, existing `PROOF.md`, relevant repo architecture/testing docs, and any repo-local scenario or API testbed contract that owns the boundary.
2. Perform Boundary Discovery and select the smallest relevant proof profile.
3. Add `Claimed Behavior Coverage` mapping each central feature claim to a real entrypoint and read-back.
4. Run an adversarial review: name at least three plausible fake or incomplete implementations, show which proof step catches each, and strengthen the proof if a central broken implementation could still pass.
5. Create or repair executable artifacts under `FEATURE_DIR/proof/` or the repo-native E2E/testbed location.
6. Write `PROOF.md` with proof scope, fake-boundary ledger, environment/readiness, manual gaps, and secondary guards.
7. Run the narrowest parser or proof-artifact check that is practical. Do not run `coding-feature-evaluator` for proof-authoring-only work; use `coding-feature-quality` for contract readiness.

## Primary Command
For serious non-trivial proof, use:

```bash
scripts/proof_run_capture --serious --feature-dir FEATURE_DIR --source-path <implementation-or-proof-input> --behavior-boundary "<producer -> activation -> consumer -> read-back>" --oracle-scope "$(cat FEATURE_DIR/PROOF.md)" --notes "<short proof result summary>" -- <command that runs FEATURE_DIR/proof/... or repo-native proof>
```

The helper must leave `FEATURE_DIR/proof/runs/<timestamp>/` evidence including `command.txt`, `result.json`, `run-metadata.json`, `oracle-scope.md`, and real optional attachments such as `provider-readback.json`, `agent-observation.md`, or `agent-observation.json`. Never fabricate absent evidence.

## External Readiness
- Prefer live proof when real provider state is the behavior claimed.
- If live proof requires unavailable credentials or external state, write a readiness artifact with exact prerequisites and clear `NEED_INPUT`; prefer `FEATURE_DIR/proof/readiness.sh` unless the repo has a native readiness path.
- Readiness artifacts may use local CLIs, apps, MCP tools, browser automation, database clients, cloud CLIs, or repo scripts.
- Record local doubles as an explicit manual gap when they cannot prove the live provider claim.

## Proof Change Guard
When `PROOF.md` changes after implementation starts, enter contract repair and record:
- why the original proof was wrong or incomplete;
- which fake implementation the revision catches;
- red evidence against the current implementation when practical;
- why behavior scope was not reduced;
- final evidence identity for the revised contract, runner, and declared sources.

Resume implementation only against that explicit contract revision.

## Rules
- Keep behavior in `FEATURE.md`; verification in `PROOF.md`.
- Gate is a repo-health guard, not feature proof.
- Unit tests, source assertions, serializer assertions, and mocked service returns are secondary guards for non-trivial user-visible behavior.
- Read back external writes, messages, files, reports, database changes, and visible UI from the same durable or user-visible boundary.
- Include `Proof Scope` with `Proves:`, `Does not prove:`, `False-green risks:`, and `Evidence strength:`.
- Include an anti-gaming review connecting fake-pass risks to concrete proof steps.
- Do not hand off with only a prose `PROOF.md` unless the work is documentation-only or awaiting `NEED_INPUT`.
