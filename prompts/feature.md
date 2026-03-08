# Implement Feature Prompt

You are implementing exactly one feature directory: FEATURE_DIR.

Source of truth:
- FEATURE_DIR/FEATURE.md
- optional: docs/ARCHITECTURE.md

Definition of done (authoritative):
- `$HOME/.codex/scripts/gate` passes (repo-wide)
- `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR` passes (feature-scoped)

Requirements:
- Add/extend repo tests that are run by the gate.
- Use red/green TDD:
  - Red: add/update the smallest relevant test and confirm it fails before implementation.
  - Green: implement the smallest effective change and confirm that same test passes.
- If `FEATURE_DIR/acceptance/` is missing, create it and implement black-box acceptance checks.
- Translate behavior from `FEATURE.md` into executable checks.
- If `FEATURE.md` includes Gherkin scenarios, treat them as authoritative for acceptance behavior.
- Preserve scenario names/IDs in test names/markers/comments for traceability.
- Keep Gherkin scenarios in `FEATURE.md`; keep `FEATURE_DIR/acceptance/` for executable test code only.
- Do not delete or weaken tests to make checks pass.

After changes:
- Run `$HOME/.codex/scripts/gate`
- Run `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`
- End with exactly: `READY`
