You are in "gate-fix" mode.

## Objective
Make `./scripts/gate` pass. Do not implement new features. Fix only what is necessary.

## Steps
1) Run `./scripts/gate`.
2) If it fails: fix the smallest root cause.
3) Re-run `./scripts/gate` until it passes or you are blocked.
4) Update `.press/status.json` with:
   - phase: GATE_FIX (or BLOCKED/DONE)
   - gate results
   - brief summary
5) End output with `READY_FOR_PRESS` (or `BLOCKED: ...`).