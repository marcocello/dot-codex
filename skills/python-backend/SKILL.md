---
name: Python-Backend
description: Use when implementing backend changes in a Python codebase (often FastAPI).
metadata:
  short-description: Optional user-facing description
---

You are implementing backend changes in a Python codebase (often FastAPI).
Default posture: reuse-first, surgical edits, service-layer ownership, tests before claims.

## Docs-first (always)
- If the repo root contains `docs/`, read `docs/INDEX.md` or `docs/README.md` first.
- If neither exists, scan `docs/` for the most relevant files before coding.
- Also consult `/Users/marcocello/.codex/DOCS_INDEX.md` when present for cross-repo docs and references.

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

This setup uses global gates (run from repo root):

- Engineering gate: `$HOME/.codex/scripts/gate`
- Acceptance gate: `$HOME/.codex/scripts/acceptance --feature features/<id>`

### Python virtualenv rule
If Python is detected in the repo, the canonical environment is a repo-local venv at:

- `.venv/` (repo root)

Do not rely on activating the venv in a shell. Prefer deterministic invocation:

- `.venv/bin/python -m pytest ...`
- `.venv/bin/python -m ruff ...`
- `.venv/bin/python -m mypy ...`

### Acceptance harness (feature-scoped)
When implementing a feature from `features/<id>/feature.yaml`, you must compile acceptance criteria into executable checks under:

- `features/<id>/acceptance/`

Preferred forms:
- `features/<id>/acceptance/tests/` (pytest)
- `features/<id>/acceptance/run.sh` (executable script)

The acceptance gate will run one of those.

### Definition of done (Python backend)
- Feature behavior matches acceptance criteria.
- `$HOME/.codex/scripts/gate` passes.
- `$HOME/.codex/scripts/acceptance --feature features/<id>` passes.
- Tests cover new behavior or regressions (smallest effective tests).

## Common pitfalls to avoid
- Duplicating logic across routes/services.
- Adding new “manager” / “helper” modules for one-off needs.
- Over-validating (double validation in route + service) unless required.
- Refactoring unrelated code while implementing a small feature.
