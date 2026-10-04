# React + FastAPI starter

An opinionated starting point: React + TypeScript + Vite, FastAPI + SQLAlchemy + Alembic, PostgreSQL, and Caddy. A small notes screen demonstrates a real browser → API → database round trip. Keep the stack and conventions until a concrete requirement justifies changing them.

## Start

Install Python 3.13, uv, Node 22.12+, and Docker with Compose 2.24.4+. From the project root:

```sh
make setup
make db migrate
make backend
```

In a second terminal, run `make frontend` and open <http://localhost:5173>. Vite proxies `/api` to the backend on port 8000. VS Code's `fullstack` task prepares locked dependencies, starts the database, applies migrations, and then starts both servers in dedicated terminals. `backend:app` and `frontend` share that prerequisite. Use `containers:up` for the complete container stack, `logs` to follow service output, and `containers:down` to stop containers without deleting data. `make setup` installs locked dependencies and creates a private root `.env` only if one is absent; an existing `.env` is preserved. Python dependencies live in root `.venv`; package metadata lives in `backend/` and `frontend/app/`.

For the complete container deployment locally, run `make up` and open <http://127.0.0.1:8080>. This one-command start needs only Python and Docker; it initializes `.env` without replacing existing settings. Database health gates migration, migration success gates the API, and API readiness gates the web server. The default stack exposes only localhost:8080; use `WEB_PORT=8081 make up smoke` to choose another port. `make db` additionally binds PostgreSQL to localhost:5432 for host development. For another database port on first setup, use `DB_PORT=15432 make setup`; setup writes the matching `DB_PORT` and host `DATABASE_URL` to `.env`. For an existing `.env`, update both values together before restarting the database.

## Change and verify

```sh
make check           # Python lint/tests, TypeScript checks, frontend production build
make up smoke        # Build containers; check the real HTTP + database round trip
```

The smoke script creates a note; use it against disposable or development data. `/api/health` checks the process; `/api/ready` checks database availability. GitHub Actions runs the same checks, container smoke, and a browser persistence test on pushes and pull requests. To run the browser tests locally after `make up`, run `npm ci`, `npx playwright install chromium`, and `npm run test:e2e` from `frontend/app/`. Set `BASE_URL` for a different local port. Unit tests do not replace PostgreSQL/container proof.

```text
backend/
  app/               FastAPI routes, domain/service code, database models
  migrations/        Alembic schema history
  tests/             API and behavior tests
  pyproject.toml     Python dependencies and tooling
frontend/
  app/               React source, npm package and lockfile, Vite config
  Dockerfile         Static production build served by Caddy
deploy/              Local and HTTPS Caddy configurations
scripts/             Safe local setup and HTTP smoke verification
compose*.yaml        Local stack, host development DB port, HTTPS deployment
.github/workflows/   CI
```

Create a migration whenever a model changes: from `backend/`, run `../.venv/bin/python -m alembic revision --autogenerate -m "describe change"`, inspect it, then run `make migrate` from the root. Build schema changes for compatibility with both old and new app versions when a rollback may be needed. The starter deliberately has one deployable application and one database.

## Kubernetes deployment

Kubernetes assets are included by default in [deploy/k8s](deploy/k8s/README.md), with a local renderer, StatefulSet/PVC, migration Job, application Deployments and Services, probes, resource limits, and TLS Ingress. Choose the registry, namespace, cluster and ingress class before publishing. Rendering does not deploy.

## Logging

Backend logs go to stdout with time, severity, component, event, request ID, and structured details. Use `LOG_FORMAT=text` for local reading or `json` for aggregation, and `LOG_LEVEL` for verbosity. Requests return `X-Request-ID` and log route templates, status, and elapsed time; bodies, headers, query strings and raw unmatched paths are not logged. Log constant event messages with safe `extra={"details": {...}}` metadata; sensitive field names are redacted recursively. Arbitrary free-text messages are not a secret scrubber. Container logs rotate at 10 MB with three files per service. `make logs` follows output; `make status` shows service health. Kubernetes retention belongs to the cluster logging system.

## Deploy to an existing Linux host

This recipe needs a host with Docker Compose, a domain pointing to it, and inbound TCP ports 80/443. Provisioning the host and publishing are separate operator actions. Use an immutable Git revision for each release.

1. Clone the repository on the host and check out the release revision. Run `python3 scripts/setup.py` to generate a host-specific database password.
2. Generate a shared deployment password hash interactively with `docker run --rm -it caddy:2-alpine caddy hash-password`. Set `SITE_ADDRESS=app.example.com`, `DEPLOY_USER=owner`, and `DEPLOY_PASSWORD_HASH` in the private `.env`. Put the hash in **single quotes** so Compose preserves its `$` characters. Keep `.env` backed up securely.
3. Start and inspect the release:

```sh
docker compose -f compose.yaml -f compose.production.yaml config --quiet
docker compose -f compose.yaml -f compose.production.yaml up --build -d --wait
curl --fail --user owner https://app.example.com/api/ready
```

Caddy obtains and renews HTTPS certificates. The production overlay requires credentials and protects the entire site with HTTP Basic Auth; sign in through the browser. This is a shared private-demo gate, **not application accounts or authorization**. Add application authentication, authorization, and suitable abuse controls before opening public registration or removing that gate. PostgreSQL and the API have no host ports in the production configuration. Do not add `compose.dev.yaml` to production.

## Operate and recover

Inspect a deployment with `docker compose -f compose.yaml -f compose.production.yaml ps` and `logs --tail=100`. `docker compose down` stops containers and preserves volumes. Never use `down -v` for data you need.

Before upgrading, take a database backup, record the deployed Git revision, and verify a restore on a separate stack:

```sh
mkdir -p backups
chmod 700 backups
umask 077
docker compose exec -T db pg_dump -U app -d app -Fc > backups/app.dump
```

For a restore drill, copy the repository to a separate directory, generate its own `.env`, and start only its database with `docker compose -p restore-check up -d --wait db`. Restore the dump into that **disposable database**, then check schema and rows:

```sh
docker compose -p restore-check exec -T db pg_restore -U app -d app --exit-on-error < /path/to/app.dump
docker compose -p restore-check exec -T db psql -U app -d app -c 'SELECT count(*) FROM notes;'
```

Store backups off the host and exercise restoration regularly. To roll back application code, check out the previous release and rebuild/restart with the production command above. Database migrations remain applied: rollback works only if the old code supports the new schema. An incompatible schema change requires a forward fix or an explicitly planned restore with downtime and possible loss of writes since the backup. This single-host starter has no high availability or automated backup scheduler.
