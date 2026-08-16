# CLI Toolkit Runtime Contract

Use this as a checklist, then verify the current repository implementation because limits can evolve.

## Archive

- Maximum archive: 5 MiB.
- Maximum expanded content: 10 MiB.
- Maximum members: 100.
- Maximum individual source/resource member: 512,000 bytes.
- Supported compression: stored or DEFLATE.
- Allowed non-directory members: root `kit.json`, `.py`, and runtime-supported `.json` resources.
- Reject absolute, parent-traversing, hidden, duplicate, aliased, symlink, executable-mode, installer, native, and unsupported-compression members.
- Read every member fully so CRC/decompression corruption fails activation.
- Parse JSON strictly: reject non-finite numbers and values beyond the runtime depth/node budget.

## Manifest

Root keys are exactly:

```json
{
  "id": "stable-kit-id",
  "version": "1.0.0",
  "name": "Customer-safe kit name",
  "description": "Customer-safe description.",
  "contract_version": "1",
  "tools": []
}
```

Each tool has exactly:

```json
{
  "name": "domain.action",
  "description": "What this deterministic operation does.",
  "entrypoint": "src/tool.py",
  "timeout_seconds": 30,
  "input_schema": {},
  "output_schema": {}
}
```

- Identity/tool names use letters, digits, dot, underscore, and hyphen, start alphanumeric, and are at most 120 characters.
- Tool names beginning with `coworker.` or `twyd.` are reserved.
- Entrypoints are relative declared `.py` members and must parse as Python.
- Timeout is greater than zero and at most 30 seconds.
- Maximum tools per kit: 50.
- Kit and tool descriptions are trimmed, nonempty, and bounded.

## Schema Subset

Supported keywords:

```text
type properties required additionalProperties items const enum
minimum maximum minLength maxLength minItems maxItems
```

Supported types: `object`, `string`, `number`, `integer`, `boolean`, and `array`.

Do not use regex patterns, formats, unions, references, conditional schemas, arbitrary additional-property schemas, or unbounded implicit alternatives. Use nested required objects to express mutually coupled values, such as `{unit, value}`.

## Invocation

- Portal wraps each MCP tool input as `{client_request_id, input}`.
- Portal validates schema and commits Team/Coworker/channel-owned invocation intent before runtime contact.
- The runtime resolves the immutable exact kit/tool, copies it to a disposable workspace, invokes Python without a shell, and supplies JSON on stdin.
- The child receives only runtime-owned bounded environment values and runs as the dedicated unprivileged identity.
- Output must be one strict finite JSON value matching `output_schema`.
- Equivalent replay returns the durable terminal receipt and must not start a second process.

## Deployment-Owned Data

Keep large, mutable, secret, licensed, or customer-specific databases outside the kit. Mount them read-only in the runtime, use one fixed subpath, and document permissions for the execution UID. Catalog, receipts, workspaces, and customer data require separate storage boundaries.
