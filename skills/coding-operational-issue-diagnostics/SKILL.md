---
name: coding-operational-issue-diagnostics
description: Diagnose runtime and operational failures with read-only checks across local processes, Docker, PostgreSQL, Azure, Kubernetes, deployments, logs, and environment boundaries.
---

# Operational Issue Diagnostics

Purpose: gather evidence quickly and safely across local runtime, databases, containers, Kubernetes, and Azure so the root cause can be narrowed before changing code or infrastructure.

## Safety Rules
- Start read-only. Do not run `kubectl delete`, `kubectl apply`, `kubectl edit`, `kubectl scale`, `az delete`, `az deployment`, restarts, rollouts, secret reads, or write operations unless the user explicitly asks for remediation.
- Treat database writes as destructive. Do not run SQL statements other than metadata or read-only `SELECT` checks unless the user explicitly asks for remediation.
- State the active Azure subscription and Kubernetes context before interpreting cloud results.
- Do not print secret values, deployment tokens, kubeconfigs, connection strings, or full environment dumps. Redact sensitive values if they appear in logs.
- Prefer bounded commands: use explicit namespaces, resource groups, time windows, and log tails.
- If production resources may be touched, pause before any command that can alter state.

## First Pass
1. Identify the symptom, expected behavior, failing environment, affected service, and timeframe.
2. Check local evidence first when the bug is reproducible locally:
   - active virtualenv/interpreter and dependency versions
   - app test command or narrow reproduction command
   - Docker image/container status when the service runs in a container
   - PostgreSQL client/readiness when database connectivity is part of the symptom
3. Run the bundled preflight script for a broad read-only baseline:

```bash
skills/coding-operational-issue-diagnostics/scripts/ops_diag_preflight.sh \
  --namespace <kubernetes-namespace> \
  --resource-group <azure-resource-group> \
  --static-web-app <swa-name>
```

Use only the flags that are known. Add `--all-namespaces` only when a broad AKS scan is justified.

4. Read `references/read-only-checks.md` for deeper command sets after preflight identifies the likely area: local runtime, PostgreSQL, Docker, AKS, Azure Static Web Apps, or Azure Monitor.

## Investigation Flow
1. Establish context
   - `pwd`, git branch/status, current app configuration file, selected `.env` pattern.
   - Relevant local service status and ports when the app runs outside Kubernetes.
   - `az account show` and `kubectl config current-context` when cloud is involved.
2. Reproduce or bracket the failure
   - Run the narrowest failing local command if available.
   - Compare local runtime values to container and cluster runtime values without exposing secrets.
3. Inspect cloud health
   - Local: process status, bound ports, logs, Docker containers, database readiness.
   - AKS: nodes, pods, events, deployments, replica sets, services, ingress, recent logs.
   - Azure Static Web Apps: resource state, environments, custom domains, deployment history when available, linked APIs/functions, and monitor logs when configured.
   - Azure Monitor/Application Insights: query recent exceptions, failed requests, dependency failures, and traces for the affected timeframe.
4. Correlate timestamps
   - Align user-reported time, deployment time, pod restarts, events, and error logs.
   - Convert time zones explicitly when needed.
5. Report findings before fixes
   - Separate confirmed evidence from hypotheses.
   - Include exact command outputs that matter, with secrets redacted.
   - Recommend the smallest next diagnostic or corrective action.

## Output
- Lead with the most likely cause if evidence supports one.
- Include a short timeline when deployments, restarts, or errors overlap.
- List commands run and their result status.
- If blocked, state the missing access, tool, namespace, subscription, resource group, or log sink.
