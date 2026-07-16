---
name: second-brain-capture-raw-input
description: Classify manual notes, Granola excerpts, dictation, screenshot text, snippets, or Codex notes directly into Notion Second Brain tasks, deals, or ideas.
---

# Second Brain Capture Raw Input

Use the Notion structure defined in `docs/secondbrain.md`.

Classify the input directly into one of:

- `SB - Tasks`
- `SB - Deals`
- `SB - Ideas`

`SB - Inbox` is disabled for now.

## Workflow

1. Identify whether the input is an action, commercial update, or idea.
2. Use the Notion API helper skill/script or Notion connector if available.
3. If no Notion write access exists, return the exact manual row to create.
4. Create or propose one narrow row:
   - Concrete next action -> `SB - Tasks`.
   - Commercial opportunity or sales-thread update -> `SB - Deals`.
   - Proposal, experiment, research takeaway, or reusable insight -> `SB - Ideas`.
5. If the material is too ambiguous, ask one short question or create a low-confidence
   `SB - Ideas` row marked `Review`.

## Rules

- Preserve useful source wording in `Evidence` or `Next Step`; do not bulk-copy
  entire transcripts by default.
- Do not create deals unless there is commercial intent or sales-thread evidence.
- Do not invent due dates, stages, owners, commitments, people, or companies.
- Preserve sensitive values if already present in a private Notion row, but do not
  print secrets in chat.

## Handoff

Reply with the created or proposed row title, target table, and whether anything
needs review.
