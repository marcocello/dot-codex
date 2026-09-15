# Four-Mode Coding Workflow Proof

## Done

- One registered `coding-workflow` skill exposes four modes through progressive disclosure and the old lifecycle skills and compact duplicates are absent.
- `AGENTS.md`, README, and consolidated harness references route through the new workflow without duplicating mode procedures.
- `status.json` is mandatory and gate-validated for adopting repositories, versioned, complete for every durable feature package, and uses `draft`, `ready`, `active`, `blocked`, and `done` with an owning `proof_run` evidence pointer.
- Shape, Ship, Fix, and Operate preserve artifact, authorization, proof, repair, runtime, and steering rules. Proof tests are purpose-built, same-checkout parallel work is the default, and early review is discretionary rather than category-triggered. Policy meaning is inspected by the fresh final reviewer; executable structure checks do not demonstrate future model behavior.
- The current installed checkout executes the tests authored specifically for this feature: `tests/unit/test_feature_status.py` for the public status commands and `tests/unit/test_coding_workflow_v2.py` for workflow package structure. `proof/run.sh` selects these tests explicitly. Generic regression suites and the repository gate are separate internal checks, not part of this proof runner or acceptance contract.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/four-mode-coding-workflow --timeout-seconds 120 --note "verify four-mode coding workflow v2"
```

## Scenario: One progressively disclosed lifecycle replaces orchestration handoffs

- Dedicated tests: `test_one_registered_workflow_replaces_lifecycle_skill_graph`, `test_progressive_references_own_each_mode_and_shared_contract`, and `test_kernel_and_docs_route_without_duplicating_mode_procedures` in `tests/unit/test_coding_workflow_v2.py`.

- Producer/activation: pytest parses `skills.toml`, the real workflow skill and references, agent metadata, `AGENTS.md`, README, and harness docs.
- Consumer: Codex receiving shaping, implementation, defect, runtime, correction, sensitive, or autonomous-continuation requests.
- Read-back: assertions require one lifecycle owner, exactly four public modes, selective reference loading, and retirement of decomposed and compact duplicate lifecycle skills.
- Fake: none.
- Catches: renaming the old pipeline, creating four new skill owners, retaining hidden compatibility routes, or losing a mode during consolidation.

## Scenario: Mandatory durable status remains small and truthful

- Dedicated tests: `tests/unit/test_feature_status.py` cases for unsupported done, competing and independent claims, stale state, ownership, atomic registration, lock timeout, and mandatory adoption; current-package checks in `tests/unit/test_coding_workflow_v2.py`.

- Producer/activation: pytest parses the actual `docs/features/status.json` and status contract.
- Consumer: feature shaping, explicit implementation, resumed work, queue continuation, blocking, completion, and later contract correction.
- Read-back: real gate subprocesses reject missing, malformed, null, failed, foreign, stale, and unresolved-newer completion evidence without legacy exceptions. Real concurrent `feature_status` subprocesses claim different features without losing updates, reject competing claims to the same feature, reject foreign-owner transitions, and preserve valid JSON on rejected writes. Separate active owners are accepted; duplicate active ownership is rejected.
- Fake: proof-result files are fixtures at the evidence boundary; the validators, atomic updater, and filesystem read-back are real.
- Catches: optional queue creation, duplicate feature entries, ready items being selected while already implemented elsewhere, status growing into a todo system, or unsupported `done` state.

## Scenario: Proof and completion strength survive consolidation

- Dedicated tests: workflow structure and current completion-pointer checks in `tests/unit/test_coding_workflow_v2.py`; strict completion and invalidated-completion reopening in `tests/unit/test_feature_status.py`.

- Producer/activation: the feature-specific workflow tests inspect Shape, Ship, Fix, Operate, proof, status, safety, and handoff policy; the final reviewer checks their meaning against the user request.
- Consumer: a user relying on a passing proof instead of manually retesting the claimed behavior.
- Read-back: assertions require public/production activation, affected-consumer or durable read-back, outer-edge-only fakes, meaningful red, internal Ship repair, exact-target verification, final-candidate freshness, one fresh separately invoked final oracle owned by Ship, and proof-defect recovery.
- Fake: none for instruction inspection; isolated repositories and local subprocesses exercise the actual status commands.
- Catches: gate-only completion, source-only runtime claims, review replacing executable evidence, or a green proof that bypasses the real consumer.

## Scenario: Existing behavior refinements become explicit transitions

- Dedicated tests: progressive-mode structure check in `tests/unit/test_coding_workflow_v2.py` and completion/reopening subprocess scenarios in `tests/unit/test_feature_status.py`. Final review, not phrase assertions, judges discretionary review and same-checkout coordination policy.

- Producer/activation: pytest reads transition and steering policy across the main workflow, Shape, Ship, Fix, and status references.
- Consumer: a user correcting terminology, interaction details, provider journey, architecture ownership, or proof expectations during implementation.
- Read-back: compatible guidance continues in Ship; material behavior or proof corrections demote the feature to `draft`; clear defects use Fix; missing capabilities use Shape.
- Fake: none.
- Catches: labeling every correction as changed business requirements, silently coding against a stale contract, or turning internal Ship failures into cross-skill handoffs.

## Scenario: Another feature's local defect does not block this task

- Producer/activation: purpose-built `test_independent_update_ignores_other_feature_local_defects` seeds two features in one temporary checkout and invokes the actual `feature_status` command.
- Consumer/read-back: task A claims and completes its feature despite task B's missing, failed, or unfinished proof, absent package artifact, or invalid notes. B's entry remains identical. A still cannot complete without its own passing proof. Collection-wide internal validation still detects B's defect.
- Fake: retained result fixtures at the evidence-file boundary, not around status update logic.
- Catches: global evidence validation serializing independent tasks, silently repairing another task's entry, or weakening target completion checks to obtain isolation.

## Scenario: Runner executes dedicated proof tests, not generic checks

- Dedicated test: `test_proof_runner_executes_only_its_dedicated_tests_and_propagates_failure` in `tests/unit/test_coding_workflow_v2.py`.
- Producer/activation: execute the actual `proof/run.sh` in an isolated checkout with a recording Python driver fixture.
- Consumer/read-back: verify exactly the two purpose-built test-module selections, no generic gate invocation, and immediate propagation of a failing proof-test command.
- Fake: Python test-driver edge only, to observe dispatch and failure handling; the normal official run executes real pytest separately.
- Catches: silently adding generic suites to proof, hiding a failed proof test, or abandoning the feature-specific selections.

## Scope

Proves:
- The current checkout exposes the accepted workflow and executable completion/concurrent-status boundaries. Tests were authored for these proof scenarios; they are not a generic existing suite relabeled as proof. Policy inspection is not behavioral evidence of future model judgment.

Does not prove:
- That every future model invocation selects the correct mode or asks every useful product question.
- Subjective UI preference that is absent from accepted observable behavior.
- Refreshed skill discovery in an already-running Codex task; boot-time skill discovery requires a new task.

False-green risks:
- Static wording could exist without coherent ownership, so executable tests cover structure and real status subprocess behavior while the final reviewer evaluates the policy changes. Neither proves that future agents always coordinate shared edits or choose the right scenarios.

Evidence method:
- deterministic purpose-built structure and status-subprocess tests plus fresh final review

Known gaps:
- Future LLM mode selection and oracle quality remain probabilistic.
- Fresh-session discovery and cooperation between tasks remain boundaries. The status helper does not lock source files or runtime resources; stable proof windows and overlap coordination are agent responsibilities, not a claimed scheduler capability.

## Environment

- Confirm the Impeccable Git declaration is absent through inventory read-back and the existing native plugin remains installed. Do not install or update the plugin for this check.
- Concurrent status tests cover stale expected-state rejection and byte-identical status after rejected mutations. The lock is a persistent sidecar and covers read through atomic replacement.
- Adoption fixtures remove the entire feature directory and require rejection for the harness profile and the application `--require-feature-status` gate flag. Git read-back verifies the executable helper is not ignored and can be delivered.

- Repository-local Python 3.13, pytest, and PyYAML through `.venv`.
- No credentials, network, deployment, paid resource, or external mutation.
