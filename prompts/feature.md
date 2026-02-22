# Implement Feature Prompt

You are implementing exactly one feature directory: FEATURE_DIR.

Source of truth:
- FEATURE_DIR/feature.yaml
- optional: FEATURE_DIR/notes.*

Definition of done (authoritative):
- `$HOME/.codex/scripts/gate` passes (repo-wide)
- `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR` passes (feature-scoped)

Requirements:
- Add/extend repo tests that are run by the gate.
- If `FEATURE_DIR/acceptance/` is missing, create it and implement black-box acceptance checks for `feature.yaml`.
- Do not delete or weaken tests to make checks pass.

After changes:
- Run `$HOME/.codex/scripts/gate`
- Run `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`
- End with exactly: `READY`