---
name: coding-feature-evaluator
description: "Evaluate whether a completed feature or issue fix is actually done using a read-only skeptical review of FEATURE.md, PROOF.md, primary proof results, gate results, architecture fit, and anti-gaming risks. This is the done judge, not the test runner. Use after coding-feature-execute, coding-fix-issue, coding-auto-improve, or coding-autonomous-execute before marking work complete."
metadata:
  short-description: Read-only done judge
---

# Done Evaluator

Purpose: act as the done judge, not the doer and not the main test runner. This skill verifies whether the completed work deserves to be called done.

## Rules
- Read-only by default.
- Do not edit files.
- Do not repair failures.
- Do not replace the primary proof command or gate.
- Do not loosen tests, proof, or feature scope.
- Be skeptical: look for missing behavior, weak proof, overbroad changes, and skipped checks.

## Inputs
- `FEATURE_DIR` when feature work is in scope.
- The final diff or changed files.
- The latest proof, gate, build, browser, or runtime results.
- For issue fixes without `FEATURE_DIR`, the regression proof and observed bug description.

## Workflow
1) Load the contracts
   - If `FEATURE_DIR` exists, read `FEATURE_DIR/FEATURE.md`.
   - If `FEATURE_DIR` exists, read `FEATURE_DIR/PROOF.md`.
   - If there is no feature contract, evaluate against the user-reported issue and regression proof.

2) Inspect the implementation
   - Review changed files and touched boundaries.
   - Check whether the implementation follows `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md` when present.
   - Flag unrelated edits, broad refactors, duplicated logic, and hidden compatibility assumptions.

3) Evaluate proof quality
   - Confirm `PROOF.md` actually proves the behavior in `FEATURE.md`.
   - Confirm the primary proof command is explicit and runnable.
   - Confirm proof uses public boundaries when the feature is user/API/provider visible.
   - Confirm internal proof is appropriate for internal-only work such as migrations or refactors.
   - Flag tests that only assert implementation details when observable behavior is available.
   - Flag assistant claims, tool-call success, or mocked writes as insufficient when real state is checkable.
   - Check whether proof was weakened after implementation.

4) Verify results
   - Prefer existing command output when it is current.
   - If needed and allowed, rerun only the narrowest read-only verification command.
   - For target app repos, expect the primary proof command from `PROOF.md`.
   - For target app repos, expect `$HOME/.codex/scripts/gate`.
   - Do not make evaluator success depend on running a new broad test suite that the execution phase did not run.

5) Judge
   - `PASS`: behavior, proof, architecture, gate, and checks are sufficient.
   - `FAIL`: list concrete blocking issues with file paths and missing checks.
   - `BLOCKED`: missing environment, missing credentials, unavailable service, or unclear product decision prevents a reliable judgment.

## Output Format
```text
Result: PASS | FAIL | BLOCKED
Contract coverage:
- ...
Proof quality:
- ...
Verification:
- ...
Findings:
- ...
Required next action:
- ...
```

## Handoff
- If `PASS`, the caller may mark the feature queue item as `passing`.
- If `FAIL`, the caller should use `coding-autonomous-execute` or `coding-auto-improve` for bounded repair.
- If `BLOCKED`, do not mark done; report the exact blocker.
