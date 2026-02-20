
You are implementing exactly ONE feature folder in a repo, intended to be driven by an orchestrator ("Press").

## Input
A feature folder exists at:
- `features/<id>/feature.yaml` (and optional `notes.md`)

## Your job
1) Read `feature.yaml` and implement the feature.
2) Ensure repo has canonical scripts:
   - `./scripts/gate`
   - `./scripts/acceptance` (must support `--feature <dir>`)
   If missing, create them first.
3) Convert acceptance criteria from `feature.yaml` into executable checks:
   - Prefer pytest for FastAPI (TestClient), or Playwright for Next.js flows.
   - Put feature-specific checks under `features/<id>/acceptance/` (tests/data/scripts).
4) Self-verify:
   - Run `./scripts/gate`
   - Run `./scripts/acceptance --feature features/<id>`
   Fix and rerun until both pass (unless blocked).
5) Write `.press/status.json` with phase + results + head sha.
6) End output with `READY_FOR_PRESS` (or `DONE` if both gates passed and feature is complete).

## Constraints
- Smallest effective changes.
- Do not weaken gates to pass.
- If blocked, write status with phase=BLOCKED and end with `BLOCKED: ...`.