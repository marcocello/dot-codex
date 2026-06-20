---
name: coding-prepare-environment
description: "Prepare local project environments before coding, tests, gates, feature proof commands, dependency/tooling work, or VS Code run-task generation. Use when Codex or another skill needs the shared setup step for Python, React/Node, PHP, Laravel, WordPress, or mixed/unknown stacks, including environment discovery, safe .env handling, whitelist-pattern .gitignore setup, virtualenv/node_modules/vendor setup, validation command selection, and `.vscode/tasks.json` for local dev loops."
---

# Prepare Environment

Purpose: centralize repo setup policy so other skills and AGENTS.md do not duplicate stack-specific environment rules.

## Caller Contract

- Use this skill before implementation or checks when the local environment is not known-good.
- Other skills should delegate setup decisions here instead of repeating stack setup rules.
- Keep setup changes minimal and reversible. Do not delete existing `.venv`, `node_modules`, `vendor`, `.env`, database files, caches, uploads, or generated assets unless the user explicitly asks.
- Never print secret values. When reporting `.env` work, mention filenames and missing keys only.
- Prefer repo-provided setup scripts, Make targets, package scripts, Docker files, and documented commands.
- If setup requires missing credentials or external services, stop with the exact blocker and continue with any checks that do not require those services.

## Workflow

1. Read local authority first:
   - `docs/ARCHITECTURE.md` if it exists.
   - `docs/TESTING.md`, `docs/CONVENTIONS.md`, `README*`, `Makefile`, and package/tool config when relevant.
2. Detect stack signals:
   - Python: `backend/pyproject.toml`, `backend/requirements*.txt`, `backend/app/requirements*.txt`, `backend/app`, root `pyproject.toml`, root `requirements*.txt`, `pytest.ini`, `tox.ini`.
   - React/Node: `frontend/package.json`, frontend lockfiles, `frontend/app`, `vite.config.*`, `next.config.*`, root `package.json`, root lockfiles.
   - PHP/Laravel: `composer.json`, `artisan`, `phpunit.xml`, `pest.php`, `.php-version`.
   - WordPress: `wp-config.php`, `wp-config-sample.php`, `wp-content/`, or WordPress Composer packages.
   - Other: Docker, devcontainer, Nix, direnv, mise, asdf, language lockfiles, or custom scripts.
3. Load only the relevant sections of [stack-reference.md](references/stack-reference.md).
4. Prepare the minimum environment needed for the current task.
5. Create or update root `.gitignore` when missing or clearly incomplete. Use the whitelist pattern from the stack reference; do not generate a blacklist-only ignore file.
6. When the project needs the standard backend/frontend local run workflow, create or update `.vscode/tasks.json` from this skill's bundled generator.
7. Run the narrowest setup verification available, then report:
   - stacks detected
   - files created or changed
   - `.gitignore` status and whether it follows the whitelist pattern
   - commands run
   - remaining blockers
   - exact command prefix future skills should use
   - dev server command future run-task skills should use, when obvious

## Selection Rules

- If multiple stacks exist, prepare only the stacks touched by the requested work or checks.
- If package managers conflict, use the lockfile or repo documentation. Do not mix `npm`, `yarn`, `pnpm`, and `bun` in one project without clear repo precedent.
- If no setup command is documented, use the ecosystem default from the stack reference.
- If local toolchains are incomplete, prefer documented containers or devcontainers over installing unrelated global tools.
- Do not add dependencies for setup convenience unless the task explicitly includes dependency work.

## Gitignore Policy

Root `.gitignore` setup belongs to this skill because it is cross-stack repo hygiene.

- Preserve an existing `.gitignore` and its style unless it is unsafe or clearly incomplete.
- When creating `.gitignore`, use a whitelist pattern:
  1. Ignore everything with `*`.
  2. Unignore required source, docs, config, and scaffold directories with `!`.
  3. Re-ignore secrets, dependencies, generated outputs, caches, uploads, databases, and local runtime artifacts.
- Stack/domain skills may require extra paths, but this skill owns the root `.gitignore` update.
- Never whitelist `.env`, secret-bearing local config, dependency directories, build outputs, caches, uploaded media, or database files.
- Do not replace a whitelist `.gitignore` with a blacklist-style file.

## VS Code Run Tasks

Generate `.vscode/tasks.json` from this skill when a software project needs the standard backend/frontend/fullstack local run workflow.

Run:

```bash
skills/coding-prepare-environment/scripts/generate_tasks.py <repo-root>
```

The bundled generator has operational defaults for the Python backend and React frontend skills, but it does not define the project structure. Override these values whenever repo docs or the owning domain skill uses different paths:

- Frontend command: `npm run dev`
- Frontend cwd: `${workspaceFolder}/frontend/app`
- Backend cwd: `${workspaceFolder}/backend/app`
- Backend app command: auto-detect FastAPI from `backend/app/main.py` plus dependency files in `backend/app` or `backend`, and use `${workspaceFolder}/.venv/bin/python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000`; otherwise use `${workspaceFolder}/.venv/bin/python main.py`
- Backend ngrok command: `ngrok http 8000`

Preserve unrelated existing tasks. Replace only generated labels: `frontend`, `backend:app`, `backend:ngrok`, `backend`, and `fullstack`. Use script flags when a repo uses different commands, paths, or a different ngrok URL. Do not start frontend or backend tasks unless the user asks to run them.

## Output Shape

Use concise handoff text:

```text
Environment prepared:
- detected: Python + React
- changed: created backend/.env from backend/.env.example; updated whitelist `.gitignore`
- commands: .venv/bin/python -m pip install -r backend/requirements.txt;
  cd frontend && pnpm install --frozen-lockfile
- use: .venv/bin/python -m pytest ..., .venv/bin/python -m uvicorn main:app --reload
  from backend/app when FastAPI is detected, and pnpm test ...
- blockers: none
```
