# On-Prem / Customer-Managed Requirement Patterns

Use this reference when drafting customer technical requirements for a customer-managed VM, cloud subscription, on-prem environment, or locked-down deployment.

## Customer-Facing Pattern

Title:

`# <Customer> / <Vendor> VM Responsibilities`

Opening:

`Date: <YYYY-MM-DD>`

`Purpose: define who owns each part of the customer-managed <product> deployment inside <customer>-controlled infrastructure.`

Use ownership headings:

`## <Customer> Provides And Maintains`

`## <Vendor> Provides And Maintains`

Use small section headings instead of dense bullets when readability matters:

`### VM`

`Azure Debian/Ubuntu VM starting at 4 vCPU and 16 GB RAM.`

`### Persistent App Storage`

`50 GB minimum persistent VM disk mounted into Docker for /data. This stores the application database, workspaces, generated documents, attachment cache, and runtime files. Storage must survive container rebuilds and restarts, and it must be expandable without changing the application.`

`### TLS And DNS`

`One hostname such as https://app.customer.com, one TLS certificate in the customer key vault or certificate store, deployment identity access to that certificate, and HTTPS termination on the VM reverse proxy.`

## Topics To Consider

VM:
CPU, RAM, OS family, whether the VM is customer-managed, and who patches it.

Storage:
Disk or file share, minimum size, mount path, persistence, backups, retention, restore test, expandability, file-locking risk, and alert threshold.

TLS/DNS:
Hostname, certificate location, certificate access, reverse proxy termination, renewal owner, and expiry alerting.

Database or mirror:
Source system, mirrored tables/files, refresh cadence, freshness visibility, read-only access, and no direct production-system access when that is the boundary.

Attachments and file exchange:
Stable folder structure, sync/extraction owner, allowed formats, source of truth, retention, and backup.

Identity and mailbox:
App registration owner, delegated versus application permissions, callback URL, client secret or certificate, mailbox scope, sender allowlist, and subject/filter rules when relevant.

LLM endpoint:
Provider, tenant, endpoint URL, deployment/model name, API key or identity method, region, quota/cost guardrails, data residency, and logging policy.

Network:
Outbound HTTPS destinations, package/container registry access, firewall/proxy rules, private endpoint requirements, and DNS resolution.

Monitoring:
VM health, disk usage, certificate expiry, backup success, data mirror freshness, file share availability, app health, container health, and alert recipient.

Vendor runtime:
Container images, Docker Compose, env vars, storage mounts, reverse proxy routes, first-run validation, app logs, job diagnostics, runtime troubleshooting, and app-level security controls.

## Internal Risk Pattern

Create a separate `internal_codebase_risks.md` when repo inspection finds mismatches between the target requirement and current implementation.

Each risk should be one short section:

`## <Risk In Plain English>`

`Current code does <observed behavior>. The customer target requires <target behavior>. The delivery work is <specific gap>.`

Good internal risks include:

Frontend not containerized while the VM target requires Docker.

Secrets stored in Key Vault while the app currently consumes env vars or mounted files.

Customer wants read-only SQL mirror while the current module consumes a workbook, CSV, local file, or mocked data.

SQLite and filesystem storage are acceptable for a pilot but need disk, backup, restore, and file-locking validation.

OAuth code uses delegated Graph scopes while the customer expects single-tenant-only or application permissions.

Existing Kubernetes, Terraform, or hosted deployment files do not match the VM package.

Health checks only verify the API/database while the customer needs deeper checks for external services, file shares, workers, and data freshness.

## Review Checklist

Before finalizing:

Check that customer-facing language states requirements, not questions.

Check that internal risks are not mixed into the customer-facing file.

Check that only one default option is recommended for open items unless the user asked for alternatives.

Check that storage includes size, persistence, mount, backup, restore, expansion, and alerting.

Check that TLS, DNS, identity, LLM, database/mirror, network, and monitoring have concrete owners.

Check that company names are correct and consistent.

Check that the final response names changed files and whether tests were run.
