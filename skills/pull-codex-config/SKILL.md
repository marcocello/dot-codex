---
name: pull-codex-config
description: Safely pull the local Codex configuration checkout from https://github.com/marcocello/dot-codex. Use when the user asks to pull, update, refresh, or get the latest dot-codex repo, Codex skills, scripts, AGENTS.md discipline, or local Codex configuration from marcocello/dot-codex.
---

# Pull Codex Config

Use this skill to update the local `marcocello/dot-codex` checkout that supplies Codex skills,
scripts, and configuration.

## Workflow

1. Run the bundled script from this skill:

   ```bash
   python skills/pull-codex-config/scripts/pull_codex_config.py
   ```

2. If the script reports local changes, stop and show the user the listed paths. Do not stash,
   reset, or overwrite those changes unless the user explicitly asks.
3. If the script succeeds, tell the user whether the repo was cloned or fast-forwarded.
4. If new or changed skills are expected in the current Codex session, mention that the UI or
   thread may need a reload before newly pulled skill metadata is visible.

## Script Behavior

- Default repository: `https://github.com/marcocello/dot-codex`.
- Default checkout path:
  - `--repo-dir`, when provided.
  - `DOT_CODEX_REPO`, when set.
  - The repo containing this installed skill, when it is already inside a Git checkout.
  - `CODEX_HOME`, when it points at a Git checkout.
  - `$HOME/software/marcocello/dot-codex`.
- Missing checkout: clone the repository.
- Existing checkout: verify the `origin` remote, refuse local changes by default, then run a
  fast-forward pull from `origin/main`.

## Useful Options

- `--repo-dir PATH`: pull into a specific checkout.
- `--repo-url URL`: override the remote, mainly for tests or mirrors.
- `--branch NAME`: pull a branch other than `main`.
- `--allow-dirty`: allow Git to attempt the pull despite local changes. Use only after explicit
  user approval.
