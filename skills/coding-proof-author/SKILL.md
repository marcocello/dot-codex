---
name: coding-proof-author
description: "Define or repair realistic executable feature evidence from boundary analysis, real usage states, focused questions, and explicit proof decisions."
---

# Proof Author

Turn a decision-complete `FEATURE.md` into the smallest executable scenario set that would fail when the accepted user outcome is broken. `FEATURE.md` owns behavior; `PROOF.md` owns how it is exercised and observed.

Proof authoring is contract work. Proof questions do not authorize implementation. This skill must not invoke `coding-feature-execute` or edit product behavior; implementation requires a separate explicit request.

## Invariants

- Every non-trivial feature has executable proof.
- Primary activation crosses the public or production boundary that owns the claim.
- Durable or visible effects are read back through the boundary a real consumer uses.
- Fakes replace only unsafe outer edges, never claimed behavior.
- A feature may use prerequisite behavior as setup or the smallest necessary integration canary, but must not import or execute another feature's complete proof.
- `proof/run.sh` contains the complete sequence and its exit code is the result.
- Official runs use `"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture"` with a scenario-specific timeout and note.
- New behavior and known defects produce a meaningful captured red before substantial implementation when safe and practical.
- Static assertions, mocks, lint, builds, typechecks, and unit tests are secondary unless that surface is the accepted boundary.

## Discover The Boundary

Name:

- producer and real input;
- activation path;
- authority that owns each central decision or state;
- primary and materially affected consumers;
- durable or visible state and read-back;
- unsafe external edge;
- plausible central break the proof must catch.

For persisted behavior, seed through the producer boundary, run the normal selector or consumer, and read back the result. Direct inner-service calls are secondary unless the feature claims only that service.

## Select Real Usage States

Choose only states relevant to the accepted outcome, but do not silently assume a fresh installation:

- new data and existing pre-change persisted data;
- save followed by refresh, remount, close/reopen, or restart;
- failure, recovery, retry, cancellation, concurrency, and idempotency;
- permissions, precedence, and multi-owner state transitions;
- provider-native variability and real integration topology;
- health during slow or blocking work;
- UI interaction topology and compatibility through affected consumers;
- the isolated source candidate versus an existing local or deployed runtime.

For configuration and persisted UI behavior, a successful write response is not sufficient read-back. When relevant, prove change -> save -> close/remount -> reopen -> visible value -> dependent behavior.

When an existing local or deployed runtime is the named consumption target, include its activation and read-back in the complete proof sequence. An isolated source pass is intermediate evidence, not a passing feature proof for that target.

Select the smallest set that attacks plausible real failures. State important unexercised states as honest gaps; do not apply every pressure to every feature.

## Decide Proof

Infer deterministic safe defaults before asking: local non-destructive target, bounded fixtures, direct read-back, an outer-edge fake for unavailable providers, and a scenario-appropriate timeout.

Ask proof-specific questions only when an unresolved user-owned choice has no safe default and changes strength, cost, safety, data, destructive effect, credentials, external mutation, or feasibility.

Show a concise proof decision before writing:

- scenarios, activation, real usage states, and read-back;
- authority and affected consumers;
- fake boundaries and central false-green pressure;
- exact environment target: isolated candidate, existing local runtime, or deployed runtime;
- known gaps, command, and timeout.

This is not an approval gate. Proceed when repository context, the request, or safe defaults resolve the choices.

## Author

1. Read current `FEATURE.md`, relevant architecture/testing context, existing proof, and runtime boundary.
2. When `docs/features/status.json` exists, synchronize it in the same task: ensure the queue entry exists as `draft`, and return a non-draft entry to `draft` before creating or materially amending the proof contract or executable proof inputs.
3. Map each central claim to activation, authority, consumer, real usage state, and read-back.
4. Select one relevant profile from [proof-profiles.md](references/proof-profiles.md):
   - bug fix/internal invariant -> Bug Fix And Internal;
   - API/OAuth/provider -> API And Provider;
   - UI/rendered artifact -> UI And Artifact;
   - worker/scheduler/webhook/messaging/queue/CLI -> Reactive And Process Boundaries;
   - semantic behavior -> Semantic Pressure.
5. Use [proof-contract-template.md](references/proof-contract-template.md) for new or materially restructured contracts.
6. Create or repair `PROOF.md`, executable `proof/run.sh`, and only necessary fixtures, tests, and readiness checks.
7. Make the runner print concise non-secret facts identifying the actual application runtime and readiness used.
8. Validate syntax or narrow proof behavior without claiming implementation completion.
9. When the existing queue applies, mark it `ready` in the same task only when the contract and executable proof are decision-complete; otherwise leave it `draft` with the exact next action.

## Execution And Change Guard

Official command:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir FEATURE_DIR --timeout-seconds N --note "reason"
```

The runner must not edit implementation or harness inputs, daemonize, call `setsid`, use `disown`, escape the capture process group, print secrets, or dump the environment. Use `set -euo pipefail` unless explicit result aggregation is required.

After implementation starts, explain any behavior or proof-strength revision. Continue when it remains within the accepted goal; ask only for a new material user-owned choice. Demonstrate strengthened proof against the missed defect when practical, rerun the full proof, and never narrow or weaken it for green. Mechanical runner or fixture repairs need an attempt note and full rerun, not renewed product discussion.

`PROOF.md` must include `Proves`, `Does not prove`, `False-green risks`, `Evidence method`, and `Known gaps`. Do not add hashes, receipts, manifests, evidence schemas, or per-check evidence files unless integrity itself is an accepted requirement.

## Handoff

Report scenarios, environment target, runner, capture command, timeout, fake boundaries, known gaps, and the queue transition. Stop after proof authoring and never claim feature completion.
