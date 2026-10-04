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

Captures retain `candidate.json` with fingerprints of the check’s determining inputs, acceptance files and automatically discovered referring feature contracts/mappings. New or changed mappings require fresh proof. The [input declaration](rounds.md#rerun-only-affected-checks) is reused automatically. CLI `--scope` and `--include` extend that declaration; without a saved or CLI scope, capture covers all tracked/non-ignored files (or the directory outside Git), excluding generated evidence and caches. Directory scopes detect additions and deletions. Keep generated runtime output outside inputs. Standalone proof and supporting runs require the same selection and target; round checks may have different scopes but must each remain current on the same target.

The default target label is `local-worktree`; use a meaningful target for the actual proof boundary. It is a recorded declaration, not automatic observation of a deployment or provider. Proof must establish the claimed runtime and read-back. Ignored inputs not included, external state, and edits reverted between observations are not automatically covered. Fingerprints detect changes; they do not sandbox the implementer or authenticate authors.

After the actual final review, the coordinator records its verdict:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/verification_receipt.py" review --root REPO \
  --proof-run docs/features/FEATURE/proof/runs/RUN \
  --implementer TASK \
  --verdict PASS --summary "Observed boundary, assessment and material limits" \
  --regression-run docs/features/FEATURE/tests/runs/RUN
```

Repeat `--regression-run` for selected supporting runs; omit only when none are needed. The implementer matches the active feature owner. Identifiers attribute the actual work; inventing role names does not create independence. The command stores `review.json` with evidence digests and rejects a PASS backed by stale, failed, or mismatched evidence. It does not perform the review or decide which regressions are sufficient. Record a FAIL when appropriate; it cannot support completion.

New `done` transitions require current proof and a matching PASS receipt. The status helper then writes a compact `completion.json` beside FEATURE; retain it in version control while raw runs remain local. This historical summary is not a substitute for current evidence. Relevant changes require renewed verification and review. Ordinary status inventory reads preserve historical completion formats without asserting that old evidence verifies today's checkout. Keep historical acceptance separate from the maintained regression checks selected for current work. No need to rerun history merely to update a status pointer or retain evidence.

Native task history owns original dialogue. Link relevant messages/corrections rather than copying entire conversations. Keep private dialogue local, redact secrets, exclude hidden reasoning/unrelated material, and never fabricate unavailable roles, usage or capture. Full automatic lifecycle capture is not configured: label partial capture honestly. Missing official proof blocks completion; incomplete dialogue capture alone does not invalidate otherwise sound verification. Recording never authorizes automatic rule changes; deliberate learning uses `coding-review-workflow`.

## Shared checks and round reviews

Capture each independently runnable package once, even when multiple features reference it:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture.py" \
  --package-dir docs/verification/customer-journey --target local-app \
  --timeout-seconds 300 --note "Round customer intake: browser save/reopen" \
  --scope src --scope tests/customer-journey --scope package.json \
  --scope docs/features/create-customer/FEATURE.md
```

These are example paths, not a mandated stack. Select the real determining inputs or omit scopes. Each package writes its own `proof/runs/`; repair and rerun that package without invalidating separately scoped unaffected checks. New failed or unfinished attempts supersede its older pass. Do not select a smaller scope after failure merely to conceal changed behavior.

After the actual review of the integrated round:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/verification_receipt.py" round --root REPO \
  --round customer-intake-01 --feature create-customer --feature reopen-customer \
  --proof-run docs/verification/customer-journey/proof/runs/RUN \
  --proof-run docs/verification/customer-permissions/proof/runs/RUN \
  --implementer TASK \
  --verdict PASS --summary "Observed journey, permission negatives and remaining limits"
"${CODEX_HOME:-$HOME/.codex}/scripts/verification_receipt.py" check-round --root REPO \
  --round-review docs/verification/rounds/customer-intake-01/review.json
```

Repeat `--feature`, `--proof-run`, and optional `--regression-run` for actual reviewed coverage. Every package mapped by the selected features must have current PASS evidence. Reviewers assess semantic completeness and shared integration risks; scripts cannot infer missing criteria or dependencies. Different scoped checks may be reused only when each still matches current determining inputs. All selected runs share one declared target. New round receipts bind each feature contract/mapping and each selected check’s inputs. Unrelated edits do not invalidate scoped completion; a selected broad check still covers the whole repository. Existing version-1 receipts retain their original full-candidate check. Ignored external inputs remain covered only by explicit capture and runtime observation, as above.

Use a new round ID for a new review; receipts are not overwritten. Record diagnostic FAIL without claiming completion. Status updates reference the PASS receipt with `--round-review`; they do not rerun checks. Inventory reads retain the historical result even after later changes, while `check-round` is the explicit current-verification check. No automatic status rewriting, missing-provider waiver, or production mutation is implied.

The `--author` and `--reviewer` arguments are optional attribution overrides when someone else actually performed that work. Both default to the implementer. There is no policy selection or risk rationale. Existing receipts remain historical records; their evidence integrity checks are unchanged.
