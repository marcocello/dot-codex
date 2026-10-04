# Shared Proof Contract

Acceptance rules for Design Specs and Proof, Implement, and feature-owned Repair. [AGENTS.md](../../../AGENTS.md) owns authorization.

Choose technique and depth for the accepted slice. Use [role briefs and boundary examples](proof-guidance.md) when helpful; they introduce no additional stage, quota, or approval.

## Separate Authorship

- Use a separate author before implementation. Supply FEATURE, dialogue/corrections, app context, and target.
- Apply [product discovery and autonomy](../../../skills/coding-product-partner/SKILL.md#discovery-and-autonomy): ground acceptance in the request, actual decisions, and justified explicit assumptions. Return unresolved consequential user choices before freezing dependent acceptance; no extra discovery round is required for sufficiently clear authorized behavior.
- The author writes PROOF, dedicated tests, and executable `proof/run.sh`.
- The author may inspect code and reuse utilities; it cannot implement behavior or edit FEATURE.
- Derive the starting state, ordinary action, and consumer result from the original request/corrections before reconciling the proposed FEATURE. Investigate disagreement instead of letting the specification and fixtures validate the same unsupported assumption. Return product gaps to Product Partner; never narrow the promise silently.
- An unavailable author does not permit implementer-authored acceptance.
- Keep acceptance under feature `proof/`; record framework-required alternative paths.
- Map scenarios to tests and all determining fixtures/helpers/configuration.
- Keep implementer regressions separate. Never import another feature's whole proof or relabel generic tests.

## Required Boundary

- Name input/producer, public activation, state owner, consumer, read-back, target, and external edge.
- Make bypassing the central behavior fail. Fake only unsafe/unavailable outer edges, never claimed behavior.
- Select relevant starting states, restart, errors, retries, concurrency, permissions, and provider variability.
- Carry accepted discovery cases into assertions.
- Prefilled fixtures alone cannot prove first-use defaults.
- Map plausible incomplete implementations to failing assertions. Uncovered material risks remain gaps.
- Reuse infrastructure. Reduce redundant machinery, not accepted coverage.
- At authoring and final review, ask: **Which promised ordinary action could fail while this proof passes?**
- Exercise the real entry/launch mode. Resolve material response-time expectations through Product Partner.
- Report measured limits without guessing causes. A generous timeout does not establish usability.
- UI: real browser/user actions and loaded, decoded, visible resources; no handler calls or dispatched DOM events.
- Domain effects: normal protected API plus read-back. Label presentation-only scope.
- API/worker/CLI: actual route/process plus observable results.
- Judge semantic outcomes across paraphrases, not exact wording.
- Gates, builds, source inspection, unobserved writes, and assistant claims are not acceptance.
- Source success is intermediate for live targets.

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

- Freeze FEATURE, PROOF, runner, tests, and all determining shared inputs before Implement.
- Compare inputs before verification/completion. Implementers edit application and separate regressions only.

### Decision Boundary

- **Setup defect:** independent author repairs between attempts. Keep FEATURE, PROOF, scenarios, assertions, outcomes, selection, target, and real/fake boundaries unchanged.
- **Technical contract error:** author may repair without asking when accepted intent is established. Preserve outcomes, coverage, assertion strength, target, observation independence, and real/fake boundaries.
- **Missing assertion:** author may add coverage for already-agreed outcomes. New product choices return to Product Partner.
- **Unresolved choice:** ask if behavior, scope, cost, permissions, meaningful risk, or accepted outcomes differ. Explain consequences; pause dependent work until answered.

Every repair:

- Ground it in retained contracts/dialogue and independent evidence, not candidate failure alone.
- Retain original failures/inputs, author, exact diff, rationale, and revised hashes.
- Keep setup repair records outside PROOF. Stay in the same feature/claim/Goal.
- Refreeze, rerun complete proof and affected checks, and obtain final review.
- An unavailable author pauses the repair.

Never:

- Infer the oracle from the candidate, relax requirements, skip assertions, or seed the tested result.
- Move claimed behavior into a fake or narrow the promise because a provider is unavailable.
- Treat read-only calls as authorization for broader credentials.
- Require approval merely because a frozen file changes, or bypass boundaries by switching modes.

After an agreed consequential revision, align FEATURE/Goal and have the author revise proof. Observed failure overrides a pass.

## Restore Unrunnable Proof

- Have a separate author restore required proof from retained contracts, history, and corrections.
- Existing verification authority covers restoration; preserve scenarios, assertions, outcomes, target, and real/fake boundaries.
- Document path mappings. Apply repair evidence and decision rules above.
- Run full captured restored proof and required review. Old passes remain history.

## Official Attempts

- Use [evidence capture](evidence.md#evidence-for-one-feature); keep regressions separate.
- Retain meaningful red, distinct failures, interruptions, and final green.
- A newer failed/unfinished official attempt invalidates an older PASS. Regressions never establish acceptance.
- Capture checks the recorded repository candidate and owning acceptance tree before/after execution, retaining scope and target. Include otherwise ignored determining inputs explicitly; see [capture limits](evidence.md#current-candidate-and-review).
- New completion requires current evidence and an attributed independent review receipt. Historical passes remain history, not current regression assurance.
- Hashes and role identifiers are audit evidence, not enforced write isolation, authentication, or external runtime attestation.
