---
name: fix-issue
description: Fix a clear issue with the smallest effective code change, regression tests, verification, and automatic autopilot-loop escalation when bounded repeated repair is needed. Use when the user asks to debug/fix an existing problem.
metadata:
  short-description: Disciplined issue-fix workflow
---

# Fix Issue

Purpose: fix an issue correctly, with the smallest effective change and proper verification.

## Default behavior
- If the issue description or expected behavior is unclear, ask for clarification before coding.
- If the issue is clear, proceed directly to implementation.

## Workflow
1) Read repo docs if present
   - If `docs/` exists, read `docs/INDEX.md` or `docs/README.md` first.
   - If neither exists, scan `docs/` for the most relevant files.

2) Understand and reproduce the issue
   - Quote exact error messages or failing tests when available.
   - Identify the owning area (backend route/service/domain, or frontend component/hook).

3) Locate existing logic
   - Search for existing functions/components that already implement similar behavior.
   - Reuse or extend existing code; do not duplicate logic.

4) Red phase (test first)
   - Add or update the smallest regression test for the issue.
   - Run the narrowest relevant test command and confirm failure.

5) Green phase (minimal fix)
   - Keep changes local to the affected area.
   - Avoid refactors unless required for correctness.
   - Do not change unrelated code.
   - Re-run the same test and confirm it passes.

6) Add verification
   - Backend: add or update the smallest regression test that would have caught the issue.
   - Frontend: add or update a minimal test if the repo uses frontend testing.
   - Run relevant tests, or state explicitly if they cannot be run here and list exact commands.

7) Finalize safely
   - Use `feature-evaluator` when the issue fix is attached to a `FEATURE_DIR`, broad behavior
     contract, UI flow, or user-visible workflow.
   - Treat evaluator `FAIL` as repair input and evaluator `BLOCKED` as a blocker.
   - If a Codex Goal is active, keep it open until the regression test, relevant broader check, and
     any required evaluator result prove completion.
   - Do not commit unless explicitly instructed by the user.
   - Do not push, open PRs, update changelogs, or close issues unless explicitly instructed.

8) Automatically use `autopilot-loop` for repeated repair
   - If the regression test, narrow verification command, or relevant broader check is still
     failing after the first focused fix attempt, automatically use `autopilot-loop`.
   - Do not wait for a separate user request.
   - Use this stop condition: the regression test and relevant verification pass, or the same
     blocker repeats three times.
   - Default budget: three loop iterations.
   - Each loop iteration must isolate the smallest failing scope, make one minimal fix, and rerun
     the narrowest failing check before any broader check.
   - Use `feature-evaluator` after each repair pass when a feature contract or user-visible workflow
     is in scope.
   - Do not start cron, scheduled automations, or background work unless the user explicitly asks
     for recurring or unattended execution.

## Behavioral Baseline
- Think before changing code: reproduce the issue or name the missing evidence before editing.
- Simplicity first: fix the observed issue without speculative cleanup or broader redesign.
- Surgical changes: change only the failing path and remove only artifacts introduced by the fix.
- Goal-driven execution: connect the fix to the regression test or verification command that proves
  the issue is resolved.
- `autopilot-loop` is an automatic bounded escalation path for stubborn failures, not permission to
  broaden scope or introduce a repo-local orchestrator.

## Output
- Output final code only unless explanation is explicitly requested.
- Keep comments minimal; explain WHY, not WHAT.
