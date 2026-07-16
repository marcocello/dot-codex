---
name: second-brain-external-sweep
description: Review Gmail, Zotero, Git, Granola, Codex work, or other native sources and create concise Notion Second Brain task, deal, or idea updates.
---

# Second Brain External Sweep

Use the Notion structure defined in `docs/secondbrain.md`.

External sources stay native:
- Gmail stays in Gmail.
- Zotero stays in Zotero.
- Git repos stay on disk.
- Granola stays in Granola unless the user captured a transcript.
- Codex threads stay in Codex unless a durable outcome should be recorded.

## Workflow

1. Identify the requested source scope and time window.
2. Use the relevant connector or local read-only checks.
3. Extract only concise derived records:
   - Commitments and waiting items -> `SB - Tasks`.
   - Commercial movement -> `SB - Deals`.
   - Research takeaways, proposals, or experiments -> `SB - Ideas`.
4. Keep source links or short evidence on every derived row.
5. Prefer `Proposed`, `Needs Review`, or low confidence when evidence is indirect.

## Rules

- Do not bulk-import source bodies, papers, repo contents, or full transcripts.
- Do not send emails, mutate external systems, deploy, push, or run destructive commands
  unless the user explicitly asks and approves when required.
- Do not treat generic activity as a task; there must be a real next action.
- For deals, do not silently advance, close, or materially rewrite a deal from indirect
  evidence.
- If no Notion write access exists, provide exact manual Notion updates.

## Handoff

Report:
- Sources checked.
- Derived tasks, deals, and ideas created or proposed.
- Any source that could not be accessed.
- Any item needing user review.
