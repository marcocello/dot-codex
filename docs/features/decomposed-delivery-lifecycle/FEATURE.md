# Decomposed Delivery Lifecycle

## Goal

Keep delivery responsibilities in focused skills while making assurance proportional, reviewer ownership unambiguous, and lifecycle coverage smaller without losing proof, repair, freshness, or runtime truth.

## Behavior

- Delivery remains decomposed across `coding-proof-author`, `coding-feature-execute`, `coding-feature-review`, and `coding-repair`; `coding-autonomous-execute` and `coding-feature-queue` remain optional coordination for accepted multi-feature work.
- `coding-feature-review` owns two fresh read-only modes: risk-triggered contract preflight before implementation and final evidence/implementation review after realistic proof.
- Global assurance categories are `focused`, `standard`, and `sensitive`. A clear isolated repair with reversible local impact is focused and uses `coding-repair` plus a focused regression. Material new or changed product behavior is standard and requires a decision-complete feature/proof package, executable proof, and fresh final review. Sensitive work adds preflight when it changes data or migration semantics, authorization or security, destructive or paid external effects, durable cross-component ownership, or leaves a material proof-target ambiguity.
- `coding-feature-execute` owns operational assurance classification at the implementation boundary from the accepted contracts and current repository risk. Explicit user, repository, or accepted-contract sensitivity is a floor that cannot be downgraded. Execution-time discovery may escalate assurance. Resume reclassifies from current evidence while preserving that floor.
- Standalone `coding-repair` owns focused repair. Repair invoked inside a standard or sensitive feature inherits the active feature assurance and returns to its proof/review lifecycle rather than resetting classification.
- Autonomous execution is a continuation mode, not an assurance tier. It applies the selected feature assurance serially and does not add proof or review requirements by itself.
- For sensitive work, `coding-feature-execute` starts a fresh separate `coding-feature-review` invocation in `preflight` mode before red evidence. Preflight receives intent and decision-complete contracts but no candidate implementation, does not execute proof, and returns `CLEAR`, `FINDINGS`, or `NEED_INPUT`; unresolved input blocks red evidence and implementation.
- After target-valid realistic proof passes for every standard or sensitive feature, `coding-feature-execute` starts another fresh separate reviewer invocation in `final` mode. It receives the passing evidence, named target, and active feature surface; performs evidence-first then implementation review; and returns `PASS`, `FINDINGS`, or `NEED_INPUT`.
- Preflight findings repair the feature/proof contract once before implementation. Final findings strengthen proof when practical, repair behavior, rerun the complete proof, and require a fresh final review.
- Final-candidate freshness, named-runtime completion truth, proof isolation, public-boundary evidence, retained attempts, and green-but-broken recovery remain active invariants.
- Legacy separate preflight and evaluator skills are retired after their positive lifecycle coverage is migrated to the consolidated reviewer and delivery surfaces.

## Constraints

- Preserve one accountable parent, one active feature, serial implementation, safety approvals, dirty-tree protection, and proof-run containment.
- Do not collapse proof, implementation, review, and repair into one delivery skill.
- Do not make every material feature run preflight; use the sensitive-work boundary.
- Do not replace semantic final review with a static gate or exact response wording.

## Non-Goals

- Changing product shaping behavior owned by `adaptive-product-partner-core`.
- Adding new queue states, receipts, hashes, dependency graphs, branches, worktrees, or orchestration services.
- Removing realistic executable proof or fresh final review for material product behavior.
