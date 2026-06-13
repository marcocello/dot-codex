---
name: coding-feature-execute
description: Implement one feature end-to-end in Codex App using existing repo skills, red/green TDD, deterministic validation, mandatory frontend/backend domain-skill handoff, and automatic coding-autonomous-execute escalation when bounded repeated repair is needed. Use when a feature contract is ready and the goal is delivery rather than planning infrastructure.
metadata:
  short-description: Codex-native feature execution
---

# Feature Execute

Purpose: deliver one feature inside Codex App without adding a repo-local orchestrator.

## Workflow
1) Start from the feature contract
   - Read `FEATURE_DIR/FEATURE.md`.
   - Use the Gherkin scenarios as the behavior contract.
   - If `FEATURE.md` has `## Implementation Routing` or `Required skills`, load those skills
     before implementation.

2) Load repo-level context when present
   - Read `docs/ARCHITECTURE.md` if it exists.
   - Read `docs/CONVENTIONS.md` if it exists.
   - Read `docs/TESTING.md` if it exists.

3) Ensure the software project baseline
   - For software projects, initialize a Git repository with `git init` when the current project
     directory is not already inside a Git worktree.
   - Do not overwrite existing Git history or reinitialize a repository that already has `.git`.
   - Use `coding-vscode-generate-run-tasks` to create or update `.vscode/tasks.json` when the
     project has or is creating the standard frontend/backend local run layout.

4) Choose the right implementation skill
   - Mandatory domain handoff: when a feature touches frontend or backend application code,
     explicitly use the matching domain skill before creating files, installing packages, or
     choosing a starter.
   - Obey skill routing declared in `FEATURE.md`; treat missing routing as a fallback case, not as
     permission to skip domain skills.
   - Use `coding-python-backend` when backend Python work is in scope, including greenfield API
     layer creation before creating backend files.
   - Use `coding-frontend` when React or Next.js UI work is in scope, including greenfield frontend
     skeleton creation before creating frontend files.
   - Use `coding-fix-issue` for small corrective changes.
   - If the chosen domain skill defines a default bootstrap, follow it before generic scaffolding,
     package setup, or first-code decisions. Do not invent a generic framework skeleton when a
     domain skill specifies the starter or baseline.

5) Prepare the environment
   - Use `coding-prepare-environment` before running tests, gates, acceptance, package installs,
     dev servers, or framework CLIs.

6) Ensure acceptance coverage exists
   - If `FEATURE_DIR/acceptance/` is missing or incomplete, use `coding-acceptance-author` first.
   - Do not continue broad implementation without the required acceptance harness.

7) Review non-trivial feature quality
   - For non-trivial feature work, use `coding-feature-quality` before implementation to scan
     ambiguity, edge cases, testability, and architecture conflicts.
   - This does not require Spec Kit or OpenSpec command phases.

8) Use red/green TDD
   - Add or update the smallest relevant test.
   - Confirm it fails before implementation.
   - Make the smallest code change.
   - Confirm the same test passes after implementation.

9) Validate
   - Run `$HOME/.codex/scripts/gate`.
   - Run `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`.

10) Evaluate independently
   - Use `coding-feature-evaluator` after implementation and deterministic checks.
   - Treat evaluator `PASS` as the condition for marking the feature complete.
   - Treat evaluator `FAIL` as a repair input.
   - Treat evaluator `BLOCKED` as a real blocker; do not claim done.
   - If a Codex Goal is active, keep it open until gate, acceptance, evaluator `PASS`, and queue
     status prove completion.
   - If `docs/features/status.json` exists, use `coding-feature-queue` to mark the feature `passing`,
     `failing`, or `blocked` based on the evaluator result.

11) Escalate only on failure
   - If gate or acceptance fails, use `coding-auto-improve`.
   - If `coding-feature-evaluator` returns `FAIL`, use `coding-auto-improve` or `coding-fix-issue` on the concrete
     findings.
   - Keep fixes within the smallest failing scope.
   - Keep making bounded fixes until required checks pass.
   - Do not hand off as done while feature acceptance is failing.

12) Automatically use `coding-autonomous-execute` for repeated repair
   - If gate, acceptance, or the feature completeness check is still failing after the first
     targeted repair pass, automatically use `coding-autonomous-execute`.
   - Do not wait for a separate user request.
   - Use this stop condition: gate passes and
     `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR` passes, or the same blocker repeats
     three times.
   - Default budget: three loop iterations.
   - Keep `coding-auto-improve` responsible for the smallest failing fix inside each iteration.
   - Run `coding-feature-evaluator` after each repair pass before marking the feature done.
   - Do not start schedulers or background work unless the user explicitly asks for recurring or
     unattended execution.

## Behavioral Baseline
- Think before changing code: state blocking ambiguity, assumptions, and material tradeoffs before
  implementation.
- Simplicity first: implement the smallest design that satisfies `FEATURE.md`; do not add
  speculative abstractions or configurability.
- Surgical changes: touch only files and lines needed for the feature, and clean up only dead code
  introduced by the current change.
- Goal-driven execution: tie each implementation step to a test, acceptance scenario, or
  deterministic validation command.

## Rules
- Keep changes local.
- Reuse existing code paths before adding new ones.
- Do not build orchestration infrastructure in this repo.
- Prefer existing domain skills over inventing new coordination logic.
- Feature execution does not require Spec Kit or OpenSpec command phases.
- `coding-autonomous-execute` is an automatic bounded escalation path, not a repo-local orchestrator.

## Handoff
- Include `Skills used:` with every skill actually loaded or followed.
- Include red evidence and green evidence, or why red/green could not run.
- Include required checks, evaluator result, queue status when updated, and concrete blockers.
