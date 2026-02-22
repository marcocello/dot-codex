# AGENTS.md — Marco Dev Discipline (Feature-Driven)

## Feature Path (source of truth)
- Work is driven by a single feature directory (FEATURE_DIR).
- The user (or an orchestrator) will provide FEATURE_DIR (e.g., `features/001-todo-api`).
- The spec is: `FEATURE_DIR/feature.yaml`
- Optional refinements: `FEATURE_DIR/notes.*`
- If FEATURE_DIR is not provided, ask once: “What is the feature directory?” Then proceed using the provided path.

## Scope
- REUSE FIRST: search codebase, extend existing code, don’t duplicate logic.
- Smallest change that satisfies the feature.
- Keep changes local; no refactors unless required.

## Quality bar
- Correctness > clarity > consistency > DRY
- Prefer explicit code over cleverness.

## Gates (authoritative)
- Engineering gate (repo-wide): `$HOME/.codex/scripts/gate`
- Feature acceptance: `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`
- Do not claim done unless both pass.

## Tests (required)
- Add/extend repo tests that are run by the engineering gate (unit/integration as appropriate).
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

## Output protocol
- If asked to “hand back control” (or when finished), end with exactly: `READY_FOR_PRESS`
- If blocked, output: `NEED_INPUT: <question>` or `BLOCKED: <reason>`

## References (skill-scoped)
- Reference repos are defined inside each skill (e.g. Python backend, frontend).
- Use them only when the active task matches the skill and current repo lacks a needed pattern.
- If you use a reference repo, state which one and what pattern you borrowed (1 line).