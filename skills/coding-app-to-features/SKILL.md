---
name: coding-app-to-features
description: "Turn one app idea into decided context, feature contracts, executable proofs, and a prioritized queue."
---

# App To Features

Purpose: shape an app with the user, create only the repository context that will guide implementation, and materialize a small sequence of independently valuable, realistically provable features.

This skill prepares work. It does not implement the application.

## Inputs
- Raw app idea or problem statement.
- Target users and core job.
- Desired first useful outcome.
- Constraints, non-goals, compliance, data, external services.
- Stack or architecture preferences when the user has them.
- Existing repository, prototype, research, or reference product when present.

Derive facts from the repository and authoritative sources before asking. Ask grouped questions that materially change the product shape, architecture boundary, data ownership, external contract, or first vertical slice.

## App Discovery
1. Clarify who uses the product, what triggers use, and what complete outcome matters.
2. Challenge scope: empty state, permissions, errors, data lifecycle, recovery, multi-user behavior, external effects, and explicit exclusions.
3. Distinguish product requirements from speculative implementation preferences.
4. Show the proposed app shape, assumptions, architecture boundary, and major non-goals.
5. Ask for material missing input once, then show the decided app shape and write authoritative context without a separate approval request. Pause only when an unresolved user-owned choice cannot be inferred safely.

Use `coding-research` when external APIs, framework limits, provider contracts, domain rules, or current product facts would otherwise be guessed.

## Workflow
1. Inspect repository baseline
   - Detect existing Git, stack, docs, code, package/runtime conventions, and architecture.
   - Initialize Git only for a genuinely new project without history.
   - Use `coding-prepare-environment` for repo-local runtimes/tasks when requested work needs them.

2. Write app context
   - Create or update `docs/APP.md` with user, problem, outcome, scope, and non-goals.
   - Create `docs/ARCHITECTURE.md` only when architecture is accepted or sufficiently authoritative to guide features.
   - Create `docs/CONVENTIONS.md` and `docs/TESTING.md` only when they prevent repeated decisions.
   - Do not impose a default stack, folder tree, architecture, feature count, or compatibility policy.

3. Derive vertical features
   - Prefer end-to-end user value over foundation-only slices.
   - Create the smallest sequence that makes the app implementable and useful.
   - Each feature must have one coherent user/system outcome and one provable boundary.
   - Merge overlapping ideas; leave speculative roadmap items out.
   - Order by dependencies and value, not a universal backend/frontend/data sequence.

4. Decide each selected feature
   - Use `coding-feature-spec` for focused feature questions, challenge, and a visible decision summary.
   - Use `coding-proof-author` for focused proof questions, boundary challenge, and a visible decision summary.
   - Do not create all artifacts from one unexplained bulk interpretation.
   - A feature package is materialized only when decision-complete `FEATURE.md`, decision-complete `PROOF.md`, and executable `proof/run.sh` exist.

5. Create queue
   - Use `coding-feature-queue` to create/update `docs/features/status.json`.
   - `ready`: complete decision-ready package.
   - `draft`: discovery/proof/artifacts incomplete.
   - `blocked`: exact external/user dependency after recovery.
   - Preserve numeric priority and realistic `files` prefixes.

6. Return to single-feature work
   - After preparation, select one ready item.
   - Hand implementation to `coding-feature-execute`.
   - Do not build an in-repo orchestrator or start implementing multiple features concurrently.

## App Documents
Keep documents small and authoritative:

- `docs/APP.md`: product intent, users, outcomes, scope, non-goals.
- `docs/ARCHITECTURE.md`: accepted components, boundaries, data flow, external dependencies, constraints.
- `docs/CONVENTIONS.md`: decisions likely to recur across features.
- `docs/TESTING.md`: repository-native test/proof/gate guidance.

Omit a document when it would contain only generic advice.

## Feature Quality
- Observable behavior, not component inventory.
- Material edge/error/recovery cases.
- Explicit external contract where needed.
- Realistic proof boundary available.
- Small enough for one parent/feature lifecycle.
- No duplicate owner with another feature.
- No hidden architecture commitment that the user did not accept.

## Rules
- User input shapes app and proof; the agent records decisions and proceeds without contract-approval gates.
- No default stack, count, tree, or foundation-first sequence.
- No speculative backlog.
- No prose-only proof package for non-trivial behavior.
- No local workflow engine, daemon, or planning router.
- Stack/domain skills own concrete implementation structure.
- App preparation ends by returning to one `FEATURE_DIR`.

## Handoff
Report the decided app shape, created/updated context docs, feature ids in recommended order, queue path/status summary, first ready item, and material unresolved input. Do not dump every proof file or start implementation unless asked.
