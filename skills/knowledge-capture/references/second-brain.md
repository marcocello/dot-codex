# Second Brain Capture

Use the existing tables, properties and conservative values in `docs/harness/secondbrain.md` in the dot-codex checkout. Only `SB - Tasks`, `SB - Deals`, and `SB - Ideas` are active; Inbox capture is disabled. Resolve actual workspace/data source IDs before access: the contract's IDs are placeholders.

Before any Notion access, follow the account and workspace selection rule in `docs/harness/secondbrain.md`: ask once at the start of Notion work unless the user already selected the account and workspace in this chat, then reuse that choice across turns and skill handoffs.

## Obtain material

- **Supplied input:** use the pasted note, dictation, Granola excerpt, screenshot text, snippet or Codex outcome directly. Do not search other systems merely because a note mentions them.
- **Requested source gathering:** resolve the requested sources and time window from the request or established context; clarify a missing material boundary before sweeping. Read only those sources through available connectors or local read-only checks. Gmail, Zotero, Git, Granola and Codex source material stays native. Extract concise outcomes with source links or short evidence and report inaccessible sources. Do not bulk-import source bodies, repositories, papers or full transcripts, send messages, or mutate the source systems.

Both inputs continue through the same process below.

## Classify, match, write and verify

1. Extract narrow records while preserving uncertainty and useful source wording:
   - Concrete next action or waiting item → `SB - Tasks`. Generic activity alone is not a task.
   - Commercial opportunity or sales-thread evidence → `SB - Deals`.
   - Proposal, experiment, research takeaway or reusable insight → `SB - Ideas`.
   - Ambiguous material → ask one concise question or propose a low-confidence Idea marked `Review`. Create it only when the same access, matching and authorization checks below succeed.
2. Inspect the real schema and relevant existing records through an available Notion connector. Use `knowledge-notion-api` only when its actual configuration and supported operation are verified. The current local helper has placeholder IDs, a limited listing and no CLI update command: its presence does not establish usable capture access. Never send requests to placeholder IDs or assume an unsupported update works. Do not modify the adapter, install tools or change schemas as part of capture.
3. Match before creating. Compare canonical source links and the actual action, opportunity or idea, including relevant context; titles alone do not establish identity. Follow available pagination or use sufficiently scoped complete queries. If reads are incomplete, do not claim duplicate absence or blindly create. Return a proposal with the missing check instead.
4. For a clear existing match, update only supported, authorized fields through an available write path, preserving unrelated values and existing evidence. If matching is ambiguous, ask or propose alternatives; never merge unrelated records. Create a new row only after sufficient matching checks establish that it is new.
5. Do not invent dates, owners, commitments, people, company relationships or deal stages. Use existing allowed values: `Review` is an Idea status, not a new `Needs Review` option. Indirect commercial evidence supports a proposed change; do not silently advance, close or materially rewrite a deal. Keep evidence distinct from interpretation and preserve sensitive values privately without printing secrets in chat.
6. Read back actual writes and confirm the destination, row identity and intended fields. Connector success alone is not verification. If verification fails, report the attempted write as unverified and inspect its identity before retrying; do not blindly create a second row.

## Unavailable access and receipt

When configured reads, a necessary write operation, or reliable matching are unavailable, return exact manual proposals: target table, create/update intent, existing row identity when known, and field/value pairs. Omit unknown values rather than inventing them, and identify the missing capability or unresolved match. Do not claim that proposed rows were saved.

For verified writes, report the row title/identity, table and anything still in `Review` or `Proposed`. For a sweep, also report sources checked and unavailable sources. Keep source evidence concise and private; no automatic Markdown note or Zotero import accompanies these Notion outcomes.
