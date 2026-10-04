---
name: coding-runtime-ops
description: Diagnose running-system symptoms from runtime evidence, perform explicitly authorized remediation, and verify recovery on the affected consumer.
---

# Runtime Ops

Diagnose and, when authorized, remediate a problem in a running environment. The exact runtime is the primary evidence boundary.

Use this lane for concrete runtime symptoms, including requests phrased as analysis, review, or understanding. Diagnosis-only requests start read-only and end with findings; they do not require remediation or authorize production changes. Follow runtime evidence across service and repository boundaries before assigning the cause.

## Start Read-Only

Identify the symptom, expected behavior, environment, service, affected users or consumers, and timeframe. Establish current local, container, database, cloud, and cluster context before interpreting results. Use bounded paths, namespaces, resource groups, time windows, and log tails; redact credentials, tokens, connection strings, customer data, and full environment dumps.

Do not restart, scale, deploy, mutate data, edit secrets, change external accounts, or run destructive commands without explicit authorization. State Azure subscription and Kubernetes context before cloud conclusions. Treat database writes as destructive.

Use the bundled [preflight helper](scripts/ops_diag_preflight.sh) for a bounded baseline when its supported local, PostgreSQL, Docker, Azure, or Kubernetes surfaces are relevant. Load [read-only checks](references/read-only-checks.md) only after the first pass identifies an owning area.

## Investigate

1. Establish repository, runtime, configuration, deployment, and time context.
2. Reproduce or bracket the failure through the narrowest safe command.
3. Compare local and running versions, configuration selection, state, readiness, and recent logs without exposing secrets.
4. Correlate user time, deployment, restart, queue, provider, and error events.
5. Separate confirmed evidence from hypotheses and recommend the smallest next diagnostic or remediation.

## Route Or Remediate

- Confirmed code defect with known behavior and authorized repair: enter `coding-repair`, carrying the original symptom, affected runtime/consumer, and required recovery read-back into the repair. For diagnosis-only scope, report the finding and proposed repair without editing. The skill transition does not close that verification obligation or authorize deployment.
- Apply [Product Partner](../coding-product-partner/SKILL.md) to inspect the surrounding consumer workflow and recovery, raise useful adjacent proposals, and clarify ambiguous expected behavior. Continue independent diagnostics; proposals grant no remediation authority.
- Missing capability with a clear intended outcome: enter `coding-design-specs-proof` within the authorized scope; diagnosis alone does not authorize implementation.
- Environment or operational cause with authorized corrective action: remain in Runtime Ops, mutate only the explicit target, and verify the live consumer afterward.
- Approval or external access still required after safe diagnostics: report the exact blocker; do not translate missing evidence into success.

A technical prerequisite is work to resolve, not by itself a reason to hand the task back. When repair is already authorized, carry the blocker into the owning skill, implement and verify the local recovery path, and continue toward the requested outcome within the existing permissions. If the workflow rejects an earlier manual operation, inspect its invariants and validate the actual state before adopting it; never fabricate a completed phase or bypass a guard. If execution needs new external authority, prepare and verify the repair first, then request only that remaining action.

## Complete

Remediation completion requires live read-back from the affected runtime or consumer, not source inspection or a local substitute. A diagnosis-only request completes with evidence-backed findings, material uncertainties, and an actionable proposed next step. Report the cause, commands and scopes used, mutation performed when any, post-remediation evidence when applicable, remaining risk, and exact blocker.

Relate the diagnostic result to the user's broader objective when conversation evidence establishes one. If access or service health is only a prerequisite, distinguish that verified step from the still-unproven usable outcome and carry forward the authorized recovery. Do not make the user discover each intervening technical step through separate questions. Diagnosis-only scope still stops before implementation or external effects.

When stopping with an unresolved outcome, give the next action, its owner, and the specific reason the agent cannot continue. For a user-owned command, supply the exact command, target context, prerequisites, and observable success condition without exposing secrets. For approval or access, ask for the precise missing authority or access rather than assigning the technical repair to the user. Explain any instruction to avoid a command together with the safe recovery path. If no user action is needed and the remaining work is authorized, continue working instead of ending with a promise to fix it later.

If the repair passes locally and the user deploys separately, report “verified locally; production verification pending.” After deployment, check the original symptom on that runtime before declaring the operational problem resolved. A diagnosis-only request stops with findings and a proposed next action. Retain relevant context through [evidence.md](../../docs/harness/coding/evidence.md).
