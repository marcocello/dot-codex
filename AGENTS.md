# AGENTS.md — Marco Dev Operating Contract

## Purpose
- AGENTS.md gives Codex the repo-wide operating contract: what to optimize for, where to route
  work, and when work is allowed to be called complete.
- Skills own detailed procedures, stack-specific choices, examples, scripts, and reference repos.
- Repo docs own durable project context when present: `docs/APP.md`, `docs/ARCHITECTURE.md`,
  `docs/CONVENTIONS.md`, and `docs/TESTING.md`.
- Do not copy full skill workflows into this file.

## Working Model
- Work one feature or issue at a time.
- For feature work, use one `FEATURE_DIR` at a time.
- Source of truth: `FEATURE_DIR/FEATURE.md`.
- FEATURE.md remains the behavior source of truth.
- If `FEATURE_DIR` is missing:
  - inspect `docs/features/*/FEATURE.md` for one clear match;
  - use that match when exactly one is clear;
  - otherwise create `docs/features/<request-slug>/FEATURE.md`;
  - ask only when multiple plausible matches would materially change scope.
- Exception: `coding-app-to-features` may bootstrap `docs/APP.md`,
  `docs/ARCHITECTURE.md`, multiple feature specs, and `docs/features/status.json`; after that,
  return to one `FEATURE_DIR` at a time.

## Autonomous Work
- `docs/features/status.json` is only a durable progress queue.
- Use `coding-feature-queue` to add, select, and update queue items.
- Use a Codex Goal only for explicit autonomous execution, queue completion, or
  "keep going until done" work.
- A Goal is runtime state. It does not replace `FEATURE.md`, `status.json`, checks, acceptance, or
  evaluator judgment.
- Do not mark a Goal or queue item complete because the implementation looks plausible.
- Completion requires gate, feature acceptance when in scope, `coding-feature-evaluator`, and queue
  progress evidence when a queue exists.
- If `coding-feature-evaluator` returns `FAIL`, repair through `coding-auto-improve`,
  `coding-fix-issue`, or `coding-autonomous-execute`.
- If `coding-feature-evaluator` returns `BLOCKED`, keep the item blocked and report the concrete
  blocker.

## Project Context
- If `docs/ARCHITECTURE.md` exists, treat it as authoritative and apply it.
- Do not override project architecture unless explicitly asked.
- Read only the current repo's architecture document.
- Keep implementation behavior aligned with `docs/APP.md`, `docs/CONVENTIONS.md`, and
  `docs/TESTING.md` when those files exist.
- For software project bootstrap or feature execution, make sure the project has a Git repository
  and use `coding-prepare-environment` to create VS Code run tasks when needed.

## Default Greenfield Architecture
When bootstrapping a greenfield application and no repo architecture overrides it:
- Use stack/domain skills before creating application folders or choosing starters.
- Prefer a React frontend that talks to backend APIs unless the user, repo docs, or selected stack
  skill points to a different architecture.
- Delegate backend framework, service layering, API details, and backend tree structure to the
  `coding-python-backend` skill.
- Delegate frontend starter, component system, UI baseline choices, and frontend tree structure to
  the `coding-frontend` skill.
- Delegate WordPress plugin, theme, full-site, and Bedrock-style tree structure to the
  `coding-wordpress` skill when WordPress is in scope.
- Keep repo-level docs focused on architecture decisions; do not define application folder
  structure outside the owning stack/domain skill.

## Skill Routing
- Use `coding-feature-spec` to create or refine `FEATURE.md`.
- Use `coding-feature-quality` before non-trivial implementation when `FEATURE.md` has ambiguity,
  missing edge cases, weak testability, or possible architecture conflicts.
- Use `coding-feature-execute` to implement a ready feature.
- Use `coding-fix-issue` for a clear reported defect or runtime bug that needs reproduction and a
  regression test.
- Use `coding-auto-improve` for a known failing command, gate, acceptance check, typecheck, lint
  result, or evaluator `FAIL`.
- Use `coding-autonomous-execute` for queue completion or repeated bounded repair.
- Use `coding-acceptance-author` when acceptance coverage is missing or weak.
- Use `coding-feature-evaluator` before marking feature or issue work complete.
- Use `coding-prepare-environment` for local setup, dependencies, `.env`, command prefixes,
  stack-specific preparation, and `.vscode/tasks.json`.
- Use `coding-commit` when the user asks to stage, commit, or draft a commit message.
- Use stack/domain skills for folder structure and implementation details instead of copying those
  rules here.
- Use reference repos only when the matching skill is active and the current repo lacks a pattern;
  state the repo and pattern reused in one line.

## Implementation Discipline
- Reuse existing code first.
- Make the smallest change that satisfies the feature or issue.
- Keep changes local; avoid unrelated refactors.
- Avoid backward compatibility work unless explicitly requested.
- Prefer explicit code over cleverness.
- Use red/green TDD for implementation and bug fixes.
- Do not delete, weaken, or bypass tests to get green.

## Verification
- Target app repo gate: `$HOME/.codex/scripts/gate`.
- Feature acceptance: `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`.
- When editing this `dot-codex` config repo itself, do not run repo gate or feature acceptance
  unless explicitly asked.
- Do not claim done unless required checks pass or a concrete blocker is reported.

## Hard Limits
- ≤100 lines per function.
- Cyclomatic complexity ≤8 where tooling exists.
- ≤5 positional parameters.
- 100-character line width unless project tooling is stricter.
- If a limit would make the design worse, state the reason and keep scope tight.

## Zero-Warning Standard
- Treat warnings as defects in touched scope.
- Fix warnings from linters, type checkers, compilers, and test runners.
- If a warning must remain, add a local ignore with a one-line justification.

## Review Order
- Review in this order: architecture → code quality → tests → performance.
- For findings, include concrete impact and file:line references.

## Dependency Hygiene
- When adding or upgrading dependencies, use current stable versions and pin explicitly unless
  ecosystem conventions prevent it.
- Run stack-appropriate dependency/security audits when dependencies change.
- Do not add dependencies when existing stdlib or repo patterns are sufficient.

## Secret-Bearing Deployment Files
- Preserve existing secret values when editing deployment YAML, Kubernetes manifests, Helm values,
  Kustomize overlays, `.env` files, and CI/CD deployment files.
- Do not replace them with placeholders such as `secret`, `REDACTED`, or `<secret>`.
- Do not print raw secrets in responses, logs, or summaries.

## Safety
- Do not force push, deploy, or run destructive commands unless explicitly requested and approved.

## Handoff
For completed feature or issue work, report:
- `Skills used:` with every skill actually loaded or followed;
- red evidence and green evidence, or why red/green could not run;
- required checks and evaluator result when used;
- queue status when updated;
- concrete blockers, if any.

## Output Token
- If blocked: `NEED_INPUT: <question>` or `BLOCKED: <reason>`.
