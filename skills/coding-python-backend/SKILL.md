---
name: coding-python-backend
description: "Implement or bootstrap Python backend APIs and applications with clear route, service, domain, persistence, and pytest boundaries."
metadata:
  short-description: Python backend API implementation
---

# Python Backend

Purpose: implement or bootstrap Python backend API/application work with clear boundaries, repo-native setup, and pytest coverage.

The coding lifecycle skills own routing, discovery, fixed acceptance, Goals, review, and recording. This skill supplies Python technique; use the light Fix path for known defects and Shape/Ship for material accepted behavior changes.

## Scope
- Applies when:
  - The feature affects backend logic
  - The feature mentions backend, API layer, endpoints, routes, services, data persistence, or server-side behavior
  - Python project detected (`backend/pyproject.toml`, `backend/requirements*.txt`, `backend/app/requirements*.txt`, or equivalent)
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
- Backend dependency and tool configuration files live under `backend/` unless repo docs provide a different established layout.
- Reuse existing patterns before creating new modules
- Follow existing naming and folder structure exactly
- Smallest change that satisfies the feature
- Avoid backward compatibility work by default; do it only when explicitly requested

## Verification
- Reuse pytest and select checks for affected routes, services, persistence, shared utilities, and their consumers. Add focused coverage for a concrete uncovered risk; reproduce the failure when practical.
- For material API features, the separate proof author should exercise HTTP against the real app runtime. Internal changes may use contract, migration, invariant, or equivalence proof matching the accepted boundary.
- Assert requested outcomes rather than incidental private structure. Generic tests support verification but do not replace dedicated feature proof.
- Implement against the fixed proof. Route proof defects through the [central proof procedure](../../docs/harness/coding/proof.md#fixed-acceptance), which distinguishes independent setup repair from user-owned acceptance decisions; this skill cannot rewrite frozen proof inputs. Repair introduced regressions within the current feature run.

## Environment
- Use `coding-prepare-environment` when setup or readiness is unknown; reuse a prepared environment.
- Treat `coding-prepare-environment` as the source of truth for `.venv`, dependency install, `.env` location, and command-prefix policy.

## Reference repos (Python backend)
Use only when the current repository lacks a needed pattern.

When using a reference repo:
- Borrow patterns, not whole implementations.
- Mention repo + pattern reused (1 line).
