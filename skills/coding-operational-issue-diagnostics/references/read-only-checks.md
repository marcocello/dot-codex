# Read-Only Diagnostic Checks

Use these commands as a menu after the preflight pass. Keep scopes narrow and redact secrets.

## Local Files, Processes, and Ports

```bash
pwd
git status --short
find . -maxdepth 2 -type f \( -name '*.log' -o -name '.env*' \) -print
lsof -iTCP -sTCP:LISTEN -n -P
ps aux | sed -n '1,40p'
```

Do not print complete `.env` files. Inspect only variable names or targeted non-secret values.

## Local Python or Virtualenv

```bash
pwd
git status --short
python --version
which python
python -m pip --version
python -m pip check
python -m pip list --format=freeze | sed -n '1,120p'
```

If the repo has tests, run the narrowest failing test first. Avoid broad installs or dependency
upgrades during diagnostics unless the user asks for repair.

## PostgreSQL and psql

```bash
psql --version
pg_isready
psql -X -v ON_ERROR_STOP=1 -d "${PGDATABASE:-postgres}" \
  -c 'select current_database(), current_user, now();'
psql -X -v ON_ERROR_STOP=1 -d "${PGDATABASE:-postgres}" \
  -c 'select datname from pg_database order by datname;'
```

Avoid connection strings on the command line when they include passwords. Prefer `PGHOST`,
`PGPORT`, `PGDATABASE`, `PGUSER`, and `PGPASSWORD` environment variables if credentials are
already configured.

## Docker

```bash
docker version
docker compose version
docker ps --all --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
docker compose ps
docker logs --tail 200 <container>
docker inspect <container> --format '{{json .State}}'
```

For image mismatch issues, compare the local image tag/digest with the deployed image:

```bash
docker image inspect <image> --format '{{index .RepoDigests 0}}'
kubectl get deployment <name> -n <namespace> -o jsonpath='{.spec.template.spec.containers[*].image}'
```

## Kubernetes and AKS

Start with the active context:

```bash
kubectl config current-context
kubectl cluster-info
kubectl get nodes -o wide
kubectl get ns
```

Narrow to the namespace whenever possible:

```bash
kubectl get deploy,rs,po,svc,ingress -n <namespace> -o wide
kubectl get events -n <namespace> --sort-by=.lastTimestamp
kubectl describe pod <pod> -n <namespace>
kubectl logs <pod> -n <namespace> --tail=200 --timestamps
kubectl logs deploy/<deployment> -n <namespace> --all-containers --tail=200 --timestamps
kubectl rollout history deploy/<deployment> -n <namespace>
kubectl top pod -n <namespace>
kubectl top node
```

For crash loops, inspect the previous container logs:

```bash
kubectl logs <pod> -n <namespace> --previous --tail=200 --timestamps
```

For AKS resource state:

```bash
az aks list -o table
az aks show -g <resource-group> -n <aks-name> \
  --query '{
    name:name,
    powerState:powerState.code,
    kubernetesVersion:kubernetesVersion,
    provisioningState:provisioningState
  }' \
  -o table
az aks nodepool list -g <resource-group> --cluster-name <aks-name> -o table
```

## Azure Static Web Apps

```bash
az staticwebapp list -o table
az staticwebapp show -g <resource-group> -n <static-web-app> \
  --query '{
    name:name,
    defaultHostname:defaultHostname,
    repositoryUrl:repositoryUrl,
    branch:branch,
    sku:sku.name
  }' \
  -o table
az staticwebapp environment list -g <resource-group> -n <static-web-app> -o table
az staticwebapp hostname list -g <resource-group> -n <static-web-app> -o table
```

Do not run commands that list secrets or deployment tokens. If the issue is a failed deployment,
check the CI provider logs and correlate with the Static Web App branch/environment.

## Azure Monitor and Application Insights

Find candidate monitoring resources:

```bash
az monitor app-insights component show -g <resource-group> -a <app-insights-name> -o table
az monitor log-analytics workspace list -g <resource-group> -o table
```

Query recent failures when the workspace or Application Insights app is known:

```bash
az monitor app-insights query \
  --app <app-insights-name> \
  --analytics-query "exceptions | where timestamp > ago(2h) | take 20" \
  -o table

az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "ContainerLogV2 | where TimeGenerated > ago(2h) | take 50" \
  -o table
```

Keep query windows small first. Expand only if the symptom predates the initial window.

## Common Failure Patterns

- Image pull errors: compare image name, registry auth, image tag, and pod events.
- CrashLoopBackOff: inspect previous logs, container command, required env vars, and health probes.
- 502/503 ingress errors: inspect service selectors, endpoints, ingress annotations, and pod
  readiness.
- Static Web App route failures: inspect `staticwebapp.config.json`, deployed branch/environment,
  and linked API/function health.
- PostgreSQL connection failures: check socket/host, port, database name, user, SSL mode, and
  container networking.
- Local-only failures: compare Python version, dependency lock state, `.env` selection, local
  ports, PostgreSQL readiness, and Docker compose service names/ports.
