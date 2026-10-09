# Shared Proof Contract

In this harness, **proof** and **acceptance test** mean the same thing: a realistic check of the specified behavior through the UI, API, or CLI as appropriate. Choose the interface that exercises the promised behavior and verify its observable result; use more than one only when needed. Do not create separate proof and acceptance-test layers. Saved run results are the evidence.

Acceptance rules for Design Specs and Proof, Implement, and feature-owned Repair. [AGENTS.md](../../../AGENTS.md) owns authorization.

Read [Coding writing](writing.md) for proof plans and reports. Preserve accepted outcomes, assertion strength, uncertainty, and observation boundaries when simplifying prose. Style checks do not establish acceptance.

Choose technique and depth for the accepted slice. Every criterion needs evidence; no feature is required to have a separate runner. Prefer [mapped focused checks and shared journeys](rounds.md) for multi-feature work. Use [boundary examples](proof-guidance.md) when helpful.

## Acceptance Authorship

Start from the narrow feature spec and original request. Write or reuse acceptance tests before dependent implementation; expected results come from the promised behavior, never from whatever the implementation happens to do. Map each criterion to focused checks or a shared journey. One journey may prove several features; do not create a full suite per feature.

The same agent may specify, author tests, implement, and check the result. Delegate when useful or explicitly requested. There are no risk levels, role modes, required separate agents, or role-selection records. Attribution records who actually did the work.

Keep the observation independent of the operation being tested: use public activation and authoritative read-back. Separate regressions from acceptance. Reusing a test requires checking that its assertions actually establish the promised outcome.

## Required Boundary

- Name input/producer, public activation, state owner, consumer, read-back, target, and external edge.
- Make bypassing the central behavior fail. Fake only unsafe/unavailable outer edges, never claimed behavior.
- Select relevant starting states, restart, errors, retries, concurrency, permissions, and provider variability.
- Assert accepted discovery cases and plausible incomplete implementations. Prefilled fixtures alone cannot prove first-use defaults; uncovered behavior remains a gap.
- At authoring and final review, ask: **Which promised ordinary action could fail while this proof passes?**
- Exercise the real entry/launch mode. Resolve material response-time expectations through Product Partner.
- Report measured limits without guessing causes. A generous timeout does not establish usability.
- UI: real browser/user actions and loaded, decoded, visible resources; no handler calls or dispatched DOM events.
- Domain effects: normal protected API plus read-back. Label presentation-only scope.
- API/worker/CLI: actual route/process plus observable results.
- Judge semantic outcomes across paraphrases, not exact wording.
- Gates, builds, source inspection and unobserved writes are not acceptance. A live-target claim needs observation on that target.

## Contract

PROOF records:

- Done, Command, environment/target, and evidence method.
- Scenario/test mapping: activation, consumer, read-back, fake, defect caught.
- Proves/Does not prove, false-green risks, and gaps.
- Deterministic assertions, sampled evidence, and unavailable live/manual checks.
- Case/repetition rationale and pass criteria for variable behavior; one sample cannot prove reliability.

Runner rules:

- Fail fast (`set -euo pipefail` unless deliberately aggregating).
- Emit non-secret readiness facts. Never edit application/acceptance, daemonize, or escape capture.
- Before expensive runs, the author checks changed helpers, readiness, fault synchronization, browser events, and cleanup as applicable.
- Reuse short checks; no mandatory preflight framework. Syntax or missing-environment exits do not prove runnable scenarios.
- Substitutes validate machinery only. Keep unavailable integration checks as prerequisites.
- Repeat machinery checks only for relevant changes or failures.

Blocked setup:

- Inspect docs, local tools, and authorized access first.
- Name the prerequisite, blocked step, safe target, success read-back, owner, and unblocking action.
- Use established credential setup; never expose secrets. Record gaps in existing evidence.
- Respect pending questions and continue independent work.

## Fixed Acceptance

Keep accepted contracts, assertions and determining inputs stable during official verification. Repair tests between attempts under the rules below, preserving ownership when work is delegated.

### Decision Boundary

- **Setup defect:** assigned author repairs between attempts. Keep FEATURE, PROOF, scenarios, assertions, outcomes, selection, target, and real/fake boundaries unchanged.
- **Technical contract error:** author may repair without asking when accepted intent is established. Preserve outcomes, coverage, assertion strength, target, observation independence, and real/fake boundaries.
- **Missing assertion:** author may add coverage for already-agreed outcomes. New product choices return to Product Partner.
- **Unresolved choice:** ask if behavior, scope, cost, permissions, meaningful risk, or accepted outcomes differ. Explain consequences; pause dependent work until answered.

Every repair:

- Ground it in retained contracts/dialogue and independent evidence, not candidate failure alone.
- Retain original failures/inputs, author, exact diff, rationale, and revised hashes.
- Keep setup repair records outside PROOF. Stay in the same feature/claim/Goal.
- [Rerun affected checks](rounds.md#rerun-only-affected-checks) and assess the combined result. Keep unchanged scoped evidence; a monolithic package requires its full rerun.

Never:

- Infer the oracle from the candidate, relax requirements, skip assertions, or seed the tested result.
- Move claimed behavior into a fake or narrow the promise because a provider is unavailable.
- Treat read-only calls as authorization for broader credentials.
- Require approval merely because a frozen file changes, or bypass boundaries by switching modes.

After an agreed consequential revision, align FEATURE/Goal and have the author revise proof. Observed failure overrides a pass.

## Restore Unrunnable Proof

- Restore required proof from retained contracts, history, and corrections.
- Existing verification authority covers restoration; preserve scenarios, assertions, outcomes, target, and real/fake boundaries.
- Document path mappings. Apply repair evidence and decision rules above.
- Capture the restored affected checks and required composed journeys, then obtain review. Old passes remain history; unchanged separately scoped checks may be reused under the round rules.

## Official Attempts

- Use [evidence capture](evidence.md#evidence-for-one-feature); keep regressions separate.
- Retain meaningful red, distinct failures, interruptions, and final green.
- A newer failed/unfinished official attempt invalidates an older PASS for that check package, not every independent check in the round. Regressions never establish acceptance by themselves.
- Capture checks the recorded repository candidate and owning acceptance tree before/after execution, retaining scope and target. Include otherwise ignored determining inputs explicitly; see [capture limits](evidence.md#current-candidate-and-review).
- New completion requires current evidence and an attributed completion receipt. Historical passes remain history, not current regression assurance.
- Hashes and role identifiers are audit evidence, not enforced write isolation, authentication, or external runtime attestation.
