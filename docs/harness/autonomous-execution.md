# Autonomous Execution

Owner: `coding-autonomous-execute`.

Shaping may produce several ready feature packages from one app idea, mixed bundle, or adjacent-capability investigation. Autonomous execution does not implement them as a batch.

Autonomous execution is a continuation mode, not an assurance tier. It is a serial loop around `coding-feature-execute`, which classifies each selected feature independently:

1. Select the lowest-priority ready feature.
2. Keep one accountable parent and one active `FEATURE_DIR`.
3. Continue proof, repair, safe local activation, and fresh final review until the named consumption target passes or a genuine blocker remains. Source proof is intermediate and cannot produce `done` for an existing runtime target.
4. Mark only that feature done, then select the next ready item.
5. Stop when no ready item remains.

For each selected feature, reset the transient changed-file and relevant-call-path surface supplied to `coding-feature-review`. That surface is a discovery entry point, not a scope ceiling: the reviewer independently follows relevance-bounded current contracts, authority, state, affected consumers, and call paths. This keeps same-checkout review accountable to one feature without commits, branches, worktrees, receipts, hashes, queue-schema growth, or a repository-wide sweep.

On resume, inspect the newest run directory. An `attempt-start.json` without `result.json` is unresolved until its recorded process is checked. Never start a competing proof or use an older `PASS` while a newer attempt is incomplete.
