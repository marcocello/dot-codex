---
name: coding-proof-author
description: "Create or repair FEATURE_DIR/PROOF.md and executable feature proof artifacts. Use when a feature needs a definition of done, primary proof command, behavioral E2E/API/scenario/regression/migration verification, or when existing proof is vague, weak, missing, static-only, or gameable."
metadata:
  short-description: Feature proof authoring
---

# Proof Author

Purpose: turn `FEATURE_DIR/FEATURE.md` into one clear proof contract plus executable
evidence.

`FEATURE.md` describes what to build. `PROOF.md` defines how completion is proven.

Proof authoring is not complete when only `PROOF.md` exists. A non-trivial feature needs
an executable proof artifact and a primary proof command that runs that artifact.

Plain version: one realistic command should prove the behavior through the public
boundary. Add complexity only when it catches a real fake-pass risk.

## Proof Profiles
Choose the smallest profile that would catch a fake, incomplete implementation, or other
high-risk behavior.

- Bug fix profile: use the smallest regression proof that fails before the fix.
- API profile: call the real route or app client and verify response, persistence, and
  relevant side effects.
- UI profile: render the component/page or drive the browser and verify visible state or
  interaction.
- Provider/live profile: submit realistic payloads or use the repo-local testbed, patch
  only the outermost external provider/client boundary locally, and prefer live-provider
  read-back in the primary proof when credentials and a safe target exist.
- Migration/internal profile: prove integrity, equivalence, migration result, or the
  internal invariant through the narrowest executable check.

Static source/file/term checks are not valid as the primary proof for user-visible, API,
provider, or workflow features. They may be secondary guards only.

## Workflow
1. Read `FEATURE_DIR/FEATURE.md` and relevant repo docs.
2. Choose one primary behavioral proof from the profiles above.
3. Run an adversarial proof review before writing artifacts:
   - List at least three plausible fake or incomplete implementations.
   - Explain how the proof would catch each fake implementation through observable
     behavior.
   - Strengthen weak proof before implementation begins.
4. Create or repair executable artifacts under `FEATURE_DIR/proof/` or the repo-native
   testbed/E2E location.
5. Write `FEATURE_DIR/PROOF.md`, then run the narrowest parser/test when practical.

## Proof Details
- Prefer `FEATURE_DIR/proof/tests/` for pytest-style checks.
- Use `FEATURE_DIR/proof/run.sh` when a shell runner is clearer.
- When a repo-local API testbed exists, read its parser/CLI contract before writing the
  proof runner.
- For messaging/webhook features, submit realistic payload fixtures to the
  listener/API boundary and assert state changes plus outbound provider-client calls.
- For idempotency or retry behavior, submit the same provider/event ID twice and assert
  exactly one persisted interaction/run/outbound send.
- For semantic behavior, include paraphrase cases and at least one non-English or
  wording-shifted case when practical. Treat hardcoded natural-language keyword lists as
  fake-pass risks, and prove the structured outcome instead of matching response phrases
  alone.
- Do not import application internals for black-box user/API/provider proof.
- Do not use mocks or monkeypatching for black-box user/API/provider proof.

## External Readiness
- Live proof is preferred when real provider state is the behavior being claimed.
- If live proof needs credentials or external state, write a readiness artifact that checks
  exact prerequisites and exits with a clear `NEED_INPUT` message.
- Prefer `FEATURE_DIR/proof/readiness.sh` for shell-based external readiness checks unless
  the repo has a native readiness/testbed convention.
- External readiness artifacts may depend on local CLIs, apps, MCP tools, browser
  automation, database clients, cloud CLIs, or repo scripts when those observe real state
  needed by the proof.
- When local doubles replace live-provider verification, record the exact missing live
  proof as a manual gap in `PROOF.md`; do not silently treat mocks or tool traces as enough.
- For external integrations, name the live provider, safe test account/object, read-back
  command or API check, and the concrete credential or environment blocker.

## Proof Change Guard
When `PROOF.md` changes after implementation starts, record:
- why the original proof was wrong or incomplete;
- which fake implementation the changed proof catches;
- red and green results when practical;
- why behavior scope was not reduced.

## PROOF.md Template
````md
# Proof Plan

## Definition Of Done
- <observable behavior required for completion>

## Primary Proof
Type: <bug-fix | api | ui | provider-live | migration-internal | existing-suite>

Command:
```bash
<command that runs FEATURE_DIR/proof/... or the repo-native proof artifact>
```

Expected evidence:
- <response, UI state, persisted state, provider read-back, or invariant>

## Secondary Guards
- <optional lint, typecheck, unit tests, static architecture checks>

## Environment And Data
- <fixtures, services, accounts, credentials, safe targets, or readiness command>

## Anti-Gaming Review
- Fake pass risk: <incomplete implementation that might look done>.
- Proof catch: <specific proof step that fails if that fake exists>.

## Manual Gaps
- None, or <live verification that still needs user-owned input and why>
````

## Rules
- Keep `FEATURE.md` product-facing; put verification detail in `PROOF.md`.
- Every non-trivial feature gets one primary proof command.
- Every non-trivial feature gets at least one executable proof artifact.
- The primary proof command is the feature completion authority and must run a behavioral
  artifact.
- Gate is only the repo-health guard; it does not prove feature completion.
- Static source/file/term checks cannot be the primary proof for user-visible, API,
  provider, or workflow features.
- `PROOF.md` must include an anti-gaming review for every non-trivial feature.
- The anti-gaming review must connect fake pass risks to concrete proof steps.
- A successful tool call or assistant claim is not sufficient proof when external state is
  checkable.
- Do not hand off with only a prose `PROOF.md` unless the feature is explicitly
  documentation-only or awaiting `NEED_INPUT`.
- Do not run `coding-feature-evaluator` for proof-authoring-only work; use
  `coding-feature-quality` when the proof contract itself needs review before
  implementation.
