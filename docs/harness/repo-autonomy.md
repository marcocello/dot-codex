# Repository Discovery And Harness Learning

## Before Artifacts
- Inspect current `APP.md`, `ARCHITECTURE.md`, conventions, testing guidance, related feature contracts, and the real behavior boundary before asking the user for repository facts.
- Treat interaction records and retained runs as historical evidence, not automatic authority. Supply verbatim goal/correction excerpts when they materially define the active outcome.
- Identify current product purpose, actor benefit, authority, state transitions, producers, affected consumers, compatibility requirements, and plausible central failures.
- Classify adjacent discoveries as current behavior, prerequisite, follow-up, alternative, or unrelated. Only accepted decisions expand artifacts or implementation scope.
- Update `APP.md` or `ARCHITECTURE.md` only when a durable app-level or cross-feature decision changes. Keep exploration in conversation.

## Inputs
- Current repository authority and behavior.
- Original user goal and material corrections.
- Failed/passing attempts + notes.
- Proof results, evaluator findings, and relevant setup diagnostics.
- User corrections/rejected directions.
- Repeated setup, diagnostic, proof, or evaluator failures.

## Owners
- Behavior -> `FEATURE.md` + implementation.
- Product identity, users, outcomes, scope -> `APP.md` when durable.
- Cross-feature ownership, state, components, data flow -> `ARCHITECTURE.md` when durable.
- Proof -> `PROOF.md`, runner, fixture, testing docs.
- Setup -> repo scripts/docs.
- Repeated cross-feature/repo issue -> smallest harness skill/doc/script/test.
- Stable preference or recurring correction -> explicit `second-brain-capture-interactions` only when the user asks to save the relevant dialogue.

One repo failure stays local. Promote only a recurring pattern or a demonstrated central harness false green. Reject harness changes that add more ceremony than useful feedback.
