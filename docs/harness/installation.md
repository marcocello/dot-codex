# Install and recover Codex and dot-codex

Run `./install.sh` from this checkout. The wizard explains one phase at a time and asks `Run this step? [y/N]`. Enter skips it; only `y` or `yes` selects it. After the last question, review the selected plan and answer `Run this plan? [y/N]`. Enter cancels without executing any selected phase. Skipping every phase exits successfully without changes or new state. Invalid answers are retried. Explicit commands provide the same operations without walking through the wizard.

The English interface follows [OpenClaw's installer style](https://openclaw.ai/install.sh): blue headings, cyan checkmarks, amber warnings, muted details, and red failure marks. A wide terminal shows a rounded banner; narrow terminals and redirected output show a simple banner. Color is automatic for supported terminals. Redirected output and `TERM=dumb` stay plain. Use `--color always` to force ANSI output or `--color never` to disable it. `NO_COLOR` disables colors even when `--color always` is supplied. All messages remain understandable without color. No additional UI package is required.

## Prerequisites

Use macOS or Linux with Python 3.11+ and Git. Downloading the CLI also needs curl. The skills/plugins phase needs Node and npm. The installer does not install system packages or change a global npm prefix.

Run the installer as the intended login user. Close Codex terminals, the desktop app, and background Codex processes before migrating an existing home. Copying active SQLite databases is not supported. Installing this script does not activate it on another machine: run it on that machine, for example from an SSH session to `media.local`.

## Select phases

| Command | Result |
| --- | --- |
| `./install.sh` | Walk through each phase with default-No questions |
| `./install.sh all` | CLI, harness, dependencies, login, service, pairing, then doctor |
| `./install.sh --wizard all` | Ask about each phase in the complete journey |
| `./install.sh --wizard --steps cli,harness,service` | Ask only about these phases |
| `./install.sh copy --destination ~/software/dot-codex-next` | Prepare another checkout without activating it |
| `./install.sh harness --mode merge` | Activate this checkout and merge absent old state |
| `./install.sh harness --destination ~/software/dot-codex-next --mode replace` | Activate the prepared checkout without merging old state; keep a backup |
| `./install.sh cli` | Install or repair the user-local Codex CLI |
| `./install.sh dependencies` | Reconcile declared skills and plugins |
| `./install.sh login` | Reuse existing authentication or start device sign-in |
| `./install.sh service` | Configure and verify persistent Remote Control |
| `./install.sh pair` | Verify connectivity, then display a temporary pairing code |
| `./install.sh doctor` | Inspect current paths, CLI, and configured startup service without changing them |
| `./install.sh resume` | Retry unfinished phases from the private checkpoint |
| `./install.sh restore` | Restore the previous home and shell setup; retain the new harness files |

Use `--steps copy,cli,harness,dependencies --destination PATH --mode merge` to select several phases. Put `copy` first. `all --destination PATH` also copies the harness when PATH does not exist. Copy includes Git-owned source and the bundled installer modules, preserves Git history, and excludes ignored runtime files. An existing copy destination is refused.

`--dry-run` prints the plan without downloading, activating, signing in, or starting a service. `--yes` accepts a selected plan and skips its final confirmation; wizard phase questions still require opt-in. It does not choose merge or replacement for a nonempty home: supply `--mode` explicitly. Prompt cancellation, EOF, and Ctrl+C are never interpreted as consent. `q` cancels a wizard question before any selected phase runs. Use the explicit `resume` and `restore` commands for recovery.

## Home activation and backups

The selected checkout becomes Codex Home. Shell startup files persist `CODEX_HOME`; `~/.codex` links to the checkout for desktop launches. Open a new terminal and fully quit/reopen the desktop app after activation. Existing processes retain their previous environment.

Choose `merge` to copy absent state while preserving files already present in the checkout. Conflicts remain in the retained old home. Validated internal standalone-package links are rebased into the new home so a working published CLI remains usable. Foreign links remain in the backup and are not activated. Copied private state is ignored by Git; the installer never stages or commits that state.

Choose `replace` to use the new harness without importing old state. `discard` remains a legacy alias, with its typed confirmation, but now retains a backup too. The installer does not permanently delete the old home.

A real home on the same filesystem is atomically renamed under private `.install-backups/<id>/`. An old home symlink, or a home on another filesystem, is retained as `~/.codex.backup.<id>`; the checkout also retains a private snapshot. The installer prints the recovery path. Cross-filesystem migration needs space for that additional snapshot. Old external symlink targets are retained.

`restore` restores the previous home and shell files. It refuses to overwrite shell files changed since activation. New harness state is kept for inspection, including data created after activation. A repeated activation of the same home retains the original restore receipt.

## CLI installation

The managed CLI is installed outside Codex Home:

- Releases: `~/.local/share/dot-codex/cli/releases/`
- Active release: `~/.local/share/dot-codex/cli/current`
- Published command: `~/.local/bin/codex`

Changing the harness cannot remove this CLI. The CLI phase persists an idempotent PATH block in shell startup files. Open a new terminal after installation, or use the published absolute path immediately. The installer prefers this executable for later phases, even when the current shell has another Codex on PATH. Existing working CLIs remain usable unless the CLI phase is selected. Previously installed `/usr/local/bin/codex` links that point to `~/.local/bin/codex` work after the user-local publication is repaired.

The service phase publishes `<CODEX_HOME>/packages/standalone` as a compatibility link to the external CLI root. The native daemon requires its `current/codex` entrypoint; verified releases include a generated `codex -> bin/codex` alias. Existing native package directories are retained as `packages/standalone.backup.<id>` before publication. A matching existing native installation is reused. A different custom CLI is refused with an actionable command. The package files remain outside the harness.

The default pinned release is `0.151.0`. Use `--version X.Y.Z` to select another release. The installer reads the official GitHub release metadata, verifies its SHA-256 digest, checks the extracted version, and atomically replaces the publication. A rejected package or interruption before publication keeps the current executable. Repeated installation reuses identical release files.

For an offline or audited package:

```bash
./install.sh cli --version X.Y.Z --package-file /path/to/package.tar.gz --sha256 DIGEST
```

`--package-url HTTPS_URL --sha256 DIGEST` is also supported. Custom package URLs are not retained in checkpoints; supply the URL again when resuming that phase. `--codex-bin /absolute/path/to/codex` selects an existing CLI for other phases.

## Skills and plugins

The dependencies phase registers the bundled marketplace, reconciles `skills.toml`, and verifies the native inventory. The public plugin supplies Shadcn, Context7, Agentation, OpenAI Docs, and ReUI. Use `--with landingfolio`, `--with originkit`, or `--with skills-registry` for explicit optional integrations. Credential-based integrations require their named environment variables. The installer never prints those values or writes them into its checkpoint.

Provider failures return a nonzero exit and name an actionable retry. Completed phases remain available. For later inventory changes, use `$harness-manage-skills`. Native plugin files are cached copies; source edits require a plugin update. Installing a plugin does not establish MCP network connectivity or authenticate external services.

Legacy `./install.sh --skip-dependencies` still performs only home activation. Existing explicit `--codex-bin` and `--with` home/dependency invocations remain supported; new automation should select phases explicitly.

## Sign-in, services, and pairing

Login, service setup, and pairing are separate operations. Login uses native Codex device authentication only when login status fails. Pairing codes are displayed directly and are not stored in checkpoints. Pairing requires a connected Remote Control result with an environment identity and no timeout.

On Linux, the service phase writes `codex-remote-control.service`, a health service, and a one-minute health timer under `~/.config/systemd/user/`. It uses the managed daemon lifecycle from codex-on-vm and preserves the detached daemon when a oneshot launcher exits. Missing executables fail visibly rather than skipping the health unit. A healthy daemon is not torn down during relay outages.

Boot persistence requires user lingering. If it is absent, rerun `./install.sh service --enable-linger`; this may request sudo through `loginctl`. The script verifies the setting, service activation, and the live Remote Control result. It does not reboot the machine. A successful service phase proves the current connection and startup configuration; an actual reboot remains a separate operator check.

On macOS, a LaunchAgent under `~/Library/LaunchAgents/` runs the persistent health helper. It starts at user login and requires a logged-in GUI session. It does not start before login as a system daemon. Both platforms keep the runner under `~/.local/share/dot-codex/`, so later checkout moves do not remove the runner.

Doctor reads the current executable and version, the resolved home, native package publication, service-manager state, and the local daemon when a startup service is configured. It does not start Remote Control or prove relay connectivity. Run the service phase for a live connection check.

## Interruptions and retry

Private state lives under `~/.local/state/dot-codex/` with a per-user mutation lock. `install.json` records phase names and statuses, selected paths, and non-secret retry options. It does not contain provider output, passwords, or pairing codes. Starting a new plan replaces the phase checkpoint; activation undo records and old-home backups remain available.

Ctrl+C stops the child process group and marks the current phase interrupted. Filesystem activation rolls back the active home, new copied state, and shell changes. Previously completed phases remain available. Package downloads and extraction occur before publication. After an uncatchable process termination, the next mutating invocation reads the pending undo record and restores the previous filesystem state before retrying.

Run `./install.sh resume` from the same source checkout. Review and provide any missing choices or credentials. Service-manager operations and authentication belong to their providers: cancellation can leave a valid service definition or completed sign-in, and rerunning reconciles that state. The installer does not claim to undo remote pairing or account authentication.

## Design references and verification

The implementation follows the separate bootstrap/onboarding structure in [OpenClaw's installer](https://openclaw.ai/install.sh), inspected as source on 2026-10-24. OpenClaw uses an optional Gum terminal interface and a separate [TypeScript wizard with @clack/prompts](https://github.com/openclaw/openclaw/blob/main/src/wizard/clack-prompter.ts). This repository keeps its existing Python runtime and sequential opt-in questions. Banner framing and status styling use the standard library, so first-use CLI installation needs no Node or UI download. Package verification and managed service patterns come from the local codex-on-vm console.

Run `bash docs/features/guided-installer/proof/run.sh` for isolated CLI journeys, real filesystem transactions, signals, and fake outer account/service providers. `bash docs/features/guided-installer/proof/native-package.sh` downloads the official pinned package and verifies installation, rerun, and native app-server start/version/stop in a disposable home. Neither command installs host services or signs in on your real machine.
