---
name: knowledge-notion-api
description: Read or write Notion Second Brain tasks, deals, and ideas through the local Notion API when direct access is requested or MCP is unavailable.
---

# Second Brain Notion API

Use this skill for direct Notion API operations on the Second Brain tables
defined in `docs/harness/secondbrain.md`.

Before any Notion access, follow the account and workspace selection rule in `docs/harness/secondbrain.md`, including its read-only review exception. For reads handed off by `knowledge-notion-review`, use the review's account and workspace scope without asking for an initial selection; verify which of those sources the local configuration can access and report any coverage gaps. Otherwise, ask once at the start of Notion work unless the user already selected the account and workspace in this chat, then reuse that choice across turns and skill handoffs.

## Safety

- Never hardcode Notion credentials in repo files.
- Read the integration token only from the local plaintext token file:
  `$HOME/.config/codex/notion_secondbrain_token`.
- Do not print, summarize, or persist the token.
- If no token is available, stop and ask the user to create that file.
- Use the script for reads and writes instead of manually retyping API requests.

## Script

Run:

```bash
python skills/knowledge-notion-api/scripts/notion_secondbrain.py --help
```

Common commands:

```bash
python skills/knowledge-notion-api/scripts/notion_secondbrain.py list tasks
python skills/knowledge-notion-api/scripts/notion_secondbrain.py create-task \
  --title "Follow up with Mario" --status Active --priority Medium
python skills/knowledge-notion-api/scripts/notion_secondbrain.py create-idea \
  --title "Granola insight" --source Granola --status Review
```

The script outputs compact JSON. Use `--raw` for full Notion API responses when
debugging.

## Tables

Use only the canonical Second Brain tables unless the user explicitly asks for
schema work:

- `tasks` -> `SB - Tasks`
- `deals` -> `SB - Deals`
- `ideas` -> `SB - Ideas`

Resolve the current data-source IDs for these tables within the selected account and workspace before first use, using the live Notion structure or user-provided context. Reuse the verified IDs for this chat; resolve them again when the user changes workspace or evidence shows they are stale. The contract contains placeholders, not usable IDs.

## Workflow

1. Read `docs/harness/secondbrain.md` for the current table contract.
2. Verify that the local configuration matches the selected account and workspace before using the script with the token stored in
   `$HOME/.config/codex/notion_secondbrain_token`.
3. For writes, create the narrowest row that matches the user's request.
4. For uncertain derived rows, use `Needs Review`, `Proposed`, or low confidence.
5. Report the changed table, row title, and resulting page URL if available.

## Fallback

If the API rejects a property name or select value, do not invent a new schema.
Return the exact attempted table, fields, values, and API error so the schema can
be adjusted deliberately.
