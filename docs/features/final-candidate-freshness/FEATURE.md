# Final-Candidate Freshness

## Goal
Prevent a tracked or autonomous feature from being marked complete after relevant files changed beyond the implementation and proof that actually received the final passing evidence.

## Behavior
- The final candidate is the implementation, contracts, proof runner and fixtures, and relevant runtime, configuration, and call paths that produced the latest passing official proof.
- Before starting the evaluator, the accountable parent confirms that no relevant candidate surface changed after that proof. A relevant edit makes the proof stale and requires the complete official proof to pass again before a fresh evaluator starts.
- An evaluator `PASS` applies only to the candidate it inspected. A relevant edit after that verdict makes both proof and verdict stale, requiring the complete proof and another fresh evaluator `PASS`.
- The parent marks the queue item `done` only while the final candidate remains unchanged since its proof and evaluation.
- Freshness checking preserves serial queue draining: after the unchanged candidate reaches `done`, autonomous execution selects the next `ready` item and continues until none remains.
- Retained attempt generation and the narrow queue transition to `done` are lifecycle bookkeeping, not candidate changes.

## Constraints
- Freshness is enforced by the single accountable parent in the serial lifecycle.
- Add no hashes, manifests, receipts, dependency graph, commit pin, branches, worktrees, queue fields, or parallel coordinator.
- When relevance is uncertain, include the file in the candidate surface and rerun; never silently declare a potentially behavior-affecting edit irrelevant.

## Non-Goals
- A cryptographic or adversarial trust root.
- Detecting edits made outside the active task without repository visibility.
- Revalidating historical completed features after unrelated later work.
- Replacing realistic proof or semantic evaluation with source-state bookkeeping.
