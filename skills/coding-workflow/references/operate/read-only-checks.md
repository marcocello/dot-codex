# Read-Only Diagnostic Menu

Load this only after the first Operate pass identifies a relevant area. Keep scopes narrow and redact secrets.

## Host, Processes, And Python

```bash
pwd
git status --short
lsof -iTCP -sTCP:LISTEN -n -P
ps aux | sed -n '1,40p'
python --version
which python
python -m pip --version
python -m pip check
```

Do not print complete `.env` files. Inspect only variable names or targeted non-secret values. Run the narrowest failing test before broad installs or upgrades.

## PostgreSQL

```bash
psql --version
pg_isready
psql -X -v ON_ERROR_STOP=1 -d "${PGDATABASE:-postgres}" -c 'select current_database(), current_user, now();'
```

Avoid password-bearing connection strings on the command line. Prefer already configured `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, and `PGPASSWORD`.

## Docker

```bash
docker version
docker compose version
docker ps --all --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
docker compose ps
docker logs --tail 200 <container>
docker inspect <container> --format '{{json .State}}'
```

For image mismatches, compare the local image tag or digest with the deployed image rather than assuming the same label means the same build.

## Kubernetes And AKS

```bash
kubectl config current-context
kubectl cluster-info
kubectl get nodes -o wide
kubectl get deploy,rs,po,svc,ingress -n <namespace> -o wide
kubectl get events -n <namespace> --sort-by=.lastTimestamp
kubectl describe pod <pod> -n <namespace>
kubectl logs <pod> -n <namespace> --tail=200 --timestamps
kubectl logs <pod> -n <namespace> --previous --tail=200 --timestamps
kubectl rollout history deploy/<deployment> -n <namespace>
az aks show -g <resource-group> -n <aks-name> --query '{name:name,powerState:powerState.code,kubernetesVersion:kubernetesVersion,provisioningState:provisioningState}' -o table
```

## Azure Static Web Apps And Monitor

```bash
az staticwebapp show -g <resource-group> -n <name> --query '{name:name,defaultHostname:defaultHostname,repositoryUrl:repositoryUrl,branch:branch,sku:sku.name}' -o table
az staticwebapp environment list -g <resource-group> -n <name> -o table
az monitor app-insights query --app <name> --analytics-query "exceptions | where timestamp > ago(2h) | take 20" -o table
```

Do not list secrets or deployment tokens. Start with short query windows and expand only when the symptom predates them.

## Common Evidence Patterns

- Image pull failure: image name, registry authorization, tag, pod events.
- Crash loop: previous logs, command, required variables, health probes.
- 502/503: service selectors, endpoints, ingress, readiness.
- Static route failure: route config, deployed branch/environment, linked API health.
- PostgreSQL failure: host, port, database, user, SSL mode, container networking.
- Local-only failure: language version, lock state, selected environment, ports, database readiness, compose service names.
