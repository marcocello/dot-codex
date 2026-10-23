---
name: coding-prepare-environment
description: "Own repository layout, alignment checks, and VS Code local run tasks; scaffold React/FastAPI projects and prepare existing application environments with environment-based deployments and selective adoption."
---

# Prepare Environment

Read [Coding writing](../../docs/harness/coding/writing.md) once per task and apply it to specifications, proof, reports, and human interaction.

Purpose: own repository layout, structure alignment, and setup policy so other skills and AGENTS.md refer to one source of truth. Domain skills own structure inside applications.

The coding lifecycle skills own routing, acceptance, execution, and completion. Prepare only the environment needed for that work; setup does not require its own feature package or review.

Apply the kernel's end-to-end journey to the operator's setup: connect the starting environment, setup/run commands and working directories, required connections, durable output location, and verification into one usable sequence. Investigate a supported alternative when a missing local dependency obstructs that sequence; do not stop at a dependency list or impose a new environment by default. Distinguish commands actually verified from proposed steps. For authorized setup, prepare the necessary local pieces and verify the normal entrypoint as far as access permits; a collection of individually valid scripts is not evidence that the operator journey works.

## Caller Contract

- Use this skill for repository structure selection or alignment review, and before implementation or proof when the local environment is not known-good.
- Other skills should delegate repository placement, alignment, and setup decisions here instead of repeating layout or stack setup rules. A structure review remains read-only unless changes are authorized.
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
2. Resolve the layout before creating manifests or installing dependencies: for web applications, apply Starter Selection below; preserve the existing layout until any proposed adoption is approved. Explicit user choices take precedence; otherwise use the greenfield layout below. Detect stack signals:
   - Python: `backend/pyproject.toml`, `backend/requirements*.txt`, Python source under `backend/app`, root manifests, `pytest.ini`, `tox.ini`, and established alternatives such as `app/backend/pyproject.toml`.
   - Node (backend or frontend): `backend/package.json`, `frontend/app/package.json`, component lockfiles, `vite.config.*`, `next.config.*`, root manifests, and established alternatives such as `app/frontend/package.json` or `frontend/package.json`.
   - PHP/Laravel: `composer.json`, `artisan`, `phpunit.xml`, `pest.php`, `.php-version`.
   - WordPress: `wp-config.php`, `wp-config-sample.php`, `wp-content/`, or WordPress Composer packages.
   - Other: Docker, devcontainer, Nix, direnv, mise, asdf, language lockfiles, or custom scripts.
3. Inspect tool availability relevant to the proof: PATH, repo scripts, Makefiles, package scripts, Docker files, local apps/connectors, browser automation, database clients, and cloud CLIs named by docs or proof.
4. Load only the relevant sections of [stack-reference.md](references/stack-reference.md).
5. Prepare the minimum environment needed for the current task.
6. Create or update root `.gitignore` when missing or clearly incomplete. Use the whitelist pattern from the stack reference; do not generate a blacklist-only ignore file.
7. For authorized preparation of a runnable application, create or update `.vscode/tasks.json` so the user can start the entire local app with `fullstack`. Preserve working repository/starter tasks and fill only missing parts. Use the bundled generator for the standard task structure and adapt its commands, component paths, dependencies, and readiness signals to the actual runtime. A read-only structure review does not create task files.
8. Apply Structure Alignment Check to the reviewed or prepared paths, then run the narrowest repository-native dependency or readiness check needed by the active work. A structure-only review need not install dependencies or start services. Do not run a full suite or gate as a routine setup prerequisite. Repository-required gates remain supporting verification under the coding lifecycle skills, separate from feature proof. Then report:
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

## Repository Files

- Do not generate `Makefile` or `PRODUCT.md` by default. Preserve existing files unless the user requests removal; an explicit artifact request can override these defaults.
- `README.md` is optional. Keep useful existing documentation. The bundled copier places its guide at `docs/README.md` and does not create a root README.
- Use direct tool commands, established package scripts, or VS Code tasks for local work. Do not introduce Make as a dependency or replace it with a new umbrella task runner solely to enforce a convention.
- Read product context from existing repository material and native task history. Do not create a mandatory replacement document under another name. Apply these defaults when a specialist such as Impeccable asks for `PRODUCT.md`; its absence does not block the user's work.

## Starter Selection

For full-stack web applications, prefer the bundled [React + FastAPI scaffold](assets/react-fastapi/docs/README.md): React/TypeScript/Vite, FastAPI, PostgreSQL, Docker Compose, and Kubernetes deployment assets. Read [scaffold guide](references/scaffold.md) for the source patterns, generation command, verification journey, and brownfield adoption checklist. Explicit stack or platform choices take precedence; frontend-only or backend-only work still creates only the required components.

- Greenfield: use the [scaffold script](scripts/scaffold.py) for an absent or empty destination. A repository containing only Git metadata or documentation is not empty; prepare a selective integration instead of overwriting it.
- Brownfield: offer concrete selective scaffold adoption when useful and obtain the user's explicit decision before applying it, even when the existing stack or layout already matches. First inspect the project and show a concrete proposal covering affected paths, dependencies, run commands, and any data or behavior migration; ask whether to adopt it or retain the existing setup. Do not make scaffold adoption a prerequisite for routine dependency repair or readiness checks. Honor an explicit decision already given for that proposal without asking again. While the decision is pending or if adoption is declined, continue only authorized setup that preserves the existing project.
- Never run the copy script over existing work or bypass its nonempty-directory guard. Apply approved brownfield changes selectively, preserving application behavior, data, secrets, and unrelated work; migration beyond setup belongs to the coding lifecycle and domain skills.
- Use the starter's direct commands, locked dependencies, environment-specific `.env`, and existing VS Code tasks. Its backend runs `app.main:app` from `backend/`; do not replace that with the generic `main:app` command or introduce ngrok into its run tasks.
- This skill owns starter selection and environment readiness. Domain skills own application implementation; the active coding lifecycle owns product acceptance and proof. The included notes demo does not define the requested product.

## Greenfield Layout

This skill is the single owner of repository placement and alignment across stacks. Use this default for new repositories; domain skills own internal application architecture and framework scaffolding:

```text
.vscode/
.venv/                 created during setup; ignored by Git
backend/
  app/
frontend/
  app/
docs/
deployments/
  dev/
  prod/
.gitignore
```

- Keep the greenfield root to these entries, plus `.git/` when initialized. Do not create root `Makefile`, `Dockerfile`, Compose files, `.env` examples, `.dockerignore`, `scripts/`, or `pipelines/`. Include `.github/` only when the user explicitly chooses GitHub Actions; its workflow path is fixed by that platform.
- Backend applications, including Node bots, workers, and APIs, live in `backend/`; frontend applications live in `frontend/app/`. A standalone backend still uses `backend/`. Do not infer frontend ownership merely from Node or npm. Framework package directories, such as the starter's `backend/app`, remain inside their component.
- Keep package manifests, lockfiles, dependency files, tool configuration, Dockerfiles, application tests, and reusable component scripts with their component. Run installs and package scripts there. Create the Python `.venv` at the repository root during setup; never copy an environment into source control.
- Keep shared architecture, development, and operational documentation under `docs/`; existing capability-local documentation can remain with its subject.
- Group deployment configuration, private env files and examples, Compose files, shared setup, rendering, and smoke helpers under `deployments/`. Put environment-specific files under `deployments/<environment>/`; a shared Compose base may live directly in `deployments/`. Terraform belongs in `tf/`, Kubernetes manifests in `k8s/`.
- Keep CI entrypoints only where a selected CI platform requires them. Do not add a platform workflow by default. Existing repository entrypoints may remain when preserving a brownfield layout; propose exact moves before clearing an existing root.
- Create only requested components, environments, and required files. The tree shows placement, not mandatory empty folders; do not add Terraform, Kubernetes, cloud resources, or a frontend solely to fill it. Environment-only setup does not authorize implementing application behavior.
- Explicit user choices and explicitly selected platform requirements take precedence. Preserve existing repository layouts unless the user approves the concrete adoption proposal under Starter Selection or a specific relocation; defaults alone do not authorize moving an existing project.
- Before relocating existing folders, show the proposed source and destination paths and ask the user for approval. A general environment-preparation request or complaint about layout does not authorize relocation. If the user has already explicitly authorized the specific relocation, proceed without asking again; otherwise continue setup that preserves the current layout while awaiting their answer.
- Before reporting readiness, verify the selected component paths and documented command working directories as well as dependencies. For a changed `.gitignore`, use `git check-ignore` to verify representative nested source/config files are visible and dependencies, secrets, and generated artifacts remain ignored. A successful dependency check or generic gate alone does not establish those outcomes.

## Structure Alignment Check

Use the repository's accepted layout as the comparison frame. An established or explicitly selected alternative is not a defect merely because it differs from the greenfield default.

- Inspect actual component, documentation, deployment, and pipeline paths; distinguish source from generated artifacts and unused legacy folders.
- Trace dependency installs, application entrypoints, tests, VS Code task working directories, Docker build contexts and COPY paths, Compose mounts, CI scripts, and documented commands to the files they use. Verify that paths resolve from each consumer's working directory.
- Check that each requested environment selects its own deployment files and Terraform state. Preserve existing state keys, resource addresses, and release ownership; a directory preference does not authorize a state or application migration.
- Check Git visibility for nested source, manifests, pipeline scripts, and deployment configuration, and exclusion of dependencies, secrets, state, and generated output.
- Report the selected layout, observed mismatches, justified exceptions, checks run, and remaining gaps. Propose concrete source/destination paths before any unapproved relocation. Generic gates support these checks but do not establish layout alignment by themselves.

## Terraform Deployment Structure

When authorized work includes Terraform scaffolding or deployment layout, read [Terraform conventions](references/terraform.md). Use its environment roots, file responsibilities, naming locals, and HCL formatting. Select the sanitized [Azure root template](assets/terraform/azure-root) for Azure. For DigitalOcean, read [DigitalOcean adaptations](references/terraform-digitalocean.md) and use the [DigitalOcean root template](assets/terraform/digitalocean-root). Other providers can reuse the organization with their own resource and state configuration.

Define Terraform configuration with `locals`, including `local.input` and separate maps for related settings. Do not introduce Terraform input variables, `var.*` references, `variables.tf`, tfvars, or `TF_VAR_*` configuration workflows. Provider authentication still uses the operator's credential environment; keep secrets out of locals. Backend blocks retain literal settings because Terraform does not allow locals there.

Terraform assets are separate from the React/FastAPI copier and are not added to every application. Create only requested components and environments. Preserve existing roots, state keys, and resource addresses; adding this convention does not authorize a migration, cloud provisioning, or deployment.

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

Authorized preparation of a runnable application must leave a usable root `.vscode/tasks.json`. Inspect the existing file first. Preserve working starter/repository tasks, environment settings, inputs, platform overrides, and prerequisite chains; add or repair only what the local run journey needs. Reuse TWYD portal's structure, not its product commands, old paths, or tunnel URL:

- `frontend`: the selected frontend dev command in its package directory.
- `backend:app`: the selected backend process or development Compose service in its actual working directory.
- `backend`: aggregate the backend and any explicitly required supporting processes.
- `fullstack`: start all required app components in parallel, with dedicated terminals. A single-component application includes only that component.
- Add finite setup, database readiness, or migration tasks before servers when the app requires them. The bundled starter already supplies `setup`, `db`, `migrate`, and `dev:ready`; preserve this graph.
- Include a stop task for a Compose-managed runtime, such as `backend:down` or the starter's `containers:down`, preserving data volumes. Stop host dev servers with VS Code's Tasks: Terminate Task command.
- Include ngrok only when the accepted local workflow needs a tunnel and that command is selected. Ordinary local startup does not require ngrok.

Generate missing standard tasks:

```bash
"${CODEX_HOME:-$HOME/.codex}/skills/coding-prepare-environment/scripts/generate_tasks.py" <repo-root>
```

The generator selects components present at `backend` and `frontend/app`, detects Node package-manager and dev/start scripts, and uses the root `.venv` for Python. Override paths for established layouts. It detects `main:app` or `app.main:app` for FastAPI; other backends can provide an explicit command. Use `--components backend|frontend|fullstack` when directory detection cannot describe the accepted runtime.

For a TWYD-style container backend, adapt these arguments to the inspected project:

```bash
"${CODEX_HOME:-$HOME/.codex}/skills/coding-prepare-environment/scripts/generate_tasks.py" <repo-root> \
  --backend-cwd '${workspaceFolder}/deployments/dev' \
  --backend-app-command 'docker compose up --build backend' \
  --backend-down-command 'docker compose down'
```

Keep the real service name, Compose/env-file paths, package manager, ports, and authentication flow from the repository. Use `--frontend-command`, `--frontend-cwd`, and `--backend-cwd` for other established entrypoints. Add existing prerequisite labels with repeated `--backend-depends-on` or `--frontend-depends-on`. Use `--backend-ngrok-command` only for an explicitly selected tunnel workflow; generating its task does not start it.

By default the generator preserves existing labels and adds missing ones. `--replace` replaces only selected standard labels after their commands and dependencies have been reviewed; never use it indiscriminately over starter tasks. Existing JSONC comments are not retained when the generator writes formatted JSON. Invalid input must remain untouched.

Run long-lived dev servers as background tasks with dedicated terminals. The generator and starter track Uvicorn and Vite startup output with background problem matchers. Supply `--backend-ready-pattern` or `--frontend-ready-pattern` for a known custom readiness line, especially when a background task is a sequential dependency or debug prerequisite. An unknown command does not acquire a guessed readiness signal. See [VS Code's task guidance](https://code.visualstudio.com/docs/debugtest/tasks) for background dependency behavior.

Before reporting setup complete, resolve `fullstack` through its dependency labels, confirm each command/cwd and prerequisite order, start the required local services when authorized verification needs them, and check the app through its actual frontend/API entrypoint. Report the task label, local URL, stop action, and any unavailable startup checks. File existence alone does not prove the entire app can run.

## Output Shape

Use concise handoff text:

```text
Environment prepared:
- detected: Python + React
- changed: created deployments/dev/.env from deployments/dev/.env.example; updated whitelist `.gitignore`
- commands: .venv/bin/python -m pip install -r backend/requirements.txt;
  cd frontend/app && pnpm install --frozen-lockfile
- use: .venv/bin/python -m pytest ... from the repo root;
  ../.venv/bin/python -m uvicorn app.main:app --reload from backend;
  pnpm test ... from frontend/app
- blockers: none
```
