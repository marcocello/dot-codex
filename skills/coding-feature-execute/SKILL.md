---
name: coding-feature-execute
description: "Implement one feature end-to-end in Codex App using FEATURE.md for desired behavior, PROOF.md for done criteria, existing repo skills, red/green proof-first work, deterministic validation, mandatory backend/frontend/WordPress domain-skill handoff, and bounded repair. Use when a feature contract and proof contract are ready or need to be made ready before delivery."
metadata:
  short-description: Codex-native proof-driven feature execution
---

# Feature Execute

Purpose: deliver one feature inside Codex App without adding a repo-local orchestrator.

## Entry Conditions
- Use this skill only for one feature implementation, not for rough feature discovery.
- `FEATURE_DIR` is known, or exactly one matching feature directory can be identified.
- `FEATURE_DIR/FEATURE.md` describes the expected behavior clearly enough to implement.
- `FEATURE_DIR/PROOF.md` defines one executable primary proof command.
- If `FEATURE.md` is missing, vague, or materially incomplete, stop feature execution and use
  `coding-feature-spec`. For non-trivial features, `coding-feature-spec` will route to
  `coding-proof-author`.
- If `FEATURE.md` is ready but `PROOF.md` is missing, stale, vague, static-only, or lacks an
  executable primary proof artifact, stop feature execution and use `coding-proof-author`.

## Workflow
1) Load the contracts
   - Read `FEATURE_DIR/FEATURE.md`.
   - Read `FEATURE_DIR/PROOF.md`.
   - If `FEATURE.md` has `## Implementation Routing` or `Required skills`, load those skills before implementation.

2) Load repo-level context when present
   - Read `docs/ARCHITECTURE.md` if it exists.
   - Read `docs/CONVENTIONS.md` if it exists.
   - Read `docs/TESTING.md` if it exists.

3) Ensure the software project baseline
   - For software projects, initialize a Git repository with `git init` when the current project directory is not already inside a Git worktree.
   - Do not overwrite existing Git history or reinitialize a repository that already has `.git`.
   - Use `coding-prepare-environment` to create or update `.vscode/tasks.json` when selected domain skills call for local run tasks.

4) Choose the right implementation skill
   - Mandatory domain handoff: when a feature touches backend, frontend, or WordPress application code, explicitly use the matching domain skill before creating files, installing packages, or choosing a starter.
   - Obey skill routing declared in `FEATURE.md`; missing routing is a fallback case, not permission to skip domain skills.
   - Use `coding-python-backend` when backend Python work is in scope.
   - Use `coding-frontend` when React or Next.js UI work is in scope.
   - Use `coding-wordpress` when WordPress plugin, theme, full-site, or Bedrock-style work is in scope.
   - Use `coding-repair` for small corrective changes.

5) Prepare the environment
   - Use `coding-prepare-environment` before running tests, proof commands, gates, package installs, dev servers, or framework CLIs.

6) Establish red proof
   - Run the primary proof command from `PROOF.md` before implementation when practical.
   - Confirm the proof fails or is unmet for the expected missing behavior.
   - If the proof already passes, inspect whether the feature is already done or whether `PROOF.md` is too weak.
   - If the proof is too weak, use `coding-proof-author` to strengthen the anti-gaming review and executable proof before implementation.

7) Review non-trivial feature quality
   - For non-trivial feature work, use `coding-feature-quality` before implementation to scan ambiguity, edge cases, testability, proof quality, and architecture conflicts.

8) Implement minimally
   - Add lower-level tests only where they reduce implementation risk.
   - Make the smallest code change that satisfies `FEATURE.md` and `PROOF.md`.
   - Do not change `PROOF.md` after implementation unless the proof was materially wrong; if changed, state why and rerun red/green evidence where possible.

9) Validate
   - Run the proof and gate required by the `AGENTS.md` Universal Lifecycle.

10) Evaluate and update status
   - Follow the `AGENTS.md` Universal Lifecycle.
   - If `docs/features/status.json` exists, use `coding-feature-queue` to update status.
   - If proof, gate, and evaluator pass but a human reports the feature still does not work, treat the proof package as insufficient.
   - In that case, use `coding-proof-author` to add a failing proof that captures the real broken behavior before changing production code again.

11) Repair only concrete failures
   - If the primary proof, gate, or evaluator fails, use `coding-repair` on the concrete
     failing behavior or check result.
   - Keep fixes within the smallest failing scope.
   - Do not hand off as done while the primary proof is failing.

12) Escalate only by AGENTS.md policy
   - If proof, gate, or evaluator judgment is still failing after the first targeted
     repair pass, follow the autonomous escalation policy in `AGENTS.md`.

## Behavioral Baseline
- Think before changing code: state blocking ambiguity, assumptions, and material tradeoffs before implementation.
- Simplicity first: implement the smallest design that satisfies `FEATURE.md` and `PROOF.md`.
- Surgical changes: touch only files and lines needed for the feature, and clean up only dead code introduced by the current change.
- Goal-driven execution: tie each implementation step to the primary proof or a narrower check that supports it.
- Green-but-broken handling: when passing proof contradicts observed behavior, improve the proof contract before repairing code.

## Rules
- Keep changes local.
- Reuse existing code paths before adding new ones.
- Do not build orchestration infrastructure in this repo.
- Prefer existing domain skills over inventing new coordination logic.
- Follow the autonomous escalation policy in `AGENTS.md`; do not build repo-local
  orchestration infrastructure.
- Do not weaken `PROOF.md`, reduce feature scope, or substitute assistant/tool claims for observable proof.

## Handoff
- Report using the `AGENTS.md` handoff format for completed feature or issue work.
