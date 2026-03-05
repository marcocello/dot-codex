# Acceptance Fix Prompt (Feature-Scoped)

You are working on one feature directory: FEATURE_DIR.

Source of truth:
- FEATURE_DIR/FEATURE.md
- optional: FEATURE_DIR/notes.*

Goal:
- Make `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR` pass.

Rules:
- If `FEATURE_DIR/acceptance/` is missing, create it.
- Translate behavior from `FEATURE_DIR/FEATURE.md` into executable checks.
- If `FEATURE.md` includes Given/When/Then scenarios, mirror them in setup/action/assertion structure.
- Preserve scenario IDs/titles in test names/markers/comments for traceability.
- Keep scenarios in `FEATURE.md`; keep `FEATURE_DIR/acceptance/` for executable test code only.
- Prefer `FEATURE_DIR/acceptance/tests/` (pytest) or `FEATURE_DIR/acceptance/run.sh`.
- Acceptance tests must be black-box and contain real assertions.
- Do not delete or weaken existing tests to get green.

After changes:
- Run `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`.
- End with exactly: `READY`
