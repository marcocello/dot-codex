---
name: coding-fix-issue
description: >-
  Fix a clear issue with the smallest effective code change, local runtime evidence,
  regression tests, verification, and automatic coding-autonomous-execute escalation when bounded
  repeated repair is needed. Use when the user asks to debug/fix an existing problem.
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

3) Gather local runtime evidence before editing
   - When the issue is reproducible locally, check app/runtime logs before changing code.
   - If Docker or Docker Compose is present, inspect bounded recent container logs, such as
     `docker compose logs --tail=200` or `docker logs --tail=200 <container>`.
   - If a dev server or test runner is already running, inspect its terminal output.
   - For browser-facing issues, use the Browser/in-app browser when available and inspect browser
     console errors plus failed network requests for the local page.
   - Capture only relevant error lines, stack frames, status codes, and timestamps.
   - Redact secrets and do not print raw environment values, tokens, cookies, or full log dumps.
   - If Docker logs or browser console logs are not applicable, state why before coding.

4) Locate existing logic
   - Search for existing functions/components that already implement similar behavior.
   - Reuse or extend existing code; do not duplicate logic.

5) Red phase (test first)
   - Add or update the smallest regression test for the issue.
   - Run the narrowest relevant test command and confirm failure.

6) Green phase (minimal fix)
   - Keep changes local to the affected area.
   - Avoid refactors unless required for correctness.
   - Do not change unrelated code.
   - Re-run the same test and confirm it passes.

7) Add verification
   - Backend: add or update the smallest regression test that would have caught the issue.
   - Frontend: add or update a minimal test if the repo uses frontend testing.
   - For local runtime or UI bugs, re-check the same app logs, Docker logs, browser console, and
     failed requests that exposed the issue.
   - Run relevant tests, or state explicitly if they cannot be run here and list exact commands.

8) Finalize safely
   - Use `coding-feature-evaluator` when the issue fix is attached to a `FEATURE_DIR`,
     broad behavior contract, UI flow, or user-visible workflow.
   - Treat evaluator `FAIL` as repair input and evaluator `BLOCKED` as a blocker.
   - If a Codex Goal is active, keep it open until the regression test, relevant broader check, and
     any required evaluator result prove completion.
   - Do not commit unless explicitly instructed by the user.
   - Do not push, open PRs, update changelogs, or close issues unless explicitly instructed.

9) Automatically use `coding-autonomous-execute` for repeated repair
   - If the regression test, narrow verification command, or relevant broader check is still
     failing after the first focused fix attempt, automatically use `coding-autonomous-execute`.
   - Do not wait for a separate user request.
   - Use this stop condition: the regression test and relevant verification pass, or the same
     blocker repeats three times.
   - Default budget: three loop iterations.
   - Each loop iteration must isolate the smallest failing scope, make one minimal fix, and rerun
     the narrowest failing check before any broader check.
   - Use `coding-feature-evaluator` after each repair pass when a feature contract or
     user-visible workflow is in scope.
   - Do not start schedulers or background work unless the user explicitly asks for recurring or
     unattended execution.

## Behavioral Baseline
- Think before changing code: reproduce the issue or name the missing evidence before editing.
- Local evidence first: for local app failures, check Docker/runtime logs and browser console logs
  before deciding the fault is understood.
- Simplicity first: fix the observed issue without speculative cleanup or broader redesign.
- Surgical changes: change only the failing path and remove only artifacts introduced by the fix.
- Goal-driven execution: connect the fix to the regression test or verification command that proves
  the issue is resolved.
- `coding-autonomous-execute` is an automatic bounded escalation path for stubborn failures, not
  permission to broaden scope or introduce a repo-local orchestrator.

## Output
- Output final code only unless explanation is explicitly requested.
- Keep comments minimal; explain WHY, not WHAT.
- Include `Skills used:` with every skill actually loaded or followed.
- Include relevant Docker/runtime log and browser console evidence, or why each did not apply.
- Include red evidence and green evidence, or why red/green could not run.
- Include verification commands, evaluator result when used, and concrete blockers.
