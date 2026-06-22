---
name: coding-feature-execute
description: "Implement one feature end-to-end in Codex App using FEATURE.md for desired behavior, PROOF.md for done criteria, existing repo skills, red/green proof-first work, deterministic validation, mandatory backend/frontend/WordPress domain-skill handoff, and bounded repair. Use when a feature contract and proof contract are ready or need to be made ready before delivery."
metadata:
  short-description: Codex-native proof-driven feature execution
---

# Feature Execute

Purpose: deliver one feature inside Codex App without adding a repo-local orchestrator.

## Workflow
1) Start from the feature and proof contracts
   - Read `FEATURE_DIR/FEATURE.md`.
   - Read `FEATURE_DIR/PROOF.md`.
   - If `PROOF.md` is missing, vague, stale, or lacks a primary proof command, use `coding-proof-author` before implementation.
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
   - Use `coding-fix-issue` for small corrective changes.

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
   - Run the primary proof command from `PROOF.md`.
   - Run `$HOME/.codex/scripts/gate`.

10) Evaluate independently
   - Use `coding-feature-evaluator` after implementation and deterministic checks.
   - Treat evaluator `PASS` as the condition for marking the feature complete.
   - Treat evaluator `FAIL` as repair input.
   - Treat evaluator `BLOCKED` as a real blocker; do not claim done.
   - If a Codex Goal is active, keep it open until proof, gate, evaluator `PASS`, and queue status prove completion.
   - If `docs/features/status.json` exists, use `coding-feature-queue` to mark the feature `passing`, `failing`, or `blocked` based on proof, gate, and evaluator result.
   - If proof, gate, and evaluator pass but a human reports the feature still does not work, treat the proof package as insufficient.
   - In that case, use `coding-proof-author` to add a failing proof that captures the real broken behavior before changing production code again.

11) Escalate only on failure
   - If the primary proof or gate fails, use `coding-auto-improve`.
   - If `coding-feature-evaluator` returns `FAIL`, use `coding-auto-improve` or `coding-fix-issue` on the concrete findings.
   - Keep fixes within the smallest failing scope.
   - Do not hand off as done while the primary proof is failing.

12) Automatically use `coding-autonomous-execute` for repeated repair
   - If proof, gate, or evaluator judgment is still failing after the first targeted repair pass, automatically use `coding-autonomous-execute`.
   - Do not wait for a separate user request.
   - Use this stop condition: primary proof passes and gate passes, or the same blocker repeats three times.
   - Default budget: three loop iterations.
   - Keep `coding-auto-improve` responsible for the smallest failing fix inside each iteration.
   - Run `coding-feature-evaluator` after each repair pass before marking the feature done.

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
- `coding-autonomous-execute` is an automatic bounded escalation path, not a repo-local orchestrator.
- Do not weaken `PROOF.md`, reduce feature scope, or substitute assistant/tool claims for observable proof.

## Handoff
- Include `Skills used:` with every skill actually loaded or followed.
- Report exactly one `Primary proof`: command from `PROOF.md`, red result, and green result.
- Report gate under `Safety checks` as `Gate: PASS` or `Gate: FAIL`; include detail only when failing.
- Do not include full passing gate/test counts unless the user asks.
- Report any extra commands under `Safety checks`, not under `Proof`.
- Report `Evaluator` separately as `PASS`, `FAIL`, or `BLOCKED`.
- Report queue status when updated.
- Report concrete blockers, or `None`.
- Do not label secondary checks, gate, or evaluator as proof.
