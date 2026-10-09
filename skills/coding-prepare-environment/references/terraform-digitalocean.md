# DigitalOcean Terraform adaptation

Use this reference after the shared [Terraform conventions](terraform.md) when the requested target is DigitalOcean. Keep the same component/stage roots, fixed `local.input` metadata, naming helpers, `this` labels, file separation, and `terraform fmt` formatting. This is an adaptation of Marco's Azure structure, not a convention observed in the source repositories.

The bundled [DigitalOcean root](../assets/terraform/digitalocean-root) contains:

| File | Responsibility |
| --- | --- |
| `main.tf` | Naming locals, `input`, and the project environment |
| `providers.tf` | `digitalocean/digitalocean` and authentication through the operator environment |
| `backend.tf` | S3-compatible remote state in an existing DigitalOcean Spaces bucket |
| `project.tf` | Component/stage Project; replaces Azure's `rg.tf` organizational role |
| `tags.tf` | Root-owned tag resources derived from the metadata map |

Add `app.tf`, `compute.tf`, `k8s.tf`, `network.tf`, `storage.tf`, `database.tf`, `custom_domain.tf`, `certificate.tf`, and `output.tf` only as needed. This starter does not choose between App Platform, Droplets, and DigitalOcean Kubernetes or provision a database by default. The React/FastAPI scaffold copier does not include these assets.

## Provider and metadata

- Copy the five files into an absent selected root; selectively adapt an existing root without changing its state or addresses. Replace every `REPLACE_*` marker before planning.
- Keep `cloud = "digitalocean"`. Set `location` to the selected DigitalOcean region slug, such as `fra1`, rather than an Azure display name. Use the requested region supported by the actual resource, not a guessed regional equivalent.
- Select Terraform `required_version` and provider `version` constraints from the target toolchain before initialization. The Spaces example uses the modern S3 backend's `endpoints` and `use_lockfile` arguments; it requires a compatible Terraform release (lockfiles require Terraform 1.10 or later). Generate and commit the root's own `.terraform.lock.hcl`.
- Supply the API token through `DIGITALOCEAN_TOKEN`. Spaces credentials for the DigitalOcean provider use `SPACES_ACCESS_KEY_ID` and `SPACES_SECRET_ACCESS_KEY` only when that provider manages Spaces resources. Do not store credentials in `locals`, tfvars, or provider blocks.
- Remove unused prefix helpers and DNS locals. For frontend roots, change `component` to `frontend`, `prefix_dns` from `api` to `app`, and the literal backend key to the frontend key.
- Set `project_environment` explicitly to `Development`, `Staging`, or `Production` to match the selected stage. The template's `Development` is a starter value, not an inferred production environment.

## Projects and tags

A DigitalOcean Project groups resources by URN; it does not supply Azure Resource Group containment, region, inherited tags, or an IAM scope. The starter names the project from the component/stage prefix so independent frontend/backend roots do not both own one project. If the application uses a shared Project instead, give its creation one owner and reference it from other roots.

When resources are added, associate their supported URNs through the Project's `resources` argument or the `digitalocean_project_resources` resource. Choose one assignment mechanism for a given Project and preserve its existing ownership; do not add a competing assignment manager in another root. An empty starter Project does not automatically collect newly created resources.

DigitalOcean tags are strings. Keep `custom_tags = local.input` as the common metadata map, then let `tags.tf` create `<prefix>:<key>:<value>` names. The prefix gives each root its own tag ownership. Empty values such as the unused `service` key are excluded. For resources that support a list of tags, use:

```hcl
tags = [for tag in digitalocean_tag.this : tag.name]
```

Do not pass the metadata map directly to a DigitalOcean resource's `tags` argument. Not every resource supports tags, and Project membership is separate from tagging. Tag names allow letters, numbers, colons, dashes, and underscores, with a 255-character limit. Use a tag-safe owner slug and region slug rather than an email or a display name with spaces. Check all final names; avoid silently sanitizing values into colliding tags. Preserve canonical capitalization for existing tags instead of renaming them to match the starter's lowercase default.

## Remote state in Spaces

The S3 backend and DigitalOcean provider authenticate separately. For the backend, supply a dedicated Spaces key through `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in the Terraform process environment. These AWS-named variables contain Spaces credentials in this setup; the DigitalOcean API token and `SPACES_*` provider variables do not configure the S3 backend. Preserve unrelated AWS credentials and use the established operator credential flow.

The template assumes an existing private state bucket. Replace `REPLACE_STATE_BUCKET`, `REPLACE_SPACES_REGION`, and the literal key. The endpoint selects the Spaces region; `region = "us-east-1"` supplies the AWS SDK signing configuration, not the compute region. Keep the key unique per stage/project/component. Do not reference locals in the backend block or provision its state bucket in the same root that needs it for initialization.

The compatibility switches skip AWS IAM/STS/metadata checks and S3 checksums for this S3-compatible service. The template does not request AWS bucket-level SSE encryption, which Spaces does not support. Confirm privacy, access policy, versioning, and recovery on the selected bucket before storing real state. Avoid CDN/public access for state.

`use_lockfile = true` requests Terraform's S3 lockfile. HashiCorp tests this backend against Amazon S3, while Spaces offers partial S3 compatibility. A successful local validation cannot establish atomic locking on Spaces. Before concurrent use, exercise lock contention against a disposable state key with the selected endpoint, Terraform version, and permissions, including lock creation, refusal by a second writer, and cleanup. If that target cannot enforce locking, use an established backend with verified locking or an explicitly serialized workflow; do not silently disable locking and call the setup ready. Never force-unlock another task's active state.

Existing remote state location or backend selection takes precedence over this example. Selecting DigitalOcean as the resource provider does not require moving an existing state store.

## Optional capability files

- `compute.tf`: requested Droplets, selected image/size, established SSH keys, and network/firewall rules. Do not open administrative access or invent a paid machine size as a formatting default.
- `app.tf`: requested App Platform app and its source/image configuration. Preserve the actual build and deployment ownership.
- `k8s.tf`: requested DigitalOcean Kubernetes cluster or data source for an existing cluster. Keep manifests beside backend `tf/` when that matches the selected project layout.
- `storage.tf`: selected volumes or Spaces data buckets. Terraform state storage and application storage have distinct ownership and credentials.
- `database.tf`: requested managed database, access controls, and sensitive connection outputs. Do not create a database merely because the app starter uses PostgreSQL locally.
- `custom_domain.tf` / `certificate.tf`: DNS records, supported certificate bindings, and renewal ownership for the selected compute platform. Reuse existing shared zones; do not copy Azure Key Vault or ACME identity resources.

Use sensitive outputs for necessary credentials. Provider schema validation is separate from API permissions, product availability, DNS propagation, resource readiness, and a real application check.

## Verification and sources

Follow the shared reference's Git whitelist and local verification commands from each root. In a disposable copy, run `terraform fmt -check -diff`, `terraform init -backend=false -input=false`, and `terraform validate`. Check backend/frontend metadata, valid tags, and distinct state keys. Remote backend initialization, plan/apply, locking, and deployed application checks require the authorized target and credentials; this template work does not perform them.

The adaptation uses DigitalOcean's [provider reference](https://docs.digitalocean.com/reference/terraform/reference/), [Project resource](https://docs.digitalocean.com/reference/terraform/reference/resources/project/), [Tag resource](https://docs.digitalocean.com/reference/terraform/reference/resources/tag/), [tag constraints](https://docs.digitalocean.com/reference/api/reference/tags/), and [Spaces S3 compatibility](https://docs.digitalocean.com/products/spaces/reference/s3-compatibility/), plus HashiCorp's [S3 backend reference](https://developer.hashicorp.com/terraform/language/backend/s3). Checked on 2026-10-09. The assets contain no account identifiers, existing state, or credentials.

Maintainer verification on 2026-10-09: Terraform 1.14.3 and DigitalOcean provider 2.104.0 validated the original template and adapted backend/frontend copies with remote state disabled. The registry connection failed over IPv6; the official package was fetched over IPv4, checked against the registry's SHA-256, and installed from a temporary filesystem mirror. Recursive formatting, skill validation, and diff checks passed. Terraform console evaluated the actual naming locals in provider-free copies: backend/frontend DNS labels and tag ownership were distinct, tags were valid, and the empty service was excluded. State keys were distinct and all new assets were visible to Git. Provider startup required execution outside the sandbox. The repository gate retained its unrelated failure on existing tracked `vendor/` fixture files in `docs/features/outcome-continuity/`. No API token, Spaces credential, cloud resource, or remote state was used. Spaces connectivity, encryption policy, versioning, locking, and deployment remain unverified. Evidence remains in native task/tool history (partial capture).
