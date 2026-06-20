---
name: coding-auto-improve
description: "Repair failing primary proof commands, gate checks, typecheck, lint, build, or evaluator failures with bounded minimal fixes after a feature attempt in Codex App. Use when implementation is in progress or complete and deterministic checks fail."
metadata:
  short-description: Bounded proof-driven repair loop
---

# Auto Improve

Purpose: self-correct after a failed implementation attempt without introducing a repo-local orchestrator.

## Workflow
1) Prepare the environment
   - Use `coding-prepare-environment` if dependencies, env files, or command prefixes are not known-good.

2) Run the authoritative checks
   - If a concrete `FEATURE_DIR` is in scope, run the primary proof command from `FEATURE_DIR/PROOF.md`.
   - Run `$HOME/.codex/scripts/gate`.

3) Isolate the smallest failing scope
   - Prefer the narrowest failing test, file, proof step, or validation command.
   - Do not broaden the repair beyond the actual failure.

4) Repair with bounded loops
   - Use a bounded retry approach.
   - Make one small fix at a time.
   - Re-run the narrowest failing check after each fix.
   - Keep making bounded fixes until required checks pass.
   - Do not hand off as done while the primary proof is failing.

5) Re-run the authoritative checks
   - Re-run the primary proof command when the feature is in scope.
   - Re-run gate.

## Behavioral Baseline
- Think before changing code: isolate the failing check and identify the most likely cause before editing.
- Simplicity first: prefer the smallest repair that turns the failing proof green.
- Surgical changes: do not broaden the repair beyond the failing scope or perform drive-by cleanup.
- Goal-driven execution: every repair loop must end by re-running the narrowest failing check, then the authoritative proof and gate.

## Rules
- Keep the loop bounded; do not keep making speculative fixes.
- Prefer existing skills such as `coding-fix-issue`, `coding-python-backend`, `coding-frontend`, `coding-wordpress`, and `coding-proof-author` for the actual code or proof change.
- Fix only the smallest failing scope.
- Do not weaken `PROOF.md`, reduce feature scope, or replace observable proof with assistant claims.
- Do not introduce a separate in-repo orchestrator.
