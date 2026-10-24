# Install a checkout as Codex Home

## Outcome

A user clones dot-codex anywhere and runs `./install.sh`. That checkout becomes the persistent Codex Home for future terminal sessions and the default home used by desktop launches. This implementation targets macOS and Linux with Python 3.11+, Git, Node/npm, and an installed Codex CLI. It does not install global tools or log in for the user.

## Acceptance

- **AC1:** A fresh install creates private local configuration from a minimal template, persists `CODEX_HOME` in shell startup files, and makes `~/.codex` resolve to the checkout. A rerun preserves existing local configuration and does not duplicate environment blocks.
- **AC2:** A nonempty existing `~/.codex` prompts for merge, discard, or cancel. Cancel, EOF, invalid prerequisites, and unsafe overlapping paths leave the old home unchanged. Discard requires typing `DELETE` and removes the old directory, or only the link when it is a symlink.
- **AC3:** Merge copies existing state into the checkout, preserving checkout files. Conflicting files and symlinks remain in a private full migration snapshot. Copied state is ignored by Git even when its extension is normally allowed. The installer never stages, commits, or pushes, and never follows destination symlinks to overwrite external files. Existing configuration is preserved when the checkout has none. Users must stop Codex before migrating live state.
- **AC4:** Install registers the bundled marketplace, installs and enables its public MCP plugin through the native Codex lifecycle, and reconciles declared skill dependencies through the existing inventory manager. Optional credential-based plugins and the local registry require explicit selection. Missing credentials and provider failures produce a nonzero exit with actionable recovery; a rerun can retry. Public MCP definitions live in plugins rather than the template.
- **AC5:** The README documents the real install command, destructive choice, merge conflict policy, private state handling, persistent environment, dependency prerequisites, optional integrations, and restart/authentication boundaries. Installation never claims that connected services have authenticated or that a desktop process already running has reloaded.

## Decisions and limits

Astro-code's installer and Codex adapter were inspected at `/Users/marcocello/software/scaleuplabs/astro-code-main`. Reuse the separation of publication and activation, repeatable reconciliation, and source identity guards; do not copy its Claude-specific hooks or separate home mirror. The checkout remains the source and runtime home. A default-home symlink covers desktop launches without relying on terminal exports; shell startup blocks set the explicit variable. Existing environment overrides later in user startup files may still need removal.

Migration snapshots live under ignored `.install-backups/`. Explicit discard deletes the original without retaining a snapshot. Merge retains a complete snapshot before replacing the old default-home entry. Unknown credentials remain private. The installed app owns its Node/browser runtime. Windows is rejected before mutation. The installer is delivered here; running it on a real user's home is a separate user action.
