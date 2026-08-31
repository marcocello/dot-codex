---
name: pull-codex-config
description: Safely clone or fast-forward a local dot-codex checkout containing Codex skills, scripts, rules, and configuration. Use when the user wants to refresh that checkout without overwriting local work.
---

# Pull Codex Config

Use the bundled script to update the user's dot-codex checkout:

```bash
python skills/pull-codex-config/scripts/pull_codex_config.py
```

## Behavior

The script resolves the checkout from `--repo-dir`, `DOT_CODEX_REPO`, the repository containing the installed skill, a Git-backed `CODEX_HOME`, or `$HOME/dot-codex`, in that order.

For an existing checkout it derives the expected repository URL from `--repo-url`, `DOT_CODEX_REPO_URL`, or the current `origin`. It refuses local changes by default and performs a fast-forward-only pull from the requested branch.

For a missing checkout, the repository URL must be supplied with `--repo-url` or `DOT_CODEX_REPO_URL`. The script then clones it into the resolved destination.

## Safety and receipt

- If local changes are reported, stop and show the affected paths. Do not stash, reset, or discard them without explicit user direction.
- Use `--allow-dirty` only after explicit user approval.
- If the command succeeds, report whether the checkout was cloned or fast-forwarded.
- Mention that the app or task may need a reload before newly pulled skill metadata is visible.

Useful overrides are `--repo-dir PATH`, `--repo-url URL`, and `--branch NAME`.
