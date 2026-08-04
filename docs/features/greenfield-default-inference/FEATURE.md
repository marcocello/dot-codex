# Greenfield Default Inference

## Goal
Let a user start a greenfield application from a short create/build request without being blocked by reversible architecture, provider, or proof choices that the harness can resolve safely.

## Behavior
- The feature and proof decision passes may contain zero user questions when the request, repository, or safe defaults resolve the material choices.
- In an empty repository, a create/build/implement request uses the smallest local-first, single-user application shape unless the request implies accounts, collaboration, cloud ownership, compliance, or another materially different product boundary.
- A generic web application defaults to a React frontend. It adds a backend API boundary when server-owned secrets, provider calls, or persistence require one, while the relevant stack skills retain ownership of concrete frameworks, starters, folders, and code layout.
- Authentication, cloud sync, paid deployment, and live external mutations remain out of the initial slice unless the user requests them or the product cannot satisfy its stated outcome without them.
- An AI capability with no named provider uses an OpenAI adapter behind a provider boundary, keeps credentials server-side, and uses a deterministic fake only at the outer provider boundary for proof. Missing live credentials or optional live spend does not block app preparation.
- Safe inferred product defaults are stated in the decision summary rather than presented as approval questions. Explicit user or repository constraints override inferred defaults.
- The harness asks and waits only when an unresolved user-owned choice has no safe default and can materially change observable behavior, data ownership, permissions, safety, cost, or external effects.
- When the user asks to create, build, or implement, app preparation continues into `coding-feature-execute` for the first ready feature in the same parent run. Planning or specification-only requests stop after preparation.
- Routing distinguishes the requested deliverable from incidental verbs: a request to write, define, design, or create feature and proof contracts is contract-authoring work, not authorization to implement the product behavior described by those contracts.
- Contract-authoring work ends after decision-complete `FEATURE.md`, `PROOF.md`, and executable `proof/run.sh` artifacts are ready. It must not invoke `coding-feature-execute`; implementation requires a separate explicit request to build, implement, or execute the product behavior.
- User replies to feature-discovery or proof questions retain the scope of the original request and do not independently authorize implementation.

## Constraints
- Preserve the distinction between high-level app-shape selection and stack-skill ownership of concrete scaffolding.
- Preserve focused questions for genuinely material ambiguity and approval-gated external effects.
- Define the policy as a durable decision invariant, not a list of prompt phrases.
- Keep Sites opt-in and preserve the existing frontend scaffold ownership contract.

## Non-Goals
- Guaranteeing deterministic compliance by every future model version.
- Changing the default frontend starter, backend framework, or folder layout owned by stack skills.
- Performing live provider calls, deployments, credential entry, or paid resource creation.
- Removing the feature and proof decision summaries or weakening realistic proof requirements.
- Treating contract readiness as feature implementation or completion.
