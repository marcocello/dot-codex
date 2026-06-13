---
name: coding-python-backend
description: Implement or bootstrap backend API/application changes with clear route/service/domain boundaries and pytest coverage. Use for backend-focused tasks, greenfield API layer creation, missing backend/app setup, API endpoints, routes, service logic, data persistence, FastAPI/service-layer projects, or Python application code even when no existing backend is detected.
metadata:
  short-description: Python backend API implementation
---

# Python Backend

Purpose: implement or bootstrap Python backend API/application work with clear boundaries,
repo-native setup, and pytest coverage.

## Scope
- Applies when:
  - The feature affects backend logic
  - The feature mentions backend, API layer, endpoints, routes, services, data persistence, or
    server-side behavior
  - Python project detected (`backend/pyproject.toml`, `backend/requirements.txt`, or equivalent)
  - Greenfield work needs a backend API layer or `backend/app`
  - No existing backend package exists and the feature requires Python API/application code
  - FastAPI / service-layer architecture is in use

## Architecture expectations
- routes -> services/use-cases -> domain -> infra/data
- No cyclic imports
- No “god” services
- Keep business logic out of routes

## Implementation rules
- In the default greenfield layout, backend application code lives in `backend/app`.
- Backend dependency and tool configuration files live under `backend/` unless repo docs provide a
  different established layout.
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
- Before running Python tooling, use `coding-prepare-environment`.
- Treat `coding-prepare-environment` as the source of truth for `.venv`, dependency install,
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
