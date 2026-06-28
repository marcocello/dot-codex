---
name: coding-proof-author
description: "Create or repair FEATURE_DIR/PROOF.md and executable feature proof artifacts. Use when a feature needs a definition of done, primary proof command, behavioral E2E/API/scenario/regression/migration verification, or when existing proof is vague, weak, missing, static-only, or gameable."
metadata:
  short-description: Feature proof authoring
---

# Proof Author

Purpose: turn `FEATURE_DIR/FEATURE.md` into one proof contract plus executable evidence.

`FEATURE.md` says what to build. `PROOF.md` says how completion is proven.

Proof authoring is not complete when only `PROOF.md` exists. Non-trivial feature:
executable proof artifact + primary proof command that runs that artifact. One realistic
command through public boundary unless extra checks catch real fake-pass risk.

## Proof Profiles
Choose smallest profile that catches fake/incomplete implementation or high-risk behavior.

- Bug fix profile: smallest regression proof that fails before fix.
- API profile: call the real route or app client; verify response, state, side effects.
- UI profile: render the component/page or drive the browser; verify visible state or
  interaction.
- Provider/live profile: realistic payloads or repo-local testbed; patch only the outermost
  external provider/client boundary locally; prefer live-provider read-back in the primary
  proof when credentials and safe target exist.
- Migration/internal profile: prove integrity, equivalence, migration result, invariant.

Static source/file/term checks are not valid as the primary proof for user-visible, API,
provider, or workflow features. Secondary guards only.

## Workflow
1. Read `FEATURE_DIR/FEATURE.md` and relevant repo docs.
2. Choose one primary behavioral proof.
3. Run an adversarial proof review before writing artifacts:
   - List at least three plausible fake or incomplete implementations.
   - Explain how the proof would catch each fake implementation through observable behavior.
   - Strengthen weak proof before implementation begins.
4. Create/repair executable artifacts under `FEATURE_DIR/proof/` or repo-native testbed/E2E.
5. Write `FEATURE_DIR/PROOF.md`; run narrowest parser/test when practical.

## Evidence Bundle
For serious feature, issue, UI, API, provider, or workflow proof runs, prefer evidence:

```text
FEATURE_DIR/proof/runs/<timestamp>/
  command.txt
  stdout.txt
  stderr.txt
  result.json
  screenshots/
  logs/
  provider-readback.json
  notes.md
```

Only real evidence. No fake screenshots/logs/provider read-back. Bundle should let
`coding-feature-evaluator` inspect latest realistic scenario without trusting summary.

Local command wrapper:

```bash
scripts/proof_run_capture --feature-dir FEATURE_DIR -- <primary proof command>
```

Helper exits with wrapped command status and writes bundle.

## Proof Details
- Prefer `FEATURE_DIR/proof/tests/` for pytest-style checks.
- Use `FEATURE_DIR/proof/run.sh` when clearer.
- When a repo-local API testbed exists, read its parser/CLI contract first.
- Messaging/webhook: submit realistic payload fixtures to the listener/API boundary; assert
  state plus outbound provider-client calls.
- Idempotency/retry: submit same provider/event ID twice; assert one persisted effect/send.
- Semantic behavior: include paraphrase cases and at least one non-English or
  wording-shifted case when practical. Treat hardcoded natural-language keyword lists as
  fake-pass risks; prove structured outcome, not response phrase only.
- Black-box API/provider proof: no app-internal imports, no mocks/monkeypatching.

## External Readiness
- Live proof is preferred when real provider state is the behavior being claimed.
- If live proof needs credentials/external state, write a readiness artifact with exact
  prerequisites and clear `NEED_INPUT`.
- Prefer `FEATURE_DIR/proof/readiness.sh` unless repo has native readiness/testbed.
- External readiness artifacts may depend on local CLIs, apps, MCP tools, browser automation,
  database clients, cloud CLIs, or repo scripts.
- Local doubles replacing live-provider verification: record the exact missing live proof
  as a manual gap in `PROOF.md`; do not treat mocks/tool traces as enough.
- External integrations: name the live provider, safe test account/object, read-back
  command/API check, concrete credential/environment blocker.
- Evidence bundle exists: reference latest bundle in `PROOF.md` or handoff.

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
- <observable behavior required>

## Primary Proof
Type: <bug-fix | api | ui | provider-live | migration-internal | existing-suite>

Command:
```bash
<command that runs FEATURE_DIR/proof/... or repo-native proof>
```

Expected evidence:
- <response, UI state, persisted state, provider read-back, invariant>

## Secondary Guards
- <optional lint, typecheck, unit tests, static checks>

## Environment And Data
- <fixtures, services, accounts, credentials, safe targets, readiness command>

## Anti-Gaming Review
- Fake pass risk: <incomplete implementation that might look done>.
- Proof catch: <specific proof step that fails if that fake exists>.

## Manual Gaps
- None, or <live verification still needing user-owned input and why>
````

## Rules
- Keep behavior in `FEATURE.md`; verification in `PROOF.md`.
- Every non-trivial feature gets at least one executable proof artifact.
- The primary proof command is the feature completion authority and must run a behavioral artifact.
- Gate is repo-health guard, not feature proof.
- Static source/file/term checks cannot be the primary proof for user-visible/API/provider/workflow.
- `PROOF.md` must include an anti-gaming review for every non-trivial feature.
- The anti-gaming review must connect fake pass risks to concrete proof steps.
- Successful tool call or assistant claim is not proof when external state is checkable.
- Do not hand off with only a prose `PROOF.md` unless documentation-only or awaiting `NEED_INPUT`.
- Do not run `coding-feature-evaluator` for proof-authoring-only work; use `coding-feature-quality` for proof contract review before implementation.
