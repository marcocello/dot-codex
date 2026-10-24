# Install and migrate dot-codex

## Install from a checkout

Use macOS or Linux with Python 3.11+, Git, Node/npm, and an installed Codex CLI that supports `codex plugin`. Install those tools separately; the installer does not perform global package installs. Install the desktop app if you use it.

```sh
git clone https://github.com/marcocello/dot-codex.git /path/to/dot-codex
cd /path/to/dot-codex
./install.sh
```

The checkout is the permanent runtime home. It must remain at this path. The installer creates a private `config.toml` only when none exists, registers the `dot-codex` marketplace from `integrations/`, and reconciles declared skills and plugins through `scripts/skill_inventory.py`. Public MCP definitions are bundled in the `dot-codex-tools` plugin. The template contains portable preferences only.

You can use `--codex-bin /absolute/path/to/codex` when the CLI is not on PATH. `--user-home /temporary/user` selects a disposable user directory for verification; omit it for ordinary installation. Windows is rejected before mutation.

## Existing home choices

Close the desktop app, Codex CLI sessions, and background Codex processes before migrating. Copying live SQLite databases is not a supported migration. When `~/.codex` is nonempty, the installer asks:

- **merge:** Copy absent entries into the checkout. Preserve existing checkout files, including its configuration when present. Preserve the full original home, including conflicting files and symlinks, under private `.install-backups/<timestamp-id>/`. Replace the old default-home entry with a link only after the snapshot matches the original. The old directory is then removed; a symlink's external target is retained.
- **discard:** Permanently remove the old directory after you type `DELETE`. No snapshot is retained. If the old entry is a symlink, only the link is removed; its target remains.
- **cancel:** Leave the existing home unchanged. An empty answer or EOF also cancels.

If the checkout already is the default home, rerunning installation does not migrate it. If the checkout sits inside the old home, installation refuses the overlap; clone outside that home first. Foreign symlinks are retained in the snapshot rather than activated, and merging never follows a destination symlink. Special files and state that changes during snapshotting stop migration.

Copied histories, databases, credentials, and personal skills stay local. The installer adds exact destination exclusions at the end of `.gitignore`, because this repository's whitelist can override `.git/info/exclude`. It never runs `git add`, commits, or pushes. Review installer-generated ignore rules before committing unrelated configuration work. An old `AGENTS.md` or conflicting skill remains in the snapshot for deliberate reconciliation; it does not replace repository guidance.

## Persistent home for terminal and desktop

The installer adds one managed `CODEX_HOME` block to `~/.profile`, `~/.zshenv`, `~/.bashrc`, and `~/.bash_profile`. It also updates existing Zsh startup files and `.bash_login`, placing the block after older assignments. Paths containing spaces are shell-quoted. Existing content outside the managed block is preserved. Symlinked startup files are rejected with their path so you can resolve the intended destination explicitly.

The installer links `~/.codex` to the checkout. Desktop launches can therefore use the default home without inheriting a terminal export. Existing processes retain their environment and open state. Fully quit and reopen the app, open a new terminal, or activate the variable in the current shell:

```sh
export CODEX_HOME=/absolute/path/to/dot-codex
```

Verify in a new terminal:

```sh
printf '%s\n' "$CODEX_HOME"
ls -ld "$HOME/.codex"
codex plugin list
codex mcp list
```

Custom launchers, `ZDOTDIR`, Fish, system environment overrides, and shells that do not read these startup files need their own `CODEX_HOME` setup. A process that already has a different value will use that value until restarted or corrected. The installer does not change macOS launch services or install a login daemon.

## Optional integrations

The core plugin activates Shadcn, Context7, Agentation, OpenAI Docs, and ReUI. Context7 can inherit `CONTEXT7_API_KEY` from the launching environment when available; the package never contains a key. npm-backed servers download their packages when Codex starts them. Installing a plugin and listing its enabled MCP definitions does not prove network connectivity or tool execution.

Optional plugins are available from the same bundled marketplace:

| Selection | Prerequisite |
| --- | --- |
| `--with landingfolio` | `LANDINGFOLIO_MCP_TOKEN` in the launching environment |
| `--with originkit` | `ORIGINKIT_API_KEY` in the launching environment |
| `--with skills-registry` | A separate registry listening at `http://127.0.0.1:5175/mcp` |

Repeat `--with` to select several plugins. The installer records the selection in `skills.toml` through the inventory manager, then installs it normally. Keep personal selections local unless they belong in the shared inventory. Configure credentials through your machine's environment or the integration's connection flow; never put tokens in manifests or source. Desktop launches need access to those credentials independently of your terminal.

The app owns browser and Node REPL runtime configuration. The installer does not copy app binaries, runtime paths, access pipes, or browser trust hashes from another machine. Existing configuration can retain them during merge, so review stale machine paths after moving state between machines. Sign in on the new machine and connect account-based integrations through their normal setup.

## Retry and updates

Rerun `./install.sh` after repairing an unavailable provider or prerequisite. The installer keeps completed migration and local preferences, avoids duplicate environment blocks, and retries dependencies. A provider failure returns a nonzero exit and identifies the affected dependency without printing provider output that might contain credentials. Run the named provider or inventory command locally for detail. Unavailable external marketplace snapshots must be configured through `codex plugin marketplace` or the desktop app; the installer does not invent marketplace sources or treat missing runtime-owned plugins as installed.

`./install.sh --skip-dependencies` performs home setup only and reports that dependencies are incomplete. Use it for offline migration, then rerun without that flag. For later skill refreshes, use `$harness-manage-skills sync`. Native plugin files are cached copies; after changing a bundled plugin, use `$harness-manage-skills update dot-codex-tools` to refresh it rather than assuming the installed copy follows source edits.

If migration stops during copying, the original default home remains until a full snapshot has been verified. If a later step fails after activation, the checkout is already the runtime home and the retained snapshot remains available. Fix the reported error and rerun. Resolve conflicts manually from `.install-backups/`; do not delete a needed snapshot until you have checked the copied history, configuration, and personal skills in the new app.

## Design references

Astro-code's `bin/install.mjs`, `lib/install.mjs`, and `lib/hosts/codex.mjs` informed the separation between installation and activation, repeated reconciliation, and self-hosted path guards. dot-codex keeps the user's selected checkout as its home rather than creating Astro's separate mirror.

Codex stores local configuration and state under [`CODEX_HOME`, defaulting to `~/.codex`](https://developers.openai.com/codex/config-advanced/#config-and-state-locations). The integration catalog follows the official [local marketplace and plugin format](https://developers.openai.com/plugins/build/plugins#how-local-marketplaces-work).
