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

Order of preference:

1. Existing `.env*` required by the app.
2. Closest checked-in example, such as `.env.example`, `.env.local.example`,
   `app/.env.example`, or `wp-config-sample.php`.
3. Documentation that lists required keys.
4. A blocker report listing missing keys or files.

Python app-folder convention:

- If an `app/` folder exists and Python application code or `app/requirements.txt` is present,
  treat `app/.env` as the default app env file.
- If `app/.env` is missing and `app/.env.example` exists, copy the example to `app/.env`.
- If only root `.env.example` exists, use it only when repo docs or code clearly read root `.env`.
- Do not move env files between root and `app/` without an explicit repo pattern.

## Python

Detect Python with `pyproject.toml`, `requirements*.txt`, `app/requirements.txt`, `pytest.ini`,
`tox.ini`, or Python source under `app/`, `src/`, or package directories.

Setup:

1. Ensure `.venv/` exists at repo root when Python is detected.
2. Never delete `.venv/`. Repair incrementally.
3. If `$HOME/.codex/scripts/ensure_venv` exists, run it first.
4. Otherwise create the venv with `python3 -m venv .venv`.
5. Upgrade packaging only when needed by the repo: `.venv/bin/python -m pip install -U pip`.
6. Install dependencies with the repo's chosen mechanism:
   - `app/requirements.txt`: `.venv/bin/python -m pip install -r app/requirements.txt`
   - `requirements.txt`: `.venv/bin/python -m pip install -r requirements.txt`
   - `pyproject.toml`: prefer documented `uv`, `poetry`, or `pip install -e .` pattern.

Command policy:

- Run Python tooling through `.venv/bin/python -m <tool>`.
- Use `.venv/bin/python -m pytest ...` for pytest.
- Use `.venv/bin/python -m ruff ...`, `.venv/bin/python -m mypy ...`, etc. when installed.
- Do not assume shell activation.

## React and Node

Detect React/Node with `package.json`, lockfiles, `vite.config.*`, `next.config.*`, `src/`,
or framework-specific config.

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
- Create local env files only from examples, commonly `.env.local` from `.env.local.example`
  or `.env.example`, without overwriting existing files.

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
- If `.env` is newly copied and `APP_KEY` is empty, run `php artisan key:generate` only for local
  development and only if it does not require unavailable services.
- Prefer SQLite for local test env only when the repo already documents or configures it.
- Run migrations only when the requested task or test requires a database and the
  target is clearly local/test.

Command policy:

- Prefer `php artisan test`, `vendor/bin/phpunit`, or `vendor/bin/pest` according
  to repo convention.
- Keep queue, mail, cache, and storage config local-safe.

## WordPress

Detect WordPress with `wp-config.php`, `wp-config-sample.php`, `wp-content/`, or Composer packages
such as `johnpbloch/wordpress`.

Setup:

- Identify whether the repo is a full WordPress install, a plugin, a theme, or a Bedrock-style app.
- Do not edit production `wp-config.php` values unless the user asks.
- For local-only config, prefer repo docs, `.env.example`, `wp-config-local.php`,
  or Docker/devcontainer setup.
- Use `wp-cli` only when it is already available locally or provided by the repo/container.
- Do not install or activate plugins/themes against a live database unless explicitly requested.

Command policy:

- For plugins/themes, prefer repo-local PHPUnit, Composer scripts, PHPCS, or npm scripts.
- For full sites, prefer documented Docker/devcontainer commands when present.

## Other or Unknown Stacks

When stack signals are unclear:

- Inspect docs and lockfiles before installing anything.
- Prefer `make setup`, `make test`, `just`, `task`, `docker compose`, `.devcontainer/`,
  `flake.nix`, `.tool-versions`, `mise.toml`, or `.envrc` when present.
- Report the detected setup surface and ask only when the next setup step would be destructive,
  credential-dependent, or ambiguous enough to risk corrupting local state.
