---
summary: 'Fix an issue correctly with tests and verification (safe, local by default).'
read_when:
  - You need a disciplined issue fix with proper verification.
---
# /fixissue

Purpose: fix an issue correctly, with the smallest effective change and proper verification.

## Default behavior
- If the issue description or expected behavior is unclear, ask for clarification before coding.
- If the issue is clear, proceed directly to implementation.

## Workflow
1) Understand and reproduce the issue
   - Quote exact error messages or failing tests when available.
   - Identify the owning area (backend route/service/domain, or frontend component/hook).

2) Locate existing logic
   - Search for existing functions/components that already implement similar behavior.
   - Reuse or extend existing code; do not duplicate logic.

3) Implement the smallest effective fix
   - Keep changes local to the affected area.
   - Avoid refactors unless required for correctness.
   - Do not change unrelated code.

4) Add verification
   - Backend: add or update the smallest regression test that would have caught the issue.
   - Frontend: add or update a minimal test if the repo uses frontend testing.
   - Run relevant tests, or state explicitly if they cannot be run here and list exact commands.

5) Commit locally
   - Create a small, traceable local commit.
   - Do not push, open PRs, update changelogs, or close issues unless explicitly instructed.

## Output
- Output final code only unless explanation is explicitly requested.
- Keep comments minimal; explain WHY, not WHAT.