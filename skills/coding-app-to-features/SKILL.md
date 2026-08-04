---
name: coding-app-to-features
description: "Turn one app idea into decided context, feature contracts, executable proofs, and a prioritized queue."
---

# App To Features

Purpose: shape an app with the user, create only the repository context that will guide implementation, and materialize the complete non-speculative feature set as independently valuable, realistically provable packages.

This skill prepares app context and feature packages. Route from the requested deliverable, not an isolated verb: when the requested outcome is an implemented app or product behavior, preparation is a phase before the first ready feature enters implementation in the same parent run. When the requested deliverable is app planning, feature contracts, or proof contracts, stop after preparation even if the user said to write, create, or define those artifacts.

Replies to discovery or proof questions preserve the original request scope and do not authorize implementation. Contract-authoring work must not invoke `coding-feature-execute`; implementing the described product behavior requires a separate explicit request.

Planning or specification-only requests stop after preparation.

## Inputs
- Raw app idea or problem statement.
- Target users and core job.
- Desired first useful outcome.
- Constraints, non-goals, compliance, data, external services.
- Stack or architecture preferences when the user has them.
- Existing repository, prototype, research, or reference product when present.

Derive facts from the repository and authoritative sources before asking. Infer and state safe defaults for unresolved smaller or reversible choices. Ask only when a remaining user-owned choice has no safe default and can materially change the product shape, data ownership, permissions, safety, cost, external effects, or first useful slice.

## App Discovery
1. Clarify who uses the product, what triggers use, and what complete outcome matters.
2. Challenge scope: empty state, permissions, errors, data lifecycle, recovery, multi-user behavior, external effects, and explicit exclusions.
3. Distinguish product requirements from speculative implementation preferences.
4. Show the proposed app shape, assumptions, architecture boundary, and major non-goals.
5. Ask for material missing input once only when no safe default exists, then show the decided app shape and write authoritative context without a separate approval request. Otherwise state the inferred defaults and proceed.

Use `coding-research` when external APIs, framework limits, provider contracts, domain rules, or current product facts would otherwise be guessed.

## Greenfield Defaults
When the repository has no established product or architecture and the requested deliverable is an implemented app or product behavior:

- Use the smallest local-first, single-user application shape that satisfies the request unless the request implies accounts, collaboration, cloud ownership, compliance, or another materially different product boundary.
- For a generic web application, use a React frontend. Add a backend API boundary when server-owned secrets, provider calls, or persistence require one.
- Leave authentication, cloud sync, paid deployment, and live external mutations out of the initial slice unless the requested outcome requires them.
- For an AI capability with no named provider, use an OpenAI adapter behind a provider boundary, keep credentials server-side, and use a deterministic fake only at the outer provider boundary for proof. Missing live credentials or optional live spend does not block app preparation.
- Prefer the safest reversible product behavior that preserves the requested capability, and label it as an inferred default.
- Explicit user or repository constraints override inferred defaults.
- State the inferred profile in the app decision summary and proceed without turning it into an approval question.

## Workflow
1. Inspect repository baseline
   - Detect existing Git, stack, docs, code, package/runtime conventions, and architecture.
   - Initialize Git only for a genuinely new project without history.
   - Use `coding-prepare-environment` for repo-local runtimes/tasks when requested work needs them.

2. Write app context
   - Create or update `docs/APP.md` with user, problem, outcome, scope, and non-goals.
   - Create `docs/ARCHITECTURE.md` when architecture is explicit, authoritative, or selected through the greenfield defaults above.
   - Create `docs/CONVENTIONS.md` and `docs/TESTING.md` only when they prevent repeated decisions.
   - Keep these files concise maps of current authority. Move superseded history outside default context and load it only for a migration that needs it.
   - Record high-level components, boundaries, data flow, external dependencies, and useful proof/testing guidance without copying concrete starters, folder trees, or implementation structure from the owning stack/domain skills.

3. Derive vertical features
   - Prefer end-to-end user value over foundation-only slices.
   - Create the complete non-speculative sequence required for the accepted app outcome.
   - Keep each feature lean: one coherent observable outcome for a user or system and one provable boundary.
   - Before a feature becomes `ready`, reject a package with multiple independently valuable observable outcomes or independently runnable proof boundaries and split it into separate feature packages. Touching multiple files or layers alone does not make a feature oversized; do not split one outcome into component-only tasks.
   - Merge overlapping ideas; leave speculative roadmap items out.
   - Order by dependencies and value, not a universal backend/frontend/data sequence.

4. Decide every current feature
   - Use `coding-feature-spec`, which invokes `coding-proof-author`, for every feature in the accepted sequence.
   - Every decided feature receives `FEATURE.md`, `PROOF.md`, and executable `proof/run.sh`; do not replace the normal feature and proof decisions with bulk prose generated only by this skill.
   - Ask only for unresolved material choices with no safe default, and do not create all artifacts from one unexplained bulk interpretation.
   - A decision-ready feature package exists only when `FEATURE.md`, `PROOF.md`, and executable `proof/run.sh` are complete.

5. Create queue
   - Use `coding-feature-queue` to create/update `docs/features/status.json`.
   - `ready`: complete decision-ready package; every decided feature from app preparation should finish here.
   - `draft`: a genuinely incomplete or newly discovered feature whose discovery, proof decisions, or artifacts are not complete.
   - `blocked`: exact external/user dependency after recovery.
   - Preserve numeric priority; do not add file-overlap or dependency fields.

6. Return to implementation
   - When the original request explicitly asked to build, implement, or execute one feature, invoke `coding-feature-execute` for that ready item in the same parent run.
   - When it asked to implement the multi-feature app, invoke `coding-autonomous-execute`; it completes ready features serially in priority order.
   - When the requested deliverable is planning or contract artifacts, stop after preparation and report the complete ready feature set. Do not reinterpret answers to discovery questions as implementation authorization.
   - Do not build an in-repo orchestrator, dependency graph, worktree manager, or branch manager.

## App Documents
Keep documents small and authoritative:

- `docs/APP.md`: product intent, users, outcomes, scope, non-goals.
- `docs/ARCHITECTURE.md`: accepted components, boundaries, data flow, external dependencies, constraints.
- `docs/CONVENTIONS.md`: decisions likely to recur across features.
- `docs/TESTING.md`: project test and proof guidance that prevents repeated decisions.

Omit a document when it would contain only generic advice.

## Feature Quality
- Observable behavior, not component inventory.
- Material edge/error/recovery cases.
- Explicit external contract where needed.
- Realistic proof boundary available.
- Small enough for one parent/feature lifecycle.
- No duplicate owner with another feature.
- No hidden architecture commitment: label inferred defaults and preserve explicit overrides.

## Rules
- User input shapes app and proof; the agent records decisions and proceeds without contract-approval gates.
- No universal folder tree, feature count, or foundation-first sequence; select the smallest applicable greenfield profile and leave concrete structure to its owning skills.
- No speculative backlog or god feature.
- No prose-only proof package for non-trivial behavior.
- No local workflow engine, daemon, or planning router.
- Stack/domain skills own concrete implementation structure.
- App preparation ends with every decided feature package ready and returns to one feature when implementation was explicitly authorized.

## Handoff
Report the decided app shape, created/updated context docs, complete lean feature ids in recommended order, queue path/status summary, ready set, and material unresolved input. Start implementation only when the original requested deliverable explicitly includes implemented app or product behavior; otherwise stop after preparation.
