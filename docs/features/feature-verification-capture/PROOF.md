# Feature verification capture proof

## Done

The installed capture CLI retains exact feature verification execution evidence, separates regression from acceptance, and the real completion boundary rejects regression evidence.

## Command

Run `proof/run.sh` through the installed `proof_run_capture --feature-dir docs/features/feature-verification-capture --timeout-seconds 60 --note "feature verification acceptance"` from this repository. The runner directly executes this feature's `proof/acceptance.py` with Python 3.

## Scenarios and dedicated tests

- `test_regression_argv_context_and_separate_storage`: real CLI receives shell-sensitive argv and a feature-local cwd; read back output, start/result metadata, notes and snapshots. Catches shell interpolation, lost arguments, wrong context and evidence mixing.
- `test_default_and_explicit_proof_compatibility`: execute real proof runner, confirm root cwd and legacy output location; repeated captures preserve prior evidence and explicitly identify proof.
- `test_regression_without_runner`: capture regressions using the required documents without any runner.
- `test_failures_and_timeout`, `test_interruption`: execute failing, missing and sleeping commands; read durable failure output and result, signal real capture process and verify child cleanup.
- `test_input_changes`: real commands alter a selected input or retained snapshot; a nominal exit zero must not produce acceptance PASS.
- `test_invalid_requests_execute_nothing`, `test_containment`: reject missing/invalid commands, inappropriate cwd, invalid timeouts, external or symlinked inputs/cwd/destinations before side effects.
- `test_completion_boundary`: drive installed feature_status CLI through its imported real gate validator using real captured proof and regressions; newer regressions leave the official pointer valid, regression results cannot complete a feature even when relocated under proof/runs, and historical results without kind remain accepted.

## Proves

Producer: feature verification commands and feature documents. Activation: real installed CLI subprocesses. Authority: capture CLI and feature_status/gate completion validator. Consumers: on-disk run evidence and lifecycle status read-back. Target: this installed checkout, isolated temporary Git repositories containing feature packages. No fake capture or validator implementations are used. Central break: regression invocation or evidence classified as proof instead of separately retained execution evidence.

## Does not prove

This does not enforce filesystem write protection, capture conversations, select tests, monitor arbitrary terminal activity, prove every historical feature, or test deployment. Workflow documentation and ignore-policy alignment require final review plus repository checks outside acceptance.

## False-green risks

Synthetic command bodies are controlled inputs to the real CLI, not replacements for capture behavior. Fixtures use minimal feature documents and exercise status validation through its production consumer. They do not substitute inner function assertions for execution. Required interruption finalization assumes the host permits ordinary child-process signals; uncatchable termination can only leave incomplete evidence.

## Evidence method

Unittest assertions read actual attempt directories and status files after subprocess execution. The outer official capture retains this runner's output and result. Red and author context are retained outside frozen inputs under evidence/.

## Known gaps

No unsafe external edge is needed. Tests cover SIGTERM finalization rather than every OS signal and do not simulate disk exhaustion or host power failure. The capture mechanism retains partial attempts under such failures but cannot guarantee finalization.

## Environment and exact acceptance inputs

POSIX host, Git, Python 3 standard library; no added dependencies. Frozen inputs: FEATURE.md, PROOF.md, proof/run.sh, proof/acceptance.py in this feature. No shared acceptance helpers or fixtures. Temporary repositories and subprocess bodies are created by acceptance.py and removed after each scenario. Implementation scripts are consumed from this checkout, never copied into fixtures.
