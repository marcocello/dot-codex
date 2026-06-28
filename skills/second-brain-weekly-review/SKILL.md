---
name: second-brain-weekly-review
description: >-
  Run a weekly review of the user's Notion Second Brain. Use when the user says
  SECOND BRAIN | Weekly Review, asks for a weekly review, wants stale
  tasks/deals/ideas reviewed, or wants Codex to summarize open loops.
---

# Second Brain Weekly Review

Use the Notion structure defined in `docs/secondbrain.md`.

Live surfaces:
- `SB - Tasks`
- `SB - Deals`
- `SB - Ideas`

## Workflow

1. Review tasks:
   - overdue or stale tasks;
   - waiting items;
   - tasks with missing next steps.
2. Review deals:
   - deals without next step;
   - deals with old next-step dates;
   - low-confidence deal changes.
3. Review ideas:
   - proposed or review ideas;
   - ideas that should become tasks;
   - ideas that should be parked or archived.
4. Produce a compact review summary.

## Rules

- Do not add new Notion tables or schema unless explicitly asked.
- Do not bulk-import external source content.
- Do not silently advance or close deals unless evidence is explicit or the user asks.
- If write access is unavailable, provide exact manual updates instead of pretending the
  system was changed.

## Handoff

Report:
- Tasks needing action.
- Deals needing next steps.
- Ideas to review.
- Suggested changes that still need approval.
