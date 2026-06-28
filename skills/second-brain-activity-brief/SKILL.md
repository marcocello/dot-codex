---
name: second-brain-activity-brief
description: >-
  Produce a concise operating brief from the user's Notion Second Brain. Use
  when the user says SECOND BRAIN | Activity Brief, asks what to focus on, asks
  for an update on activities, tasks, deals, waiting items, stale work, or ideas.
---

# Second Brain Activity Brief

Use the Notion structure defined in `docs/secondbrain.md`.

Read only:
- `SB - Tasks`
- `SB - Deals`
- `SB - Ideas`

## Workflow

1. Read active, scheduled, and waiting tasks.
2. Read deals with open next steps or stale next-step dates.
3. Read ideas with `Status = Proposed` or `Status = Review`.
4. Produce a compact brief.

## Brief Format

Use this order:

1. `Now`: the highest-leverage tasks or deal next steps.
2. `Waiting`: people or external dependencies blocking movement.
3. `Stale`: tasks or deals with old or missing next steps.
4. `Ideas`: proposed or review ideas worth deciding.
5. `Suggested next actions`: practical actions, clearly labeled as suggestions.

## Rules

- Separate confirmed Notion state from recommendations.
- Do not create or update rows unless the user asks.
- Keep the brief short enough to act on.
- If Notion access is unavailable, say what could not be read and avoid inventing state.
