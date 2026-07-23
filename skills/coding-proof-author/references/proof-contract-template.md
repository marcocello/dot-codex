# Proof Template

```md
# Proof

## Done
- <observable result>

## Command
```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir FEATURE_DIR --timeout-seconds N --note "reason"
```

## Scenario: <name>
- Producer/activation: <real path>
- Consumer: <normal path>
- Read-back: <durable/visible evidence>
- Fake: <unsafe outer edge only|none>
- Catches: <central break>

## Scope
Proves:
- <claim>

Does not prove:
- <gap>

False-green risks:
- <risk>

Evidence method:
- deterministic | probabilistic

Known gaps:
- none | live | manual | scale | timing | provider | environment

## Environment
- <runtime/data/readiness>
- Runner stdout: <actual application executable path/version and other relevant non-secret runtime facts>
```

Show this design to user before writing. Accepted proof only. Direct runner. No implementation edits, daemonization, or process-group escape. Print the actual application runtime used by the scenario; do not dump the full environment.
