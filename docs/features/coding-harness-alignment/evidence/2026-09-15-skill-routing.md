# Explicit coding-skill routing

The user clarified that the requested verification concerns whether the current agent instructions select the correct coding skills: anti-pattern review, architecture assessment, commit, environment preparation, backend/frontend work, and the other current coding capabilities.

Observed gap: all ten coding skills were declared, available in the active catalog, and allowed implicit selection, but the central instructions named only the lifecycle and workflow-reflection skills. Most domain selection depended on the broad instruction to use an appropriate skill. This was a wiring clarification and focused fix within the current alignment contract; its accepted behavior and frozen proof inputs remain unchanged.

Change: `AGENTS.md` now points to the single domain-selection table in `skills/coding-workflow/SKILL.md`. That table links all nine specialized coding skills, explains when to select them, distinguishes Python implementation from code-quality and architecture reviews, coordinates UI toolkit/frontend ownership, reuses known-good environments, and preserves commit/audit/review authorization boundaries. It does not require every skill on every task or add another lifecycle owner.

Local checks confirmed that the active Codex home resolves to this checkout, no coding skill has a disabled configuration override, and all ten entrypoints have matching invocation prompts with implicit selection available. All nine domain skill links resolve from the workflow entrypoint.

Captured supporting verification under `tests/runs/`:

- `20260915T145408680189Z`: updated skill metadata validator PASS.
- `20260915T145408691329Z`: current inventory doctor PASS, 36 dependencies.
- `20260915T145408701779Z`: repository gate PASS.

Fresh actor `/root/skill_routing_exercise` received no inherited conversation or rubrics. It answered the original six cases and nine targeted skill-selection scenarios in `proof/runs/20260915-routing-exercise/transcript.md`. The separate assessor is `/root/current_proof_author`; original semantic acceptance remains the same six-case contract, and the nine additional routing cases are supporting verification against actual skill instructions. Candidate and assessed evidence are retained alongside the transcript. Native task attribution remains `01a0a570-1b40-7a61-bc79-4c8e8bd7fd6d`.

## Completion

All six frozen workflow cases and all nine targeted routing cases passed independent assessment. Official proof `proof/runs/20260915T145815445821Z` passed all eight groups. Fresh separate reviewer `/root/final_routing_review` returned PASS with no actionable findings, confirming all 60 candidate hashes, transcript and assessment integrity, correct conditional skill selection, and preserved lifecycle/authorization boundaries. The reviewed candidate digest is `0b6f072a45e2882cb96fda1daa3ade16fa76f065d488e74cb66119fd4eb3d10b`.

The feature was recorded done against that latest official proof after review. No relevant inputs changed after review. This establishes current instruction wiring and observed bounded skill-selection decisions; it does not guarantee future implementation quality or run the selected skills against live products.
