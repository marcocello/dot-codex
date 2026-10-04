# Shared journey verification acceptance

## Done and command

Run `bash docs/features/shared-journey-verification/proof/run.sh` from this harness checkout. PASS requires all black-box CLI scenarios in `proof/acceptance.py` to pass. Capture the runner with the ordinary harness evidence command for official attempts. The runner uses Python 3, Git, and Bash, creates disposable local repositories under the system temporary directory, invokes this checkout's actual public scripts in subprocesses, reads retained JSON/files, and removes its disposable repositories afterward. No production application, network, credentials, or remote provider is used.

## Boundary

Input producer: a feature author supplies FEATURE.md and COVERAGE.json plus shared executable check packages. Public activation: `feature_status.py`, `proof_run_capture.py`, and `verification_receipt.py` subcommands. State owner: the disposable repository's status, package evidence and round receipt. Consumer: an implementation task requesting completion and a reviewer checking current verification. Read-back: CLI exit statuses, lifecycle JSON, retained evidence, and public `check-round`. Target: real local harness CLI behavior. Outer substitute: tiny fixture shell runners check disposable source files; these stand in for application journeys, and do not claim any application workflow is correct. The central capture, fingerprint, mapping, receipt and completion behavior is real and must not be mocked.

## Scenario mapping

All determining fixtures are created by `proof/acceptance.py`; `proof/run.sh` is the launcher. Tests never import implementation validators as an oracle.

| Scenario | Test | Defect caught |
| --- | --- | --- |
| Two implemented features complete from one shared journey and one focused check, with no feature runners | `test_shared_journey_completes_two_features_without_own_runners` | Compulsory duplicated runners, unsupported shared coverage, missing implementation/verification separation |
| Empty coverage and unavailable required external check reject completion | `test_unmapped_criterion_and_unavailable_check_cannot_complete` | Empty mapping accepted, required check silently omitted |
| Unrelated edits allow scoped reuse; selected edits require rerun; independently unaffected evidence reused | `test_scoped_freshness_and_unaffected_evidence_reuse` | Whole repository unnecessarily invalidates scoped evidence, or relevant changed input remains green |
| Explicit ignored determining input becomes stale | `test_included_ignored_input_is_binding` | Scope silently drops explicit includes |
| New failed or unfinished attempts prevent using historical green | `test_newer_failed_and_unfinished_attempts_supersede_pass` | Cherry-picked historical pass |
| Different targets, merged author roles, or wrong completion implementer reject | `test_wrong_target_and_roles_rejected` | Incompatible evidence or attribution accepted |
| Mapping, receipt, and evidence mutation prevent completion | `test_coverage_receipt_and_evidence_tampering_block_completion` | Review remains valid after its inputs or receipt change |
| Public current-round check and new completion reject candidate changed after review | `test_round_binds_candidate_after_review` | Stale round presented as current |
| Directory scope catches newly added and deleted determining files | `test_directory_scope_tracks_additions_and_deletions` | Existing-files-only fingerprint misses additions or deletions |
| Historical inventory remains readable, but current-round check fails after later source changes | `test_historical_inventory_survives_later_candidate_changes` | Historical completion incorrectly becomes current assurance or inventory cannot be read |
| Implemented can reopen or block without a completion claim | `test_implemented_can_reopen_without_claiming_verification` | Intermediate state traps work or falsely marks verification |
| Legacy own proof, broad capture, regression receipt and active-to-done continue working | `test_legacy_own_proof_and_regression_completion` | Existing workflow compatibility broken |

## Proves, limitations and independent review

These deterministic scenarios prove the local scripts accept and reject representative ordinary requests at their public boundary. One execution per state transition is appropriate; there is no model variability, provider availability, or probabilistic reliability claim here. Retained failures remain in each scenario until fixture cleanup; an official outer capture retains the acceptance output and candidate.

There is deliberately no Markdown criteria parser: the independent acceptance author and final reviewer must check every semantic promise against COVERAGE.json. An omitted prose criterion can escape machine detection. Tests establish nonempty mapping enforcement and required-package completeness, not natural-language coverage discovery. Explicit scopes are supplied by reviewers; a scoped pass does not establish scope adequacy or automatic dependency discovery. Role identifiers are attribution, not identity authentication. Fingerprints do not attest remote runtimes.

The CLI tests do not establish instruction quality on an actual implementation task, visual/browser behavior, Arbitrator correctness, measurable runtime improvement, or production provider delivery. Final review must assess the instruction changes and independently forward-test the instructions on a different small application task using raw context with withheld expectations, as required by FEATURE. External integrations remain missing acceptance until legitimately exercised. This acceptance is not an exhaustive security audit.

The ordinary action most likely to escape this proof is an author supplying an incomplete scope or semantically incomplete criterion mapping while every selected check passes. Documentation and independent review must make that boundary explicit, rather than treating the receipt as evidence of exhaustive coverage.
