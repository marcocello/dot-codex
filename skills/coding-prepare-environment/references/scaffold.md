# Reusable React + FastAPI environment

Use this bundle for an authorized greenfield full-stack application. It is self-contained under this skill; it does not depend on the original reference repositories or the separate SSH harness. For an explicitly different framework or a single component, follow that scope instead of generating an unwanted full stack.

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/skills/coding-prepare-environment/scripts/scaffold.py" /absolute/empty/project
```

The copier refuses nonempty targets, files, and destination symlinks. It does not merge brownfield files, initialize Git, install tools globally, start services, publish images, or deploy. Generate outside this skill's assets. Repository-local installation and service startup follow the user's active setup/implementation authority.

## What is reused

Patterns inspected in `meshify-monorepo`, `fieldmate`, and `twyd-portal`:

| Reference surface | Reusable decision |
| --- | --- |
| All three: `frontend/app`, Vite, React, TypeScript | Component-local package and lockfile, API client, proxy, production static build |
| All three: `.vscode/tasks.json` | Named backend/frontend/fullstack tasks, explicit cwd, dedicated terminals; add readiness prerequisites and stop/log tasks |
| Meshify/Fieldmate: `backend/app/config/log.py` and `log_context.py`; TWYD: `backend/app/log.py` | Shared component logger, severity, safe structured details, context isolation; generic request IDs replace product-specific user/job metadata |
| All three: backend deployment Compose files | Healthy persistent PostgreSQL, isolated service networking, development vs production exposure |
| Meshify/Fieldmate/TWYD: production Kubernetes deployment assets | Separate app/database lifecycle, probes, resources, persistent storage; use Secret references and migration sequencing |

The existing SSH React/FastAPI starter supplied the working notes round trip, SQLAlchemy/Alembic, lockfiles, Caddy, Compose and CI baseline. This bundle adds portable operational patterns from the references. It does not copy product logic, service accounts, customer domains, identity integrations, worker fleets, tunnels, or secret values. The notes feature is a replaceable persistence example, not a product requirement. Cloud provisioning, scheduler services, CI registry publication and application authentication are added when the chosen product and deployment target call for them. For requested Terraform deployment roots, use the separate [Terraform conventions and template](terraform.md); the application copier does not include them or relocate the starter's `deploy/k8s` assets.

## Verify the generated journey

- On a disposable generated project, run `make setup check`, then `make up smoke`. The latter builds the container images, waits for readiness and saves/reads data through the web proxy against PostgreSQL.
- Install the locked Playwright browser and run `npm run test:e2e` from `frontend/app` against the running stack. The persistence test reloads the page and the failure test preserves an unsaved draft.
- For host development, `make dev-ready` prepares the DB and migrations; `make backend` and `make frontend` start reload servers. Validate the VS Code commands/cwd and expected startup ordering.
- Verify `/api/health`, `/api/ready`, request IDs, and that logging omits request secrets. Check Git visibility of nested source, lockfiles, migrations and dotfiles; dependencies, build products and `.env` stay ignored.
- Render Kubernetes locally using `scripts/render_k8s.py`. Review the generated manifests and migration order in `deploy/k8s/README.md`. A real rollout requires an explicitly selected authorized cluster, namespace, registry, TLS and Secret configuration; local validation does not prove deployment.
- Use a unique Compose project and port for evaluation, stop its services afterward, and preserve user data. Report unavailable runtime checks rather than treating generated files as proof.

## Existing-project adoption

Inspect the existing app boundaries, package managers, lockfiles, task labels, environment loading, data schema/migrations, logs, deployment tooling and CI before proposing adoption. Present the smallest useful set of changes: source/destination paths, overwritten commands, dependency changes, deployment target, and migration/data implications. Ask the user whether to adopt that concrete proposal or retain the current setup, unless the same proposal is already authorized. Keep ordinary setup and diagnosis moving without requiring adoption.

Never run the copier on an existing repository, including one containing only docs or Git metadata. Apply approved additions selectively and preserve unrelated task entries/settings, source, secrets, data, and existing deployment paths. Do not replace a working application with the notes demo. A folder migration or platform switch requires specific authorization; adding a log helper or run task does not imply that migration. Record the resulting repository's actual entrypoints so later work uses them instead of generic commands.

## Maintainer verification

Verified on 2026-09-28 using disposable generated projects: locked dependency installation; Python lint and API/logging tests; TypeScript checks and production build; Docker Compose build, PostgreSQL migrations, readiness and save/read-back; Playwright persistence and failed-save behavior against both container and host-development entrypoints; configured database port; Kubernetes manifest rendering and authenticated Caddy configuration; copy refusal/preservation; Git visibility; existing task-generator regressions; skill validator and repository gate. Independent skill forward-testing found no remaining blocker after repairs. Evidence is retained in native task/tool history (partial capture, not a deployment receipt).

Kubernetes cluster admission, registry publication, TLS provisioning, rollout, cloud infrastructure and backup restoration were not exercised. Before deployment, follow the generated target-specific checks. TCP web readiness verifies a listener; the authenticated HTTP readiness check verifies the proxy and application.

For bundle maintenance, run `python3 -m unittest discover -s skills/coding-prepare-environment/tests -v` from the harness root, then repeat the generated-project journey above for changes affecting runtime behavior. Keep installations and build output in disposable copies, outside the bundled assets.
