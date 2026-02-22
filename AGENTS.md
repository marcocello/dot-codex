# AGENTS.md — Marco Dev Discipline (Feature-Driven)

## Feature Path
- Work is driven by a single feature directory: `FEATURE_DIR`.
- The user or orchestrator provides `FEATURE_DIR` (e.g. `features/001-todo-api`).
- Source of truth:
  - `FEATURE_DIR/feature.yaml`
  - optional: `FEATURE_DIR/notes.*`
- If `FEATURE_DIR` is missing, ask once: “What is the feature directory?” Then proceed.

## Project Architecture (Optional)
If the current repository contains `docs/architecture/overview.md`:
- Treat it as authoritative project architecture.
- Apply its constraints (module layout, boundaries, integration rules).
- Do not quote it; apply it.
- Do not override it unless explicitly asked.
- Only read `docs/architecture/overview.md` if it exists in the current repo.
- Do not search other repos for architecture documents.

## Scope
- REUSE FIRST: search and extend existing code; don’t duplicate logic.
- Smallest change that satisfies the feature.
- Keep changes local; no refactors unless required.

## Quality
- Correctness > clarity > consistency > DRY
- Prefer explicit code over cleverness.

## Deterministic checks (authoritative)
- Repo gate: `$HOME/.codex/scripts/gate`
- Feature acceptance: `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`
- Do not claim done unless both pass.

## Tests (required)
- Add/extend repo tests that are run by the gate (pytest/unit/integration as appropriate).
- Acceptance harness:
  - If `FEATURE_DIR/acceptance/` is missing, create it.
  - Translate acceptance criteria in `FEATURE_DIR/feature.yaml` into executable checks.
  - Prefer `FEATURE_DIR/acceptance/tests/` (pytest) or `FEATURE_DIR/acceptance/run.sh`.
- No cheating:
  - Don’t delete/loosen tests to get green.
  - Tests must contain real assertions.

## Python virtualenv (only if Python detected)
- If Python is detected anywhere in the repo, `.venv/` at repo root is required.
- Never delete `.venv`. Prefer incremental repair.
- If available, use `$HOME/.codex/scripts/ensure_venv`.
- Run python tooling via `.venv/bin/python -m <tool>` (no shell activation assumptions).

## References (skill-scoped)
- Reference repos are defined inside skills (Python backend, frontend, infra).
- Use reference repos only when the matching skill is active and current repo lacks a pattern.
- If you use one, state which repo and what pattern you reused (1 line).

## Output token
- When handing control back, end with exactly: `READY`
- If blocked: `NEED_INPUT: <question>` or `BLOCKED: <reason>`