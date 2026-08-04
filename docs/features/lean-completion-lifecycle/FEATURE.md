# Lean Completion Lifecycle

## Goal
Reduce tracked and autonomous completion time while preserving realistic proof, fresh semantic evaluation, and retained failure history without parallel orchestration or extra completion stages.

## Behavior
- Lightweight work remains outside the feature lifecycle and completes with its focused regression or narrow check. It does not require a feature package, captured proof, queue mutation, or evaluator.
- Tracked and autonomous work proceeds one feature and one accountable parent at a time.
- A tracked or autonomous feature is complete only after its current realistic feature proof passes and a fresh read-only evaluator returns `PASS` for that implementation and proof.
- The evaluator runs after proof passes for every tracked or autonomous feature. There is no ordinary/high-risk distinction and no pre-implementation evaluator stage.
- Evaluator `FINDINGS` return the feature to proof and repair: preserve the material finding in the next attempt note, strengthen proof so the missed defect fails when practical, repair the owning behavior, rerun the complete proof, and invoke another fresh evaluator. Repeat until `PASS` or an exact user-owned or external dependency remains.
- The evaluator remains read-only. The accountable parent owns contract/proof repair, implementation, queue mutation, and completion.
- No repository fast check, generic gate, whole-project sweep, or separate preflight result is a tracked-feature completion stage. Repository-owned commands may still be used as narrow diagnostics or inside a realistic feature proof when they directly support that proof.
- Queue state uses only `draft`, `ready`, `blocked`, and `done`. Automatic overlap invalidation, `revalidate`, `files`, and `revalidate_on` remain removed.
- App preparation creates concise current architecture and testing context, derives the complete non-speculative feature set required for the accepted app outcome, and routes every feature through normal feature-spec and proof authoring. Each feature owns one coherent observable outcome and one realistic proof boundary.
- Autonomous execution selects only the lowest-priority-number `ready` feature, completes its full lifecycle serially, then selects the next ready feature.
- Official evidence retains a meaningful initial red when practical, materially distinct failures, evaluator-driven strengthened-proof failures when practical, and the final passing proof. Narrow debugging checks are not official attempts.
- `PROOF.md` remains the current executable evidence contract. Retained attempt copies and notes preserve material changes without hashes, receipts, completion notes, or additional queue state.
- Repository context remains progressively disclosed: current app and architecture documents are concise maps, feature contracts own detailed behavior, and superseded history is loaded only when the active migration requires it.

## Constraints
- Preserve public-boundary activation, realistic durable or visible read-back, outer-edge fakes, central failure pressure, and green-but-broken proof strengthening.
- Preserve one accountable parent, one active feature, and one active proof attempt at a time.
- Preserve explicit proof timeouts, retained official output, evaluator independence, and honest known gaps.
- A fresh evaluator must inspect the current goal and corrections, accepted contracts, current implementation, latest passing proof, and relevant current architecture. It does not need unrelated history or the full repository by default.
- Do not add proof tiers, dependency graphs, freshness hashes, evaluator receipts, new queue states, worktrees, branch orchestration, or schedulers.
- Keep Graphify and other repository-specific indexing tools out of the global harness.

## Non-Goals
- Removing realistic executable proof.
- Removing the feature evaluator.
- Parallel implementation of queue features.
- Adding a repository-wide completion check outside the feature proof.
- Deleting retained historical proof attempts.
