---
name: coding-feature-execute
description: "Implement one feature end-to-end in Codex App using FEATURE.md for desired behavior, PROOF.md for done criteria, existing repo skills, red/green proof-first work, deterministic validation, mandatory backend/frontend/WordPress domain-skill handoff, and bounded repair. Use when a feature contract and proof contract are ready or need to be made ready before delivery."
metadata:
  short-description: Codex-native proof-driven feature execution
---

# Feature Execute

Purpose: deliver one feature. No repo-local orchestrator.

## Entry
- One `FEATURE_DIR`.
- `FEATURE_DIR/FEATURE.md` ready enough to implement.
- `FEATURE_DIR/PROOF.md` defines executable primary proof.
- If `FEATURE.md` is missing, vague, or materially incomplete, stop and use
  `coding-feature-spec`.
  For non-trivial features, `coding-feature-spec` will route to `coding-proof-author`.
- If `FEATURE.md` is ready but `PROOF.md` is missing, stale, vague, static-only, or lacks
  executable proof, stop and use `coding-proof-author`.
- If `PROOF.md` defines a raw primary proof command that does not call
  `scripts/proof_run_capture`, stop before implementation and use `coding-proof-author`.
- Missing/weak/static/uncaptured `PROOF.md`: stop, use `coding-proof-author`.

## Workflow
1. Load contracts
   - Read `FEATURE.md`, `PROOF.md`.
   - Load `Required skills` / `Implementation Routing` if present.

2. Load repo context
   - Read `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, `docs/TESTING.md` when present.

3. Ensure baseline
   - If software project lacks Git, `git init`.
   - Do not overwrite existing Git history.
   - Use `coding-prepare-environment` when setup/tasks are needed.

4. Route implementation
   - Backend Python: `coding-python-backend`.
   - React/Next UI: `coding-frontend`.
   - WordPress: `coding-wordpress`.
   - Small corrective change: `coding-repair`.
   - Domain handoff before starters, folders, packages.

5. Establish red proof
   - Run primary proof before implementation when practical; for any `FEATURE_DIR`, this
     must be the captured command from `PROOF.md` using `scripts/proof_run_capture`.
   - Confirm expected failure/unmet behavior.
   - If already green, inspect whether done or `PROOF.md` too weak.
   - Weak or uncaptured proof: strengthen via `coding-proof-author` before code.

6. Trust ready contracts, review stale contracts
   - If a queue item is already `ready`, do not run `coding-feature-quality` again unless
     `FEATURE.md` or `PROOF.md` is stale, weak, contradictory, or changed before
     implementation starts.
   - Otherwise use `coding-feature-quality` when uncertainty is material.
   - Once implementation code changes begin, freeze `FEATURE.md`, `PROOF.md`, proof
     artifacts.

7. Implement
   - Smallest change satisfying `FEATURE.md` and `PROOF.md`.
   - Add lower-level tests only when they reduce risk.
   - Semantic behavior: implement invariant at owning boundary; no hardcoded natural-language phrase lists, wording gates, or tool hiding as substitute for
     state/object/provider validation.
   - Once implementation code changes begin, do not change contracts/proof artifacts. If
     contract is wrong, stop, move to contract repair, apply the Proof Change Guard there,
     restart from red proof.

8. Validate
   - Run proof and gate required by `AGENTS.md` Universal Lifecycle.
   - If proof/gate/evaluator fails, use `coding-repair` on the concrete failing behavior or
     check result.
   - Do not hand off as done while primary proof fails.

9. Evaluate/status
   - Run `coding-feature-evaluator`.
   - If `docs/features/status.json` exists, update via `coding-feature-queue`.
   - If proof, gate, evaluator pass but human-visible behavior fails, treat the proof package as insufficient.
     Stop implementation; repair contract with failing proof before changing production code again.

10. Escalate
   - If proof/gate/evaluator still fails after first targeted repair, follow the autonomous escalation policy in `AGENTS.md`.
   - Active Goal: continue through `coding-autonomous-execute` while proof remains
     unsatisfied.

## Rules
- Think before code when ambiguity blocks correctness.
- Reuse existing paths.
- Keep changes local.
- No orchestration infrastructure.
- Do not weaken `PROOF.md`, reduce scope, or substitute assistant/tool claims for
  observable proof.
- Do not mix implementation code edits with `FEATURE.md`, `PROOF.md`, or proof-artifact
  edits in the same implementation pass.

## Handoff
- Report using the `AGENTS.md` short receipt format for completed feature or issue work.
- Outcome, changed surface, verification.
- Technical appendix only when asked or needed for audit/debug.
