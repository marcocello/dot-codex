---
name: coding-python-backend
description: "Implement or bootstrap Python backend APIs and applications with clear route, service, domain, persistence, and pytest boundaries."
metadata:
  short-description: Python backend API implementation
---

# Python Backend

Read [Coding writing](../../docs/harness/coding/writing.md) once per task and apply it to specifications, proof, reports, and human interaction.

Purpose: implement or bootstrap Python backend API/application work with clear boundaries, repo-native setup, and pytest coverage.

The coding lifecycle skills own routing, discovery, fixed acceptance, Goals, review, and recording. This skill supplies Python technique; use the light Repair path for known defects and Design Specs and Proof/Implement for material accepted behavior changes, following [product discovery and autonomy](../coding-product-partner/SKILL.md#discovery-and-autonomy).

## Scope
- Applies when:
  - The feature affects backend logic
  - The feature mentions backend, API layer, endpoints, routes, services, data persistence, or server-side behavior
  - Python project detected (dependency manifests or Python source in the selected backend component)
  - Greenfield work needs a backend API layer or the selected backend component
  - No existing backend package exists and the feature requires Python API/application code
  - FastAPI / service-layer architecture is in use

## Architecture expectations
- Separate routes, use cases, domain policy, and persistence when those responsibilities warrant it. Simple operations need not introduce a class or layer for each label.
- No cyclic imports
- No “god” services
- Keep reusable domain policy and substantial orchestration outside transport handlers; straightforward request/response mapping may stay local.

## Implementation rules
- Follow the greenfield component locations owned by `coding-prepare-environment`: use that skill's selected backend component path.
- Keep backend dependency and tool configuration with the component selected by `coding-prepare-environment`, preserving established repository conventions.
- Reuse existing patterns before creating new modules
- Follow existing naming and folder structure exactly
- Smallest change that satisfies the feature
- Preserve established consumers and accepted contracts. Add compatibility machinery only for an actual supported consumer or migration need; ask before consequential breaking changes outside the request.

## Verification
- Reuse pytest and select checks for affected routes, services, persistence, shared utilities, and their consumers. Add focused coverage for a concrete uncovered risk; reproduce the failure when practical.
- For material API features, exercise HTTP against the real app runtime. Internal changes may use contract, migration, invariant, or equivalence proof matching the accepted boundary.
- Assert requested outcomes rather than incidental private structure. Reuse existing tests as feature proof when they exercise and assert the accepted behavior.
- Implement against the fixed proof. Route proof defects through the [central proof procedure](../../docs/harness/coding/proof.md#fixed-acceptance), preserving accepted behavior when repairing test setup or assertions. Repair introduced regressions within the current feature run.

## Environment
- Use `coding-prepare-environment` when setup or readiness is unknown; reuse a prepared environment.
- Treat `coding-prepare-environment` as the source of truth for `.venv`, dependency install, `.env` location, and command-prefix policy.

## Reference repos (Python backend)
Use only when the current repository lacks a needed pattern.

When using a reference repo:
- Borrow patterns, not whole implementations.
- Mention repo + pattern reused (1 line).
