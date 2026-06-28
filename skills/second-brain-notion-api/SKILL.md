---
name: second-brain-notion-api
description: >-
  Read and write the user's Notion Second Brain through the Notion API instead
  of MCP. Use when the user says SECOND BRAIN | Notion API, asks to read or
  write SB - Tasks, SB - Deals, or SB - Ideas with local API access,
  or when the Notion MCP connector is unavailable, indirect, or plan-gated.
---

# Second Brain Notion API

Use this skill for direct Notion API operations on the Second Brain tables
defined in `docs/secondbrain.md`.

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
python skills/second-brain-notion-api/scripts/notion_secondbrain.py --help
```

Common commands:

```bash
python skills/second-brain-notion-api/scripts/notion_secondbrain.py list tasks
python skills/second-brain-notion-api/scripts/notion_secondbrain.py create-task \
  --title "Follow up with Mario" --status Active --priority Medium
python skills/second-brain-notion-api/scripts/notion_secondbrain.py create-idea \
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

At the beginning of each interaction, read or confirm the current data-source IDs for these
tables from `docs/secondbrain.md`, the live Notion structure, or user-provided context before
running write operations.

## Workflow

1. Read `docs/secondbrain.md` for the current table contract.
2. Use the script with the token stored in
   `$HOME/.config/codex/notion_secondbrain_token`.
3. For writes, create the narrowest row that matches the user's request.
4. For uncertain derived rows, use `Needs Review`, `Proposed`, or low confidence.
5. Report the changed table, row title, and resulting page URL if available.

## Fallback

If the API rejects a property name or select value, do not invent a new schema.
Return the exact attempted table, fields, values, and API error so the schema can
be adjusted deliberately.
