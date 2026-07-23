---
name: coding-proof-author
description: "Define realistic executable evidence from boundary analysis, focused questions, and explicit proof decisions."
---

# Proof Author

Purpose: decide evidence that should fail when the feature’s central behavior is broken, then write `PROOF.md` and executable proof artifacts without a contract-approval gate.

`FEATURE.md` says what to build. `PROOF.md` says how the intended behavior will be exercised and observed. Scripts make execution trustworthy; they do not make a weak scenario realistic.

## Invariants
- Every non-trivial feature has at least one executable proof artifact.
- The primary scenario crosses the public or production boundary that owns the claim.
- Durable or visible effects are read back from the same boundary a real consumer uses.
- Fakes replace only unsafe outer edges, never the behavior being claimed.
- `proof/run.sh` contains the complete executable sequence; its exit code is the suite result.
- Official runs use `"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture"` with an explicit timeout and reason.
- New behavior and known defects should produce a captured failing attempt before substantial implementation when the decision-complete proof can run safely and meaningfully.
- Static checks, source assertions, mocks, lint, typecheck, and unit tests are secondary unless the asserted surface is itself the feature boundary.

## Boundary Discovery
Name these before proposing proof:

- Producer: what creates the real input.
- Activation: route, browser action, listener, worker pickup, scheduler, command, callback, or import path the proof drives.
- Consumer: normal application path that must run unchanged.
- Durable/visible state: database row, provider object, file, runtime state, artifact, message, or UI.
- Read-back: query, provider GET, screenshot, extraction, received message, trace, log, or public response.
- Unsafe edge: external mutation that must be live, approval-gated, or replaced at the outermost boundary.
- Central break: plausible incomplete implementation the scenario must catch.

For persisted work, seed input through the producer boundary, allow the normal selector/consumer to run, then read the durable result. Direct inner-service calls are secondary unless the feature explicitly claims only that inner service.

## Proof Questions And Decision
1. Ask proof-specific questions that can change strength, cost, safety, or feasibility: live target, data, destructive effects, credentials, fakes, read-back, probabilistic thresholds, known gaps, timeout.
2. Challenge proxy-only proof. Explain when a unit test or source assertion could pass while the user-visible feature remains broken.
3. Show the proposed proof in chat before writing:
   - scenarios and exact activation;
   - durable/visible read-back;
   - fake boundaries;
   - expected failure pressure;
   - environment/readiness;
   - known gaps;
   - command and timeout.
4. Treat the proposal as a visible decision summary, not an approval request. After answers, write the proof artifacts and continue.
5. Ask and wait only when an unresolved user-owned choice, credential, safe target, destructive effect, live cost, or central known gap prevents a safe and honest proof decision. When the repository and request resolve those choices, proceed directly.

## Profile Routing
Read only the relevant section of [proof-profiles.md](references/proof-profiles.md):

- bug fix/internal invariant -> Bug Fix And Internal;
- API/OAuth/provider -> API And Provider;
- UI/rendered artifact -> UI And Artifact;
- worker/scheduler/webhook/messaging/queue/CLI -> Reactive And Process Boundaries;
- semantic behavior -> Semantic Pressure.

Use [proof-contract-template.md](references/proof-contract-template.md) when creating or materially restructuring the proof contract.

## Workflow
1. Read decision-complete `FEATURE.md`, existing proof, repository architecture/testing docs, and the real runtime boundary.
2. Perform Boundary Discovery and select the smallest realistic profile.
3. Map every central feature claim to activation and read-back.
4. Name plausible fake or incomplete implementations and ensure a concrete step catches each central one.
5. Run Proof Questions And Decision.
6. Create or repair `PROOF.md`, executable `proof/run.sh`, and only necessary fixtures/tests/readiness checks.
7. Make `proof/run.sh` print concise non-secret facts about the actual application runtime and readiness used by the scenario.
8. Keep the runner direct and deterministic where possible. Use `set -euo pipefail` for shell runners unless the scenario requires explicit result aggregation.
9. Validate the proof artifact syntax or narrow behavior without claiming implementation completion.
10. Mark the feature `ready` only when `FEATURE.md`, `PROOF.md`, and executable proof are decision-complete and no material user-owned question remains.

## Capture Contract
Official execution command:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir FEATURE_DIR --timeout-seconds N --note "reason"
```

The caller selects a positive scenario-specific timeout. The runner must not edit implementation or harness inputs, daemonize, call `setsid`, use `disown`, or escape the capture process group. Do not print secrets or customer data.

Generic capture records the capture process, not the application stack. At the start of `proof/run.sh`, print the relevant actual application runtime to stdout: executable path and version for the selected interpreter/tool, plus only the non-secret runtime mode, container/service versions, or readiness facts needed to explain the scenario. Do not dump the full environment.

Do not add file hashes, manifests, receipts, evidence locators, schema versions, or per-check evidence files merely to attest the run. Use direct assertions and captured output. Add integrity metadata only when integrity is itself an accepted feature requirement.

## External Readiness
- Prefer safe live proof when real provider state is central and credentials plus a safe target exist.
- When live proof is unavailable, fake only the outer provider/client boundary and declare the gap honestly.
- Add a focused readiness command when environment or credentials can be checked mechanically.
- Approval-risk or destructive proof requires the exact command, target, effect, and reason.
- A central unproven behavior cannot be downgraded to an acceptable manual gap merely to declare completion.

## Proof Change Guard
After implementation starts:

- Behavior or proof-strength change: explain the defect, show the revised decision, and continue when it remains within the user’s stated goal. Ask only when the revision creates a material unresolved product, safety, cost, or external-effect choice.
- Mechanical runner, fixture, or setup repair with unchanged meaning: explain in the next attempt note and rerun the full proof.
- When practical, demonstrate that the strengthened proof fails against the incomplete implementation for the intended reason.
- Compare retained copies to ensure the final proof did not narrow the accepted goal.
- Never weaken, skip, or delete proof to get green.

Before substantial implementation of new behavior or a known defect:

- Capture the decision-complete proof failing for the intended reason when it can run safely and meaningfully.
- A passing attempt means the behavior may already exist or the proof may be weak; investigate before coding.
- When a useful red attempt cannot be produced, retain the exact reason in the first implementation attempt note. Do not present an older PASS as red pressure.

## Rules
- Keep behavior in `FEATURE.md`; verification in `PROOF.md`.
- Include `Proves`, `Does not prove`, `False-green risks`, `Evidence method`, and `Known gaps`.
- Gate, evaluator, build, lint, and source inspection do not replace realistic proof.
- No hashes or evidence-control metadata for ordinary feature proof.
- Successful tool calls and assistant prose are not read-back.
- Proof-authoring-only work does not run the final evaluator.
- If executable proof cannot be designed honestly, return `NEED_INPUT` with the exact product, environment, credential, or safe-target requirement.

## Handoff
Report the decided scenarios, executable runner path, official capture command, timeout, fake boundaries, known gaps, and queue readiness. Do not claim feature completion until implementation is exercised.
