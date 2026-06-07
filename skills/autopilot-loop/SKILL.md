---
name: autopilot-loop
description: Run Codex in bounded loop, cron, scheduled automation, or autopilot workflows with explicit stop conditions, verification, audit logs, and worktree isolation. Use when the user asks for loop, cron, recurring, scheduled, monitor, autopilot, keep going until done, or background Codex work.
metadata:
  short-description: Bounded Codex loop and automation workflow
---

# Autopilot Loop

Purpose: make Codex repeat or schedule useful work without adding a repo-local workflow engine.
Do not introduce a repo-local workflow engine.

## Choose the Smallest Automation Layer
1) In-session loop
   - Use for current-turn repair: failing tests, incomplete feature work, migration batches, or
     inbox-style triage.
   - Keep it bounded: define a stop condition plus a token budget, iteration budget, or time budget.
   - Prefer one small fix per loop, then rerun the narrowest relevant check.

2) Codex App automations
   - Use for reminders, monitors, recurring follow-ups, or scheduled checks that should survive the
     current conversation.
   - When creating, viewing, updating, or deleting these, use the Codex App automation tool
     (`automation_update`) when it is available. Do not write raw automation directives by hand.
   - Each automation prompt must be self-contained: repo path, branch/worktree rule, success
     criteria, budget, allowed checks, and where to report.

3) OS cron or launchd
   - Use only for CLI-safe jobs that can finish without interactive follow-up.
   - Prefer macOS `launchd` for this machine; use cron only for simple portable schedules.
   - Log stdout/stderr to an audit log file and keep the command idempotent.
   - Do not use destructive commands, pushes, force flags, secret edits, or deploy actions in
     unattended schedules.

4) Parallel worktrees
   - Use one branch/worktree per background task.
   - Do not run multiple autonomous Codex sessions against the same checkout.
   - Use `codex/` branch prefixes unless the user explicitly asks otherwise.

## In-Session Loop Pattern
1) State the goal and stop condition.
   - Good: "Continue until `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR` passes or three
     repair attempts fail on the same issue."
   - Bad: "Keep improving this."

2) Set a budget.
   - Default to three repair iterations for code changes.
   - Use a token budget if the user gives one.
   - Stop early when the same blocker repeats and report `BLOCKED: <reason>`.

3) Run the smallest feedback loop.
   - For implementation and fixes, use red/green TDD.
   - Run the narrowest failing test first.
   - Then run `$HOME/.codex/scripts/gate`.
   - If `FEATURE_DIR` is in scope, run `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`.

4) Record what changed.
   - Summarize attempts, failing checks, passing checks, skipped checks, and remaining risk.
   - Do not claim done until required checks pass.

## Scheduled Prompt Template
Use this shape for Codex App automations or CLI-safe schedules:

```text
Repo: /absolute/path/to/repo
Branch/worktree: create or use an isolated codex/<task> branch; never mutate main directly.
Goal: <specific outcome>
Stop condition: <passing check, empty queue, or explicit report-only condition>
Budget: <token/time/iteration limit>
Allowed actions: <read-only, test-only, draft PR, local edit, etc.>
Forbidden actions: no destructive commands, no force push, no deploy, no secret edits.
Verify: run the narrowest relevant check, then $HOME/.codex/scripts/gate, and acceptance when
FEATURE_DIR is in scope.
Audit log: write a short summary of commands, files changed, and results.
Report: <where to post or what final answer should include>
```

## Permission Baseline
- Keep unattended runs conservative.
- Do not use destructive commands in automation prompts.
- Do not auto-approve writes to secrets, deployment files, CI credentials, or mainline branches.
- For read-only monitors, deny file edits entirely.
- For repair loops, allow local edits only inside the target repo and require verification before
  any handoff.
- Keep an audit log for every unattended run: command, repo, branch, changed files, checks, and
  final status.

## Promotion Rule
- First prove the workflow manually in one Codex session.
- Then use a bounded in-session loop.
- Then promote stable recurring checks to Codex App automations.
- Use cron or launchd only when Codex App automations are unavailable or the job must be owned by
  the local OS scheduler.

## Handoff Checklist
- Goal and stop condition were explicit.
- Budget was explicit or defaulted to three iterations.
- Background work used an isolated branch or worktree.
- Audit log or final run summary exists.
- Narrowest checks were run.
- `$HOME/.codex/scripts/gate` was run for target app repos.
- `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR` was run when a feature directory was in
  scope.
- Any skipped check is explained with the exact reason.
- No repo-local workflow engine was introduced.
