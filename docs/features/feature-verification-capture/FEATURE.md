# Feature verification capture

## Outcome

Every verification run used to support a feature's completion has retained execution evidence. Extend the installed `scripts/proof_run_capture` to capture selected regression commands separately from official acceptance proof, and route current workflow instructions through those capture modes.

## Accepted behavior

- Existing invocations remain official proof: execute the owning feature's `proof/run.sh` from the repository root and store attempts in `docs/features/<id>/proof/runs/<attempt>/`.
- Add `--kind regression` with an executable and arguments after `--`. Execute the argument vector directly, without implicit shell interpretation. Proof mode is the default (`--kind proof` may be explicit) and rejects supplied commands.
- Regression mode accepts optional `--cwd` specifying an existing directory within the repository, resolved relative to the repository root. Default cwd is the repository root. Reject invalid/outside/symlinked working directories and reject `--cwd` in proof mode. Commands relative to cwd resolve there through normal subprocess behavior. Missing regression commands are usage errors and execute nothing.
- Store regression attempts separately under `docs/features/<id>/tests/runs/<attempt>/`. Each attempt records `kind`, exact command arguments, actual cwd, note, start/runtime metadata, stdout, stderr, duration, return code, and final PASS/FAIL/TIMEOUT/INTERRUPTED result when finalization can complete. Start metadata exists before command execution; preserve incomplete attempts.
- Regression capture requires the feature's `FEATURE.md` and `PROOF.md`, but does not require an executable proof runner. Snapshot those two documents for regression; retain the three existing snapshots for proof. Preserve selected input-change detection and process-group cleanup behavior in both modes. Existing containment and symlink restrictions apply to captured inputs and attempt destinations.
- Retain failed, timed-out, interrupted, and executable-not-found attempts as evidence with nonzero exit status. Preserve stdout and stderr separately. Repeated invocations never overwrite earlier attempts. Reject non-finite or nonpositive timeouts.
- New proof metadata explicitly says `kind: proof`; new regression metadata says `kind: regression`. Regression runs never become official proof, never supersede the latest official proof pointer, and cannot satisfy feature completion validation. The status validator also rejects explicitly non-proof results even if copied into a proof directory. Existing historical proof results without `kind` remain interpretable as the preexisting proof-only format.
- Current instructions require captured execution for official proof and selected regressions used to support material-feature completion. Commands used only for investigation may remain in native conversation. The capture tool does not automatically monitor terminal commands, capture whole conversations, or decide which tests are relevant. Regression PASS must never be described as feature acceptance.
- Regression run evidence follows the same local/private ignore policy as proof run evidence. User decisions and corrections stay in conversation; accepted behavior remains in the feature specification, with relevant conversation/evidence links.

## Existing behavior to preserve

Preserve proof invocation compatibility, official proof output location, nonzero exit propagation, timeout/interruption handling, process-group cleanup, input snapshots/change detection, status ownership and path validation, and historical completion interpretation. Leave unrelated dirty work and historical feature proofs unchanged. Keep root `tests/` and `evals/` absent; new acceptance belongs to this feature.

## Consumption target

This installed dot-codex checkout: real CLI subprocesses, on-disk attempt records, and the real feature status/gate validation boundaries. Use isolated temporary feature repositories for destructive/error scenarios. Demonstrate a captured regression and captured proof on this feature's actual package before completion.

## Non-goals

Terminal monitoring, full conversation capture, automatic test selection, rebuilding unrelated historical proofs, filesystem-enforced acceptance protection, external deployment, or a new orchestration system.
