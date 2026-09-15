---
name: second-brain-review
description: Review Notion Second Brain tasks, deals, and ideas as a concise activity brief or a deeper weekly review, surfacing waiting items, stale work, and proposed next steps.
---

# Second Brain Review

Use the existing structure in `docs/harness/secondbrain.md`. Read only `SB - Tasks`, `SB - Deals`, and `SB - Ideas` through an available connector or `second-brain-notion-api`. Preserve the current schema.

## Select depth

Use brief mode for an activity brief, current priorities, or an unspecified review. Use weekly mode for a weekly review or a deeper examination of open loops and follow-up decisions. A weekly review request does not itself schedule recurring work.

## Brief

Read active, scheduled, and waiting tasks; deals with open or stale next steps; and ideas marked Proposed or Review. Return a compact brief in this order:

1. Now: the tasks and deal next steps most relevant to current priorities.
2. Waiting: people or external dependencies blocking progress.
3. Stale: old or missing next steps.
4. Ideas: proposed or review ideas worth deciding.
5. Suggested next actions: clearly marked recommendations.

## Weekly

Review overdue and stale tasks, waiting items, and missing next steps. Examine deals without a next step, with old next-step dates, or with low-confidence proposed changes. Review ideas to promote into tasks, park, or archive. Return tasks needing action, deals needing next steps, ideas to review, and proposed decisions for the coming week. Show source evidence and uncertainty when relevant; do not invent owners, dates, commitments, or stages.

## Read and write boundaries

A review or brief is read-only. Separate confirmed Notion state from suggestions; do not create or update rows unless the user requests those changes. Requested updates remain subject to the shared contract, including deal safeguards and schema boundaries. Do not silently advance or close deals based on indirect evidence. Do not bulk-import source content or add tables.

If read access is unavailable, identify what could not be read and do not invent a review. If explicitly requested updates cannot be written, provide the exact proposed manual updates and disclose that nothing changed. Report the reviewed scope and any inaccessible state. Keep brief mode short enough to act on.
