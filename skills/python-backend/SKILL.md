---
name: python-backend
description: Implement backend changes in Python codebases (especially FastAPI/service-layer projects) with clear route/service/domain boundaries and pytest coverage. Use only for backend-focused tasks where Python application code is in scope.
metadata:
  short-description: Optional user-facing description
---

## Scope
- Applies when:
  - The feature affects backend logic
  - Python project detected (pyproject.toml / requirements.txt)
  - FastAPI / service-layer architecture is in use

## Architecture expectations
- routes -> services/use-cases -> domain -> infra/data
- No cyclic imports
- No “god” services
- Keep business logic out of routes

## Implementation rules
- Application code must be located in `app/` folder
- `requirements.txt` must be located in `app/` folder
- Reuse existing patterns before creating new modules
- Follow existing naming and folder structure exactly
- Smallest change that satisfies the feature
- Avoid backward compatibility work by default; do it only when explicitly requested

## Tests (required)
- Add/extend repo tests (pytest) so that:
  - Red phase: at least one relevant test fails before implementation
  - Green phase: the same test passes after the code change
  - New behavior is covered
- Tests must contain real assertions
- Do not weaken or delete existing tests

## Acceptance harness
- If `FEATURE_DIR/acceptance/` is missing:
  - Create `FEATURE_DIR/acceptance/tests/`
  - Use FastAPI TestClient
  - Write black-box tests hitting actual endpoints
- Translate behavior described in `FEATURE.md` into executable checks

## Environment
- Before running Python tooling, use `prepare-environment`.
- Treat `prepare-environment` as the source of truth for `.venv`, dependency install,
  `.env` location, and command-prefix policy.

## Reference repos (Python backend)
Use only if current repo lacks a needed pattern.

- `$HOME/software/marcocello/meshify-backend`
  - FastAPI service layout
  - pytest fixtures style
  - ruff config conventions

When using a reference repo:
- Borrow patterns, not whole implementations.
- Mention repo + pattern reused (1 line).
