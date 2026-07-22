# Destructive Proof Allowlist

Optional: `.codex/approvals/destructive-proof-allowlist.json`.

```json
{
  "approvals": [{
    "id": "provider-test",
    "enabled": true,
    "cwd": "/absolute/repo",
    "command": "exact command",
    "target": "provider:resource",
    "expires": "YYYY-MM-DD"
  }]
}
```

All fields exact. Enabled. Unexpired. No wildcard, shell chain, broad delete, unknown target, similar-command inference.

Repo allowlist never overrides platform approval.
