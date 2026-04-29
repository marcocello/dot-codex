---
name: prepare-environment
description: >-
  Prepare local project environments before coding, tests, gates, acceptance
  checks, or dependency/tooling work. Use when Codex or another skill needs the
  shared setup step for Python, React/Node, PHP, Laravel, WordPress, or
  mixed/unknown stacks, including environment discovery, safe .env handling,
  virtualenv/node_modules/vendor setup, and validation command selection.
---

# Prepare Environment

Purpose: centralize repo setup policy so other skills and AGENTS.md do not
duplicate stack-specific environment rules.

## Caller Contract

- Use this skill before implementation or checks when the local environment is not known-good.
- Other skills should delegate setup decisions here instead of repeating stack setup rules.
- Keep setup changes minimal and reversible. Do not delete existing `.venv`,
  `node_modules`, `vendor`, `.env`, database files, caches, uploads, or
  generated assets unless the user explicitly asks.
- Never print secret values. When reporting `.env` work, mention filenames and missing keys only.
- Prefer repo-provided setup scripts, Make targets, package scripts, Docker files,
  and documented commands.
- If setup requires missing credentials or external services, stop with the exact
  blocker and continue with any checks that do not require those services.

## Workflow

1. Read local authority first:
   - `docs/ARCHITECTURE.md` if it exists.
   - `docs/TESTING.md`, `docs/CONVENTIONS.md`, `README*`, `Makefile`, and
     package/tool config when relevant.
2. Detect stack signals:
   - Python: `pyproject.toml`, `requirements*.txt`, `app/requirements.txt`, `pytest.ini`, `tox.ini`.
   - React/Node: `package.json`, lockfiles, `vite.config.*`, `next.config.*`, `src/`, `app/`.
   - PHP/Laravel: `composer.json`, `artisan`, `phpunit.xml`, `pest.php`, `.php-version`.
   - WordPress: `wp-config.php`, `wp-config-sample.php`, `wp-content/`, or
     WordPress Composer packages.
   - Other: Docker, devcontainer, Nix, direnv, mise, asdf, language lockfiles, or custom scripts.
3. Load only the relevant sections of [stack-reference.md](references/stack-reference.md).
4. Prepare the minimum environment needed for the current task.
5. Run the narrowest setup verification available, then report:
   - stacks detected
   - files created or changed
   - commands run
   - remaining blockers
   - exact command prefix future skills should use

## Selection Rules

- If multiple stacks exist, prepare only the stacks touched by the requested work or checks.
- If package managers conflict, use the lockfile or repo documentation. Do not mix
  `npm`, `yarn`, `pnpm`, and `bun` in one project without clear repo precedent.
- If no setup command is documented, use the ecosystem default from the stack reference.
- If local toolchains are incomplete, prefer documented containers or devcontainers
  over installing unrelated global tools.
- Do not add dependencies for setup convenience unless the task explicitly includes dependency work.

## Output Shape

Use concise handoff text:

```text
Environment prepared:
- detected: Python + React
- changed: created app/.env from app/.env.example
- commands: .venv/bin/python -m pip install -r app/requirements.txt; pnpm install --frozen-lockfile
- use: .venv/bin/python -m pytest ... and pnpm test ...
- blockers: none
```
