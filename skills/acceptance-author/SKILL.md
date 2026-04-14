---
name: acceptance-author
description: Generate or repair executable feature acceptance checks from FEATURE.md using black-box behavior and repo-native test conventions. Use when a feature needs acceptance coverage or its acceptance harness is failing.
metadata:
  short-description: Feature acceptance authoring
---

# Acceptance Author

Purpose: turn `FEATURE.md` into executable acceptance coverage without introducing orchestration.

## Workflow
1) Read the contract
   - Treat `FEATURE_DIR/FEATURE.md` as the behavior contract.
   - Mirror scenario titles and outcomes in acceptance test names where practical.

2) Create or repair the harness
   - Create `FEATURE_DIR/acceptance/tests/` if missing.
   - Prefer pytest-based acceptance tests under `acceptance/tests`.
   - Use `FEATURE_DIR/acceptance/run.sh` only when pytest is not appropriate.

3) Keep checks black-box
   - Assert observable behavior only.
   - Avoid implementation-coupled assertions.

4) Verify
   - Run the narrowest acceptance test first.
   - Run `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`.

## Rules
- Keep `FEATURE.md` as the source of truth.
- Do not move Gherkin scenarios into a separate orchestration system.
- Do not invent behavior that is not implied by the feature contract.
