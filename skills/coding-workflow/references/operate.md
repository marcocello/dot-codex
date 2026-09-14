# Operate

Diagnose and, when authorized, remediate a problem in a running environment. The exact runtime is the primary evidence boundary.

## Start Read-Only

Identify the symptom, expected behavior, environment, service, affected users or consumers, and timeframe. Establish current local, container, database, cloud, and cluster context before interpreting results. Use bounded paths, namespaces, resource groups, time windows, and log tails; redact credentials, tokens, connection strings, customer data, and full environment dumps.

Do not restart, scale, deploy, mutate data, edit secrets, change external accounts, or run destructive commands without explicit authorization. State Azure subscription and Kubernetes context before cloud conclusions. Treat database writes as destructive.

Use `scripts/ops_diag_preflight.sh` for a bounded baseline when its supported local, PostgreSQL, Docker, Azure, or Kubernetes surfaces are relevant. Load [operate/read-only-checks.md](operate/read-only-checks.md) only after the first pass identifies an owning area.

## Investigate

1. Establish repository, runtime, configuration, deployment, and time context.
2. Reproduce or bracket the failure through the narrowest safe command.
3. Compare local and running versions, configuration selection, state, readiness, and recent logs without exposing secrets.
4. Correlate user time, deployment, restart, queue, provider, and error events.
5. Separate confirmed evidence from hypotheses and recommend the smallest next diagnostic or remediation.

## Route Or Remediate

- Confirmed code defect with known behavior: enter Fix.
- Missing capability or ambiguous expected behavior: enter Shape.
- Environment or operational cause with authorized corrective action: remain in Operate, mutate only the explicit target, and verify the live consumer afterward.
- Approval or external access still required after safe diagnostics: report the exact blocker; do not translate missing evidence into success.

## Complete

Completion requires live read-back from the affected runtime or consumer, not source inspection or a local substitute. Report the cause, commands and scopes used, mutation performed when any, post-remediation evidence, remaining risk, and exact blocker.

If the repair passes locally and the user deploys separately, report “verified locally; production verification pending.” After deployment, check the original symptom on that runtime before declaring the operational problem resolved. A diagnosis-only request stops with findings and a proposed next action. Retain relevant context through [evidence.md](evidence.md).
