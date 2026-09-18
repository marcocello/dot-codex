# Shared Verification Capture

Read when Ship records material proof/regressions, proof authors retain acceptance versions/repairs, or package-owned Fix verifies completion. Standalone Fix, analysis, and diagnosis use native task history and linked results; logging does not create a feature or a Second Brain action.

## Evidence For One Feature

Capture every material completion-supporting verification run with the appropriate mode:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture.py" --feature-dir docs/features/FEATURE --timeout-seconds N --note "reason"
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture.py" --feature-dir docs/features/FEATURE --kind regression --timeout-seconds N --note "affected check" -- COMMAND ARGS
```

Default proof mode runs the feature's `proof/run.sh` from the repository root and writes `proof/runs/`; regression mode runs the argument vector after `--` and writes `tests/runs/`. Use real commands/timeouts; `--cwd` may select a repository subdirectory. See `--help` for options. Regression results cannot replace/supersede official proof. Investigation commands may remain in native history; direct commands are not automatically captured.

Capture records command/target context, timestamps, output, duration/result and contract snapshots; an interrupted attempt may remain unfinished and must be retained. Keep meaningful failures and pass paths for review. Record task/any Goal, actual authors/reviewer, used skill versions, fixed acceptance hashes, target, selected checks, corrections, outcome and gaps alongside the feature evidence. Proof setup/restoration records follow [proof.md](proof.md), not duplicated acceptance documents.

Native task history owns original dialogue. Link relevant messages/corrections rather than copying entire conversations. Keep private dialogue local, redact secrets, exclude hidden reasoning/unrelated material, and never fabricate unavailable roles, usage or capture. Full automatic lifecycle capture is not configured: label partial capture honestly. Missing official proof blocks completion; incomplete dialogue capture alone does not invalidate otherwise sound verification. Recording never authorizes automatic rule changes; deliberate learning uses `coding-review-workflow`.
