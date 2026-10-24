# Guided installation and recovery

## Outcome

A user runs `./install.sh` on macOS or Linux and selects one phase, several phases, or a complete installation. The same operations are available as explicit CLI commands. The installer separates preparing a harness, activating its home, installing the CLI, installing dependencies, signing in, starting a persistent service, pairing, and checking the result.

## Acceptance

- **AC1:** An interactive launch presents the phases and their effects before execution. Explicit phase selection works without a terminal. Dry-run prints the selected plan without changing files, downloading packages, signing in, or starting services. Cancellation and EOF exit without treating an unanswered prompt as consent.
- **AC2:** Copy publishes Git-owned harness files and the bundled installer runtime into a new checkout without activating it or copying ignored runtime state. Existing destinations are refused. Home activation offers merge, replacement with a retained backup, or cancel. Merge preserves destination files, private state, and validated internal standalone-package links. Foreign links are retained in the backup and never activated. Activation verifies any previously working CLI through its original published path after changing the home; an invalid result restores the previous home and shell configuration.
- **AC3:** CLI installation verifies the package digest and version before publication. The managed CLI lives under `~/.local/share/dot-codex/cli`, outside Codex Home. Fresh installation, repeat installation, and version changes publish the requested executable atomically. Invalid packages leave the current CLI intact.
- **AC4:** Each selected phase has explicit prerequisites and fails with an actionable next command. Completed phases remain usable after later failure. A private checkpoint supports retrying unfinished phases. Ctrl+C during a prompt or filesystem activation restores the prior active home; interrupted package extraction does not change the published CLI. Concurrent mutations of one user home are refused.
- **AC5:** Dependencies reuse the existing inventory and native marketplace lifecycle. Login uses Codex device authentication only when required. Pairing runs separately and only after a connected, non-timed-out Remote Control result with an environment identity. Pairing codes and provider output are never stored in checkpoints.
- **AC6:** The service phase writes a Linux user service or macOS LaunchAgent using the verified CLI path and selected home. Linux boot persistence requires lingering and reports its absence. Service activation verifies the service manager and the live Remote Control result; missing executables, failed services, stale preparation files, or connecting responses cannot produce readiness. Doctor is read-only and reports the actual executable, home, and configured service state.
- **AC7:** The README and installation guide document independent commands, full installation, copy versus activation, backup and restore, interruption/retry, prerequisites, and external verification limits. Existing explicit home/dependency flags remain usable.

## Decisions and boundaries

`install.sh` remains the shell entrypoint and Python 3.11+ runs the wizard without adding a UI dependency. Numbered selection supports SSH terminals and plain input. The shell/bootstrap and onboarding separation follows OpenClaw; its TypeScript wizard uses `@clack/prompts`, but this checkout already has a Python installer. VM provisioning supplies the package/version/read-back and service patterns, without Azure or Terraform coupling.

Replacement retains state rather than deleting it. The explicit legacy discard confirmation remains accepted, but discard now means replacement with a backup. The installer never silently changes an existing working CLI unless its CLI phase is selected. Installing or activating on a real machine remains an operator action; implementation verification uses disposable homes and service/network/provider boundaries.
