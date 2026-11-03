# Install the coding harness

Install Codex separately, then clone or copy this repository and run:

```bash
./install.sh
```

The installer links the checkout to `~/.codex`, exposes its skills under `~/.agents/skills`, and copies `config.template.toml` to `config.toml` only when it is absent. It performs no downloads, login, service setup or cloud operations. Repeating it preserves existing configuration and unrelated skills. An unrelated existing home or conflicting skill stops installation before publication; migrate that content explicitly instead of overwriting it.

Codex uses `~/.codex` by default, so the link normally needs no environment variable. To select this checkout explicitly in the current shell:

```bash
eval "$(./install.sh --print-env)"
```

Alternatively, source `~/.codex/env.sh` from a shell or launcher that needs the explicit default home. A child installer cannot export into its parent shell. GUI launchers may have a different environment; the default home link works without relying on shell startup files.

## Optional dependencies

The core instructions and owned skills are local. External skills and plugins are declared in `skills.toml`. Install them separately when needed, with Codex and their required launchers already available:

```bash
codex plugin marketplace add ./integrations --json
python3 scripts/skill_inventory.py --manifest skills.toml --skills-root skills sync
python3 scripts/skill_inventory.py --manifest skills.toml --skills-root skills doctor
```

Run these commands with this checkout selected as `CODEX_HOME`. Credentials and provider authentication remain private setup; do not infer readiness from plugin membership alone. Runtime-owned OpenAI skills and plugins stay outside the inventory.

## Separate second brain

The sibling `secondbrain` repository owns personal knowledge skills, context services, gateways, Docker and remote setup. Its launcher uses a private Codex profile. Coding installation does not require or activate that runtime.

Private research, analysis, presentations and exports default to `${OBSIDIAN_VAULT:-$HOME/ObsidianVault}/Dot-codex/`, preserving existing topic folders. Acceptance contracts, reusable source assets and product documentation stay in their repositories. Existing local deliverables were moved with a private manifest in the vault; they are not public source.
