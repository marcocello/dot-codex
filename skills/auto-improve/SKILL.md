---
name: auto-improve
description: Repair failing gate or feature acceptance checks with bounded, minimal fixes after a feature attempt in Codex App. Use when implementation is in progress or complete and deterministic checks fail.
metadata:
  short-description: Bounded check-driven repair loop
---

# Auto Improve

Purpose: self-correct after a failed implementation attempt without introducing a repo-local
orchestrator.

## Workflow
1) Prepare the environment
   - Use `prepare-environment` if dependencies, env files, or command prefixes are not known-good.

2) Run the authoritative checks
   - Run `$HOME/.codex/scripts/gate`.
   - If a concrete `FEATURE_DIR` is in scope, run
     `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`.

3) Isolate the smallest failing scope
   - Prefer the narrowest failing test, file, or validation command.
   - Do not broaden the repair beyond the actual failure.

4) Repair with bounded loops
   - Use a bounded retry approach.
   - Make one small fix at a time.
   - Re-run the narrowest failing check after each fix.

5) Re-run the authoritative checks
   - Re-run gate.
   - Re-run feature acceptance when the feature is in scope.

## Rules
- Keep the loop bounded; do not keep making speculative fixes.
- Prefer existing skills such as `fix-issue`, `python-backend`, `frontend`, and
  `acceptance-author` for the actual code change.
- Fix only the smallest failing scope.
- Do not introduce a separate in-repo orchestrator.
