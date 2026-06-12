## dot-codex

## Objective
Keep Codex App predictable while letting it work autonomously through a feature set.

This repo is a Codex harness: it defines the context, contracts, feedback loops, and repair rules
around the model. It does not add a hidden workflow engine.

## Harness Model

```text
Idea or change request
  -> Codex Goal for autonomous runtime
  -> feature contracts
  -> feature queue
  -> one-feature implementation
  -> deterministic checks
  -> read-only evaluator
  -> bounded repair loop
  -> queue progress update
  -> next feature
```

The core rule is simple: Codex works on one feature at a time, proves it, gets judged, repairs
bounded failures, marks progress, then moves to the next feature.

A Codex Goal is the thread-scoped completion contract for autonomous runs. It keeps the current
thread working toward an auditable finish line. It does not replace the repo files: `FEATURE.md`
still defines behavior, and `docs/features/status.json` still tracks durable progress.

## Workflow

The manual entry point for one ready feature is still:

```text
codex "Use the feature-execute skill for docs/features/<feature-id>"
```

For autonomous multi-feature work, create or update the queue first, then run `autopilot-loop`.

## Core Artifacts
- `AGENTS.md`: global engineering discipline and safety rules.
- `docs/APP.md`: overall product context when present.
- `docs/ARCHITECTURE.md`: authoritative architecture when present.
- `docs/features/<feature-id>/FEATURE.md`: behavior source of truth for one feature.
- `docs/features/status.json`: machine-readable queue and progress tracker.
- `/goal`: thread-scoped runtime objective for long-running autonomous work.
- `$HOME/.codex/scripts/gate`: repo-level deterministic check.
- `$HOME/.codex/scripts/acceptance --feature <FEATURE_DIR>`: feature acceptance check.

`FEATURE.md` remains the behavior contract. `status.json` only tracks progress.

## Roles
- `app-to-features`: greenfield planner. Turns an app idea into app docs, feature specs, and a
  feature queue.
- `feature`: brownfield or single-feature planner. Creates/refines `FEATURE.md` and updates the
  queue.
- `feature-queue`: maintains `docs/features/status.json` and selects the next pending/failing
  feature.
- `acceptance-author`: creates or repairs executable feature acceptance checks.
- `feature-execute`: implements one feature with red/green TDD and deterministic validation.
- `fix-issue`: fixes a clear defect with regression coverage.
- `feature-evaluator`: read-only skeptical judge. Returns `PASS`, `FAIL`, or `BLOCKED`.
- `auto-improve`: repairs the smallest failing check.
- `autopilot-loop`: turns queue or repair work into a bounded Codex Goal plus loop discipline. It
  is not cron and not a daemon.

## Greenfield Workflow
1. Describe the app.
2. Use `app-to-features`.
3. Review the generated `docs/APP.md`, `docs/ARCHITECTURE.md`, feature specs, and
   `docs/features/status.json`.
4. Use `autopilot-loop` to execute the queue.
5. Codex repeatedly:
   - selects one feature with `feature-queue`
   - ensures acceptance exists
   - implements with `feature-execute`
   - runs gate and feature acceptance
   - judges with `feature-evaluator`
   - repairs bounded failures with `auto-improve` or `fix-issue`
   - marks the queue item `passing`, `failing`, or `blocked`
6. The run is complete when all features are `passing` or the remaining items are `blocked`.

## Brownfield Workflow
1. Describe one or more changes.
2. Use `feature` to create or refine one `FEATURE.md` per coherent behavior change.
3. Use `feature-queue` to add those features to `docs/features/status.json`.
4. Use `autopilot-loop` for the same execution path as greenfield.

Brownfield and greenfield intentionally converge after feature creation.

For either path, the autonomous form is:

```text
Use autopilot-loop to set a Codex Goal for the queue, then keep executing one FEATURE_DIR at a
time until all items are passing or the remaining items are blocked with concrete reasons.
```

## Autonomy Boundaries
- No in-repo orchestrator, daemon, or scheduler.
- No cron or Codex App automation unless the user explicitly asks for recurring or unattended
  execution.
- A Codex Goal is runtime thread state, not global memory and not repo state.
- One feature is implemented at a time.
- Repair loops are bounded to three iterations by default.
- `feature-evaluator` is read-only and never fixes its own findings.
- Do not mark work done until deterministic checks and evaluator judgment pass.

## Checks
For target app repos:
- Always run `$HOME/.codex/scripts/gate`.
- Run `$HOME/.codex/scripts/acceptance --feature <FEATURE_DIR>` when a feature is in scope.

When editing this `dot-codex` config repo itself, do not run gate or feature acceptance unless the
user explicitly asks.
