---
name: Python-Backend
description: Use when implementing backend changes in a Python codebase (often FastAPI).
metadata:
  short-description: Optional user-facing description
---

You are implementing backend changes in a Python codebase (often FastAPI).
Default posture: reuse-first, surgical edits, service-layer ownership, tests before claims.

## First move (always)
1) Locate the real owner of the behavior:
   - route/controller, service/use-case, domain logic, data/infra.
2) Search for existing functions/services that already do 60–90% of the job.
3) Identify the smallest change that satisfies the request without refactoring the world.

## Architecture assumptions (unless repo says otherwise)
- routes/controllers: orchestration only (request parsing, auth, call service, return response).
- services/use-cases: business logic + transactions + orchestration of domain + infra.
- domain: pure logic (no DB sessions, no network, no framework imports).
- data/infra: ORM models, repositories/adapters, external clients.

## Service-layer discipline (Marco default)
- Prefer cohesive service classes/functions that encapsulate both business logic and data access,
  *unless* the repo clearly uses repositories already.
- Avoid creating new layers/interfaces “just in case.”
- If a function is the owner of a rule, everyone calls it—no re-implementations.

## Data & DB changes
- Prefer small, explicit queries over clever abstractions.
- Keep transaction boundaries clear (one request → one unit of work, unless async/job).
- When changing schema/contracts:
  - update model/schema
  - update validators/serializers
  - update tests
  - update any downstream call sites

## API behavior
- Be explicit about:
  - status codes
  - error shapes
  - validation rules
  - idempotency where relevant
- Do not silently swallow errors at boundaries (DB, network, parsing).
- Return stable response schemas; avoid breaking clients.

## Code quality defaults
- Types: add/adjust typing where it improves correctness and readability.
- Logging: only at boundaries and key business events; avoid noisy logs.
- Comments: rare; explain WHY, not WHAT.

## Testing & verification (required before claiming success)
Pick what exists in repo; minimal but real:
- Unit test for service logic.
- FastAPI TestClient test for route + validation.
- If async tasks: test the task function directly.

If you cannot execute tests here:
- state that explicitly
- provide exact commands:
  - pytest (and any markers)
  - lint/typecheck commands used by the repo

## Common pitfalls to avoid
- Duplicating logic across routes/services.
- Adding new “manager” / “helper” modules for one-off needs.
- Over-validating (double validation in route + service) unless required.
- Refactoring unrelated code while implementing a small feature.