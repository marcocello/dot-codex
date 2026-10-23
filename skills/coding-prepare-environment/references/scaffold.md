# React + FastAPI scaffold

Use this bundle for an authorized greenfield full-stack application. It contains a replaceable notes example, not a product requirement. For a different framework or one component, prepare only the selected stack.

    python3 "${CODEX_HOME:-$HOME/.codex}/skills/coding-prepare-environment/scripts/scaffold.py" /absolute/empty/project

The copier refuses nonempty destinations and destination symlinks. It does not install dependencies, initialize Git, start services, publish images, or deploy. It creates the source layout in the skill's Greenfield Layout section. The root .venv appears only after dependency setup. Pass --github-actions only when the user chooses GitHub Actions; this is the sole option that adds .github to the generated root.

## Generated run journey

From the generated repository root:

    python3 deployments/setup.py
    UV_PROJECT_ENVIRONMENT=$PWD/.venv uv sync --project backend --frozen
    npm --prefix frontend/app ci
    docker compose --env-file deployments/dev/.env -f deployments/compose.base.yaml -f deployments/dev/compose.yaml up -d --wait db
    (cd backend && ../.venv/bin/python -m alembic upgrade head)
    (cd backend && ../.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000)
    npm --prefix frontend/app run dev

Open http://localhost:5173. VS Code's fullstack task performs the same prerequisite chain and starts both servers in dedicated terminals. The setup script creates deployments/dev/.env once with mode 0600. An existing file is preserved. Stop host servers through VS Code and stop the database with the containers:down task; keep the database volume.

For the complete container stack, use the same Compose prefix followed by up --build -d --wait. Run python3 deployments/dev/smoke.py http://127.0.0.1:8080. The smoke script writes a note, then reads it back. Use disposable or development data. Verify frontend, API readiness, validation failure, and saved state through the public web endpoint.

Run bash backend/check.sh and bash frontend/app/check.sh. Install the locked Playwright browser, then run npm run test:e2e from frontend/app against the running stack. The browser test covers persistence and failed saves. The component scripts and VS Code tasks use the component working directories.

## Deployment assets

The shared Compose base is deployments/compose.base.yaml. Development and production overlays live in deployments/dev/compose.yaml and deployments/prod/compose.yaml. Invoke Compose with an explicit --env-file and both files. Relative build contexts and Caddy mounts resolve from deployments/, the first Compose file's directory. The backend and frontend Dockerfiles stay with their components. The frontend image receives the selected Caddyfile at runtime through the environment overlay.

The production setup command is python3 deployments/setup.py --environment prod. It creates deployments/prod/.env with a generated database password and blank deployment values. The operator must set the domain and authentication values before running the production Compose pair. Publishing or rolling out requires authorization.

The Kubernetes templates live under deployments/prod/k8s. Render them locally with deployments/render_k8s.py and explicit image, domain, namespace, release, ingress class, and output flags. An environment without manifests fails before creating output. Review deployment order in deployments/prod/k8s/README.md. Rendering does not contact a cluster.

## Brownfield adoption

Inspect existing component paths, package managers, lockfiles, task labels, env loading, data and migrations, deployment commands, and CI. Present the smallest useful source-to-destination mapping and command changes before asking to relocate existing files. Do not run the copier on a nonempty repository. Preserve existing private env files, data, dependencies, and unrelated work. A clean greenfield root does not authorize deleting or moving a brownfield root without that proposal.

## Maintainer verification

Run the skill's unit tests and quick validator. On a disposable generated project, check the exact root entries, root .venv creation after setup, Git visibility, VS Code task dependency paths, both Compose configurations, both Docker builds, manifest rendering, and the public smoke journey. Use a distinct Compose project and stop containers afterward. Report checks that could not run; file presence alone does not establish readiness.
