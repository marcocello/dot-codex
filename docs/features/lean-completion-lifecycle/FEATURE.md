# Lean Completion Lifecycle

## Goal
Reduce tracked and autonomous completion time by challenging correlated feature/proof assumptions before implementation while preserving realistic proof, fresh final semantic evaluation, and retained failure history.

## Behavior
- Lightweight work remains outside the feature lifecycle and completes with its focused regression or narrow check. It does not require a feature package, captured proof, queue mutation, or evaluator.
- Tracked and autonomous work proceeds one feature and one accountable parent at a time.
- Feature decisions state the accepted interpretation and, when material ambiguity exists, the strongest rejected interpretation plus its consequence. Proof decisions identify the authoritative decision or state owner, materially affected consumers, and a central incomplete implementation the proof must catch.
- After tracked or autonomous `FEATURE.md`, `PROOF.md`, and executable `proof/run.sh` artifacts are decision-complete and implementation is explicitly authorized, `coding-feature-execute` starts one fresh separate read-only reviewer context using `coding-feature-preflight` before red evidence or implementation. An inline role switch by the authoring or executing parent is not fresh preflight.
- The preflight receives the original goal and corrections, current contracts and runner, and only relevant current repository context. It may follow existing behavior needed to identify authority or consumers, but it does not review a candidate implementation or execute proof.
- The preflight performs one bounded challenge of intent, authority and state transitions, affected consumers, central false-green pressure, and feature cohesion. It returns `CLEAR`, `FINDINGS`, or `NEED_INPUT`, with no more than three material findings.
- The accountable parent resolves supported findings in the contracts or proof, rejects unsupported scope expansion with evidence, and asks only for an exact user-owned decision. `NEED_INPUT` blocks red evidence and implementation until that decision is resolved. The preflight is not repeated until `CLEAR`, creates no durable receipt, does not mutate artifacts or queue state, and has no implementation or completion authority.
- A tracked or autonomous feature is complete only after its current realistic feature proof passes and a fresh read-only evaluator returns `PASS` for that implementation and proof.
- The implementation evaluator runs after proof passes for every tracked or autonomous feature. It remains distinct from the contract-only preflight; there is no pre-implementation implementation verdict or early completion authority.
- Evaluator `FINDINGS` return the feature to proof and repair: preserve the material finding in the next attempt note, strengthen proof so the missed defect fails when practical, repair the owning behavior, rerun the complete proof, and invoke another fresh evaluator. Repeat until `PASS` or an exact user-owned or external dependency remains.
- The evaluator remains read-only. The accountable parent owns contract/proof repair, implementation, queue mutation, and completion.
- No repository fast check, generic gate, whole-project sweep, or preflight result is a tracked-feature completion stage. Repository-owned commands may still be used as narrow diagnostics or inside a realistic feature proof when they directly support that proof.
- Queue state uses only `draft`, `ready`, `blocked`, and `done`. Automatic overlap invalidation, `revalidate`, `files`, and `revalidate_on` remain removed.
- App preparation creates concise current architecture and testing context, derives the complete non-speculative feature set required for the accepted app outcome, and routes every feature through normal feature-spec and proof authoring. Each feature owns one coherent observable outcome and one realistic proof boundary.
- Autonomous execution selects only the lowest-priority-number `ready` feature, completes its full lifecycle serially, then selects the next ready feature.
- Official evidence retains a meaningful initial red when practical, materially distinct failures, evaluator-driven strengthened-proof failures when practical, and the final passing proof. Narrow debugging checks are not official attempts.
- `PROOF.md` remains the current executable evidence contract. Retained attempt copies and notes preserve material changes without hashes, receipts, completion notes, or additional queue state.
- Repository context remains progressively disclosed: current app and architecture documents are concise maps, feature contracts own detailed behavior, and superseded history is loaded only when the active migration requires it.

## Constraints
- Preserve public-boundary activation, realistic durable or visible read-back, outer-edge fakes, central failure pressure, and green-but-broken proof strengthening.
- Preserve one accountable parent, one active feature, and one active proof attempt at a time.
- Preserve the preflight reviewer's fresh separate context, read-only role, bounded findings, placement on the real implementation entry path, and separation from final implementation evaluation.
- Preserve explicit proof timeouts, retained official output, evaluator independence, and honest known gaps.
- A fresh evaluator must inspect the current goal and corrections, accepted contracts, current implementation, latest passing proof, and relevant current architecture. It does not need unrelated history or the full repository by default.
- Do not add proof tiers, dependency graphs, freshness hashes, evaluator receipts, new queue states, worktrees, branch orchestration, or schedulers.
- Do not persist preflight status, findings, receipts, scores, counters, or another approval gate.
- Keep Graphify and other repository-specific indexing tools out of the global harness.

## Non-Goals
- Removing realistic executable proof.
- Removing the feature evaluator.
- Reusing the final implementation evaluator as the preflight reviewer.
- Repeating preflight until a passing verdict.
- Parallel implementation of queue features.
- Adding a repository-wide completion check outside the feature proof.
- Deleting retained historical proof attempts.
