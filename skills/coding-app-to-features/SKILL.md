---
name: coding-app-to-features
description: "Turn one app idea into decided context, feature contracts, executable proofs, and a prioritized queue."
---

# App To Features

Purpose: shape an app with the user, create only the repository context that will guide implementation, and materialize a small sequence of independently valuable, realistically provable features.

This skill prepares app context and feature packages. When the user asks to create, build, or implement the app, preparation is a phase before the first ready feature enters implementation in the same parent run. Planning or specification-only requests stop after preparation.

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
When the repository has no established product or architecture and the user asks to create, build, or implement:

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
   - Record high-level components, boundaries, data flow, and external dependencies without copying concrete starters, folder trees, or implementation structure from the owning stack/domain skills.

3. Derive vertical features
   - Prefer end-to-end user value over foundation-only slices.
   - Create the smallest sequence that makes the app implementable and useful.
   - Each feature must have one coherent user/system outcome and one provable boundary.
   - Merge overlapping ideas; leave speculative roadmap items out.
   - Order by dependencies and value, not a universal backend/frontend/data sequence.

4. Decide each selected feature
   - Use `coding-feature-spec` for the feature challenge and visible decision summary; ask only for unresolved material choices with no safe default.
   - Use `coding-proof-author` for the proof boundary challenge and visible decision summary; ask only when a safe honest proof cannot be inferred.
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
   - When the user asked to create, build, or implement, invoke `coding-feature-execute` for that item in the same parent run.
   - Planning or specification-only requests stop after preparation and report the first ready item.
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
- No hidden architecture commitment: label inferred defaults and preserve explicit overrides.

## Rules
- User input shapes app and proof; the agent records decisions and proceeds without contract-approval gates.
- No universal folder tree, feature count, or foundation-first sequence; select the smallest applicable greenfield profile and leave concrete structure to its owning skills.
- No speculative backlog.
- No prose-only proof package for non-trivial behavior.
- No local workflow engine, daemon, or planning router.
- Stack/domain skills own concrete implementation structure.
- App preparation ends by returning to one `FEATURE_DIR`.

## Handoff
Report the decided app shape, created/updated context docs, feature ids in recommended order, queue path/status summary, first ready item, and material unresolved input. Start implementation only when the request asked to create, build, or implement; otherwise stop after preparation.
