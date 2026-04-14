## dot-codex

## Objective
Keep Codex App predictable for feature-driven work.

This config keeps the repo skill-based, spec-first, and validation-driven:
- `docs/features/<feature-id>/FEATURE.md` is the source of truth for one feature.
- Skills help Codex write specs, research unknowns, generate acceptance, implement, and repair.
- `$HOME/.codex/scripts/gate` and `$HOME/.codex/scripts/acceptance --feature <FEATURE_DIR>` decide done.
- No in-repo orchestrator.

## Workflow

Greenfield:
1. `codex "Use the app-to-features skill for this app idea"`
2. Pick one generated feature directory.
3. `codex "Use the feature skill for docs/features/<feature-id>"`
4. If needed, `codex --search "Use the research skill for docs/features/<feature-id>"`
5. `codex "Use the acceptance-author skill for docs/features/<feature-id>"`
6. `codex "Use the feature-execute skill for docs/features/<feature-id>"`
7. Run gate and feature acceptance.

Brownfield:
1. Choose one `FEATURE_DIR`.
2. `codex "Use the feature skill for docs/features/<feature-id>"`
3. If needed, `codex --search "Use the research skill for docs/features/<feature-id>"`
4. `codex "Use the acceptance-author skill for docs/features/<feature-id>"`
5. `codex "Use the feature-execute skill for docs/features/<feature-id>"`
6. If checks fail, `codex "Use the auto-improve skill for docs/features/<feature-id>"`
7. Run gate and feature acceptance.
