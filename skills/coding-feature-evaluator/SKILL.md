---
name: coding-feature-evaluator
description: "Evaluate whether a completed feature or issue fix is actually done using a read-only skeptical review of FEATURE.md, PROOF.md, primary proof results, gate results, architecture fit, and anti-gaming risks. This is the done judge, not the test runner. Use after coding-feature-execute, coding-repair, or coding-autonomous-execute before marking work complete."
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
- For issue fixes, evidence that `docs/features/*/FEATURE.md` was inspected or a clear reason why feature lookup did not apply.

## Workflow
1) Load the contracts
   - If `FEATURE_DIR` exists, read `FEATURE_DIR/FEATURE.md`.
   - If `FEATURE_DIR` exists, read `FEATURE_DIR/PROOF.md`.
   - If there is no feature contract, evaluate against the user-reported issue and regression proof.
   - For issue fixes, check whether the caller looked for one clear matching `docs/features/*/FEATURE.md`.
   - If exactly one matching feature existed and was ignored, return `FAIL`.
   - If no feature clearly matched, accept a focused local regression proof without requiring new feature artifacts.

2) Inspect the implementation
   - Review changed files and touched boundaries.
   - Check whether the implementation follows `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md` when present.
   - Flag unrelated edits, broad refactors, duplicated logic, and hidden compatibility assumptions.

3) Evaluate proof quality
   - Behavior coverage: confirm `PROOF.md` actually proves the behavior in `FEATURE.md`.
     For issue fixes, confirm the proof catches or was strengthened to catch the regression.
   - Proof integrity: confirm the primary proof command is explicit, runnable, anti-gameable,
     and not weakened after implementation. Check whether a broken implementation could
     still pass the primary proof. Return `FAIL` when the proof can pass while the feature
     is visibly, externally, or behaviorally broken.
   - Contract freeze: return `FAIL` when implementation code changes and `FEATURE.md`,
     `PROOF.md`, or proof artifacts were edited in the same implementation pass. Contract
     repair must happen before implementation restarts, not during code repair.
   - Boundary fit: public behavior should use public boundaries. For UI/workflow features,
     prefer live browser/runtime evidence over static component or source assertions. For
     API/provider features, prefer real route, persisted-state, outbound boundary, and
     read-back evidence where available.
   - Semantic fit: Flag phrase-locked fixes, hardcoded natural-language keyword lists,
     language-specific gates, or tool removal based on user wording when domain validation
     is required. Return `FAIL` when semantic behavior should survive paraphrases or other
     languages but proof only covers exact terms.
   - Proof Change Guard: return `FAIL` when contract repair changes `FEATURE.md`,
     `PROOF.md`, or proof artifacts without explaining why the original contract was wrong
     or incomplete, which fake implementation the changed proof catches, red/green evidence
     when practical, and why behavior scope was not reduced.

4) Verify results
   - Execution evidence: prefer current command output. Rerun only the narrowest read-only
     verification command when needed and allowed.
   - For target app repos, expect the primary proof command from `PROOF.md` and
     `$HOME/.codex/scripts/gate`.
   - Do not require a broad new suite that execution did not run.
   - Return `FAIL` when `NEED_INPUT` was reported before recovery, available tools, repo
     scripts, browser/app automation, MCP/app connectors, local CLIs, or readiness checks
     were tried where relevant.
   - Return `FAIL` when a destructive or external primary proof was marked `NEED_INPUT` or
     blocked even though approval was available to request for the exact command, target
     resource, expected effect, and proof reason.
   - Return `FAIL` when a destructive primary proof was marked `NEED_INPUT` even though
     `.codex/approvals/destructive-proof-allowlist.json` had an enabled, unexpired entry
     matching the current `cwd`, full `command`, and `target`.

5) Judge
   - `PASS`: behavior, proof, anti-gaming coverage, architecture, gate, and checks are sufficient.
   - `FAIL`: list concrete blocking issues with file paths and missing checks.
   - `NEED_INPUT`: a missing environment, credential, safe external target, unavailable
     service, or unclear product decision still prevents judgment after documented
     recovery attempts.
   - Return `FAIL` when recovery was skipped and the executor could still inspect, set up,
     repair, add readiness checks, or retry with available local tools.

## Output Format
```text
Result: PASS | FAIL | NEED_INPUT
Summary:
- <one or two lines>
Findings:
- <only blocking issues or "none">
Verification:
- Primary proof: <PASS|FAIL|NOT RUN>
- Gate: <PASS|FAIL|NOT RUN>
Required next action:
- <one concrete action or "none">
```

Keep evaluator output concise. Do not repeat long logs, file lists, skill lists, token
usage, run IDs, prompt text, or implementation summaries unless they are the direct reason
for `FAIL` or `NEED_INPUT`.

## Handoff
- If `PASS`, the caller may mark the feature queue item as `done`.
- If `FAIL`, the caller should use `coding-repair` for a focused repair, or
  `coding-autonomous-execute` according to the autonomous escalation policy in
  `AGENTS.md`.
- If `NEED_INPUT`, do not mark done; report the exact user-owned input or external action.
