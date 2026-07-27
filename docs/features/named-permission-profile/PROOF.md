# Named Permission Profile Proof

## Proves
- The installed Codex CLI strictly loads the real active configuration.
- The active configuration selects `projects-write`, defines the intended workspace roots, enables network access, and contains no legacy sandbox settings that would override the profile.
- The template has the same permission-profile structure with portable roots.
- Codex's diagnostic boundary reports a restricted filesystem sandbox with networking enabled after loading the active configuration.
- The removed `js_repl` flag remains absent and multi-agent behavior remains explicitly disabled.

## Evidence Method
- Parse both TOML artifacts through Python's standard `tomllib`.
- Assert the exact permission profile, inheritance, roots, network setting, preserved feature setting, and absence of conflicting legacy keys.
- Start the installed Codex app server with strict configuration handling and close it through standard-input EOF.
- Run `codex doctor --json` against the active configuration and read back the targeted `config.load` and `sandbox.helpers` checks.

## False-Green Risks
- TOML syntax alone could pass while `sandbox_mode` silently overrides the new profile; the proof rejects either legacy sandbox key.
- A template-only migration could pass while the live configuration remains unchanged; the proof reads both the repository template and `~/.codex/config.toml`.
- Source assertions could pass while Codex rejects the configuration; strict app-server loading and doctor read-back exercise the installed CLI.
- The diagnostic command can return a nonzero overall status for unrelated terminal checks; the proof parses and requires the configuration and sandbox checks specifically.

## Does Not Prove
- That an already-running task reloads configuration without restart.
- That every allowed root is writable through every operating-system permission or protected-path exception.
- That unrestricted network access is least privilege for every future task.
- That a future beta permission-profile schema remains backward compatible.

## Known Gaps
- Workspace-root membership is asserted from the loaded artifact because the current diagnostic output reports the effective sandbox class and network state but does not enumerate effective roots.
- The permission-profile feature is documented as beta and may require later migration.

## Execution
- Runner: `docs/features/named-permission-profile/proof/run.sh`
- Official timeout: 60 seconds.
- The runner performs read-only configuration and diagnostic checks and creates only a temporary diagnostic file.
