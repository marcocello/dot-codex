---
name: fix-issue
description: Fix a clear issue with the smallest effective code change, regression tests, and verification. Use when the user asks to debug/fix an existing problem.
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
   - Do not commit unless explicitly instructed by the user.
   - Do not push, open PRs, update changelogs, or close issues unless explicitly instructed.

## Output
- Output final code only unless explanation is explicitly requested.
- Keep comments minimal; explain WHY, not WHAT.
