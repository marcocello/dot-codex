---
name: coding-vscode-generate-run-tasks
description: Create or update VS Code .vscode/tasks.json entries for fullstack local development, especially repos with frontend/app and backend/app layouts. Use when Codex needs to generate tasks that boot a frontend dev server, run a Python backend app, expose the backend through ngrok, and run frontend/backend tasks together from VS Code.
---

# VS Code Generate Run Tasks

## Overview

Generate `.vscode/tasks.json` entries for the standard frontend/backend/fullstack
developer loop. Prefer the bundled script so generated JSON stays valid and
unrelated tasks are preserved.

## Workflow

1. Inspect the repo before editing:
   - Read any existing `.vscode/tasks.json`.
   - Check `frontend/app/package.json` for the package manager and dev script.
   - Check `backend/app` for the backend entrypoint and virtualenv assumptions.
   - Use `coding-prepare-environment` before installing dependencies or running dev commands.
   - Use `coding-frontend` for frontend app conventions; keep the generated VS Code task label
     as `frontend`.
2. Review existing `.vscode/tasks.json` before writing:
   - Report unrelated labels that will be preserved.
   - Report generated labels that will be replaced.
   - Report each improvement the generated run tasks will add, such as missing
     `backend:ngrok` or `fullstack` tasks.
3. Preserve existing unrelated VS Code tasks. Replace only generated labels:
   `frontend`, `backend:app`, `backend:ngrok`, `backend`, and `fullstack`.
4. Generate strict JSON. VS Code task files do not allow trailing commas.
5. Do not start the frontend or backend unless the user asks to run the tasks.

## Generator

Run:

```bash
python skills/coding-vscode-generate-run-tasks/scripts/generate_tasks.py <repo-root>
```

Defaults match the dot-codex greenfield layout:

- Frontend command: `npm run dev`
- Frontend cwd: `${workspaceFolder}/frontend/app`
- Backend cwd: `${workspaceFolder}/backend/app`
- Backend app command: `${workspaceFolder}/.venv/bin/python main.py`
- Backend ngrok command: `ngrok http --url=unranting-salome-kaleidoscopically.ngrok-free.app 8000`

Use script flags when a repo uses different commands, paths, or a different ngrok URL.

## Expected Tasks

- `frontend`: shell task that runs the frontend dev server in a dedicated panel.
- `backend:app`: background shell task that runs the backend app with the project virtualenv.
- `backend:ngrok`: background shell task that exposes port 8000 through ngrok.
- `backend`: aggregate task that runs `backend:app` and `backend:ngrok` in parallel.
- `fullstack`: aggregate task that runs `frontend` and `backend` in parallel.
