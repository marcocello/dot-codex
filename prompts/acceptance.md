# Acceptance Fix Prompt (Feature-Scoped)

You are working on one feature directory: FEATURE_DIR.

Source of truth:
- FEATURE_DIR/feature.yaml
- optional: FEATURE_DIR/notes.*

Goal:
- Make `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR` pass.

Rules:
- If `FEATURE_DIR/acceptance/` is missing, create it.
- Translate acceptance criteria from `FEATURE_DIR/feature.yaml` into executable checks.
- Prefer `FEATURE_DIR/acceptance/tests/` (pytest) or `FEATURE_DIR/acceptance/run.sh`.
- Acceptance tests must be black-box and contain real assertions.
- Do not delete or weaken existing tests to get green.

After changes:
- Run `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`.
- End with exactly: `READY`