# Stack Reference

Use this file as the shared setup policy. Keep stack skills thin by pointing them here.

## Global Safety

- Do not overwrite existing `.env` files.
- Do not invent production credentials or service URLs.
- Do not print secret values from env files or command output.
- Prefer copying from checked-in examples over hand-writing env files.
- Prefer repo-local tools over global tools.
- Prefer existing lockfiles and documented commands over ecosystem defaults.

## Environment Files

Environment files follow the established repository layout or the greenfield component locations in this skill's SKILL.md.

Order of preference:

1. Existing `.env*` required by the app.
2. Closest checked-in example, such as `.env.example`, `.env.local.example`, `backend/.env.example`, `frontend/.env.local.example`, or `wp-config-sample.php`.
3. Documentation that lists required keys.
4. A blocker report listing missing keys or files.

Python backend convention:

- If `backend/app` exists or backend dependency files are present, treat `backend/.env` as the default backend env file.
- If `backend/.env` is missing and `backend/.env.example` exists, copy the example to `backend/.env`.
- If only root `.env.example` exists, use it only when repo docs or code clearly read root `.env`.
- Do not move env files between root, `backend/`, and `frontend/` without an explicit repo pattern.

## Repository Ignore Policy

When creating a new root `.gitignore`, use a whitelist pattern by default:

```gitignore
## Whitelist-style monorepo ignore.
## Ignore by default, then allow source/config/docs file types explicitly.

# 1. Ignore everything.
*

# 2. Allow Git to descend into directories.
!*/

# 3. Allow repo metadata and source files.
!.gitignore
!README*
!*.md
!*.py
!*.php
!*.ts
!*.mts
!*.cts
!*.tsx
!*.js
!*.jsx
!*.mjs
!*.cjs
!*.html
!*.css
!Makefile
!.nvmrc
!package.json
!package-lock.json
!pnpm-lock.yaml
!yarn.lock
!composer.json
!composer.lock
!pyproject.toml
!requirements*.txt
!tsconfig*.json
!tasks.json
!.env.example
!.env.local.example

# 4. Block generated, local, secret, and runtime artifacts.
.git/
.venv/
node_modules/
vendor/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.next/
dist/
build/
coverage/
.cache/
.env
.env.*
!.env.example
!.env.local.example
*.pem
*.key
*.log
*.tsbuildinfo
*.sqlite
*.sqlite3
*.db
.DS_Store
uploads/
auth_info_baileys/
.auth/
sessions/
wordpress/app/wp-content/cache/
```

Rules:

- Preserve a safe existing whitelist's project-specific entries while aligning it with these four sections when updating it. Do not rewrite an unrelated existing ignore file solely for formatting.
- Keep sections 1 and 2 unchanged unless technically unavoidable; explain any exception. Tailor section 3 to the actual stack's source/config/docs file types and specific filenames, and section 4 to its generated, local, secret, and runtime artifacts.
- Do not allow whole directory trees with `!directory/**`; directory traversal is already enabled by `!*/`.
- Keep real `.env*` files ignored. The example exceptions after the environment block intentionally allow only checked-in examples; examples must not contain credentials.
- Never whitelist dependency directories, generated output, uploads, caches, or databases. Verify block rules also exclude otherwise allowed extensions inside those directories.
- Validate nested source/config visibility and artifact exclusion with `git check-ignore --no-index`; for an uninitialized project, use a temporary Git repository rather than initializing the user's project just for validation.

## Python

Detect Python with `backend/pyproject.toml`, `backend/requirements*.txt`, `backend/app/requirements*.txt`, `backend/app`, root `pyproject.toml`, root `requirements*.txt`, `pytest.ini`, `tox.ini`, or Python source under documented package directories.

Setup:

1. Ensure `.venv/` exists at repo root when Python is detected.
2. Never delete `.venv/`. Repair incrementally.
3. Create the venv with `python3 -m venv .venv` when missing.
4. Upgrade packaging only when needed by the repo: `.venv/bin/python -m pip install -U pip`.
5. Install dependencies with the repo's chosen mechanism:
   - `backend/requirements.txt`: `.venv/bin/python -m pip install -r backend/requirements.txt`
   - `backend/app/requirements.txt`: `.venv/bin/python -m pip install -r backend/app/requirements.txt`
   - `requirements.txt`: `.venv/bin/python -m pip install -r requirements.txt`
   - `backend/pyproject.toml`: prefer documented `uv`, `poetry`, or `pip install -e backend` pattern.
   - `pyproject.toml`: prefer documented `uv`, `poetry`, or `pip install -e .` pattern.

Command policy:

- Run Python tooling through `.venv/bin/python -m <tool>`.
- Use `.venv/bin/python -m pytest ...` for pytest.
- Use `.venv/bin/python -m ruff ...`, `.venv/bin/python -m mypy ...`, etc. when installed.
- For FastAPI apps with `app = FastAPI()` in `backend/app/main.py`, run the dev server from `backend/app` with `../../.venv/bin/python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000`, or use the quoted absolute path to the repository's `.venv/bin/python` when the app lives elsewhere.
- Do not assume shell activation.

## React and Node

Detect Node backends and frontends with `backend/app/package.json`, `frontend/app/package.json`, `frontend/package.json`, frontend lockfiles, `frontend/app`, `vite.config.*`, `next.config.*`, root `package.json`, root lockfiles, or framework-specific config.

Package manager priority:

1. `packageManager` field in `package.json`.
2. Lockfile: `pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`, `bun.lockb`, `bun.lock`.
3. Existing repo scripts or documentation.
4. Default to `npm` only if no signal exists.

Setup:

- Use `corepack` when the repo declares Yarn or pnpm through `packageManager`.
- Run one install command matching the package manager:
  - pnpm: `pnpm install --frozen-lockfile` when a lockfile exists.
  - yarn: `yarn install --immutable` for modern Yarn, otherwise `yarn install --frozen-lockfile`.
  - npm: `npm ci` when `package-lock.json` exists, otherwise `npm install`.
  - bun: `bun install --frozen-lockfile` when a lockfile exists.
- Create local env files only from examples, commonly `.env.local` from `.env.local.example` or `.env.example`, without overwriting existing files.
- Run package-manager commands from the selected package directory: by default `backend/app` for Node backends and `frontend/app` for frontends. Preserve established alternatives such as `frontend/package.json`, which requires commands from `frontend/`.

Command policy:

- Use package scripts from `package.json` for tests, lint, typecheck, build, and dev servers.
- Do not add a new package manager lockfile unless dependency work explicitly requires it.

## PHP and Composer

Detect PHP with `composer.json`, PHP source files, `phpunit.xml`, `.php-version`, or framework CLIs.

Setup:

1. Inspect required PHP version and extensions from `composer.json`.
2. Run `php -v` and `composer --version` when available.
3. Run `composer install` when `vendor/` is missing or dependencies are not installed.
4. Use `composer install --no-interaction --prefer-dist` unless repo docs specify otherwise.
5. Create `.env` from `.env.example` only when the project clearly expects it.

Command policy:

- Prefer `vendor/bin/phpunit`, `vendor/bin/pest`, framework CLIs, or Composer scripts.
- Do not run destructive database commands without explicit user approval.

## Laravel

Laravel is PHP plus `artisan`.

Setup:

- Run `php artisan about` only after dependencies and env are present enough for it to boot.
- If `.env` is newly copied and `APP_KEY` is empty, run `php artisan key:generate` only for local development and only if it does not require unavailable services.
- Prefer SQLite for local test env only when the repo already documents or configures it.
- Run migrations only when the requested task or test requires a database and the target is clearly local/test.

Command policy:

- Prefer `php artisan test`, `vendor/bin/phpunit`, or `vendor/bin/pest` according to repo convention.
- Keep queue, mail, cache, and storage config local-safe.

## WordPress

Detect WordPress with `wp-config.php`, `wp-config-sample.php`, `wp-content/`, or Composer packages such as `johnpbloch/wordpress`.

Setup:

- Identify whether the repo is a full WordPress install, a plugin, a theme, or a Bedrock-style app.
- Do not edit production `wp-config.php` values unless the user asks.
- For local-only config, prefer repo docs, `.env.example`, `wp-config-local.php`, or Docker/devcontainer setup.
- Use `wp-cli` only when it is already available locally or provided by the repo/container.
- Do not install or activate plugins/themes against a live database unless explicitly requested.

Command policy:

- For plugins/themes, prefer repo-local PHPUnit, Composer scripts, PHPCS, or npm scripts.
- For full sites, prefer documented Docker/devcontainer commands when present.

## Other or Unknown Stacks

When stack signals are unclear:

- Inspect docs and lockfiles before installing anything.
- Prefer `make setup`, `make test`, `just`, `task`, `docker compose`, `.devcontainer/`, `flake.nix`, `.tool-versions`, `mise.toml`, or `.envrc` when present.
- Report the detected setup surface and ask only when the next setup step would be destructive, credential-dependent, or ambiguous enough to risk corrupting local state.
