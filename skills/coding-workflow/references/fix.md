# Fix

Restore known expected behavior with the smallest verified change. Fix is an entry mode for a clear defect, not the repair subroutine used while Ship is active.

## Enter

- Clear symptom and known expected behavior: proceed.
- Unclear expectation, changed goal, or missing capability: return to Shape.
- A standalone isolated defect does not create a feature package or queue entry.
- Defect owned by an existing feature: read its contracts and status. Reopen `done -> active` when the completed claim is no longer true; preserve the feature's proof obligations.
- Runtime or deployment symptom without an established code cause: enter Operate first.

Regressions introduced while a feature is being implemented stay in that feature's Ship repair loop, Goal, allowance, and final review. Do not reopen each affected old feature or create another package merely to repair that candidate. The reopening rule above applies to defects invalidating delivered behavior.

## Classify and explain the scope

Fix describes restoration of known behavior, not a size or effort category. “Implement this ticket” can route to Fix when the ticket describes a defect; a one-line addition can require Shape when it introduces new behavior. Before editing, state the expected behavior, the evidence establishing it, whether an existing feature claim is invalidated, and the resulting completion requirements. If investigation changes that classification, explain the change before continuing.

- **Standalone Fix:** no existing feature's accepted delivery claim is invalidated. Use a focused check and affected regressions; no mandatory package, Goal, independent acceptance author, or final reviewer. Sharing a source file with a feature is not sufficient reason to reopen it.
- **Reopened feature Fix:** the defect contradicts behavior accepted by an existing delivered feature. Identify the contract/scenario, reopen the existing package through its ownership rules, and retain its realistic proof and fresh final-review requirements regardless of patch size. Do not call this standalone merely because the repair is narrow.
- **Active Ship regression:** repair inside the current Ship run and its existing completion requirements.

For example, mapping runtime statuses to existing conversation tabs is Fix if the established contract already requires those conversations to appear. If that contract belongs to a delivered feature, it is a reopened feature Fix. Deciding whether an additional status should count as “Completed” requires Shape or a user acceptance decision when the existing contract does not answer it; do not silently include that change in the repair.

## Repair

No category of Fix automatically requires early review. Use it only for a concrete identified risk or explicit request, without creating a package just for review. Exercise the actual permission, data, migration, or external-effect risk in the focused regression where relevant. Required approvals remain intact; review is not mutation permission.

Parallel focused fixes remain package-free and use the same checkout by default. Independent areas proceed together; coordinate a single writer for overlapping edits and shared-runtime mutations. Establish stable relevant inputs for the focused regression without pausing unrelated work. If inputs change, repeat that regression. Do not modify another task's owned feature or shared runtime without coordination; package-owned fixes use the status ownership rules. Worktrees are optional.

1. Reproduce the symptom through the narrowest real boundary.
2. Read the exact error, affected call path, adjacent tests, and relevant runtime signal.
3. Reuse the failing check or add a focused regression and confirm red when practical. Keep new tests with the feature behavior they verify, following its existing organization; a standalone fix remains package-free. Implementers preserve existing frozen proof inputs. Demonstrably faulty acceptance setup follows the independent author's repair procedure in [proof.md](proof.md#fixed-acceptance); a change to acceptance or unresolved meaning returns to the user before revision.
4. Identify root cause before broad edits; add a narrow diagnostic when cause is unknown. If required historical proof is missing or obsolete, follow [proof restoration](proof.md#restore-unrunnable-proof) to recover it through an independent author and continue verification.
5. Reuse existing logic and make the smallest effective repair.
6. Rerun the focused regression and the signal that exposed the issue.

Do not hide required-runtime failures, add language-specific phrase gates for semantic behavior, catch and downgrade errors, weaken proof, or perform unrelated refactoring.

## Complete

A standalone focused fix completes after its focused regression or narrow check passes, with broader checks proportional to concrete risk. A reopened material feature reruns its realistic proof against the named target and follows Ship's fresh final oracle before returning to `done` with current evidence.

For a reopened feature, distinguish “the narrow repair passes its regression” from “the feature is verified complete.” If required official proof still fails, retain the failed attempt and keep feature completion open; a focused regression or review of the patch cannot replace the required proof. Report evidenced pre-existing failures separately, identifying whether they block required feature proof or only an unrelated regression check. Do not expand the repair into unrelated product changes to obtain a green result.

Select affected existing tests from shared code and consumers; run all when cheap or broad impact warrants it. No mandatory full-suite baseline is needed. Repair introduced regressions and report evidenced unrelated pre-existing failures separately. Record the result through [evidence.md](evidence.md); do not create a Goal or package solely for a small fix.
