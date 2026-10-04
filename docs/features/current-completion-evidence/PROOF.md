# Current completion evidence proof

## Done and command

The installed capture, review-receipt, and status CLIs demonstrate the accepted completion contract against disposable local Git repositories. Run `"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture.py" --feature-dir docs/features/current-completion-evidence --timeout-seconds 180 --note "current completion acceptance"`. The executable `proof/run.sh` runs `proof/acceptance.py` with Python 3 and Git; it needs no credentials, packages, commits, network, or external service.

The acceptance author is the separate `completion_proof` agent. Its inputs are FEATURE.md, the shared proof contract, retained capture behavior, and the proposed public CLI and evidence format supplied before implementation. The author does not edit application scripts or derive expected outcomes from candidate output.

The separate `input_scope_proof` agent repaired missing input-coverage assertions on 2026-09-25 under the existing requirement to reject mismatched supporting evidence. Original inputs, focused red, the pre-fix false completion, exact diff, rationale, and revised hashes are retained in `proof/author-notes/input-scope-repair/`.

## Boundary and observation

The producer is a disposable repository containing a real feature, executable proof, application, test, and fixture. Public activation is a new subprocess of the actual scripts in this harness checkout. State owners are retained attempt directories, review.json, and status.json; consumers are the receipt and lifecycle CLI commands. Assertions read their exit status, separated output, candidate metadata, receipts, and durable lifecycle state. Only the sample application and its accepted behavior are synthetic. Capture, fingerprinting, review validation, process handling, and lifecycle consumers are real. Runtime is the local worktree, with an explicit alternative target label exercised as metadata; no claim of remote target attestation is made.

## Scenario mapping

All scenarios live in `proof/acceptance.py`; its fixture generator is determining acceptance code, not an application replacement.

| Tests | Activation and read-back | Incomplete implementation caught |
| --- | --- | --- |
| successful_receipt_backed_completion_and_reopening; owner_is_preserved_on_rejected_transition | Capture → review → done → reopen; inspect receipt, pointer, owner, and byte-for-byte unchanged rejection | Mandatory receipt cannot be created; valid completion never works; unauthorized ownership takeover; reopened done bypass |
| capture_metadata_determinism_scope_target_and_no_source_dump | Capture twice on unchanged Git-visible and untracked inputs; independently hash candidate.json; inspect scope, target, logs | Timestamp/evidence/status writes self-invalidate; untracked input omitted; target missing; source/config values dumped in metadata |
| missing_receipt_or_fingerprint_cannot_complete | Remove receipt, manifest, or digest; invoke review/done | Legacy PASS accidentally qualifies for a new completion |
| source_acceptance_test_fixture_edits_additions_and_deletions_stale | Edit app/test/fixture/FEATURE/PROOF/runner/helper, add source, delete tracked and untracked inputs after review | Fingerprint covers only three acceptance files, only tracked files, or fails to represent deletions |
| in_run_candidate_or_selected_snapshot_change_converts_zero_to_failure | A zero-exit proof/regression edits an app/helper or retained FEATURE snapshot; inspect runner status versus capture status | Nominal zero exit masks changed candidate or old snapshot protection regresses |
| explicit_ignored_inputs_are_bound_without_dumping_values | Change ignored input with default selection and with explicit --include | Claimed includes are not bound, or default silently claims ignored runtime observation |
| regressions_pass_current_target_matched_and_cannot_replace_proof | Bind passing regression, try it as acceptance including relocation, then complete with proof | Regression substitution, receipt omits support, generated regression evidence self-invalidates |
| failed_stale_or_different_target_regressions_cannot_support_pass | Bind failed, earlier-candidate, or different-target regression to fresh proof | Supporting runs are named without validation |
| mismatched_input_coverage_cannot_support_pass_review; legacy_pass_receipt_with_mismatched_inputs_cannot_complete; matching_normalized_inputs_pass_and_mismatch_allows_diagnostic_review | Capture with differing ignored-input coverage; attempt PASS review and legacy-receipt completion; compare matching normalized includes and diagnostic FAIL review | Each run passes independently but does not cover the same inputs; only new receipt creation is fixed while an older mismatched receipt still closes work; include order or diagnostic evidence is rejected unnecessarily |
| changed_bound_evidence_and_receipt_prevent_completion | Alter proof output/result/manifest, review rationale, or bound regression output after review | Receipt checks only PASS strings or does not bind evidence and its own accidental alteration |
| distinct_attribution_and_actual_verdict_are_required | Reuse identities, omit rationale, record FAIL, or mismatch implementer and active owner | Independent attribution is optional; FAIL becomes done; receipt belongs to another implementation owner |
| newer_failed_or_unfinished_official_attempt_invalidates_older_pass | Retain older PASS, create later FAIL or interrupted-format STARTED directory, then review/done | Cherry-picked earlier PASS; altered candidate alone masks the latest-attempt requirement |
| historical_inventory_is_readable_but_reopened_completion_requires_current_evidence | Gate an old-format done entry against changed source; reopen and attempt new done | Inventory requires contemporary rerun of history, or grandfathering leaks into new transitions |
| draft_only_registration_and_nonempty_structural_readiness | Register FEATURE-only draft; attempt ready/active with missing, blank, or nonexecutable inputs | Placeholder files required before discovery, blank artifacts falsely establish structure |
| failure_timeout_and_interruption_evidence_and_child_cleanup | Execute failure, timeout, and real SIGTERM interruption; read outputs, results, and OS process existence | Changed capture drops retained failures, conflates streams, or leaks its ordinary child |

## Pass criteria and limits

Every deterministic scenario must pass. Cases vary mutation kind, lifecycle state, attribution, evidence kind, and target where they change the accepted outcome; repetition of identical deterministic calls would not improve the claim. Two unchanged captures establish deterministic manifest behavior on the tested fixture. This is executable CLI behavior proof, not a source-wording or mock-import test.

The legacy mismatched-receipt case supplies historical input to the real completion CLI. A retained pre-fix PASS receipt grounds its format; each run obtains fresh evidence bindings through the public diagnostic-review command, then independently restores the historical PASS verdict and canonical digest. No production validator is imported or replaced. Matching normalized includes exercise valid completion, and a diagnostic FAIL receipt remains recordable without qualifying for completion.

This proves the tested local commands reject ordinary stale, altered, incorrectly attributed, or substituted evidence and preserve useful historical/draft behavior. It does not prove identity authentication, cryptographic tamper resistance against an actor rewriting all hashes, semantic reviewer quality, observed production behavior, all ignored runtime state, transient edit-and-restore detection, inaccessible external service state, universal concurrency safety, every supported operating system, or every form of process-tree escape. Target labels describe the review claim; they do not authenticate a deployment. The preserved capture suite's unaffected cases are separate regressions, not imported as this feature's acceptance.

False-green risks include an untested selection edge such as submodules or unusual filesystem entries, a caller bypassing the status helper and editing JSON directly, and a model asserting completion conversationally without invoking these tools. These remain stated boundaries. The final reviewer must assess implementation and instruction integration in addition to this executable proof.

## Fixed inputs

Freeze FEATURE.md, this PROOF.md, proof/run.sh, and proof/acceptance.py before implementation. No determining external fixture or helper exists. Keep author repair records under proof/author-notes; each repair must retain the prior failure, independent reason, changed files, and revised hashes. Evidence run directories do not change the acceptance oracle.
