# Proof

Proof is the most realistic executable test of the accepted feature: exercise the actual journey or agreed boundary and observe whether it works correctly. `FEATURE.md` owns behavior; `PROOF.md` owns activation and observation; `proof/run.sh` owns the executable result.

## Separate Authorship

Before implementation, a separate agent receives the specification, relevant original conversation and corrections, repository context, and named target. It writes the proof document, dedicated tests, fixtures, and runner. It can inspect source and reuse utilities, but cannot implement the feature or change its specification. Missing decisions return to the main agent's Shape conversation. An unavailable separate author is a missing capability, not permission for the implementer to author acceptance.

Verify requested outcomes and agreed interfaces. Internal filenames, functions, or architecture are acceptance only when the user or specification requires them. Keep scenarios concrete rather than adding a probabilistic-proof framework.

Create tests specifically for the feature's proof scenarios and keep them with the feature under `docs/features/<id>/proof/`. `PROOF.md` maps each scenario to its dedicated proof test or test group and records the exact acceptance inputs; `proof/run.sh` executes that selection. When a framework requires another location, preserve the feature grouping there and record those paths in `PROOF.md`. Reuse fixtures, drivers, and assertion utilities, but do not relabel a generic existing suite as proof. Internal gates, builds, lint, and broader regressions are the agent's responsibility, outside the user-facing proof contract and proof runner.

Organize tests by the feature behavior they verify. Keep implementer-authored internal and regression tests alongside the owning feature, separately from frozen acceptance, for example in `docs/features/<id>/tests/`. Reuse shared test utilities across features while keeping scenarios and assertions associated with their owner. Later changes select checks for all affected features; test maintenance follows that ownership and the fixed-acceptance rules below. Retain original acceptance and run evidence when an agreed behavior change requires revised tests.

## Required Boundary

Name the producer and real input, public or production boundary, authority that owns central decisions or state, primary and affected consumer, relevant usage states, visible or durable read-back, unsafe external edge, exact consumption target, and most plausible central break.

Strong proof:

- activates the real public or production boundary;
- reads the effect back through the affected consumer or durable state a real consumer uses;
- uses fakes only at an unsafe outer edge, never around the claimed behavior;
- includes relevant existing persisted state, refresh/reopen/restart, failure, retry, cancellation, concurrency, permissions, precedence, or provider variability without applying every pressure universally;
- fails when the central implementation is removed, bypassed, or routed to the wrong owner;
- distinguishes an isolated candidate from an existing local or deployed target.

The dedicated tests must reach the accepted boundary. Successful writes without read-back, direct inner-service calls for a claimed user journey, handler invocation without real UI interaction, source URLs without rendered resources, and assistant prose cannot substitute for that boundary. Purpose-built tests of a parser, CLI, or invariant can be proof when that is the feature's actual claim; a generic passing unit suite is not.

## Profiles

- Bug/internal: focused regression, real invariant, equivalence, migration result, parser, or generator.
- API/provider: call the real route/client, fake only unavailable outer provider calls, and verify state plus public status or side effects.
- UI/artifact: use genuine browser/user actions and rendered/readable output. Calling handlers or directly dispatching DOM events is not interaction proof. Confirm resources are loaded, decoded, and visible rather than checking only a URL or source attribute. Domain effects cross the real protected application API through its normal authentication/authorization path and verify visible or durable state. Keep presentation-only states explicit, and fake only unsafe outer providers. Inspect screenshot or artifact layout when material.
- Worker/webhook/CLI/process: seed the producer's real payload, activate the worker/listener/subprocess boundary, and verify persisted output, ordering, retry, and observable command context.
- Semantic: assert structured outcomes across paraphrases and wording shifts rather than exact natural-language phrases.

## Contract

`PROOF.md` includes:

```text
Done
Command
Scenario(s): producer/activation, consumer, read-back, fake, catches
Dedicated proof test(s) for each scenario
Proves
Does not prove
False-green risks
Evidence method
Known gaps
Environment and target
```

The executable runner uses `set -euo pipefail` unless deliberate result aggregation is required, prints concise non-secret runtime and readiness facts, does not edit implementation or accepted proof inputs, and does not daemonize or escape the capture process group.

A feature runner must not import or execute another feature's complete proof. Reproduce prerequisite behavior as setup, reuse shared utilities, and author any needed boundary scenario specifically for the current proof. Run supporting regression checks separately.

## Official Attempts

Run:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir FEATURE_DIR --timeout-seconds N --note "reason"
```

The default capture kind is `proof`. Capture supporting regression commands separately with `--kind regression` as described in [per-feature evidence](evidence.md#evidence-for-one-feature); those runs never establish acceptance. Debugging checks are not official attempts. Retain meaningful red when practical, materially distinct failures, and final green. Do not use an older pass while a newer attempt is incomplete or unresolved. Retain authorship, input versions, target, and relevant dialogue links through [evidence.md](evidence.md).

The final `proof_run` path is repository-relative, lives under the owning feature's `proof/runs/`, and contains a `result.json` with `PASS`. Passing source evidence remains intermediate when the named target is an existing runtime.

## Restore Unrunnable Proof

When proof needed for the current work cannot run because its tests were removed, paths became obsolete, or its execution setup no longer matches the repository, proceed with restoration through a separate proof author. Existing authorization to verify or repair the feature covers this recovery; do not ask for approval solely to restore executability. Restore the relevant feature's proof when needed, rather than rebuilding every historical package.

Retain the original contracts, runner, available tests, previous run evidence, and the observed failure before editing. The independent author reconstructs the executable proof under the feature's current `proof/` structure from its accepted specification, original proof, available history, and user corrections. Preserve scenarios, assertions, expected outcomes, target, and real/fake boundaries. Update runner paths and document path mappings in `PROOF.md` as needed, retaining the original version and a restoration rationale. This is a recovery of the same acceptance; passing current implementation behavior is not a source of expected outcomes.

If the accepted checks cannot be recovered unambiguously, ask only for the missing behavior decision and continue independent work. Missing runtime access remains an access dependency; it does not justify substituting a weaker target. An executable proof reporting incorrect product behavior requires code repair, not reconstruction to obtain a pass.

Record the author, original failure, old-to-new test mapping, and revised input versions with the feature's evidence. Freeze the restored inputs, run complete proof through `proof_run_capture`, and obtain the review required by the current workflow before claiming renewed verification. Old results remain historical evidence and cannot validate the restored proof. This restoration procedure permits the necessary file/path changes while the fixed-acceptance rules continue to govern behavior and subsequent implementation.

## Fixed Acceptance

At the start of Ship, record versions of `FEATURE.md`, `PROOF.md`, runner, acceptance tests, and all fixtures/helpers/configuration determining acceptance, including shared inputs outside the feature directory. Keep them fixed except for the independent setup repair below, and compare their versions before verification and completion. Implementers may change application code and add separate regression tests; they cannot edit frozen proof inputs.

The independent proof author may repair demonstrably faulty test setup without asking the user. Establish the error from the unchanged specification, proof document, conversation, and existing repository contracts, not merely the candidate's behavior or a failing test. Change only setup code, including fixtures/helpers/configuration, wherever defined; keep `FEATURE.md`, `PROOF.md`, scenarios, required assertions, expected outcomes, test selection, target, and real/fake boundaries unchanged. For example, configure an approval policy before the activity that snapshots it, or create a truly separate channel for an existing access-denial test. Never skip a check, relax an assertion, seed the result being tested, or move the tested behavior into a fake.

Make setup corrections between proof attempts. Retain the original inputs and failure plus the author's identity, exact diff, and evidence-based rationale in run evidence outside `PROOF.md`. Record the revised input versions, rerun affected checks, and run complete feature proof before final review; an earlier PASS cannot validate revised inputs. The existing final reviewer checks the correction. Keep the same feature, Ship claim, Goal, and allowance; this repair does not return to Shape or require an extra reviewer. The implementer can diagnose and request the author's repair but cannot make it. If the independent author is unavailable, pause that repair rather than granting it to the implementer.

If observed behavior contradicts proof, preserve the evidence and distinguish ordinary code repair, independent setup repair, and an acceptance decision. A correction that changes required behavior, assertions, coverage, or test boundaries, or whose meaning cannot be established from the agreed contract, requires the user's decision before revision. Pause only dependent work, ask once, and continue authorized independent work. After agreement, the separate author revises proof, the specification and Goal are aligned, and acceptance is fixed again before dependent implementation resumes. The same rules apply to reviewer findings. A later behavior request normally starts a new cycle while retaining the completed run's originals.

The current `proof_run_capture` detects changes to `FEATURE.md`, `PROOF.md`, and `run.sh` and their retained copies during one attempt. It does not protect all test inputs across implementation, nor prevent a writer from changing the checkout between attempts. Recorded digests are an audit guard, not a trusted write boundary. Strong protection requires runtime permissions the implementer cannot rewrite; do not claim that skills or current capture provide that guarantee.
