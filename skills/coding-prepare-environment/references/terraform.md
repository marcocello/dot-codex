# Environment-based Terraform conventions

Use this reference when preparing requested Terraform roots under `deployments/<environment>/tf`. File responsibilities and internal style draw on `twyd-portal` and `meshify-monorepo`, inspected on 2026-10-09. Their historical component-local placement is provenance; the selected default now groups deployment configuration by environment. This convention does not require Azure or cloud provisioning for every project.

For a selected DigitalOcean target, apply the shared layout and internal style below, then read [DigitalOcean adaptations](terraform-digitalocean.md) instead of copying Azure-specific resources or backend settings.

## Placement and files

Use one Terraform root per requested environment, beside that environment's Kubernetes configuration:

```text
deployments/
  dev/
    tf/
      main.tf
      providers.tf
      backend.tf
      rg.tf                 # Azure; DigitalOcean uses project.tf and tags.tf.
      backend_app.tf        # When backend resources are requested.
      frontend_app.tf       # When frontend resources are requested.
      storage.tf            # When persistent infrastructure is required.
      certificate.tf        # When this root owns certificate provisioning.
      output.tf             # When consumers need outputs.
      templates/            # When Terraform renders manifests.
        pv.tpl
        pvc.tpl
    k8s/
  prod/
    tf/
    k8s/
```

Create only required environments, tools, and capability files. Each environment root has its own state key and provider lock file. Backend and frontend resources can share that root while keeping distinct names, metadata, and resource labels. Do not copy two starter roots into one directory or let multiple configurations own the same resource. An accepted requirement for independently owned state can justify separate roots within `deployments/<environment>/tf`; document the concrete ownership and command paths rather than making that split the default.

Preserve existing roots, state keys, resource addresses, and archived environments. This convention does not authorize relocating a component root, merging state, or recreating unused stages. Use environment directories rather than substituting Terraform workspaces for the selected layout.

| File | Responsibility |
| --- | --- |
| `main.tf` | Shared identity data sources, derived naming/tag locals, `input`, and separate maps for existing infrastructure |
| `providers.tf` | `required_providers` and provider configuration; declare every provider used by the root |
| `backend.tf` | Remote state location, separate from the application's backend component |
| `rg.tf` | Azure environment resource groups, with component labels where needed |
| `project.tf` / `tags.tf` | DigitalOcean grouping and metadata adaptation; read the DigitalOcean reference |
| `backend_app.tf` / `frontend_app.tf` | Requested component hosting resources; established descriptive names can remain |
| `storage.tf` | Disks, scoped identity access, and optional PV/PVC rendering |
| `certificate.tf` / `custom_domain.tf` | Certificate lifecycle and domain bindings, when requested |
| `output.tf` | Values consumed outside the root; keep credential outputs sensitive |

Add descriptive files for distinct capabilities when needed. TWYD's `branding.tf` and `branding_certificate.tf` are product-specific extensions, not common starter files. Keep resource-specific data sources and helper locals with the resources that use them.

## Internal style

Use the bundled [Azure root](../assets/terraform/azure-root) as an editable starting point. Its `main.tf` preserves the observed order: shared data sources, naming locals, then `local.input`. Terraform resolves references independently of that textual order.

- Define configuration values and derived settings with `locals`. Keep `input` keys in the observed order: `stage`, `project`, `component`, `service`, `cloud`, `location`, `managedBy`, `owner`. Use separate local maps for other settings. Do not introduce `variable` blocks, `var.*` references, `variables.tf`, tfvars, or `TF_VAR_*` workflows, including for configurable settings. Pass local values to external module arguments when needed. Preserve existing interfaces unless their migration is authorized.
- Provider and backend credential environment variables are authentication, not Terraform input variables. Keep that authentication flow and never put secret values in locals. Backend configuration retains literal values because it cannot reference locals.
- Derive `prefix`, `prefix_condensed`, and `prefix_cut` from stage/project/component. Use hyphenated names where supported and condensed names only where provider constraints require them. Check length and collision constraints; three-character truncation alone does not guarantee uniqueness.
- Use `api` for a production backend DNS prefix and `app` for a production frontend; other stages prepend `<stage>.`. A combined environment root uses distinct component naming maps, DNS locals, and descriptive resource labels instead of reusing one backend prefix for both. Omit DNS locals when no DNS is required.
- Set `custom_tags = local.input`. Apply these tags to taggable resources; use `merge(local.custom_tags, { purpose = each.key })` for a resource-specific tag.
- Use `this` for the primary object of a resource/data type. Use descriptive snake_case labels when multiple objects share a type, such as `aks_disk_access` or `branding`.
- Put related existing-infrastructure values in separate `locals` blocks in `main.tf`, such as `dns`, `keyvault`, and `k8s`. Look up those existing resources with data sources rather than duplicating shared infrastructure.
- Use two-space indentation, aligned assignments, spaces after commas, snake_case Terraform identifiers, and blank lines between blocks. Preserve the existing `managedBy` metadata key. Run `terraform fmt` to resolve spacing rather than copying Meshify's inconsistent alignment.
- Group resource identity/location fields first, operational settings next, and tags after those settings when the block needs grouping. Keep comments brief and explain a constraint or ownership decision.

Example of an optional shared-infrastructure map:

```hcl
locals {
  dns = {
    name                = "REPLACE_DNS_ZONE"
    resource_group_name = "REPLACE_DNS_RESOURCE_GROUP"
  }
}
```

Add corresponding maps for Key Vault or AKS only when the selected deployment uses them. For rendered manifests, read templates with `templatefile("${path.module}/templates/pv.tpl", { ... })`. With the default environment layout, output to the sibling `k8s/` directory. If independent roots are explicitly selected inside `tf/`, adapt the output path to the environment's actual `k8s/` directory. Avoid competing ownership between Terraform-generated files and hand-edited manifests.

## Adapt the template

The steps below describe the Azure asset. For DigitalOcean, use the provider-specific adaptation linked above.

1. Select the provider, component, stage, region, ownership metadata, and existing remote state store from the authorized project context. If Azure is not selected, reuse the organization and adapt provider-specific files rather than copying Azure resources.
2. Copy the four common `.tf` assets once into an absent `deployments/<environment>/tf` root. For an existing root, apply only authorized additions and preserve its layout, backend, resource labels, and lock file. The React/FastAPI scaffold script does not copy these assets.
3. Replace every `REPLACE_*` marker. For a frontend-only root, set `component = "frontend"` and use `app` in `prefix_dns`. For a combined root, adapt the identity map to the selected product ownership and add separate component maps, names, and labels. Remove unused data sources and naming helpers; add only requested capability files.
4. Choose supported Terraform/provider constraints from the project's toolchain and the resources being added. Add `required_version` and provider `version` constraints before initialization; the asset deliberately does not freeze either source repository's historical versions. Declare `azuread`, `acme`, `tls`, `time`, or `local` only when used.
5. Keep a distinct literal backend key per environment root, conventionally `<stage>-<project>`. Explicitly independent roots also need a root-specific suffix. Backend configuration cannot reference `local.input` or other named values. The template assumes an existing state store; provisioning one is separate authorized work.
6. Keep credentials in the operator's established authentication environment. The template contains no subscription IDs, source emails, domains, cloud accounts, state, or private keys. Its `features {}` keeps provider defaults; the sources' `prevent_deletion_if_contains_resources = false` override is not a reusable formatting preference.

For a necessary credential output, follow TWYD's pattern:

```hcl
output "api_key" {
  value     = azurerm_static_web_app.this.api_key
  sensitive = true
}
```

Do not copy Meshify's `nonsensitive(...)` API-key output. Sensitive output marking limits display; it does not remove the value from state. Protect state and saved plans. Certificate renewal, DNS propagation, and identity permissions need target-specific checks; fixed sleeps are not readiness proof.

## Git visibility

Extend the root whitelist's source section for Terraform only when those files are present:

```gitignore
!*.tf
!.terraform.lock.hcl
!*.tpl
```

In the final artifact-blocking section, include:

```gitignore
**/.terraform/
*.tfstate
*.tfstate.*
*.tfplan
*.tfvars
*.tfvars.json
crash.log
crash.*.log
override.tf
override.tf.json
*_override.tf
*_override.tf.json
```

Commit each root's generated `.terraform.lock.hcl`, not a lock copied from a reference project. Do not create tfvars or tfvars examples; configure through locals. Keep the tfvars ignore rules to protect existing local files. Retain other secret/artifact blocks from the stack reference. Verify nested `.tf`, `.tpl`, and lock files are visible with `git check-ignore --no-index`; `.terraform`, state, and plan artifacts must remain ignored. Ignore custom saved-plan filenames too; do not assume every plan has a `.tfplan` suffix.

## Verify the prepared root

Run from each actual root, or use `terraform -chdir=<root> ...`:

```sh
terraform fmt -check -diff
terraform init -backend=false -input=false
terraform validate
```

Use a disposable copy for template maintenance so provider downloads and lock files do not enter the assets. `init -backend=false` installs required providers without initializing remote state. Report provider availability failures separately from formatting results. Validation does not connect to the target cloud or establish deployment readiness.

Before real planning, replace all markers, verify the subscription/state selection, initialize the chosen backend using the established authentication flow, and run the authorized plan. Scaffold preparation does not authorize apply, destroy, state migration, or cluster rollout. Report exactly which local checks ran and which target checks remain.

## Provenance and supporting sources

Inspected source: TWYD revision `a754668f2bcde9ca34f07a22714d70e6f7951c87` and Meshify revision `465b42b42bc9047d4ad26d98a35afb09ad6dcec1`, especially the historical paths `backend/deployment/prod/tf/{main,providers,backend,rg,storage,certificate}.tf` and `frontend/deployment/prod/{main,providers,backend,rg,app,custom_domain,output}.tf`. These paths describe the source projects, not the current default. The reference repositories were read only; future use needs no access to them. The reusable assets contain sanitized shared patterns, not their deployment configuration.

Terraform behavior checked against HashiCorp's [backend configuration](https://developer.hashicorp.com/terraform/language/backend), [formatting command](https://developer.hashicorp.com/terraform/cli/commands/fmt), [dependency lock file](https://developer.hashicorp.com/terraform/language/files/dependency-lock), and [validation command](https://developer.hashicorp.com/terraform/cli/commands/validate) documentation.

Maintainer verification on 2026-10-09: Terraform 1.14.3 formatting passed. A disposable copy initialized with the existing cached AzureRM 4.71.0 provider and remote backend disabled. The original template and adapted backend/frontend roots passed `terraform validate`; provider startup required execution outside the filesystem sandbox. The documented whitelist kept nested sources, templates, and lock files visible while excluding state, plans, overrides, tfvars, and provider caches. Skill validation and diff checks passed. The repository gate's harness checks passed, but its common check failed on pre-existing tracked `vendor/` fixture files under `docs/features/outcome-continuity/`. No source repository, cloud resource, or remote state was changed. Evidence remains in native task/tool history (partial capture). This historical validation preceded the environment-based placement; it does not claim a state migration or combined-resource deployment was tested.
