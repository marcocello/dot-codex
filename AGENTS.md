# AGENTS.md — Marco Dev Discipline (Feature-Driven)

## Feature Path
- Work is driven by a single feature directory: `FEATURE_DIR`.
- The user or orchestrator provides `FEATURE_DIR` (e.g. `features/001-todo-api`).
- Source of truth:
  - `FEATURE_DIR/FEATURE.md`
  - optional: `FEATURE_DIR/notes.*`
- If `FEATURE_DIR` is missing, ask once: “What is the feature directory?” Then proceed.

## Project Architecture (Optional)
If the current repository contains `docs/ARCHITECTURE.md`:
- Treat it as authoritative project architecture.
- Apply its constraints (module layout, boundaries, integration rules).
- Do not quote it; apply it.
- Do not override it unless explicitly asked.
- Only read `docs/ARCHITECTURE.md` if it exists in the current repo.
- Do not search other repos for architecture documents.

## Living Documentation
- Keep `FEATURE_DIR/FEATURE.md` updated whenever implemented behavior changes or expands during the conversation.
- If an implementation introduces an architectural change, update `docs/ARCHITECTURE.md` in the same change.
- If an architectural change occurs and `docs/ARCHITECTURE.md` does not exist yet, create it with the new baseline architecture.

## Scope
- REUSE FIRST: search and extend existing code; don’t duplicate logic.
- Smallest change that satisfies the feature.
- Keep changes local; no refactors unless required.
- AVOID backward compatibility by default; only preserve it when explicitly requested.

## Quality
- Correctness > clarity > consistency > DRY
- Prefer explicit code over cleverness.

## Deterministic checks (authoritative)
- Repo gate: `$HOME/.codex/scripts/gate`
- Feature acceptance: `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`
- Do not claim done unless both pass.

## Tests (required)
- Add/extend repo tests that are run by the gate (pytest/unit/integration as appropriate).
- If acceptance tests are missing, use `prompts/acceptance.md` to derive and generate them from `FEATURE.md`.
- Acceptance harness:
  - If `FEATURE_DIR/acceptance/` is missing, create it.
  - Translate behavior described in `FEATURE_DIR/FEATURE.md` into executable checks.
  - Use scenarios described in `FEATURE.md` (including Gherkin blocks) as authoritative behavior.
  - Preserve scenario IDs/titles in test names/markers/comments for traceability.
  - Prefer `FEATURE_DIR/acceptance/tests/` (pytest) or `FEATURE_DIR/acceptance/run.sh`.
- For spec-driven acceptance refinement outputs:
  - Keep `FEATURE.md` as the source-of-truth feature document.
  - Keep `FEATURE.md` less schematic: title + feature description minimum; optional user stories and Gherkin scenarios.
  - Put Gherkin scenarios in `FEATURE.md` (not in `FEATURE_DIR/acceptance/features/`).
  - Keep `FEATURE_DIR/acceptance/` for executable test code only.
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
