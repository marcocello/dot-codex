---
name: python-backend
description: Use when implementing backend implementations and changes in a Python codebase (often FastAPI).
metadata:
  short-description: Optional user-facing description
---

## Scope
- Applies when:
  - The feature affects backend logic
  - Python project detected (pyproject.toml / requirements.txt)
  - FastAPI / service-layer architecture is in use

## Architecture expectations
- routes → services/use-cases → domain → infra/data
- No cyclic imports
- No “god” services
- Keep business logic out of routes

## Implementation rules
- Reuse existing patterns before creating new modules
- Follow existing naming and folder structure exactly
- Smallest change that satisfies the feature

## Tests (required)
- Add/extend repo tests (pytest) so that:
  - New behavior is covered
  - At least one failing test exists before change and passes after
- Tests must contain real assertions
- Do not weaken or delete existing tests

## Acceptance harness
- If `FEATURE_DIR/acceptance/` is missing:
  - Create `FEATURE_DIR/acceptance/tests/`
  - Use FastAPI TestClient
  - Write black-box tests hitting actual endpoints
- Translate acceptance criteria in `feature.yaml` into executable checks

## Virtualenv policy
- If Python is detected:
  - `.venv/` at repo root is required
  - Never delete `.venv`
  - Prefer incremental repair
  - If available, use `$HOME/.codex/scripts/ensure_venv`
- All Python tools must be run via `.venv/bin/python -m <tool>`

## Reference repos (Python backend)
Use only if current repo lacks a needed pattern.

- ~/software/marcocello/meshify-backend
  - FastAPI service structure
  - pytest setup
  - ruff configuration
  - service-layer conventions

When using a reference repo:
- Borrow patterns, not whole implementations
- Mention which repo and what pattern was reused (1 line)