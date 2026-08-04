# Proof Capture Hardening Proof

## Done
- The real capture executable is covered by subprocess-level tests for success, failure, timeout, interruption, descendant cleanup, path validation, snapshots, and proof-input mutation.
- Independently baselined end-state mutation of an accepted proof input or retained copy cannot produce `PASS`, including ordinary mode changes, inode replacement, and overwrite-and-restore that changes filesystem metadata.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/proof-capture-hardening --timeout-seconds 30 --note "verify proof capture supervision and input integrity"
```

## Scenario: Terminal outcomes are retained truthfully
- Producer/activation: pytest creates temporary Git repositories and invokes the real `scripts/proof_run_capture` with controlled executable proof runners, including one terminated directly by a signal.
- Consumer: the parent feature lifecycle reading the retained attempt and process exit status.
- Read-back: tests parse the real `attempt-start.json`, `result.json`, stdout, stderr, signal, and copied contracts for successful, failing, timed-out, and interrupted runs.
- Fake: temporary repositories and controlled proof runners only; the capture executable and operating-system subprocess/signal boundaries are real.
- Catches: a passing wrapper around a failing runner, lost output, absent terminal result, wrong status mapping, or snapshots taken after runner mutation.

## Scenario: Processes and proof inputs are contained
- Producer/activation: controlled runners spawn long-lived children before timeout, interruption, and normal exit; receive a real signal; change content or mode; replace an inode; rewrite both live and retained copies; or directly change then restore live and retained inputs.
- Consumer: later proof attempts and the repository state relied upon by evaluation.
- Read-back: tests confirm every child PID no longer exists, cleanup is not `remaining`, interrupted evidence is retained, and every mutation attack produces `FAIL` with capture code `126` and the changed live or retained surface.
- Fake: none beyond the controlled runner behavior.
- Catches: leaked descendants, timeout without cleanup, signal loss, mutation of the writable retained reference, change-then-restore, or a proof runner manufacturing green by changing its own contract.

## Scenario: Unsafe input is rejected
- Producer/activation: pytest invokes the executable with an escaping feature path, outside-repository nested symlinks, an in-repository accepted-input symlink, and missing or non-executable runners.
- Consumer: capture argument validation.
- Read-back: the command exits `2`, prints the exact validation problem, creates no misleading retained attempt, and leaves the outside directory empty.
- Fake: temporary repository only.
- Catches: following nested symlinks to execute proof inputs or write attempts outside the repository, or treating an unusable runner as proof execution.

## Scope
Proves:
- Deterministic capture supervision and evidence retention behave as documented on the current platform.
- Accepted proof inputs cannot change during a successful official attempt.

Does not prove:
- Semantic quality of target feature proofs.
- Cleanup after uncatchable `SIGKILL` or host failure.
- Exact final implementation-candidate freshness after the proof finishes.
- Detection of transient pathname or parent-directory substitution that restores the untouched original entry or tree; the harness is not an OS event monitor or secure trust root against a dishonest same-user runner.

False-green risks:
- Platform-specific process and filesystem metadata semantics outside the current supported environment may differ.
- A same-user process can evade end-state filesystem metadata by temporarily substituting a pathname or parent directory and restoring the untouched original. This deliberate evasion is outside the accepted accidental-mutation threat model and requires OS event monitoring or protected infrastructure to detect generally.
- A proof runner can still mutate implementation unless target proof and lifecycle policy catch it; this feature protects only the accepted proof inputs.

Evidence method:
- deterministic

Known gaps:
- environment

## Environment
- Repository-local Python 3 and pytest on a POSIX process-group platform.
- Runner stdout prints the selected Python executable/version and platform before executing the focused test module.
