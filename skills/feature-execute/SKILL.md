---
name: feature-execute
description: Implement one feature end-to-end in Codex App using existing repo skills, red/green TDD, and deterministic validation. Use when a feature contract is ready and the goal is delivery rather than planning infrastructure.
metadata:
  short-description: Codex-native feature execution
---

# Feature Execute

Purpose: deliver one feature inside Codex App without adding a repo-local orchestrator.

## Workflow
1) Start from the feature contract
   - Read `FEATURE_DIR/FEATURE.md`.
   - Use the Gherkin scenarios as the behavior contract.

2) Load repo-level context when present
   - Read `docs/ARCHITECTURE.md` if it exists.
   - Read `docs/CONVENTIONS.md` if it exists.
   - Read `docs/TESTING.md` if it exists.

3) Choose the right implementation skill
   - Use `python-backend` when backend Python work is in scope.
   - Use `frontend` when React or Next.js UI work is in scope.
   - Use `fix-issue` for small corrective changes.

4) Prepare the environment
   - Use `prepare-environment` before running tests, gates, acceptance, package installs,
     dev servers, or framework CLIs.

5) Ensure acceptance coverage exists
   - If `FEATURE_DIR/acceptance/` is missing or incomplete, use `acceptance-author` first.
   - Do not continue broad implementation without the required acceptance harness.

6) Use red/green TDD
   - Add or update the smallest relevant test.
   - Confirm it fails before implementation.
   - Make the smallest code change.
   - Confirm the same test passes after implementation.

7) Validate
   - Run `$HOME/.codex/scripts/gate`.
   - Run `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`.

8) Escalate only on failure
   - If gate or acceptance fails, use `auto-improve`.
   - Keep fixes within the smallest failing scope.

## Rules
- Keep changes local.
- Reuse existing code paths before adding new ones.
- Do not build orchestration infrastructure in this repo.
- Prefer existing domain skills over inventing new coordination logic.
