---
name: coding-repair
description: "Repair a clear issue or failing check with the smallest effective code change, local runtime evidence, existing feature proof lookup, regression tests, and verification. Use when the user asks to debug/fix an existing problem or repair a concrete proof, gate, typecheck, lint, build, or evaluator failure."
metadata:
  short-description: Disciplined issue and failing-check repair workflow
---

# Repair

Purpose: fix an issue correctly, with the smallest effective change and proper verification.

## Default behavior
- If the issue description or expected behavior is unclear, ask for clarification before coding.
- If the issue or failing check is clear, proceed directly to implementation.

## Workflow
1) Read repo docs if present
   - If `docs/` exists, read `docs/INDEX.md` or `docs/README.md` first.
   - If neither exists, scan `docs/` for the most relevant files.

2) Route through existing feature proof when possible
   - Before fixing, inspect `docs/features/*/FEATURE.md` for one clear matching feature
     unless the user supplied an explicit `FEATURE_DIR`.
   - If exactly one feature matches, treat that `FEATURE_DIR` as in scope, read its
     `FEATURE.md` and `PROOF.md`, and run the existing primary proof when practical
     before editing.
   - If the existing primary proof misses the bug, extend that feature proof package with
     a focused failing regression before implementation.
   - Use `coding-proof-author` when the matching `FEATURE_DIR/PROOF.md` is missing,
     vague, stale, or cannot host the regression cleanly.
   - If multiple features plausibly match and the choice materially changes scope, ask
     before attaching the bug to a feature.
   - If no feature clearly matches, do not create `FEATURE.md` by default; create the
     smallest local regression test or proof near the affected code.
   - Create or update `FEATURE.md` and `PROOF.md` only when the expected behavior itself
     needs durable definition or changes product behavior.

3) Understand and reproduce the issue
   - Quote exact error messages or failing tests when available.
   - Identify the owning area (backend route/service/domain, or frontend component/hook).
   - Follow the real call path before deciding the fix: entrypoint, validation/parsing,
     routing or dispatch, owner module, shared helper, persistence, network, or runtime
     boundary.
   - Identify the root cause and state confidence as `clear`, `likely`, or `unknown`.
   - If root cause is `unknown`, create the smallest diagnostic or reproduction that would
     make the next step concrete before editing production code.
   - Prefer current source, executable proof, and runtime evidence over stale comments,
     assumptions, or old CI output.

4) Gather local runtime evidence before editing
   - When the issue is reproducible locally, check app/runtime logs before changing code.
   - If Docker or Docker Compose is present, inspect bounded recent container logs, such as
     `docker compose logs --tail=200` or `docker logs --tail=200 <container>`.
   - If a dev server or test runner is already running, inspect its terminal output.
   - For browser-facing issues, use the Browser/in-app browser when available and inspect
     browser console errors plus failed network requests for the local page.
   - Capture only relevant error lines, stack frames, status codes, and timestamps.
   - Redact secrets and do not print raw environment values, tokens, cookies, or full log dumps.
   - If Docker logs or browser console logs are not applicable, state why before coding.

5) Locate existing logic
   - Search for existing functions/components that already implement similar behavior.
   - Reuse or extend existing code; do not duplicate logic.
   - Read adjacent tests and ownership-boundary code, not only the first file that
     mentions the error.

6) Red phase (test first)
   - Add or update the smallest regression test for the issue.
   - If the issue is attached to a `FEATURE_DIR`, make sure `PROOF.md` covers the
     regression or use `coding-proof-author` to repair it before implementation.
   - Run the narrowest relevant test command and confirm failure.

7) Green phase (minimal fix)
   - Keep changes local to the affected area.
   - Avoid refactors unless required for correctness.
   - Do not change unrelated code.
   - Re-run the same test and confirm it passes.

8) Add verification
   - Backend: add or update the smallest regression test that would have caught the issue.
   - Frontend: add or update a minimal test if the repo uses frontend testing.
   - For local runtime or UI bugs, re-check the same app logs, Docker logs, browser
     console, and failed requests that exposed the issue.
   - Run relevant tests, or state explicitly if they cannot be run here and list exact commands.

9) Finalize safely
   - Use `coding-feature-evaluator` before marking every issue fix complete.
   - Treat evaluator `FAIL` as repair input and evaluator `BLOCKED` as a blocker.
   - If a Codex Goal is active, keep it open until the regression test, relevant broader
     check, and evaluator `PASS` prove completion.
   - If a `FEATURE_DIR` is in scope, run the primary proof command from `PROOF.md`.
   - Do not commit unless explicitly instructed by the user.
   - Do not push, open PRs, update changelogs, or close issues unless explicitly instructed.

10) Escalate only by AGENTS.md policy
   - If the regression test, narrow verification command, or relevant broader check is still
     failing after the first focused fix attempt, follow the autonomous escalation policy
     in `AGENTS.md`.

## Behavioral Baseline
- Think before changing code: reproduce the issue or name the missing evidence before
  editing.
- Root cause first: trace the owning call path and explain why the failing behavior
  occurs before choosing a patch.
- Local evidence first: for local app failures, check Docker/runtime logs and browser
  console logs before deciding the fault is understood.
- Simplicity first: fix the observed issue without speculative cleanup or broader redesign.
- Surgical changes: change only the failing path and remove only artifacts introduced by the fix.
- Goal-driven execution: connect the fix to the regression test or verification command
  that proves the issue is resolved.
- Follow the autonomous escalation policy in `AGENTS.md`; do not broaden scope or
  introduce a repo-local orchestrator.

## Output
- Output final code only unless explanation is explicitly requested.
- Keep comments minimal; explain WHY, not WHAT.
- Include relevant Docker/runtime log and browser console evidence, or why each did not apply.
- Report using the `AGENTS.md` handoff format for completed feature or issue work.
