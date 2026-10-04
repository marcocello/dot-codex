# Shared Verification Capture

Read when Implement records material proof/regressions, proof authors retain acceptance versions/repairs, or package-owned Repair verifies completion. Standalone Repair, analysis, and diagnosis use native task history and linked results; logging does not create a feature or a Second Brain action.

## Evidence For One Feature

Capture every material completion-supporting verification run with the appropriate mode:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture.py" --feature-dir docs/features/FEATURE --target TARGET --timeout-seconds N --note "reason"
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture.py" --feature-dir docs/features/FEATURE --target TARGET --kind regression --timeout-seconds N --note "affected check" -- COMMAND ARGS
```

Default proof mode runs the feature's `proof/run.sh` from the repository root and writes `proof/runs/`; regression mode runs the argument vector after `--` and writes `tests/runs/`. Use real commands/timeouts; `--cwd` may select a repository subdirectory. See `--help` for options. Regression results cannot replace/supersede official proof. Investigation commands may remain in native history; direct commands are not automatically captured.

Capture records command/target context, timestamps, output, duration/result and contract snapshots; an interrupted attempt may remain unfinished and must be retained. Keep meaningful failures and pass paths for review. Record task/any Goal, actual authors/reviewer, used skill versions, fixed acceptance hashes, target, selected checks, corrections, outcome and gaps alongside the feature evidence. Proof setup/restoration records follow [proof.md](proof.md), not duplicated acceptance documents.

## Current Candidate And Review

New captures retain `candidate.json` with file fingerprints and selection scope. In Git repositories the default is tracked and non-ignored untracked files plus the owning acceptance tree; evidence run directories, lifecycle status, and cache artifacts are excluded. Without Git, capture uses the repository directory with documented exclusions. Add `--include PATH` for otherwise ignored relevant input files/directories. Use the same includes and target for proof and supporting runs. Keep generated runtime output outside source inputs.

The default target label is `local-worktree`; use a meaningful target for the actual proof boundary. It is a recorded declaration, not automatic observation of a deployment or provider. Proof must establish the claimed runtime and read-back. Ignored inputs not included, external state, and edits reverted between observations are not automatically covered. Fingerprints detect changes; they do not sandbox the implementer or authenticate authors.

After the actual independent final review, the coordinator records its verdict:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/verification_receipt.py" review --root REPO \
  --proof-run docs/features/FEATURE/proof/runs/RUN \
  --implementer IMPLEMENTER_TASK --author AUTHOR_TASK --reviewer REVIEWER_TASK \
  --verdict PASS --summary "Observed boundary, assessment and material limits" \
  --regression-run docs/features/FEATURE/tests/runs/RUN
```

Repeat `--regression-run` for selected supporting runs; omit only when none are needed. The three roles must be distinct; the implementer matches the active feature owner. Identifiers attribute the actual work; inventing role names does not create independence. The command stores `review.json` with evidence digests and rejects a PASS backed by stale, failed, or mismatched evidence. It does not perform the review or decide which regressions are sufficient. Record a FAIL when appropriate; it cannot support completion.

New `done` transitions require current proof and a matching PASS receipt. Relevant changes require renewed verification and review. Ordinary status inventory reads preserve historical completion formats without asserting that old evidence verifies today's checkout. Keep historical acceptance separate from the maintained regression checks selected for current work. No need to rerun history merely to update a status pointer or retain evidence.

Native task history owns original dialogue. Link relevant messages/corrections rather than copying entire conversations. Keep private dialogue local, redact secrets, exclude hidden reasoning/unrelated material, and never fabricate unavailable roles, usage or capture. Full automatic lifecycle capture is not configured: label partial capture honestly. Missing official proof blocks completion; incomplete dialogue capture alone does not invalidate otherwise sound verification. Recording never authorizes automatic rule changes; deliberate learning uses `coding-review-workflow`.
