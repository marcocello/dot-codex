# Single service

Use one component for an API, bot, or worker. Here the application is an import worker:

```text
project/
├── import-worker/
│   ├── pyproject.toml
│   ├── src/
│   ├── tests/
│   ├── Dockerfile
│   └── tools/                 # Worker-specific diagnostics, if needed
├── deployments/
│   ├── local/compose.yml
│   └── prod/compose.yml
├── docs/
├── .vscode/tasks.json
└── .gitignore
```

The worker's parser, package dependencies, tests, build, and diagnostics belong to `import-worker/`. Deployment files choose mounts, images, environment configuration, and persistent storage. Add containers and environment directories only when the selected runtime needs them. Host Python setup can create an ignored root `.venv/`.

An existing `backend/` component is equally valid. A Node bot would keep its `package.json`, lockfile, and source inside its component instead of adding a Python manifest. Do not create `frontend/` or a second service merely to fit a conventional tree.

Verify the documented working directory, package entrypoint, and ordinary start/stop path. Starting a process alone does not establish that the worker processed and saved a result.
