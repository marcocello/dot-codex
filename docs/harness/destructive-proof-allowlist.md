# Destructive Proof Allowlist

Some realistic provider proofs need destructive setup, cleanup, or send actions. These actions
must remain explicit and narrow.

## File

Use this optional repo-local file:

```text
.codex/approvals/destructive-proof-allowlist.json
```

Shape:

```json
{
  "approvals": [
    {
      "id": "hubspot-base-test",
      "enabled": true,
      "cwd": "/absolute/repo/path",
      "command": "exact command string",
      "target": "provider:resource",
      "expires": "YYYY-MM-DD"
    }
  ]
}
```

## Match Rules

A destructive proof may proceed only when all fields match:

- `enabled` is `true`
- `expires` is unexpired
- `cwd` exactly matches the current working directory
- `command` exactly matches the full command string
- `target` exactly names the provider and resource

Do not infer approval from similar commands. Do not allow wildcards, shell chains, broad delete
commands, unknown targets, or expired entries.

The allowlist is repo policy only. Platform or runtime approval prompts still take precedence.
