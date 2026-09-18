# Second Brain Contract

Use this file for personal operating work that is not software feature implementation, issue repair, code review, deployment, or repo maintenance.

## Second Brain

Use Notion as the operating system for activity tracking, manual notes, Granola captures, Gmail follow-ups, Zotero-derived ideas, Git/Codex work summaries, deal tracking, and activity briefs.

Notion is the system of record for organized state. Native source systems stay where they are.

The hub and data source IDs below are placeholders, not usable configuration. Resolve the actual IDs from the connected Notion workspace or user-provided context before API access. Keep credentials outside repository documentation.

Canonical Notion hub: https://app.notion.com/p/<second-brain-hub-id>

## Account and workspace for this chat

For read-only `knowledge-notion-review` work, including reads handed to `knowledge-notion-api`, use all connected accounts and their accessible workspaces by default without an initial selection question. Honor any explicit user scope, keep connection identities and resolved IDs separate by workspace, and label findings with their source. Offer optional narrowing after the review and report unavailable sources while continuing with accessible ones. This exception does not select a destination for writes; the selection rules below still apply to requested updates and other Notion work.

At the start of Notion work in a chat, before searching, reading, or writing Notion content, ask once: “Which Notion account and workspace should I use for this chat?” If the user already explicitly selected both in this chat, use that selection without asking again. Available connection labels may help present the choices; do not infer the destination from a default connection, a single connected account, or a previous chat.

Keep the selected account, workspace, connection identity, and resolved data-source IDs in the conversation context. Reuse them for every subsequent Notion operation and across Notion skill handoffs in this chat, including after compaction. Do not ask again on each turn or persist this choice as a default for other chats.

Use only a connector or local API configuration verified to access the selected account and workspace. If the selection is ambiguous or unavailable, ask for the missing detail or report the access blocker before accessing content; never silently switch accounts or workspaces. If the user explicitly changes the selection, replace the chat context and resolve the destination IDs again. A conflicting page link or destination requires clarification before access, not an automatic switch.

## Notion Structure

Use only these three active tables by default:

- `SB - Tasks`: concrete next actions and waiting items.
- `SB - Deals`: commercial opportunities and sales-thread state.
- `SB - Ideas`: proposals, experiments, research takeaways, and non-action insights.

`SB - Inbox` is not part of the active workflow for now. Do not write new rows there unless the user explicitly asks to restore inbox capture.

Do not add separate projects, sources, resources, activity-log, archive, people, companies, inbox, or notes databases unless the user explicitly asks.

## Data Sources

Resolve these placeholders to the actual Notion data source IDs before API access:

- `tasks`: `<tasks-data-source-id>`
- `deals`: `<deals-data-source-id>`
- `ideas`: `<ideas-data-source-id>`

## Fields

Use the existing Notion properties. If a property is missing, do not create a new table or schema by default; report the exact manual adjustment needed.

Recommended fields by table:

- `SB - Tasks`: `Task`, `Status`, `Priority`, `Due Date`, `Next Step`, `Evidence`, `Confidence`, `Source Link`.
- `SB - Deals`: `Deal`, `Stage`, `Next Step`, `Next Step Date`, `Evidence`, `Confidence`, `Source Link`.
- `SB - Ideas`: `Idea`, `Status`, `Next Step`, `Evidence`, `Confidence`, `Source`.

Use conservative select values:

- Task status: `Active`, `Waiting`, `Scheduled`, `Done`, `Dropped`.
- Idea status: `Proposed`, `Review`, `Active`, `Parked`, `Archived`.
- Deal stage: `Lead`, `Discovery`, `Proposal`, `Negotiation`, `Won`, `Lost`, `Dormant`.
- Confidence: `High`, `Medium`, `Low`.
- Source: `Manual`, `Granola`, `Gmail`, `Zotero`, `Git Repo`, `Codex`, `Other`.

## Native Sources

Keep external systems native:

- Gmail stays in Gmail.
- Zotero stays in Zotero.
- Git repos stay on disk.
- Granola stays in Granola unless the user asks Codex to extract outcomes.
- Codex threads stay in Codex unless a durable outcome should become a task, deal, or idea.

Codex may inspect native sources when requested, then write concise derived records into Notion.

## Skills

Use these local skills for Second Brain work:

- `knowledge-capture` (Second Brain mode: supplied material or requested source gathering)
- `knowledge-notion-review` (brief or weekly mode)
- `knowledge-notion-api`

User-facing workflow names:

- `KNOWLEDGE | Capture` (Second Brain destination)
- `KNOWLEDGE | Notion Review` (brief or weekly)
- `KNOWLEDGE | Notion API`

## Operating Rules

- Classify manual notes, Granola extracts, pasted snippets, and Codex outcomes directly into `SB - Tasks`, `SB - Deals`, or `SB - Ideas`.
- Create `SB - Tasks` rows only for concrete next actions.
- Create or update `SB - Deals` only for commercial opportunities or sales-thread updates.
- Create `SB - Ideas` rows for proposals, experiments, research takeaways, and reusable insights that are not yet actions.
- If raw material is too ambiguous to classify, ask one short question or create a low-confidence `SB - Ideas` row marked `Review`.
- Use `Review`, `Proposed`, or low confidence when evidence is weak.
- Keep source links or short evidence on derived records.
- Do not bulk-import Gmail, Zotero, Git repo content, or full Codex transcripts.
- Do not invent owners, due dates, deal stages, commitments, people, or company relationships.

## Tooling

Prefer an available Notion connector for capture. Use the local `knowledge-notion-api` skill/script when its actual configuration and required operation are verified and MCP table reads are unavailable, plan-gated, or too indirect. Its current placeholder IDs and limited CLI do not establish usable read/write access; incomplete reads cannot establish that a record is absent. If the required operation is unavailable, return exact manual proposals instead.

Never hardcode Notion credentials in repo files. The local API script must read the local plaintext token file outside the repo. If no Notion write access exists in the current session, do not pretend records were changed. Return the exact Notion table, fields, and values the user should create or update.

## Deal Safety

Deals are commercial state. Codex may propose deal updates from indirect evidence, but should not silently advance, close, or materially rewrite a deal unless the user asks or the source evidence is explicit.

## Handoff

Default to a short human receipt:

- What was captured, processed, or reviewed.
- Which Notion tables changed.
- What remains in `Review` or `Proposed`.
- Any external systems checked.
