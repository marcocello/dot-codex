# Acceptance Fix Prompt (Feature-Scoped)

You are working on one feature directory: FEATURE_DIR.
Example feature directory: `docs/features/todo-api`.

Source of truth:
- FEATURE_DIR/FEATURE.md
- optional: FEATURE_DIR/notes.*

Goal:
- Make `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR` pass.

Rules:
- If `FEATURE_DIR/acceptance/` is missing, create it.
- Place feature-scoped acceptance checks under `FEATURE_DIR/acceptance/tests/` (or `FEATURE_DIR/acceptance/run.sh`).
- Translate behavior from `FEATURE_DIR/FEATURE.md` into executable checks.
- Use `FEATURE.md` as the BDD source of truth:
  - Keep scenarios in valid Gherkin (`Feature`, `Scenario`/`Scenario Outline`, `Given/When/Then`).
  - Mirror each scenario in setup/action/assertion structure.
  - Mirror each `Scenario Outline` with parameterized acceptance checks.
- Use red/green TDD for acceptance behavior changes:
  - Red: ensure at least one relevant acceptance check fails before code changes.
  - Green: implement the smallest fix and make that same check pass.
- Preserve scenario IDs/titles in test names/markers/comments for traceability.
- Keep scenarios in `FEATURE.md`; keep `FEATURE_DIR/acceptance/` for executable test code only.
- Prefer `FEATURE_DIR/acceptance/tests/` (pytest) or `FEATURE_DIR/acceptance/run.sh`.
- Acceptance tests must be black-box and contain real assertions.
- Do not delete or weaken existing tests to get green.

After changes:
- Run `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`.
- End with exactly: `READY`
