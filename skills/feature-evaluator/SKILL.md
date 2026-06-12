---
name: feature-evaluator
description: Evaluate whether a completed feature or issue fix is actually done using a read-only skeptical review, deterministic checks, acceptance coverage review, and clear PASS/FAIL/BLOCKED output. Use after feature-execute, fix-issue, auto-improve, or autopilot-loop before marking work complete.
metadata:
  short-description: Read-only skeptical feature judge
---

# Feature Evaluator

Purpose: act as the judge, not the doer. This skill verifies whether work is complete.

## Rules
- Read-only by default.
- Do not edit files.
- Do not repair failures.
- Do not loosen tests, acceptance, or feature scope.
- Be skeptical: look for missing behavior, weak acceptance, overbroad changes, and skipped checks.

## Inputs
- `FEATURE_DIR` when feature work is in scope.
- The final diff or changed files.
- The latest test, gate, build, browser, or acceptance results.
- For issue fixes without `FEATURE_DIR`, the regression test and observed bug description.

## Workflow
1) Load the contract
   - If `FEATURE_DIR` exists, read `FEATURE_DIR/FEATURE.md`.
   - Treat Gherkin scenarios as the behavior contract.
   - If there is no feature contract, evaluate against the user-reported issue and regression test.

2) Inspect the implementation
   - Review changed files and touched boundaries.
   - Check whether the implementation follows `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, and
     `docs/TESTING.md` when present.
   - Flag unrelated edits, broad refactors, duplicated logic, and hidden compatibility assumptions.

3) Evaluate acceptance quality
   - Confirm every important `FEATURE.md` scenario is covered by an executable check or a clearly
     justified manual verification.
   - Confirm acceptance tests use public boundaries and real assertions.
   - Flag tests that merely assert implementation details.

4) Verify results
   - Prefer existing command output when it is current.
   - If needed and allowed, rerun the narrowest read-only verification command.
   - For target app repos, expect `$HOME/.codex/scripts/gate`.
   - When `FEATURE_DIR` is in scope, expect
     `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`.

5) Judge
   - `PASS`: behavior, acceptance, architecture, and checks are sufficient.
   - `FAIL`: list concrete blocking issues with file paths and missing checks.
   - `BLOCKED`: missing environment, missing credentials, unavailable service, or unclear product
     decision prevents a reliable judgment.

## Output Format
```text
Result: PASS | FAIL | BLOCKED
Contract coverage:
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
- If `FAIL`, the caller should use `autopilot-loop` or `auto-improve` for bounded repair.
- If `BLOCKED`, do not mark done; report the exact blocker.
