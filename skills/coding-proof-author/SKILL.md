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
command through public boundary unless extra checks catch real fake-pass risk. The primary
proof command must call `scripts/proof_run_capture` so every feature proof run leaves
`FEATURE_DIR/proof/runs/<timestamp>/` evidence.

Default stance: the primary proof is not a unit test, source assertion, serializer assertion, mocked service return, or assistant-text assertion. Those checks can be secondary guards. The primary proof should look like a real user, provider, webhook, scheduled worker, API client, browser, CLI process, or report consumer caused the behavior, and then it should read back durable state or user-visible output.

The proof boundary must match the behavior boundary. If the feature is triggered by a persisted row, queue item, scheduled poll, webhook, CLI command, or API request, the primary proof must create or submit that real boundary input, run the normal consumer path, and verify the durable result. Directly instantiating an inner worker/service is only acceptable when that is the real public boundary being claimed.

## Boundary Discovery
Before choosing a proof profile, name the real boundary:
- Producer: what creates the input in production, such as a user click, provider webhook, OAuth callback, mailbox event, transcript ingest, scheduler, CLI process, or API request.
- Activation path: the route, listener, browser flow, worker pickup, command, or provider callback the proof will drive.
- Consumer: the worker, endpoint, orchestrator, sender, renderer, or service path that must run unchanged.
- Durable state: the table row, provider object, file, runtime directory, trace row, generated artifact, or browser-visible state that must change.
- Read-back: the database query, provider GET, rendered screenshot, downloaded artifact, received message, tool trace, log capture, or API response that proves the effect.
- Unsafe edge: the external system that must be live, explicitly guarded, or replaced only by an outer provider-compatible fake.

If this boundary cannot be named, the proof contract is not ready.

## Proof Profiles
Choose smallest profile that catches fake/incomplete implementation or high-risk behavior.

- Bug fix profile: smallest regression proof that fails before fix.
- API profile: call the real route or app client; verify response, state, side effects.
- UI profile: render the component/page or drive the browser; verify visible state or
  interaction.
- Worker/scheduler profile: seed realistic persisted input or enqueue the job, run the
  scheduler/worker pickup path the app uses, and verify persisted state plus side effects.
- Provider/live profile: realistic payloads or repo-local testbed; patch only the outermost
  external provider/client boundary locally; prefer live-provider read-back in the primary
  proof when credentials and safe target exist.
- Migration/internal profile: prove integrity, equivalence, migration result, invariant.
- Static/documentation profile: allowed only when the feature itself is static analysis,
  documentation, generated reports, configuration manifests, or source policy. Prefer running
  the generator/parser and checking machine-readable output over string assertions.

## Realistic Proof Recipes
- CRM/provider workflow: clean a safe provider/test workspace or provider-compatible fake server, ingest feature fixture data, ask through the public app/test ingress, then read back created/updated provider objects. Do not pass from serializer strings, tool-call traces, or assistant claims alone.
- Transcript workflow: seed `transcript_records` or equivalent domain rows exactly as the provider ingest path would, run normal worker pickup paths, verify phase transitions, CRM/provider read-back, notification metadata, and idempotent second run.
- Messaging workflow: send through the actual webhook/listener path when possible. For live-capable channels, use a real safe sender/receiver. For local proof, submit signed realistic webhook payloads and capture sender-gateway calls. Verify acknowledgement/final-reply ordering and outbound provider-call order.
- Frontend integration workflow: run the frontend and an API stub/server, drive it with a browser, click connect/disconnect/toggle flows, reload, inspect visible state and screenshots. Source checks are secondary only.
- OAuth/API connection workflow: run the API with a test database and fake provider OAuth/token/profile endpoints, drive authorize -> callback or manual exchange -> status -> select active backend -> disconnect, then verify database rows and status response.
- Workflow-disabled behavior: disable through the public preferences/API path, reload/read status, run the automation that would normally write, and prove no provider write occurs while connection state remains intact.
- Email/read/draft workflow: seed mailbox connection plus provider-compatible mailbox corpus, ask through public app/test ingress or MCP/API tool, verify provider read/draft calls and stored draft content. Do not pass from final assistant text alone.
- PDF/report workflow: seed the source context, call the actual endpoint/orchestration path, render or extract the artifact, and verify grounded content plus missing-fact behavior.
- CLI/subprocess workflow: when an external CLI is the unsafe boundary, a fake executable is acceptable only if the proof crosses the real subprocess boundary and verifies argv/env/cwd/runtime files, durable rows, traces, and user-visible output.

Static source/file/term checks are not valid as the primary proof for user-visible, API,
provider, messaging, frontend, worker, or workflow features. Unit tests and source checks are secondary guards only.

## Workflow
1. Read `FEATURE_DIR/FEATURE.md` and relevant repo docs.
2. Perform Boundary Discovery and write the chosen boundary into `PROOF.md`.
3. Choose one primary behavioral proof from the realistic profiles/recipes above.
4. Run an adversarial proof review before writing artifacts:
   - List at least three plausible fake or incomplete implementations.
   - Explain how the proof would catch each fake implementation through observable behavior.
   - Strengthen weak proof before implementation begins.
5. Create/repair executable artifacts under `FEATURE_DIR/proof/` or repo-native testbed/E2E.
6. Write `FEATURE_DIR/PROOF.md`; run narrowest parser/test when practical.

## Evidence Bundle
For serious feature, issue, UI, API, provider, or workflow proof runs, prefer evidence:

```text
FEATURE_DIR/proof/runs/<timestamp>/
  command.txt
  stdout.txt
  stderr.txt
  result.json
  run-metadata.json
  oracle-scope.md
  attempts.json
  repair-notes.md
  agent-observation.md
  agent-observation.json
  screenshots/
  logs/
  provider-readback.json
  notes.md
```

Only real evidence. No fake screenshots/logs/provider read-back. Bundle should let
`coding-feature-evaluator` inspect latest realistic scenario without trusting summary.
`agent-observation.md` is optional and belongs only to serious autonomous runs where repeated
repair, tactic change, `NEED_INPUT`, evaluator failure, green-but-broken handling, or contract
repair happened.
When the observation may teach project or harness behavior, also include `agent-observation.json`
with the schema in `docs/harness/proof-lifecycle.md`; use it for searchable signals, not a
transcript.

Local command wrapper for serious non-trivial proof:

```bash
scripts/proof_run_capture \
  --serious \
  --feature-dir FEATURE_DIR \
  --behavior-boundary "<producer -> activation -> consumer -> read-back>" \
  --oracle-scope "$(cat FEATURE_DIR/PROOF.md)" \
  --notes "<short proof result summary>" \
  -- <primary proof command>
```

Helper exits with wrapped command status and writes bundle. Do not mark proof authoring
complete when the primary proof is only a raw test command.

## Proof Details
- Prefer `FEATURE_DIR/proof/tests/` for pytest-style checks.
- Use `FEATURE_DIR/proof/run.sh` when clearer.
- When a repo-local API testbed exists, read its parser/CLI contract first.
- If using pytest for primary proof, the test must still drive the realistic boundary and
  read back durable/user-visible effects. Pytest as a runner does not make a unit test
  acceptable as primary proof.
- Messaging/webhook: submit realistic payload fixtures to the listener/API boundary; assert
  state plus outbound provider-client calls.
- Database/queue-driven workflows: seed the same tables, statuses, event IDs, or queue payloads
  the producer writes; let the normal polling/consumer code select the work; assert persisted
  status/output/read-back after the run.
- Idempotency/retry: submit same provider/event ID twice; assert one persisted effect/send.
- Semantic behavior: include paraphrase cases and at least one non-English or
  wording-shifted case when practical. Treat hardcoded natural-language keyword lists as
  fake-pass risks; prove structured outcome, not response phrase only.
- Black-box API/provider proof: no app-internal imports, no mocks/monkeypatching.
- Mocks, fakes, and monkeypatches may replace unsafe or external edges outside the claimed
  boundary, but must not replace the activation path or durable state transition being proven.

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
Type: <scenario-provider | worker-scheduler | webhook-messaging | browser-ui | oauth-api | mailbox | report-artifact | cli-subprocess | migration-data | static-doc | bug-fix>

Boundary:
- Producer: <real producer of the input>
- Activation path: <route/listener/worker pickup/browser flow/CLI/provider callback>
- Consumer: <normal app path that runs unchanged>
- Durable state: <DB/provider/file/artifact/UI/runtime state changed>
- Read-back: <query/provider GET/screenshot/artifact extraction/received message/trace/log proving it>
- Unsafe edge: <live guarded edge or outer fake boundary>

Command:
```bash
scripts/proof_run_capture --serious --feature-dir FEATURE_DIR --behavior-boundary "<producer -> activation -> consumer -> read-back>" --oracle-scope "$(cat FEATURE_DIR/PROOF.md)" --notes "<short proof result summary>" -- <command that runs FEATURE_DIR/proof/... or repo-native proof>
```

Expected evidence:
- <response, UI state, persisted state, provider read-back, invariant>

## Proof Scope
Proves:
- <specific behavior, state transition, side effect, or invariant the proof observes>

Does not prove:
- <important behavior, production condition, live provider state, scale, timing, or path not covered>

False-green risks:
- <how an incomplete or proxy implementation could still pass if the proof scope is too narrow>

Evidence strength:
- deterministic | probabilistic | live gap | manual gap

## Secondary Guards
- <optional lint, typecheck, unit tests, static checks>

## Environment And Data
- <fixtures, services, accounts, credentials, safe targets, readiness command>

## Anti-Gaming Review
- Fake pass risk: <incomplete implementation that might look done>.
- Proof catch: <specific proof step that fails if that fake exists>.
- Boundary: <real trigger/input path the proof drives, and why direct inner calls are enough or not enough>.

## Manual Gaps
- None, or <live verification still needing user-owned input and why>
````

## Rules
- Keep behavior in `FEATURE.md`; verification in `PROOF.md`.
- Every non-trivial feature gets at least one executable proof artifact.
- The primary proof command is the feature completion authority, must run a behavioral artifact, and must be wrapped with `scripts/proof_run_capture`.
- `PROOF.md` must include `Proof Scope` for every non-trivial feature.
- Oracle scope must name what the proof proves, what it does not prove, false-green risks,
  and evidence strength.
- Gate is repo-health guard, not feature proof.
- Static source/file/term checks cannot be the primary proof for user-visible/API/provider/workflow.
- Unit tests, source assertions, serializer assertions, and mocked service-return checks cannot be the primary proof for non-trivial user-visible, provider, messaging, frontend, worker, or workflow behavior.
- If the feature writes externally, reads externally, sends a message, creates a file/report, updates a database row, or changes visible UI, the proof must read that result back from the same durable/user-visible boundary.
- `PROOF.md` must include an anti-gaming review for every non-trivial feature.
- The anti-gaming review must connect fake pass risks to concrete proof steps.
- Successful tool call or assistant claim is not proof when external state is checkable.
- Do not hand off with only a prose `PROOF.md` unless documentation-only or awaiting `NEED_INPUT`.
- Do not run `coding-feature-evaluator` for proof-authoring-only work; use `coding-feature-quality` for proof contract review before implementation.
