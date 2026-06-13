---
name: coding-critical-secret-audit
description: Audit the current git checkout for critical hardcoded secrets with GitGuardian ggmcp. Use when the user asks Codex to scan local tracked, staged, modified, or untracked non-ignored files for leaked credentials, API keys, tokens, passwords, private keys, or other critical secrets before commit, publish, deploy, or handoff.
---

# Critical Secret Audit

Purpose: scan the current checkout for exposed credentials without putting raw secret values in the
conversation.

## Default Workflow

1. Confirm the working directory is the repository to audit:
   - `git rev-parse --show-toplevel`
   - `git status --short`
2. Prefer the bundled helper:
   - `python skills/coding-critical-secret-audit/scripts/scan_current_checkout.py --root <repo-root>`
3. If the helper cannot be used, reproduce its file-selection rule exactly:
   - `git ls-files --cached --others --exclude-standard -z`
   - Include tracked and untracked non-ignored files from the current checkout.
   - Skip ignored files, deleted paths, directories, binary files, and oversized files.
4. Send file contents to GitGuardian ggmcp `scan_secrets`, not to the user-facing answer.
5. Report only redacted metadata:
   - file path
   - detector or policy-break type
   - line range
   - severity or `unknown`
   - remediation action
6. Do not print raw secret values, matched substrings, request payloads, or file contents.

## GitGuardian ggmcp

Use GitGuardian/ggmcp as the scanner. The current ggmcp server exposes `scan_secrets`, whose
arguments are:

```json
{
  "documents": [
    {"document": "<file content>", "filename": "path/from/repo"}
  ]
}
```

The helper calls the HTTP tool endpoint:

```bash
ENABLE_LOCAL_OAUTH=false MCP_PORT=8000 MCP_HOST=127.0.0.1 \
  uvx --from git+https://github.com/GitGuardian/ggmcp.git gg-mcp-server
```

Then, in another shell:

```bash
GGMCP_URL=http://127.0.0.1:8000 \
  GITGUARDIAN_PERSONAL_ACCESS_TOKEN=<token> \
  python skills/coding-critical-secret-audit/scripts/scan_current_checkout.py --root <repo-root>
```

If a native GitGuardian MCP tool is already callable in the active Codex session, it is acceptable
to call `scan_secrets` directly. Keep the same file-selection and redaction rules.

## Severity Rules

- Treat explicit `critical` and `high` severities as critical.
- Treat scan findings with no severity as critical until triaged; proactive scan responses may not
  include incident severity.
- Treat every detected secret as requiring immediate revoke/rotate unless GitGuardian validity or
  incident context proves otherwise.

## Remediation Output

For each finding, recommend:

1. Revoke or rotate the credential in its provider first.
2. Remove the secret from the working tree.
3. Replace it with an environment variable, secret manager lookup, or local ignored config file.
4. Re-run the same scan command.

Do not edit files automatically unless the user asked for remediation, because removing secrets can
break local configuration and the credential still must be revoked.

## Failure Handling

- If ggmcp is unavailable, say the scan is blocked and provide the exact server command above.
- If authentication is missing, say a GitGuardian token or OAuth-authenticated ggmcp session is
  required.
- If the scan fails for size or rate limits, reduce `--batch-size` or `--max-bytes` and retry.
- If findings are present, do not claim the checkout is safe.
