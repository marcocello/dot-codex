# React + FastAPI starter

This starter contains a React/Vite frontend, a FastAPI backend, PostgreSQL, and Caddy. The notes screen demonstrates a browser-to-database round trip.

## Layout

- backend/app contains the FastAPI application. Backend package files, migrations, tests, and Dockerfile stay in backend.
- frontend/app contains the React application, its package files, tests, and Dockerfile.
- deployments/compose.base.yaml defines the shared services. deployments/dev and deployments/prod hold environment-specific Compose files, Caddy configuration, and private settings.
- deployments/prod/k8s contains optional Kubernetes templates. deployments/render_k8s.py renders them locally.
- docs contains shared documentation; .vscode contains the local run tasks.
- .venv appears at the root after backend setup. It is ignored by Git.

The default scaffold has no root Makefile, Dockerfile, Compose file, env file, scripts directory, or GitHub workflow. GitHub Actions is included only when the scaffold is called with --github-actions.

## Start locally

Install Python 3.13, uv, Node 22.12+, and Docker with Compose 2.24.4+. From the project root, run:

    python3 deployments/setup.py
    UV_PROJECT_ENVIRONMENT=$PWD/.venv uv sync --project backend --frozen
    npm --prefix frontend/app ci
    docker compose --env-file deployments/dev/.env -f deployments/compose.base.yaml -f deployments/dev/compose.yaml up -d --wait db
    (cd backend && ../.venv/bin/python -m alembic upgrade head)
    (cd backend && ../.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000)

In a second terminal, run npm --prefix frontend/app run dev and open http://localhost:5173. VS Code's fullstack task prepares the same dependencies, starts the database, runs migrations, and starts both host servers. Terminate those tasks in VS Code to stop them. The private deployments/dev/.env file is created once and never overwritten.

To run the complete container stack, run:

    python3 deployments/setup.py
    docker compose --env-file deployments/dev/.env -f deployments/compose.base.yaml -f deployments/dev/compose.yaml up --build -d --wait
    python3 deployments/dev/smoke.py http://127.0.0.1:8080

The smoke check writes a note. Use disposable or development data. To stop containers while retaining the database volume, use the same Compose prefix followed by down. Use WEB_PORT and DB_PORT in deployments/dev/.env to change host ports. On first setup, DB_PORT=15432 python3 deployments/setup.py writes the matching host database URL.

## Check changes

    bash backend/check.sh
    bash frontend/app/check.sh

Install Chromium and run npm run test:e2e from frontend/app while the container stack is running. The tests cover saved state and an unsuccessful save. The backend check runs Ruff and pytest; the frontend check runs TypeScript and the production build.

## Production and Kubernetes

For a Linux host deployment, run python3 deployments/setup.py --environment prod. Edit the private deployments/prod/.env to set SITE_ADDRESS, DEPLOY_USER, and DEPLOY_PASSWORD_HASH. Keep that file backed up securely. The production Compose files publish HTTPS through Caddy and do not publish database or API ports:

    docker compose --env-file deployments/prod/.env -f deployments/compose.base.yaml -f deployments/prod/compose.yaml config --quiet
    docker compose --env-file deployments/prod/.env -f deployments/compose.base.yaml -f deployments/prod/compose.yaml up --build -d --wait

The Caddy login is a shared private-demo gate. Add application accounts and authorization before opening public registration. Record an immutable release revision and test database restores before upgrades. Do not use down -v with data you need.

Kubernetes rendering does not contact a cluster. Run python3 deployments/render_k8s.py with explicit image, domain, namespace, release, ingress class, and output flags. Follow deployments/prod/k8s/README.md for the release order. Cluster deployment and registry publication require separate authorization.
