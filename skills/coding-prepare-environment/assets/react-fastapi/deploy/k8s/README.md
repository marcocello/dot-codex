# Kubernetes release

The included single-replica baseline follows the reference projects' separate application/database deployments, probes, resource budgets, and persistent storage. It needs an existing cluster, default storage class, ingress controller, registry access, and a TLS Secret named `app-tls`. There is no cloud provisioning or certificate-controller installation. PostgreSQL is a single StatefulSet, not a highly available managed database. Back up and restore-test data before upgrades.

Build and push the backend (`docker build -t REGISTRY/backend:RELEASE backend`) and web (`docker build -f frontend/Dockerfile -t REGISTRY/web:RELEASE .`) only when publishing is authorized. Use immutable release tags or digests. Configure image pull credentials on the namespace service account if the registry is private. Select the target context explicitly for every cluster command.

Render locally, without credentials or cluster access:

```sh
python3 scripts/render_k8s.py --backend-image registry.example.com/app/backend:r1 --web-image registry.example.com/app/web:r1 --domain app.example.com --namespace my-app --release r1 --ingress-class nginx --output build/k8s-r1
```

Create the namespace and an `app-secrets` Secret through your secret manager or a private env file using `kubectl --context CONTEXT -n my-app create secret generic app-secrets --from-env-file=/private/path/k8s.env`. Required keys: `POSTGRES_PASSWORD`, `DATABASE_URL` (SQLAlchemy `postgresql+psycopg` URL pointing to `db:5432/app`, user `app`, with the same URL-encoded password), `DEPLOY_USER`, `DEPLOY_PASSWORD_HASH` (Caddy bcrypt hash). Do not reuse the host-development database URL. The Secret file must be outside the checkout, mode 0600; never put it in rendered assets. Install `app-tls` separately. The web image gates all paths with Basic Auth; replace that shared demo gate only after implementing appropriate application access controls.

After inspecting rendered files and selecting/authorizing the destination, run each stage in order. A migration failure must stop the release:

```sh
kubectl --context CONTEXT -n my-app apply -f build/k8s-r1/db-service.json -f build/k8s-r1/db.json
kubectl --context CONTEXT -n my-app rollout status statefulset/db --timeout=180s
kubectl --context CONTEXT -n my-app apply -f build/k8s-r1/migrate.json
kubectl --context CONTEXT -n my-app wait --for=condition=complete job/migrate-r1 --timeout=300s
kubectl --context CONTEXT -n my-app apply -f build/k8s-r1/backend-service.json -f build/k8s-r1/backend.json
kubectl --context CONTEXT -n my-app rollout status deployment/backend --timeout=180s
kubectl --context CONTEXT -n my-app apply -f build/k8s-r1/web-config.json -f build/k8s-r1/web-service.json -f build/k8s-r1/web.json
kubectl --context CONTEXT -n my-app rollout status deployment/web --timeout=180s
kubectl --context CONTEXT -n my-app apply -f build/k8s-r1/ingress.json
curl --fail --user owner https://app.example.com/api/ready
```

Use a unique release name per migration attempt; inspect `kubectl ... logs job/migrate-r1` on failure. Do not apply the whole directory at once: Kubernetes does not order independent resources or wait for migrations. Do not automate these lines without fail-fast handling. Validate manifests with server-side dry-run on the chosen cluster before the first release when access is authorized.

Inspect `kubectl ... get pods,svc,ingress,pvc`, `logs deployment/backend --tail=100`, and `logs deployment/web --tail=100`. PostgreSQL backup: `kubectl ... exec db-0 -- pg_dump -U app -d app -Fc > /private/backup.dump` with `umask 077`; verify restores on a separate namespace/database. Protect backups and keep copies outside the cluster. Application rollback: render the previous image revisions with a new release name, apply only the application deployments, and verify readiness. Migrations remain applied; incompatible schemas require a forward fix or an explicitly planned restore. Secret/ConfigMap changes require an application rollout restart. Deleting a namespace/PVC can destroy data; it is not part of rollback.
