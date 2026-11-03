# Web and API

For a browser application and a separate API, `frontend/` and `backend/` can represent the actual applications. The bundled React/FastAPI scaffold uses:

```text
project/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── pyproject.toml
│   ├── uv.lock
│   └── Dockerfile
├── frontend/
│   └── app/
│       ├── src/
│       ├── tests/
│       ├── package.json
│       ├── package-lock.json
│       └── Dockerfile
├── deployments/
│   ├── compose.base.yaml
│   ├── dev/compose.yaml
│   └── prod/compose.yaml
├── docs/
├── .vscode/tasks.json
└── .gitignore
```

API commands run from `backend/`; browser package commands run from `frontend/app/`. Follow the [scaffold guide](../../references/scaffold.md) for its actual setup, commands, and environment loading. The copier's existing paths and entrypoints do not change when another project chooses a different layout.

A project can instead use root `api/` and `web/` components when that is established or selected. Keep manifests, Dockerfiles, tests, and component utilities with the selected applications. Add a root `worker/` only for a real separate worker responsibility; do not nest unrelated services under `backend/` solely because they run server-side.

Deployment configuration wires the API, browser application, database image, and environment settings. Verify the public browser-to-API journey and saved result as well as individual process readiness. A single full-stack framework can remain one application when it owns both presentation and server logic.
