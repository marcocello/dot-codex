You are in "acceptance-fix" mode for ONE feature folder.

## Objective
Make `./scripts/acceptance --feature <dir>` pass.
If acceptance harness does not exist, create it from the natural-language acceptance criteria in `feature.yaml`.

## Steps
1) Identify active feature folder:
   - Prefer `.press/active_feature.txt` if present, otherwise choose the only folder under `features/`, otherwise ask.
2) Run: `./scripts/acceptance --feature <dir>`
3) If it fails because harness is missing:
   - Create feature-specific checks under `<dir>/acceptance/`
   - Wire them into `./scripts/acceptance --feature <dir>`
4) Fix failures and rerun until green or blocked.
5) Update `.press/status.json` with:
   - phase: ACCEPTANCE_FIX (or BLOCKED/DONE)
   - acceptance results and failed AC ids if known
6) End output with `READY_FOR_PRESS` (or `BLOCKED: ...`).