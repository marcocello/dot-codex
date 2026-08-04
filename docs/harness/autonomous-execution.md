# Autonomous Execution

Owner: `coding-autonomous-execute`.

Autonomous execution is a serial continuation loop around `coding-feature-execute`:

1. Select the lowest-priority ready feature.
2. Keep one accountable parent and one active `FEATURE_DIR`.
3. Continue proof, repair, and fresh evaluation until evaluator `PASS` or a genuine blocker.
4. Mark only that feature done, then select the next ready item.
5. Stop when no ready item remains.

For each selected feature, reset the transient changed-file and relevant-call-path surface supplied to its evaluator. This keeps same-checkout review feature-local without commits, branches, worktrees, receipts, hashes, or queue-schema growth.

On resume, inspect the newest run directory. An `attempt-start.json` without `result.json` is unresolved until its recorded process is checked. Never start a competing proof or use an older `PASS` while a newer attempt is incomplete.
