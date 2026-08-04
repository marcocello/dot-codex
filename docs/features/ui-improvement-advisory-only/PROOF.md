# Advisory-Only UI Improvement Skill Proof

## Done
- The published trigger metadata describes written, component-specific UI guidance and excludes implementation authority.
- The skill makes advisory-only behavior unconditional, forbids product and feedback mutations, and routes implementation to a separate task.
- The required MCP-routing reference preserves the same read-only boundary for Agentation and external component registries.
- The required output is specific enough for later implementation: local component/file, exact change, relevant states and responsive/accessibility behavior, acceptance check, and cited external candidate details when applicable.
- The skill folder passes its native structural validator.

## Command
```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/ui-improvement-advisory-only --timeout-seconds 60 --note "reason"
```

## Scenario: advisory contract survives implementation-shaped requests
- Producer/activation: Load the real `coding-ui-improvement` trigger metadata and instruction body used when the skill is invoked.
- Consumer: A Codex task follows the published skill contract for UI critique, redesign, or improvement requests.
- Read-back: Focused pytest assertions read the real skill, required MCP-routing reference, and agent metadata and require the advisory boundary plus the complete component-specific output contract.
- Fake: None.
- Catches: A skill or required reference that authorizes edits for words such as improve or fix, retains an implementation workflow, mutates Agentation feedback, runs component-add commands, or offers generic recommendations without naming the affected component and exact change.

## Scope
Proves:
- The reusable skill contract and invocation metadata expose advisory-only UI improvement behavior.
- Implementation-shaped wording does not grant edit authority inside this skill.
- Agentation and component-registry routing remain inspection-only and cannot reopen an implementation path.
- The written result must identify components and provide concrete, verifiable instructions for later implementation.
- External component candidates must be cited rather than silently adopted.

Does not prove:
- Deterministic compliance by every future model or Codex surface.
- The quality of a recommendation when no rendered UI or relevant source is available.
- That a separately requested implementation task applies the brief correctly.

False-green risks:
- Generic read-only wording could coexist with a hidden implementation path in a required reference; the regression inspects both the main skill and MCP-routing instructions, rejects implementation authorization, and requires explicit mutation prohibitions.
- A component name alone could still produce an unusable brief; the regression requires affected source, exact change, states, accessibility/responsive behavior, and an acceptance check.
- Static contract validation cannot exercise model judgment; a fresh forward-test supplements the executable artifact proof before final evaluation.
- The earlier proof omitted the required MCP-routing reference and passed despite contradictory mutation instructions; the strengthened regression makes that branch part of the central proof boundary.

Evidence method:
- Deterministic contract validation, supplemented by a fresh behavioral forward-test.

Known gaps:
- Model adherence remains probabilistic.

## Environment
- Repository-local Python and pytest validate the checked-out skill artifacts without network access or external mutation.
- Runner stdout: Python executable and version, skill path, validator path, and focused test path.
