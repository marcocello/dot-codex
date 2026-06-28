# Second Brain Contract

Use this file for personal operating work that is not software feature
implementation, issue repair, code review, deployment, or repo maintenance.

## Second Brain

Use Notion as the operating system for activity tracking, manual notes, Granola
captures, Gmail follow-ups, Zotero-derived ideas, Git/Codex work summaries,
deal tracking, and activity briefs.

Notion is the system of record for organized state. Native source systems stay
where they are.

Canonical Notion hub:
https://app.notion.com/p/<second-brain-hub-id>

## Notion Structure

Use only these three active tables by default:

- `SB - Tasks`: concrete next actions and waiting items.
- `SB - Deals`: commercial opportunities and sales-thread state.
- `SB - Ideas`: proposals, experiments, research takeaways, and non-action insights.

`SB - Inbox` is not part of the active workflow for now. Do not write new rows
there unless the user explicitly asks to restore inbox capture.

Do not add separate projects, sources, resources, activity-log, archive, people,
companies, inbox, or notes databases unless the user explicitly asks.

## Data Sources

Use these Notion data source IDs for API access:

- `tasks`: `<tasks-data-source-id>`
- `deals`: `<deals-data-source-id>`
- `ideas`: `<ideas-data-source-id>`

## Fields

Use the existing Notion properties. If a property is missing, do not create a new
table or schema by default; report the exact manual adjustment needed.

Recommended fields by table:

- `SB - Tasks`: `Task`, `Status`, `Priority`, `Due Date`, `Next Step`, `Evidence`,
  `Confidence`, `Source Link`.
- `SB - Deals`: `Deal`, `Stage`, `Next Step`, `Next Step Date`, `Evidence`,
  `Confidence`, `Source Link`.
- `SB - Ideas`: `Idea`, `Status`, `Next Step`, `Evidence`, `Confidence`,
  `Source`.

Use conservative select values:

- Task status: `Active`, `Waiting`, `Scheduled`, `Done`, `Dropped`.
- Idea status: `Proposed`, `Review`, `Active`, `Parked`, `Archived`.
- Deal stage: `Lead`, `Discovery`, `Proposal`, `Negotiation`, `Won`, `Lost`,
  `Dormant`.
- Confidence: `High`, `Medium`, `Low`.
- Source: `Manual`, `Granola`, `Gmail`, `Zotero`, `Git Repo`, `Codex`, `Other`.

## Native Sources

Keep external systems native:

- Gmail stays in Gmail.
- Zotero stays in Zotero.
- Git repos stay on disk.
- Granola stays in Granola unless the user asks Codex to extract outcomes.
- Codex threads stay in Codex unless a durable outcome should become a task,
  deal, or idea.

Codex may inspect native sources when requested, then write concise derived
records into Notion.

## Skills

Use these local skills for Second Brain work:

- `second-brain-capture-raw-input`
- `second-brain-external-sweep`
- `second-brain-activity-brief`
- `second-brain-weekly-review`
- `second-brain-notion-api`

User-facing workflow names:

- `SECOND BRAIN | Capture Raw Input`
- `SECOND BRAIN | External Sweep`
- `SECOND BRAIN | Activity Brief`
- `SECOND BRAIN | Weekly Review`
- `SECOND BRAIN | Notion API`

## Operating Rules

- Classify manual notes, Granola extracts, pasted snippets, and Codex outcomes
  directly into `SB - Tasks`, `SB - Deals`, or `SB - Ideas`.
- Create `SB - Tasks` rows only for concrete next actions.
- Create or update `SB - Deals` only for commercial opportunities or sales-thread
  updates.
- Create `SB - Ideas` rows for proposals, experiments, research takeaways, and
  reusable insights that are not yet actions.
- If raw material is too ambiguous to classify, ask one short question or create
  a low-confidence `SB - Ideas` row marked `Review`.
- Use `Review`, `Proposed`, or low confidence when evidence is weak.
- Keep source links or short evidence on derived records.
- Do not bulk-import Gmail, Zotero, Git repo content, or full Codex transcripts.
- Do not invent owners, due dates, deal stages, commitments, people, or company
  relationships.

## Tooling

Prefer the local `second-brain-notion-api` skill/script for Notion reads and
writes when MCP table reads are unavailable, plan-gated, or too indirect.

Never hardcode Notion credentials in repo files. The local API script must read
the local plaintext token file outside the repo. If no Notion write access
exists in the current session, do not pretend records were changed. Return the
exact Notion table, fields, and values the user should create or update.

## Deal Safety

Deals are commercial state. Codex may propose deal updates from indirect
evidence, but should not silently advance, close, or materially rewrite a deal
unless the user asks or the source evidence is explicit.

## Handoff

Default to a short human receipt:

- What was captured, processed, or reviewed.
- Which Notion tables changed.
- What remains in `Review` or `Proposed`.
- Any external systems checked.
