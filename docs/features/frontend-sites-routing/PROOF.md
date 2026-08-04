# Frontend And Sites Routing Proof

## Done
- The real shared gate accepts a target repository without project-local agent instructions.
- The harness profile, rather than the common target-repository profile, owns the requirement for the global kernel source.
- The active configuration still enables Sites.
- The global kernel and frontend skill expose the accepted pre-scaffold routing boundary.
- The broken self-referential `.codex` symlink is absent.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/frontend-sites-routing --timeout-seconds 60 --note "verify frontend and Sites routing repair"
```

## Scenario: Target repository without local agent instructions
- Producer/activation: pytest creates a temporary repository-shaped directory containing README and `.gitignore`, then invokes the real `scripts/gate --profile other` subprocess.
- Consumer: the gate's normal common-profile path.
- Read-back: subprocess exit status and gate output.
- Fake: the temporary repository contents only; the gate executable is unchanged.
- Catches: retaining the unconditional common `AGENTS.md` requirement or merely changing its message.

## Scenario: Global kernel ownership
- Producer/activation: pytest creates a minimal temporary harness-shaped repository without `AGENTS.md`, then invokes the real gate harness profile.
- Consumer: the gate's normal harness-profile path.
- Read-back: the reported failure owner and message.
- Fake: the temporary harness repository; the gate executable is unchanged.
- Catches: removing the kernel requirement entirely or leaving it owned by the common target-repository profile.

## Scenario: Routing policy and enabled Sites configuration
- Producer/activation: pytest parses the active TOML configuration and reads the global kernel plus `coding-frontend` skill artifacts.
- Consumer: Codex's actual static configuration and instruction sources.
- Read-back: structured TOML state and explicit routing invariants in the instruction artifacts.
- Fake: none.
- Catches: disabling Sites, omitting the pre-existing-manifest boundary, allowing current-task manifests to self-authorize Sites, or losing frontend structure ownership.

## Scenario: Codex-home filesystem shape
- Producer/activation: pytest inspects the dot-codex root.
- Consumer: the local filesystem.
- Read-back: `.codex` is not a self-referential symlink; a regular repository-owned configuration directory is allowed.
- Fake: none.
- Catches: retaining or recreating the self-referential symlink.

## Scope
Proves:
- Mechanical gate ownership and exit behavior.
- Sites remains enabled in the active configuration.
- The accepted routing policy is present in the instruction surfaces Codex loads.
- The local Codex home no longer contains the broken nested symlink.

Does not prove:
- Deterministic instruction compliance by every future model or product version.
- Sites deployment behavior after Sites is intentionally selected.
- Behavior in an already-running task that loaded older instructions.

False-green risks:
- Static policy assertions can pass while a future model ignores the policy; the proof therefore distinguishes instruction availability from probabilistic model adherence.
- A unit-only gate test could bypass CLI wiring; the regression invokes the real gate subprocess.
- Removing the common requirement could accidentally remove all kernel validation; the harness-profile scenario requires the failure at its new owner.

Proof change:
- The original assertion rejected every `.codex` entry even though the accepted behavior forbids only the broken self-referential symlink. The final queue sweep exposed a legitimate `.codex/hooks.json` directory. The corrected oracle checks the owning filesystem invariant without deleting repository configuration.

Evidence method:
- deterministic

Known gaps:
- Model routing remains probabilistic and requires a new task to load changed global instructions.

## Environment
- Repository-local Python virtual environment and pytest.
- Temporary repository fixtures created by pytest.
- Runner stdout: resolved Python executable and version, gate path, and Sites configuration state without secrets.
