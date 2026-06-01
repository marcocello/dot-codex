# AGENTS.md — Marco Dev Discipline (Feature-Driven)

## Feature Path
- Work is driven by a single feature directory: `FEATURE_DIR`.
- The user or orchestrator provides `FEATURE_DIR` (e.g. `docs/features/todo-api`).
- Source of truth: `FEATURE_DIR/FEATURE.md`
- If `FEATURE_DIR` is not explicitly provided, resolve it autonomously:
  - First inspect `docs/features/*/FEATURE.md` for a clear match to the user's request.
  - If exactly one existing feature clearly matches, use that directory as `FEATURE_DIR`.
  - If no existing feature clearly matches, create `docs/features/<request-slug>/FEATURE.md`
    from the request and use that new directory as `FEATURE_DIR`.
  - Ask for input only when multiple existing feature directories plausibly match and choosing one
    would materially change scope, or when the repository cannot be inspected/updated.
- Exception: when `app-to-features` is explicitly used for greenfield bootstrap, it may create
  `docs/APP.md`, optionally `docs/ARCHITECTURE.md`, and multiple `docs/features/<slug>/FEATURE.md`
  files. After that bootstrap step, return to the normal single-`FEATURE_DIR` workflow.

## Project Architecture (Optional)
If the current repository contains `docs/ARCHITECTURE.md`:
- Treat it as authoritative project architecture.
- Apply its constraints (module layout, boundaries, integration rules).
- Do not quote it; apply it.
- Do not override it unless explicitly asked.
- Only read `docs/ARCHITECTURE.md` if it exists in the current repo.
- Do not search other repos for architecture documents.

## Default Greenfield Architecture
When bootstrapping a greenfield application and no repository architecture overrides it:
- Use a React frontend.
- The frontend talks to the backend through APIs; do not couple frontend code to backend
  internals.
- The repo root contains `backend/`, `frontend/`, and `docs/`.
- Inside `backend/`, use `app/`, `deployment/`, and `pipelines/`, yielding `backend/app`,
  `backend/deployment`, and `backend/pipelines`.
- Inside `frontend/`, use `app/`, `deployment/`, and `pipelines/`, yielding `frontend/app`,
  `frontend/deployment`, and `frontend/pipelines`.
- Delegate backend framework, service layering, and API implementation details to the
  python-backend skill.
- Delegate frontend starter, component system, and UI baseline choices to the frontend skill.

## Living Documentation
- Keep `FEATURE_DIR/FEATURE.md` updated whenever implemented behavior changes or expands during the conversation.
- If an implementation introduces an architectural change, update `docs/ARCHITECTURE.md` in the same change.
- If an architectural change occurs and `docs/ARCHITECTURE.md` does not exist yet, create it with the new baseline architecture.

## Scope
- REUSE FIRST: search and extend existing code; don’t duplicate logic.
- Smallest change that satisfies the feature.
- Keep changes local; no refactors unless required.
- AVOID backward compatibility by default; only preserve it when explicitly requested.

## Quality
- Correctness > clarity > consistency > DRY
- Prefer explicit code over cleverness.

## Hard Limits
- Target limits for newly written or modified code:
  - ≤100 lines per function.
  - Cyclomatic complexity ≤8 where tooling exists.
  - ≤5 positional parameters.
  - 100-character line width unless project tooling is stricter.
- If a limit cannot be met without worse design, state the reason and keep scope tight.

## Zero-Warning Standard
- Treat warnings as defects in touched scope.
- Fix warnings from linters, type checkers, compilers, and test runners.
- If a warning must remain, add a local ignore with a one-line justification.

## Review Order
- Review in this order: architecture → code quality → tests → performance.
- For findings, include concrete impact and file:line references.

## Dependency Hygiene
- When adding or upgrading dependencies, use current stable versions and pin explicitly unless ecosystem conventions prevent it.
- Run stack-appropriate dependency/security audits when dependencies change.
- Do not add dependencies when existing stdlib or current repo patterns are sufficient.

## Red/Green TDD (mandatory)
- Use red/green TDD for implementation and bug fixes.
- Red phase:
  - Add or update the smallest test that captures the required behavior/regression.
  - Run that test (or the narrowest relevant test command) and confirm it fails.
- Green phase:
  - Implement the smallest effective code change.
  - Re-run the same test and confirm it passes.
- Then run broader checks (`$HOME/.codex/scripts/gate` and feature acceptance when applicable).
- In handoff, state red evidence (failing test command/result) and green evidence (passing command/result).
- If red/green cannot be executed, state exactly why.

## Deterministic checks (authoritative)
- Repo gate: `$HOME/.codex/scripts/gate`
- Feature acceptance: `$HOME/.codex/scripts/acceptance --feature FEATURE_DIR`
- Exception: when working inside the `dot-codex` configuration repo itself, do not run repo gate
  or feature acceptance unless the user explicitly asks for those commands.
- Required checks for target app repos:
  - Always run repo gate.
  - Run feature acceptance when a concrete `FEATURE_DIR` is in scope.
- Do not claim done unless all required checks pass.

## Tests (required)
- Add/extend repo tests that are run by the gate (pytest/unit/integration as appropriate).
- Place repo-level tests under `tests/` (for example `tests/unit/` or `tests/integration/`).
- If acceptance tests are missing, use `prompts/acceptance.md` to derive and generate them from `FEATURE.md`.
- Acceptance tests must exercise public system boundaries instead of implementation internals:
  - API features must call real HTTP endpoints with a normal HTTP client.
  - Non-API backend behavior must be triggered through public commands, workers, scheduled jobs,
    files, queues, or equivalent external boundaries.
  - Do not import application internals from `app`, `backend`, `src`, `server`, or `api`.
  - Do not use mocks, monkeypatching, in-process route clients, or direct function calls for
    feature acceptance.
- BDD-first scenario authoring:
  - Treat `FEATURE.md` scenarios as the canonical behavior contract.
  - Write scenarios in valid Gherkin with `Feature`, `Scenario`/`Scenario Outline`, `Given`, `When`, `Then` (and `And`/`But` when needed).
  - Keep step wording black-box and domain-focused (no implementation details).
  - Cover at least one happy path and the key edge/error paths.
- Acceptance harness:
  - If `FEATURE_DIR/acceptance/` is missing, create it.
  - Place feature-scoped executable checks under `FEATURE_DIR/acceptance/tests/` (or `FEATURE_DIR/acceptance/run.sh`).
  - Translate behavior described in `FEATURE_DIR/FEATURE.md` into executable checks.
  - Use scenarios described in `FEATURE.md` (including Gherkin blocks) as authoritative behavior.
  - Preserve scenario IDs/titles in test names/markers/comments for traceability.
  - Prefer `FEATURE_DIR/acceptance/tests/` (pytest) or `FEATURE_DIR/acceptance/run.sh`.
- For spec-driven acceptance refinement outputs:
  - Keep `FEATURE.md` as the source-of-truth feature document.
  - Keep `FEATURE.md` concise and behavior-first.
  - Prefer no separate `## Description` section.
  - Use Gherkin scenarios as the default BDD artifact for feature behavior.
  - Include at least one happy-path scenario and key edge/error scenarios.
  - Put Gherkin scenarios in `FEATURE.md` (not in `FEATURE_DIR/acceptance/features/`).
  - Keep `FEATURE_DIR/acceptance/` for executable test code only.
- No cheating:
  - Don’t delete/loosen tests to get green.
  - Tests must contain real assertions.

## Environment preparation
- Use `skills/prepare-environment` as the single source of truth for stack setup.
- Delegate Python, React/Node, PHP, Laravel, WordPress, `.env`, dependency install,
  and command-prefix decisions to that skill instead of duplicating setup rules here.

## References (skill-scoped)
- Reference repos are defined inside skills (Python backend, frontend, infra).
- Use reference repos only when the matching skill is active and current repo lacks a pattern.
- If you use one, state which repo and what pattern you reused (1 line).

## Commit Messages
- When asked to generate a commit message, read the actual changes first:
  - Prefer `git diff --staged` for staged commits.
  - Use `git diff` as well when unstaged changes are part of the requested scope.
  - Include untracked files only when the user asks to include them or they are clearly part of
    the change.
- Use a best-practice Conventional Commits format:
  - Subject: `<type>(<scope>): <imperative summary>`
  - Keep the subject concise, specific, and under 72 characters when practical.
  - Use `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`, or `revert`.
  - Add a body when it helps reviewers understand what changed and why.
  - Add footers for breaking changes, issue references, or migration notes.
- Prefer accurate, change-specific wording over generic summaries.
- Do not invent intent, issue numbers, or external context not present in the diff or user request.

## Output token
- If blocked: `NEED_INPUT: <question>` or `BLOCKED: <reason>`
