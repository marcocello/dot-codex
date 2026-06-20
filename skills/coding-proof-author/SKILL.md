---
name: coding-proof-author
description: "Create or repair FEATURE_DIR/PROOF.md and executable feature proof artifacts. Use when a feature needs a definition of done, primary proof command, behavioral E2E/API/scenario/regression/migration verification, or when existing proof is vague, weak, missing, static-only, or gameable."
metadata:
  short-description: Feature proof authoring
---

# Proof Author

Purpose: turn `FEATURE_DIR/FEATURE.md` into a concrete proof contract and executable evidence.

`FEATURE.md` describes what to build. `PROOF.md` defines how completion is proven.

Proof authoring is not complete when only `PROOF.md` exists. A non-trivial feature needs an executable proof artifact and a primary proof command that runs that artifact.

## Workflow
1) Read the feature contract
   - Read `FEATURE_DIR/FEATURE.md`.
   - Read `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md` when present.
   - Treat user-visible behavior, internal invariants, constraints, and non-goals as proof inputs.

2) Choose one primary behavioral proof
   - User-visible UI workflow: use a browser E2E proof that renders or drives the app.
   - API behavior: use a black-box HTTP/API proof against the app runtime.
   - Agent/provider workflow: use `coding-real-user-scenario-tests` and provider read-back.
   - Messaging/webhook integration: drive the real listener/API/worker boundary with saved provider payload fixtures, assert persisted state, duplicate suppression, and outbound send intent at the external provider-client boundary.
   - Bug fix: use the smallest regression proof that fails before the fix.
   - Migration/database/internal change: use integrity, equivalence, migration, or performance proof.
   - Refactor: use existing behavior suites plus a targeted regression or contract proof.
   - Static source/file/term checks are not valid as the primary proof for user-visible, API, provider, or workflow features. They may be secondary architecture guards only.

3) Create or repair executable proof artifacts
   - Create or update at least one executable proof artifact before claiming proof authoring is complete.
   - Prefer `FEATURE_DIR/proof/tests/` for pytest-style proof checks.
   - Use `FEATURE_DIR/proof/run.sh` only when a shell runner is clearer than native test tooling.
   - Use repo-native E2E or integration test locations when the repo already has a clear pattern.
   - For scenario testbeds, keep fixtures in `FEATURE_DIR/proof/fixtures/` unless the repo has an established demo/testbed fixture location.
   - For scenario testbeds, the proof must include saved prompt/input fixtures, provider payload fixtures, or API/browser scenario fixtures that represent the real workflow.
   - For provider integrations, use deterministic provider doubles for local proof only when live credentials are unavailable; keep a manual live-provider read-back gap in `PROOF.md`.
   - For API features, call the real route or app client and assert response status, response body, persistence, and relevant side effects.
   - For UI features, render the component/page or drive the browser and assert visible user-facing state or interactions.
   - For messaging/webhook features, submit realistic payload fixtures to the listener/API boundary and assert state changes plus outbound provider-client calls.
   - For idempotency or retry behavior, submit the same provider/event ID twice and assert exactly one persisted interaction/run/outbound send.
   - Patch or fake only the outermost external provider/client boundary. Do not replace the route, worker, service, sender gateway, persistence, or orchestrator path being proven.
   - Do not import application internals for feature proof unless the chosen proof type is explicitly an internal contract, migration, or equivalence proof.
   - Do not use mocks or monkeypatching for black-box user/API/provider proof.

4) Write `FEATURE_DIR/PROOF.md`
   - Include definition of done.
   - Include proof type.
   - Include the primary proof command that runs the executable artifact created above.
   - Include expected evidence and observable state.
   - Include required environment, fixtures, credentials, or provider setup.
   - Include anti-gaming constraints such as no mocks, no internal imports, or no weakened coverage when those constraints matter.
   - Include manual gaps only when automation is not currently possible, with the reason.
   - Do not set the primary proof command to the repo safety gate, a legacy feature-check wrapper, or a static source contract test. Those may be listed as secondary guards only.
   - If no executable proof artifact can be created, mark the proof `BLOCKED` and report the missing input or environment requirement instead of claiming a proof contract exists.

5) Validate the proof surface
   - Run the narrowest proof parser/test when practical.
   - If implementation is not present yet, confirm the primary proof fails or is unmet for the expected reason.
   - Do not make the proof pass by weakening `FEATURE.md` or reducing the claimed behavior.
   - Handoff must list the executable proof files created or changed. If the list is empty, the proof authoring task is not done.

## PROOF.md Template
````md
# Proof Plan

## Definition Of Done
- <observable condition required for completion>
- <safety or regression condition>

## Primary Proof
Type: <e2e | api | scenario-testbed | integration | regression | migration | existing-suite>

Command:
```bash
<command that runs FEATURE_DIR/proof/... or the repo-native E2E/testbed artifact>
```

Expected evidence:
- <specific output, persisted state, provider read-back, file content, or invariant>

Secondary guards:
- <optional static architecture/source checks, type checks, or contract checks>

## Environment And Data
- <runtime services, fixtures, accounts, seeded records, credentials, or provider state>

## Anti-Gaming Constraints
- <what must not be mocked, bypassed, weakened, or asserted only through model claims>

## Repo Safety Gate
Command:
```bash
$HOME/.codex/scripts/gate
```

## Manual Gaps
- None, or <manual verification that remains and why it cannot be automated yet>
````

## Rules
- Keep `FEATURE.md` product-facing; put verification detail in `PROOF.md`.
- Every non-trivial feature gets one primary proof command.
- Every non-trivial feature gets at least one executable proof artifact.
- The primary proof command is the feature completion authority and must run a behavioral artifact.
- Gate is only the repo-health guard; it does not prove feature completion.
- Static source/file/term checks cannot be the primary proof for user-visible, API, provider, or workflow features.
- For provider writes, require read-back from the provider when the runtime can verify it.
- A successful tool call or assistant claim is not sufficient proof when external state is checkable.
- Do not hand off with only a prose `PROOF.md` unless the feature is explicitly documentation-only or blocked.
