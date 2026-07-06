---
name: coding-feature-evaluator
description: "Evaluate whether a completed feature or issue fix is actually done using a read-only skeptical review of FEATURE.md, PROOF.md, primary proof results, gate results, architecture fit, and anti-gaming risks. This is the done judge, not the test runner. Use after coding-feature-execute, coding-repair, or coding-autonomous-execute before marking work complete."
metadata:
  short-description: Read-only done judge
---

# Done Evaluator

Purpose: act as the done judge, not the doer and not the main test runner.

Calibration fixtures live in `docs/harness/evaluator-fixtures.json`. Use them as examples of expected `PASS`, `FAIL`, and `NEED_INPUT` judgment shape; do not treat them as evidence for the current feature.

## Rules
- Read-only by default.
- Do not edit files.
- Do not repair failures.
- Do not replace the primary proof command or gate.
- Do not loosen tests, proof, or scope.
- Be skeptical: missing behavior, weak proof, broad changes, skipped checks.

## Inputs
- `FEATURE_DIR` when feature work is in scope.
- Final diff/changed files.
- Latest proof, gate, build, browser, runtime results.
- Latest `FEATURE_DIR/proof/runs/<timestamp>/` evidence bundle when one exists.
- `agent-observation.md` when present in the evidence bundle.
- `agent-observation.json` when present in the evidence bundle.
- Issue fix without `FEATURE_DIR`: regression proof + observed bug.
- Issue fix: evidence feature lookup happened, or clear reason it did not apply.

## Workflow
1. Load contracts
   - If `FEATURE_DIR`: read `FEATURE.md` and `PROOF.md`.
   - No feature contract: evaluate against reported issue and regression proof.
   - For issue fixes, check one clear matching `docs/features/*/FEATURE.md`.
   - If exactly one matching feature existed and was ignored, return `FAIL`.
   - If no feature clearly matched, accept a focused local regression proof without requiring new feature artifacts.

2. Inspect implementation
   - Review changed files and touched boundaries.
   - Check `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, `docs/TESTING.md` when present.
   - Flag unrelated edits, broad refactors, duplicated logic, hidden compatibility.

3. Evaluate proof quality
   - Behavior coverage: confirm `PROOF.md` proves behavior in `FEATURE.md`; for issues,
     proof catches or was strengthened to catch regression.
   - Proof adequacy: inspect `Proof Scope` when present. Return `FAIL` when a non-trivial
     feature has no proof scope, when false-green risks are not declared, when evidence
     strength is overstated, or when the evaluator is being asked to substitute judgment for
     missing executable evidence.
   - Proof integrity: primary proof explicit, runnable, anti-gameable, not weakened. Check
     whether a broken implementation could still pass the primary proof. Return `FAIL` when the proof can pass while feature is visibly/externally/behaviorally broken.
   - Green but weak: return `FAIL` when proof passes but its proof scope is obviously too narrow
     for the claimed behavior, even if no visible break has been reproduced yet.
   - Contract freeze: return `FAIL` when implementation code and `FEATURE.md`, `PROOF.md`,
     or proof artifacts were edited in the same implementation pass.
   - Boundary fit: public behavior should use public boundaries. UI/workflow: prefer live browser/runtime evidence. API/provider: prefer route, persisted state, outbound
     boundary, read-back evidence.
   - Semantic fit: Flag phrase-locked fixes, hardcoded natural-language keyword lists,
     language-specific gates, or tool removal when domain validation is required. Return `FAIL` when semantic behavior should survive paraphrases or other languages but proof only covers exact terms.
   - Proof Change Guard: return `FAIL` when contract repair changes `FEATURE.md`,
     `PROOF.md`, or proof artifacts without explaining why the original contract was wrong
     or incomplete, which fake implementation the changed proof catches, red/green evidence
     when practical, and why behavior scope was not reduced.

4. Verify results
   - Execution evidence: prefer current output. Rerun only narrowest read-only check when
     needed and allowed.
   - Evidence bundle: inspect its `command.txt`, `result.json`, bounded output, logs,
     screenshots, provider read-back, `notes.md`.
   - Captured primary proof: for completed `FEATURE_DIR` work, return `FAIL` when the primary
     proof result is only raw command output and no `FEATURE_DIR/proof/runs/<timestamp>/`
     bundle from `scripts/proof_run_capture` exists.
   - Agent observation: when `agent-observation.md` exists, inspect context loaded, routing
     decision, failure pattern, repairs attempted, tactic change, contract status, and remaining
     risk. Do not require this file for simple one-shot success. Return `FAIL` when it shows
     skipped recovery, repeated same tactic without change, contract mutation during
     implementation, or a remaining risk that invalidates the claimed done state.
   - Structured agent observation: when `agent-observation.json` exists, inspect the signal booleans.
     Return `FAIL` when `skipped_local_recovery`, `fake_proof_attempted`, `ignored_repo_architecture`,
     or `contract_changed_after_code` is true and the final evidence does not show the issue was
     corrected before claiming done.
   - Target app repo: expect primary proof from `PROOF.md` and `$HOME/.codex/scripts/gate`.
   - Do not require broad new suite execution did not run.
   - Return `FAIL` when `NEED_INPUT` was reported before recovery, available tools, repo
     scripts, browser/app automation, MCP/app connectors, local CLIs, or readiness checks
     were tried where relevant.
   - Return `FAIL` when destructive/external proof was marked `NEED_INPUT` or blocked even
     though approval was available to request for exact command, target, effect, proof reason.
   - Return `FAIL` when destructive primary proof was marked `NEED_INPUT` despite an entry
     matching the current `cwd`, full `command`, and `target`.

5. Judge
   - `PASS`: behavior, proof, anti-gaming coverage, architecture, gate, checks sufficient.
   - `FAIL`: concrete blockers with paths/missing checks.
   - `NEED_INPUT`: missing environment, credential, safe external target, service, or product
     decision still blocks judgment after documented recovery.
   - Return `FAIL` when recovery was skipped and executor could inspect/setup/repair/add
     readiness/retry with local tools.

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
usage, run IDs, prompt text, or implementation summaries unless direct reason for `FAIL`
or `NEED_INPUT`.

## Handoff
- `PASS`: caller may mark queue item `done`.
- `FAIL`: caller should use `coding-repair` for a focused repair, or
  `coding-autonomous-execute` by `AGENTS.md` policy.
- `NEED_INPUT`: do not mark done; report exact user-owned input or external action.
