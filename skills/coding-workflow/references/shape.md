# Shape

Understand the requested outcome through conversation, then define acceptance before implementation.

## Discover And Decide

Inspect the request, relevant existing code and feature contracts, product/architecture/testing context, and authoritative external facts when needed. Walk through the user's trigger, journey, outcome, state changes, permissions, failures, existing data, affected consumers, compatibility, constraints, and non-goals.

Investigate discoverable facts independently. Ask when different plausible answers produce different observable behavior or consequences. Use concrete examples and focused conversational rounds rather than a fixed questionnaire. Resolve material questions and disclose assumptions before writing the accepted specification; human reading/sign-off is optional.

Inspect likely shared components and note existing behavior to preserve. For example: “Feature 9 changes the filter used by features 2 and 6; their filtering behavior must remain unchanged.” Resolve intended compatibility changes now. This note guides regression selection; no pre-implementation full-suite run is required.

Keep one feature per independently valuable observable outcome and independently runnable proof boundary. Do not split merely because several files or layers change. Include accepted prerequisites; keep unrelated improvements and alternatives outside scope. Material refactors specify invariants or equivalence to preserve.

## Specify And Author Proof

Write `FEATURE.md`: accepted outcomes, journeys/scenarios, decisions, boundaries, constraints, non-goals, and the brief compatibility note. Read [status.md](status.md) to create the complete material-feature scaffold and register it as `draft` without overwriting another task. Initialize an empty version 2 `docs/features/status.json` only when absent; automatically migrate an existing old-format index before registration, without another approval.

Delegate `PROOF.md`, dedicated acceptance tests, and executable `proof/run.sh` to a separate agent. Give it the specification, relevant original request and corrections, repository context, and named target. Read [proof.md](proof.md). It may inspect source and reuse utilities, but must not implement behavior or rewrite the specification. Missing decisions return to the main agent's conversation.

The author verifies runner feasibility and meaningful failure when practical; otherwise records the concrete limitation. Maintain `draft` until behavior and executable proof are ready. A draft runner may fail explicitly while proof is incomplete; it is never passing evidence. Use `ready` only when acceptance is decision-complete, independently authored, and runnable against the agreed boundary. Record proof-author identity and frozen input versions using [evidence.md](evidence.md).

If independent authorship is unavailable, surface that required capability rather than substituting implementer-written acceptance. Questions already answered and implementation already authorized do not need another approval.

## Stop Or Continue

Planning, analysis, specification, and proof-authoring requests stop at the requested deliverable. A build request retains its existing implementation authorization through discovery. When ready, read [ship.md](ship.md), claim the feature, establish authorized native Goal execution, and continue.

Later behavior requests normally start a new change cycle after the current one completes. Preserve original run evidence. Honor user interruption. A necessary acceptance decision during Ship pauses dependent work until resolved with the user before revising specification, separate author's proof, and Goal. Compatible guidance and independent test-setup repairs under [proof.md](proof.md#fixed-acceptance) stay in Ship without reopening Shape.
