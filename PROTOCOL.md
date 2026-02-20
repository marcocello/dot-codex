# Press ↔ Codex Protocol (Minimal)

This repo may be driven by an orchestrator ("Press").
Codex must behave deterministically and emit machine-readable status.

## Required status artifact
After each run, write:

- `.press/status.json`

Minimum schema:
```json
{
  "feature_dir": "features/001-example",
  "phase": "IMPLEMENT|GATE_FIX|ACCEPTANCE_FIX|DONE|BLOCKED",
  "head_sha": "abc123",
  "gate": { "cmd": "./scripts/gate", "passed": true },
  "acceptance": { "cmd": "./scripts/acceptance --feature features/001-example", "passed": false, "failed_acs": ["AC-2"] },
  "summary": ["..."],
  "files_changed": ["..."]
}```

## Required end token
End your final message with exactly ONE of:
- `READY_FOR_PRESS`
- `DONE`
- `BLOCKED: <reason>`
- `NEED_INPUT: <question>`

Press is authoritative and will re-run scripts/gate and scripts/acceptance.