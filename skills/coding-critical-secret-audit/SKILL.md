---
name: coding-critical-secret-audit
description: Audit tracked, staged, modified, and non-ignored untracked files for critical hardcoded secrets with GitGuardian before commit, publish, deploy, or handoff.
---

# Critical Secret Audit

Purpose: scan the current checkout for exposed credentials without putting raw secret values in the conversation.

## Default Workflow

1. Confirm the working directory is the repository to audit:
   - `git rev-parse --show-toplevel`
   - `git status --short`
2. Prefer the bundled lifecycle runner:
   - `python skills/coding-critical-secret-audit/scripts/run_gitguardian_audit.py --root <repo-root>`
   - It uses `GGMCP_URL` when explicitly configured; otherwise it provisions an ephemeral loopback server through `uvx`.
   - It requires `GITGUARDIAN_PERSONAL_ACCESS_TOKEN`. Missing authentication blocks the explicit audit; it is never reported as a skip or gate result.
3. If a native GitGuardian MCP tool is already callable, invoke `scan_secrets` directly with the same scope and redaction rules.
4. If neither path can be used, reproduce the bundled scanner's file-selection rule exactly:
   - `git ls-files --cached --others --exclude-standard -z`
   - Include tracked and untracked non-ignored files from the current checkout.
   - Skip ignored files, deleted paths, directories, binary files, and oversized files.
5. Send file contents to GitGuardian ggmcp `scan_secrets`, not to the user-facing answer.
6. Report only redacted metadata:
   - file path
   - detector or policy-break type
   - line range
   - severity or `unknown`
   - remediation action
7. Do not print raw secret values, matched substrings, request payloads, or file contents.

## GitGuardian ggmcp

Use GitGuardian/ggmcp as the scanner. The current Streamable HTTP server exposes `scan_secrets` through JSON-RPC `tools/call` at `/mcp`, whose tool arguments are:

```json
{
  "params": {
    "documents": [
      {"document": "<file content>", "filename": "path/from/repo"}
    ]
  }
}
```

The skill-owned runner installs or reuses ggmcp through the official uvx distribution path, starts a managed loopback Streamable HTTP server when `GGMCP_URL` is unset, calls the checkout scanner, and terminates the server. `scripts/gate` never invokes this workflow.

```bash
ENABLE_LOCAL_OAUTH=false MULTI_TENANCY_ENABLED=true MCP_PORT=8000 MCP_HOST=127.0.0.1 \
  uvx --from git+https://github.com/GitGuardian/ggmcp.git gg-mcp-server
```

An explicitly managed service remains supported:

```bash
GGMCP_URL=http://127.0.0.1:8000 \
  GITGUARDIAN_PERSONAL_ACCESS_TOKEN=<token> \
  python skills/coding-critical-secret-audit/scripts/scan_current_checkout.py --root <repo-root>
```

The runner prints controlled provisioning, readiness, and audit status only. It suppresses raw installer/server output and never passes the PAT to the managed server environment or process arguments.

## Severity Rules

- Treat explicit `critical` and `high` severities as critical.
- Treat scan findings with no severity as critical until triaged; proactive scan responses may not include incident severity.
- Treat every detected secret as requiring immediate revoke/rotate unless GitGuardian validity or incident context proves otherwise.

## Remediation Output

For each finding, recommend:

1. Revoke or rotate the credential in its provider first.
2. Remove the secret from the working tree.
3. Replace it with an environment variable, secret manager lookup, or local ignored config file.
4. Re-run the same scan command.

Do not edit files automatically unless the user asked for remediation, because removing secrets can break local configuration and the credential still must be revoked.

## Failure Handling

- If ggmcp or `uvx` is unavailable, say the explicit audit is blocked and report the runner's actionable error.
- If authentication is missing, return `NEED_INPUT` for a GitGuardian PAT or use an already authenticated native MCP session. Do not downgrade the requested audit to success or skip.
- If the scan fails for size or rate limits, reduce `--batch-size` or `--max-bytes` and retry.
- If findings are present, do not claim the checkout is safe.
