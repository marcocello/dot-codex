# Installer verification

## Done and command

Run `bash docs/features/checkout-installer/proof/run.sh` from the repository root. Pass when every CLI journey succeeds and its independent filesystem, Git, and Codex read-back assertions pass.

## Boundary and scenarios

The producer is a disposable checkout plus a disposable user home. The public activation is its copied `install.sh`. The owners are the filesystem, shell startup files, local Git ignore rules, and Codex's plugin store. Tests read those owners after the installer exits and launch a fresh shell to read `CODEX_HOME`.

AC1–AC3 and AC5 use real installer subprocesses, real copies/symlinks, and real Git queries. Outer dependency providers are skipped explicitly for migration-only cases. Cases cover fresh install and rerun, merge and conflicting content, Git visibility of copied Markdown, discard confirmation, cancel/EOF, overlap, and symlink boundaries.

AC4 uses the real installed Codex CLI in a disposable Codex Home to register the local marketplace, install the public plugin, list its enabled installation, and read all five enabled MCP definitions with `codex mcp list --json`. Inventory orchestration uses a recorded fake provider at its process boundary for deterministic failure/retry checks; the native local plugin lifecycle remains real. Remote marketplaces, Git/npm downloads, MCP startup, service authentication, and desktop relaunch are not established by these local checks.

Skipping marketplace registration, losing a copied skill, overwriting checkout source, failing to persist the environment, exposing migrated private Markdown to Git, or claiming success after a provider failure must fail the checks. Evidence is partial native capture plus official CLI proof output; no private real-machine state is migrated during verification.
