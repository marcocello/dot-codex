## dot-codex

## Objective
Keep Codex App predictable while letting it work autonomously through a feature set.

This repo is a Codex harness: it defines the context, contracts, feedback loops, and repair rules around the model. It does not add a hidden workflow engine.

## Harness Model

```text
Idea or change request
  -> FEATURE.md
  -> PROOF.md + executable proof tests
  -> status.json queue entry
  -> Codex Goal / autonomous runtime
  -> one-feature implementation
  -> primary proof
  -> gate
  -> read-only done evaluator
  -> bounded repair loop
  -> queue progress update
  -> next feature
```

The core rule is simple: Codex works on one feature at a time, proves it, gets judged, repairs bounded failures, marks progress, then moves to the next feature.

A Codex Goal is the thread-scoped runtime driver for autonomous runs. It keeps the current thread working toward an auditable finish line. It does not replace the repo files: `FEATURE.md` still defines behavior, `PROOF.md` defines completion evidence, and `docs/features/status.json` still tracks durable progress.

## Lifecycle
1. Feature/spec phase
   - `coding-feature-spec` writes or refines `FEATURE.md`.
   - For non-trivial features it invokes `coding-proof-author`.
   - `coding-proof-author` writes `PROOF.md` and executable proof artifacts.
   - `coding-feature-queue` records the feature in `docs/features/status.json` when a queue exists.
2. Execution phase
   - `coding-autonomous-execute` uses a Goal to select pending/failing queue items.
   - `coding-feature-execute` implements exactly one `FEATURE_DIR`.
3. Evidence phase
   - `coding-feature-execute` runs the primary proof command from `PROOF.md`.
   - `coding-feature-execute` runs `$HOME/.codex/scripts/gate`.
4. Judgment phase
   - `coding-feature-evaluator` is the read-only done judge.
   - It reads `FEATURE.md`, `PROOF.md`, changed files, proof output, and gate output.
   - It returns `PASS`, `FAIL`, or `BLOCKED`.
5. Queue phase
   - `coding-feature-queue` marks the item `passing`, `failing`, or `blocked`.

The proof command executes evidence. The gate protects repo health. The evaluator judges whether the evidence and implementation are enough. The Goal only keeps runtime moving.

## Workflow

The manual entry point for one ready feature is still:

```text
codex "Use the coding-feature-execute skill for docs/features/<feature-id>"
```

For autonomous multi-feature work, create or update the queue first, then run `coding-autonomous-execute`.

The `docs/features/*` artifacts are created in the target software repository that Codex is building or maintaining. This `dot-codex` repository supplies the reusable operating contract, skills, and scripts.

## Core Artifacts
- `AGENTS.md`: global engineering discipline and safety rules.
- `docs/APP.md`: overall product context when present.
- `docs/ARCHITECTURE.md`: authoritative architecture when present.
- `docs/features/<feature-id>/FEATURE.md`: behavior source of truth for one feature.
- `docs/features/<feature-id>/PROOF.md`: definition of done and primary proof command.
- `docs/features/status.json`: machine-readable queue and progress tracker.
- `/goal`: thread-scoped runtime objective for long-running autonomous work.
- `$HOME/.codex/scripts/gate`: repo-level deterministic check.

`FEATURE.md` remains the behavior contract. `PROOF.md` is the completion contract. `status.json` only tracks progress.

## Roles
### Coding Harness
- `coding-app-to-features`: greenfield planner. Turns an app idea into app docs, feature specs, proof packages, and a feature queue.
- `coding-feature-spec`: brownfield or single-feature planner. Creates/refines `FEATURE.md`, invokes proof authoring for non-trivial features, and updates the queue.
- `coding-proof-author`: creates/refines `PROOF.md` and executable proof artifacts.
- `coding-feature-quality`: pre-implementation review for ambiguity, missing edge cases, proof gaps, testability gaps, and architecture conflicts.
- `coding-feature-queue`: maintains `docs/features/status.json` and selects the next pending/failing feature.
- `coding-feature-execute`: implements one feature with red/green proof and deterministic validation.
- `coding-fix-issue`: fixes a clear defect with regression coverage.
- `coding-feature-evaluator`: read-only done judge for features and bug fixes. Returns `PASS`, `FAIL`, or `BLOCKED`.
- `coding-auto-improve`: repairs the smallest failing check.
- `coding-autonomous-execute`: turns queue or repair work into a bounded Codex Goal. It is not cron, a scheduler, or a daemon.
- `coding-prepare-environment`: central setup policy for Python, Node, PHP, Laravel, WordPress, `.env`, dependency installs, command prefixes, and VS Code fullstack run tasks.
- `coding-commit`: stages selected paths and creates local Conventional Commits when explicitly requested.

### Domain Coding Skills
- `coding-python-backend`: backend API/application work, including greenfield backend structure.
- `coding-frontend`: React/Next.js frontend work, including greenfield frontend structure.
- `coding-wordpress`: WordPress plugin, theme, full-site, and Bedrock-style implementation.
- `coding-laravel-feature-builder`: Laravel feature implementation and tests.
- `coding-php-legacy-maintainer`: plain PHP or framework-light PHP maintenance.
- `coding-operational-issue-diagnostics`: read-only local/cloud runtime diagnostics.
- `coding-critical-secret-audit`: GitGuardian-backed current-checkout secret audit.
- `coding-maintainability-review`, `coding-architecture-deep-dive`, and `coding-compare-architectures`: review and decision-support skills. They are useful but not part of the default autonomous feature loop.

### Non-Coding Skills
- `research`: bounded external evidence for planning.
- `prospecting-*`: GTM signal context, detection, and LinkedIn content workflows.
- `capture-note`, `casual-message-rewriter`, `codex-session-showcase`, `no-bullshit-technical-writing`, and `html-presentations`: personal productivity, writing, and presentation workflows. They should not be invoked for software feature execution unless the user explicitly asks for that output.

## Repair Routing
- Use `coding-fix-issue` when the entry point is a user-reported bug or broken behavior.
- Use `coding-auto-improve` when the entry point is a concrete failing check or evaluator `FAIL`.
- Use `coding-autonomous-execute` when repeated bounded repair or queue completion needs a Codex Goal.

## Greenfield Workflow
1. Describe the app.
2. Use `coding-app-to-features`.
3. Review the generated `docs/APP.md`, `docs/ARCHITECTURE.md`, feature specs, and `docs/features/status.json`.
4. Use `coding-autonomous-execute` to execute the queue.
5. Codex repeatedly:
   - selects one feature with `coding-feature-queue`
   - ensures `PROOF.md` and executable proof exist
   - implements with `coding-feature-execute`
   - runs the primary proof command and gate
   - judges with `coding-feature-evaluator`
   - repairs bounded failures with `coding-auto-improve` or `coding-fix-issue`
   - marks the queue item `passing`, `failing`, or `blocked`
6. The run is complete when all features are `passing` or the remaining items are `blocked`.

## Brownfield Workflow
1. Describe one or more changes.
2. Use `coding-feature-spec` to create or refine one `FEATURE.md` per coherent behavior change and invoke `coding-proof-author` for executable proof.
3. Use `coding-feature-queue` to add those features to `docs/features/status.json`.
4. Use `coding-autonomous-execute` for the same execution path as greenfield.

Brownfield and greenfield intentionally converge after feature creation.

For either path, the autonomous form is:

```text
Use coding-autonomous-execute to set a Codex Goal for the queue, then keep executing one FEATURE_DIR at a time until all items are passing or the remaining items are blocked with concrete reasons.
```

## Autonomy Boundaries
- No in-repo orchestrator, daemon, or scheduler.
- No cron or Codex App automation unless the user explicitly asks for recurring or unattended execution.
- A Codex Goal is runtime thread state, not global memory and not repo state.
- One feature is implemented at a time.
- Repair loops are bounded to three iterations by default.
- `coding-feature-evaluator` is read-only and never fixes its own findings.
- Do not mark work done until deterministic checks and evaluator judgment pass.

## Checks
For target app repos:
- Always run `$HOME/.codex/scripts/gate`.
- Run the primary proof command defined in `FEATURE_DIR/PROOF.md` when a feature is in scope.

When editing this `dot-codex` config repo itself, do not run gate or feature proof commands unless the user explicitly asks.

## Completion Output
Completed feature and bugfix handoffs should separate evidence from judgment:

```text
Primary proof:
- Red: <failed or unmet before implementation>
- Green: <primary proof command> -> PASS

Safety checks:
- Gate: PASS

Evaluator:
- PASS

Queue:
- <feature-id> -> passing
```

Do not report gate, evaluator, or secondary checks as proof. Do not include full passing gate/test counts unless the user asks.
