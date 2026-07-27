# Cross-Task Commit Scope Proof

## Proves
- The real `coding-commit` trigger metadata makes cross-task repository commit work discoverable.
- The skill defines user request plus Git state, rather than task provenance, as the scope boundary.
- Explicitly scoped requests remain narrow while unscoped requests cover the complete local change set.
- Independent concerns may become multiple coherent commits.
- Cross-task provenance alone does not cause exclusion, refusal, or confirmation.
- Existing explicit-path staging, no-push, and message-only safeguards remain intact.
- The skill folder passes its native structural validator.

## Evidence Method
- Parse the real `skills/coding-commit/SKILL.md` frontmatter and instruction body.
- Read the real `skills/coding-commit/agents/openai.yaml` invocation metadata.
- Assert the accepted scope precedence and retained safety boundaries through a focused pytest regression.
- Run the skill creator's real `quick_validate.py` against the skill folder.

## False-Green Risks
- Generic commit wording could exist while task provenance still narrows scope; the regression requires the explicit invariant and both scoped and unscoped precedence rules.
- Repository-wide wording could accidentally remove staging safeguards; the regression also requires explicit-path staging, preserved staged selection, message-only behavior, and no-push behavior.
- Static instructions cannot guarantee deterministic behavior by every future model; the proof claims instruction availability and consistency, not universal compliance.

## Does Not Prove
- That an already-running task reloads changed skill instructions.
- Deterministic compliance by every model or Codex surface.
- Successful Git commits for every repository state, hook, signing, or credential configuration.

## Known Gaps
- Model adherence remains probabilistic and should be exercised from a newly loaded task when live behavioral validation is desired.

## Execution
- Runner: `docs/features/cross-task-commit/proof/run.sh`
- Official timeout: 60 seconds.
- The runner performs read-only validation of repository artifacts.
