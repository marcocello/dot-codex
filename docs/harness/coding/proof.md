# Shared Proof Contract

Read when Shape delegates acceptance, Ship freezes/runs it, or Fix restores required proof or diagnoses its setup. This reference owns the shared acceptance boundary; each skill owns its delivery procedure.

## Separate Authorship

Before implementation, a separate author receives the specification, relevant original dialogue/corrections, repository context, and consumption target. It writes `PROOF.md`, dedicated tests, and executable `proof/run.sh`; it may inspect source/reuse utilities but cannot implement behavior or change the specification. Compare the specification with the original user outcome and challenge omitted ordinary states that could defeat it. Missing decisions go to the user through Shape; do not silently reduce the claim to match the specification. Missing authorship is not permission for implementer-authored acceptance.

Place acceptance under the feature's `proof/`; if a framework requires elsewhere, preserve feature grouping and record paths. Map scenarios to dedicated tests and all acceptance-determining fixtures/helpers/configuration. Keep implementer regressions separately with the owning feature, e.g. `tests/`. Do not relabel a generic suite as proof or execute/import another feature's whole proof; reuse utilities and reproduce prerequisites as setup.

## Required Boundary

Name real input/producer, public activation, state/decision owner, affected consumer, visible/durable read-back, exact target, unsafe external edge, and plausible central break. Exercise the accepted journey or invariant so removing/bypassing the central behavior fails. Use fakes only at unsafe/unavailable outer edges, not around claimed behavior. Cover relevant state, reopening/restart, error/retry, concurrency, permissions, or provider variability without applying every pressure universally. Include the relevant starting condition that defeats a shallow implementation: for automatic defaults, a pre-populated fixture alone cannot establish first-use behavior with no configured default. Carry accepted discovery cases into observable assertions.

UI proof uses genuine user/browser actions and loaded, decoded, visible resources—not handler calls or dispatching DOM events. Claimed domain effects cross the normal protected API and are read back; presentation-only scope is explicit. API/worker/CLI proof activates the real route/process and verifies observable or persisted effects. Semantic proof judges outcomes across paraphrases, not exact wording. Generic build/lint/gates, source inspection, writes without read-back, or assistant claims cannot replace the accepted boundary. Source success is intermediate for a live target.

## Contract

`PROOF.md` records Done, Command, scenario/test mapping (activation, consumer, read-back, fake, defect caught), Proves/Does not prove, false-green risks, evidence method, gaps, and environment/target. The runner is fail-fast (`set -euo pipefail` unless deliberately aggregating), emits concise non-secret readiness facts, never edits implementation/acceptance, and never daemonizes or escapes capture.

## Fixed Acceptance

Freeze versions of `FEATURE.md`, `PROOF.md`, runner, tests, and every acceptance-determining shared input before Ship; compare before verification/completion. Implementers change application code and separate regressions only.

Only the independent author may correct demonstrably faulty setup between attempts. Establish the error from unchanged contracts/dialogue, not merely a failing candidate. Keep specification, proof document, scenarios, assertions, outcomes, selection, target, and real/fake boundaries unchanged. Never skip assertions, seed the tested result, or move behavior into a fake. Retain original failure/inputs, author, exact diff, contract-grounded rationale, and revised hashes outside `PROOF.md`; rerun affected checks and complete proof, then let the final reviewer inspect the correction. Stay in the same feature/claim/Goal; unavailable author pauses that repair.

Changed or ambiguous acceptance requires the user's decision before revision. Preserve failed evidence, pause dependent work only, then the separate author revises proof and the specification/any Goal are aligned before refreezing. Switching modes cannot bypass this rule. Broken observed behavior overrides a passing claim.

## Restore Unrunnable Proof

For required proof with obsolete/missing tests or setup, a separate author restores executability from retained contracts, history, and user corrections. Existing verification authorization covers restoration. Archive originals/failure; preserve scenarios, assertions, outcomes, target and real/fake boundaries, documenting necessary path mappings and rationale. Candidate behavior is not the expected-results oracle. Ambiguous acceptance needs the user; absent access cannot justify a weaker target. Freeze restored inputs, rerun full captured proof and required review; old passes remain history.

## Official Attempts

Use [evidence capture](evidence.md#evidence-for-one-feature) for official proof and separate supporting regressions. Retain meaningful red, distinct failures, interrupted attempts, and final green. A newer failed/unfinished official attempt invalidates an older PASS; regressions never establish acceptance.

Capture currently detects changes to FEATURE/PROOF/runner during an attempt, not all test inputs across implementation. Recorded hashes are audit evidence, not a trusted write boundary; do not claim runtime isolation the host does not provide.
