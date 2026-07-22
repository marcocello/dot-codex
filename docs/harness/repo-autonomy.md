# Harness Learning

## Inputs
- Failed/passing attempts + notes.
- Plain per-attempt `completion.md` gate/evaluator/correction context.
- Evaluator findings.
- User corrections/rejected directions.
- Repeated setup/diagnostic/proof failures.

## Owners
- Behavior -> `FEATURE.md` + implementation.
- Architecture -> repo architecture docs.
- Proof -> `PROOF.md`, runner, fixture, testing docs.
- Setup -> repo scripts/docs.
- Repeated cross-feature/repo issue -> smallest harness skill/doc/script/test.
- Stable preference -> memory only when user asks.

One repo failure stays local. Promote only recurring pattern. Reject harness changes that add more ceremony than useful feedback.
