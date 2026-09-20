---
name: coding-prepare-environment
description: "Prepare repo-local Python, Node, PHP, Laravel, WordPress, or mixed environments for coding, proof, dependencies, and VS Code tasks."
---

# Prepare Environment

Purpose: centralize repo setup policy so other skills and AGENTS.md do not duplicate stack-specific environment rules.

The coding lifecycle skills own routing, acceptance, execution, and completion. Prepare only the environment needed for that work; setup does not require its own feature package or review.

## Caller Contract

- Use this skill before implementation or proof when the local environment is not known-good.
- Other skills should delegate setup decisions here instead of repeating stack setup rules.
- Keep setup changes minimal and reversible. Do not delete existing `.venv`, `node_modules`, `vendor`, `.env`, database files, caches, uploads, or generated assets unless the user explicitly asks.
- Never print secret values. When reporting `.env` work, mention filenames and missing keys only.
- Prefer repo-provided setup scripts, Make targets, package scripts, Docker files, and documented commands.
- If setup requires missing credentials or external services, stop with the exact blocker and continue with any checks that do not require those services.
- Discover relevant local CLIs, package managers, containers, browser/app automation, MCP tools, and repo scripts before reporting that setup cannot continue.
- Report the exact install or enablement needed for a missing capability. Independent supporting checks can continue, but cannot replace unavailable required proof.

## Workflow

1. Read local authority first:
   - `docs/ARCHITECTURE.md` if it exists.
   - `docs/TESTING.md`, `docs/CONVENTIONS.md`, `README*`, `Makefile`, and package/tool config when relevant.
2. Resolve the layout before creating manifests or installing dependencies: preserve an established repository layout or explicit user choice; otherwise use the greenfield layout below. Detect stack signals:
   - Python: `backend/pyproject.toml`, `backend/requirements*.txt`, `backend/app/requirements*.txt`, `backend/app`, root `pyproject.toml`, root `requirements*.txt`, `pytest.ini`, `tox.ini`.
   - Node (backend or frontend): `backend/app/package.json`, `frontend/app/package.json`, `frontend/package.json`, component lockfiles, `vite.config.*`, `next.config.*`, root `package.json`, root lockfiles.
   - PHP/Laravel: `composer.json`, `artisan`, `phpunit.xml`, `pest.php`, `.php-version`.
   - WordPress: `wp-config.php`, `wp-config-sample.php`, `wp-content/`, or WordPress Composer packages.
   - Other: Docker, devcontainer, Nix, direnv, mise, asdf, language lockfiles, or custom scripts.
3. Inspect tool availability relevant to the proof: PATH, repo scripts, Makefiles, package scripts, Docker files, local apps/connectors, browser automation, database clients, and cloud CLIs named by docs or proof.
4. Load only the relevant sections of [stack-reference.md](references/stack-reference.md).
5. Prepare the minimum environment needed for the current task.
6. Create or update root `.gitignore` when missing or clearly incomplete. Use the whitelist pattern from the stack reference; do not generate a blacklist-only ignore file.
7. When the project needs the standard backend/frontend local run workflow, create or update `.vscode/tasks.json` from this skill's bundled generator.
8. Run the narrowest repository-native dependency or readiness check needed by the active work. Do not run a full suite or gate as a routine setup prerequisite. Repository-required gates remain supporting verification under the coding lifecycle skills, separate from feature proof. Then report:
   - stacks detected
   - files created or changed
   - `.gitignore` status and whether it follows the whitelist pattern
   - commands run
   - remaining blockers
   - exact command prefix future skills should use
   - readiness result and remaining setup failures
   - dev server command future run-task skills should use, when obvious

## Selection Rules

- If multiple stacks exist, prepare only the stacks touched by the requested work or checks.
- If package managers conflict, use the lockfile or repo documentation. Do not mix `npm`, `yarn`, `pnpm`, and `bun` in one project without clear repo precedent.
- If no setup command is documented, use the ecosystem default from the stack reference.
- If local toolchains are incomplete, prefer documented containers or devcontainers over installing unrelated global tools.
- Do not add dependencies for setup convenience unless the task explicitly includes dependency work.

## Greenfield Layout

This skill owns the default component locations for environment preparation across stacks; domain skills own internal application architecture and framework scaffolding.

- Backend applications, including Node bots, workers, and APIs, live in `backend/app`; frontend applications live in `frontend/app`. A standalone backend still uses `backend/app`. Do not infer frontend ownership merely from Node or npm.
- Keep Node package manifests, lockfiles, and tool configuration with their component package (`backend/app` or `frontend/app`), and run installs and package scripts there. Python dependency/tool configuration defaults to `backend/`, with `.venv` at the repository root.
- Create only components required by the request. Environment-only setup does not authorize implementing application behavior or inventing a frontend.
- Existing repository layouts, explicit user choices, and explicitly selected platform requirements take precedence. Do not relocate an existing project just to match these defaults.
- Before relocating existing folders, show the proposed source and destination paths and ask the user for approval. A general environment-preparation request or complaint about layout does not authorize relocation. If the user has already explicitly authorized the specific relocation, proceed without asking again; otherwise continue setup that preserves the current layout while awaiting their answer.
- Before reporting readiness, verify the selected component paths and documented command working directories as well as dependencies. For a changed `.gitignore`, use `git check-ignore` to verify representative nested source/config files are visible and dependencies, secrets, and generated artifacts remain ignored. A successful dependency check or generic gate alone does not establish those outcomes.

## Gitignore Policy

Root `.gitignore` setup belongs to this skill because it is cross-stack repo hygiene.

- Preserve project-specific rules in an existing `.gitignore`; when creating or updating it for setup, align it with the four-section policy below. Leave unrelated ignore files alone.
- Use the four-section template in the stack reference. Keep section 1 (`*`) and section 2 (`!*/`) unchanged unless technically unavoidable; explain any necessary exception.
- Section 3 allows required source/config/docs file types or specific filenames. Do not allow entire trees with `!directory/**`.
- Section 4 blocks generated, local, secret, and runtime artifacts, including allowed file types inside those directories.
- Stack/domain skills may require extra paths, but this skill owns the root `.gitignore` update.
- Never whitelist `.env`, secret-bearing local config, dependency directories, build outputs, caches, uploaded media, or database files.
- Do not replace a whitelist `.gitignore` with a blacklist-style file.

## VS Code Run Tasks

Generate `.vscode/tasks.json` from this skill when a software project needs the standard backend/frontend/fullstack local run workflow.

Run:

```bash
"${CODEX_HOME:-$HOME/.codex}/skills/coding-prepare-environment/scripts/generate_tasks.py" <repo-root>
```

The bundled generator follows the component locations above, with Python backend and React frontend command defaults. Override commands for other runtimes (including Node backends), and paths for established repository layouts:

- Frontend command: `npm run dev`
- Frontend cwd: `${workspaceFolder}/frontend/app`
- Backend cwd: `${workspaceFolder}/backend/app`
- Backend app command: auto-detect FastAPI from `backend/app/main.py` plus dependency files in `backend/app` or `backend`, and use `${workspaceFolder}/.venv/bin/python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000`; otherwise use `${workspaceFolder}/.venv/bin/python main.py`
- Backend ngrok command: `ngrok http 8000`

Preserve unrelated existing tasks and shared settings such as input definitions, environment options, and platform overrides. Accept existing JSONC task files with comments and trailing commas; output is formatted JSON, so comments are not retained. Replace only generated labels: `frontend`, `backend:app`, `backend:ngrok`, `backend`, and `fullstack`. Default backend tasks launch Python as a process with separate arguments so workspace paths containing spaces work; explicit command overrides retain shell execution. Use script flags when a repo uses different commands, paths, or a different ngrok URL. Start local services when required by authorized implementation or proof; generating tasks alone does not require starting them. External tunnels require applicable authorization.

## Output Shape

Use concise handoff text:

```text
Environment prepared:
- detected: Python + React
- changed: created backend/.env from backend/.env.example; updated whitelist `.gitignore`
- commands: .venv/bin/python -m pip install -r backend/requirements.txt;
  cd frontend && pnpm install --frozen-lockfile
- use: .venv/bin/python -m pytest ... from the repo root;
  ../../.venv/bin/python -m uvicorn main:app --reload from backend/app;
  pnpm test ... from frontend/app
- blockers: none
```
