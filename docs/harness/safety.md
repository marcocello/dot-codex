# Safety, Operations, And Handoff

## Approval Boundary

Explicit approval is required for global installs, paid resources, destructive commands, deployments, force pushes, secret edits, credential entry, external account mutations, and service or data changes outside already authorized implementation scope. Repository-local setup and declared dependencies are pre-authorized.

Before a destructive action, resolve the exact target with read-only checks, avoid broad paths and unresolved variables, prefer recoverable operations, and state the expected effect. Treat database writes, infrastructure mutation, restarts, scaling, and external messages as effects—not diagnostics.

## Operate Read-Only First

Runtime investigation starts by identifying environment, service, affected consumer, timeframe, deployment version, context, and bounded logs. Redact credentials, tokens, connection strings, customer data, and full environment dumps. State cloud subscription, cluster context, namespace, resource group, and time window before drawing conclusions.

After evidence identifies the cause, remain in Operate for an authorized environment repair, enter Fix for a known code defect, or enter Shape for missing or ambiguous behavior. Completion requires read-back from the same affected runtime or consumer.

## Repository Safety

Preserve unrelated dirty-tree work and pre-existing repository instructions. Reuse existing ownership, make the smallest coherent change, and establish meaningful failing checks when practical. Keep acceptance requirements fixed. Independent setup repairs and user-owned acceptance decisions follow [the coding proof procedure](../../skills/coding-workflow/references/proof.md#fixed-acceptance). Do not downgrade errors or create target-repository instruction files merely because the shared harness exists.

There is no category-triggered early review. The agent may choose an extra read-only reviewer for a concrete identified risk, or the user may request one. Ordinary uncertainty calls for investigation and questions. Required approvals and proof of relevant security/data/effect boundaries remain intact; review is never mutation permission. A standalone Fix needs no package just for optional review.

## Handoff

Keep the final receipt compact and factual:

- outcome and changed surface;
- realistic proof or focused regression;
- fresh final oracle for material Ship work;
- runtime state: `active runtime proven`, `source proven; activation required`, or `not applicable`;
- known gaps and exact blocker.

Never label a generic gate, build, lint, source inspection, or reviewer as feature proof. Missing input pauses dependent work; continue authorized independent work. Ask one exact question, using `NEED_INPUT` only if it has not already been asked asynchronously or in an earlier turn. Automatic continuations must not repeat pending questions or unchanged approval explanations. Explain again when the user asks or the decision materially changes.
