---
name: coding-secret-audit
description: Audit tracked and non-ignored untracked checkout files for hardcoded secrets with GitGuardian and for personal information such as emails, local user-home paths, and cloud subscription identifiers before commit, publish, deploy, or handoff.
---

# Secret And Personal Information Audit

Purpose: detect exposed credentials and personal information, keep credentials redacted, and show exact personal-information matches in the conversation.

## Workflow

1. Confirm the repository:
   - `git rev-parse --show-toplevel`
   - `git status --short`
2. Run the bundled lifecycle:
   - `python skills/coding-secret-audit/scripts/run_gitguardian_audit.py --root <repo-root>`
   - Use `GGMCP_URL` only for an explicitly managed server; otherwise the runner installs or reuses ggmcp through `uvx`, starts it on loopback, scans, and stops it.
   - Require `GITGUARDIAN_PERSONAL_ACCESS_TOKEN`. Missing authentication blocks the explicit audit; never report it as a skip or gate result.
3. Review the structured report:
   - Secret findings always block.
   - Personal-information findings block only when repository visibility is confirmed `public`.
   - Confirmed `private` or `unknown` visibility emits a warning and continues when there are no secret findings.
   - Print every reported personal-information value in chat with its repository-relative file, line, detector, visibility, and disposition.
4. Contextually inspect the same checkout for possible personal names, postal addresses, phone numbers, customer identifiers, or account details that deterministic structure cannot establish safely. For a supported finding, print only the smallest exact personal-information value needed to identify it, not the surrounding line or file contents. Apply the same public/private rule to findings supported by context.
5. Recommend remediation; do not edit or revoke anything unless the user asks.

The deterministic scanner selects files with:

```bash
git ls-files --cached --others --exclude-standard -z
```

It skips ignored files, deleted paths, directories, binary files, and oversized files. It detects structured personal emails, absolute macOS/Linux/Windows user-home paths, and UUID subscription identifiers in subscription configuration fields. Do not expand this into an open-ended natural-language keyword list.

## Repository Visibility

Resolve visibility in this order:

1. `AUDIT_REPOSITORY_VISIBILITY=public|private|internal|unknown`
2. provider CI contracts such as `GITHUB_REPOSITORY_VISIBILITY` or `CI_PROJECT_VISIBILITY`
3. read-only `gh repo view --json visibility --jq .visibility`
4. `unknown`

Only confirmed `public` makes personal-information findings blocking. An unavailable or unauthenticated provider lookup remains `unknown` and must be reported.

## PAT Storage

Keep the GitGuardian PAT outside repository config:

```bash
export GITGUARDIAN_PERSONAL_ACCESS_TOKEN="<token>"
```

Prefer a shell secret manager, password-manager injection, or CI secret. Never write the PAT into `config.toml`, `.env` committed to Git, skill files, prompts, memories, or command arguments.

## Output And Disclosure

For every personal-information finding, print in chat:

- repository-relative file path
- detector or category
- line range
- exact matched personal-information value
- repository visibility and source
- blocking or warning disposition
- remediation action

Do not mask, truncate, hash, or replace a detected personal-information value with `[redacted]`. Never print raw secrets, provider error bodies, request payloads, surrounding file contents, or the PAT.

## Remediation

For a secret:

1. Revoke or rotate it at the provider.
2. Remove it from the working tree and history where necessary.
3. Replace it with an environment variable, secret manager lookup, or ignored local config.
4. Re-run the audit.

For personal information:

1. Confirm whether publication is intentional.
2. Replace local paths and identifiers with portable placeholders or configuration.
3. Remove unnecessary identity data.
4. Re-run the audit and verify repository visibility.

## Failure Handling

- If ggmcp or `uvx` is unavailable, report the actionable setup failure.
- If authentication is missing, return `NEED_INPUT` for a GitGuardian PAT. Do not downgrade the requested audit to success.
- If visibility cannot be confirmed, warn and continue for personal information only; secret findings and scanner failures still block.
- If provider responses are incomplete or inconsistent, fail closed without printing the response body.
- `scripts/gate` never invokes this skill.
