---
name: customer-tech-requirements
description: Turn transcripts, decks, repo context, or dictation into customer-facing technical requirements, deployment prerequisites, responsibility splits, and separate internal risk notes.
---

# Customer Tech Requirements

## Workflow

1. Ground the document in current evidence before writing. Read the user-provided transcript, deck, existing requirement doc, repo docs, deployment files, Terraform, Docker/Kubernetes assets, and relevant code paths. Do not rely only on the user's rough description when local artifacts exist.

2. Separate audiences. Put customer-facing requirements in one document and codebase or delivery risks in a separate internal document when both are needed. Do not mix "what the customer must provide" with "what our code still lacks" unless the user explicitly wants one combined file.

3. Use practical ownership sections. For most customer asks, start with "Customer Provides And Maintains" and "Vendor Provides And Maintains", replacing the labels with real company names when known. Let headings carry ownership so every paragraph does not repeat "Customer provides..." or "Vendor maintains...".

4. Prefer one concrete default over option lists. If an aspect is open, propose one recommended path and mark it as the working assumption. Add alternatives only when the user asks for options.

5. Keep the customer document short and specific. Use section-based prose or short bullets depending on the user's format preference. Avoid bold-heavy checklists, abstract headings like "Azure environment", and vague asks like "access to cloud resources".

6. Translate codebase mismatches into internal risks. If current code expects env vars, a local disk, SQLite, OAuth delegated scopes, a static frontend deployment, or a workbook input, say that internally. In the customer-facing doc, state the target requirement cleanly.

7. Finish with changed files and any verification. For Markdown-only changes, say no tests were run. If risks are based on current code inspection, cite the files or paths that support them in the final response.

## Default Output Shape

When creating files, default to:

`docs/<customer>_<deployment>/customer_requirements.md`

`docs/<customer>_<deployment>/internal_codebase_risks.md`

Use lowercase folder names with underscores only when the repo already prefers that style or the user asks for it. Otherwise follow the repo's existing document naming style.

## Requirement Topics

Cover only topics that are relevant to the deployment. Common sections:

VM, persistent app storage, shared file storage, VM access, OS and backups, TLS and DNS, SQL/database mirror, attachment file share, identity app registration, mailbox or API access, LLM endpoint, network allowlisting, infrastructure monitoring, deployment package, container health, application runtime, and application security.

For storage, specify the minimum size, mount type, mount path if known, persistence behavior, backup retention, restore test expectation, expandability, and low-storage alert threshold. For a small single-VM pilot, a practical baseline can be "50 GB minimum persistent VM disk mounted into Docker for `/data`" if the user has not given a different value.

For identity, state the app registration owner and the required permission mode. Do not hide important implementation facts such as delegated OAuth versus application permissions.

For secrets and certificates, distinguish source from consumption. A customer can keep secrets and certificates in Key Vault, while the VM deployment may still need to inject them into Docker as environment variables or mounted files and pass the TLS certificate to the reverse proxy.

For data integrations, preserve the customer's target architecture even if current code is not wired yet. Put the implementation gap in the internal risk file.

## Style Rules

Use the customer's real name when the user asks for it. Use "ScaleUp Labs", not "ScaleUp", when referring to this company.

Prefer concrete nouns and numbers: "4 vCPU and 16 GB RAM", "50 GB persistent disk", "nightly backups with 30-day retention", "alerting at 80% capacity", "read-only SQL access".

Avoid weak requirement language such as "should confirm", "might provide", or "we need to ask if possible". Write the requirement directly unless it is genuinely unresolved.

Keep public wording calm and operational. Do not expose internal code shortcomings in the customer-facing file unless the user asks for a transparent technical gap list.

Read `references/onprem-requirements-patterns.md` when drafting a VM/on-prem/customer-managed deployment requirement.
