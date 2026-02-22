You are in "gate-fix" mode.

Objective
- Make `$HOME/.codex/scripts/gate` pass.
- Do not implement new features.
- Fix only what is necessary.

Rules
- Do NOT weaken/delete tests to make the gate pass.
- If Python/.venv is involved: do NOT delete `.venv`; use `$HOME/.codex/scripts/ensure_venv`.

Steps
1) Run `$HOME/.codex/scripts/gate` from the repo root.
2) If it fails: fix the smallest root cause.
3) Re-run `$HOME/.codex/scripts/gate` until it passes or you are blocked.
4) If blocked, output `BLOCKED: <reason>` and what information/permission is needed.

End
- End output with exactly: `READY`