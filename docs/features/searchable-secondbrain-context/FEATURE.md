# Search selected Outlook and WhatsApp context

The operator selects one Microsoft 365 mailbox and explicit WhatsApp chats, collects their readable text into a private workspace, and retrieves source-linked context through the CLI or a read-only MCP tool. Live tools remain available through the existing harness/plugin system.

## Acceptance

- C1: An example configuration starts with sources disabled. Validation requires explicit account/folder or chat scope. Disabled sources and changed scopes cannot expose previously indexed content. No mailbox credential or WhatsApp session material is copied into the index.
- C2: Outlook uses delegated read-only Microsoft Graph access, validates the signed-in mailbox, follows per-folder delta links, and atomically saves each complete page with its checkpoint. Retries do not duplicate documents. Provider failures preserve the affected checkpoint and do not stop independent sources. Deleted messages lose retained payloads. Expired delta state produces an actionable recovery error. A filtered initial import reports Graph's 5,000-message limitation.
- C3: WhatsApp ingestion reads the configured wacli archive without modifying it or connecting to WhatsApp. It imports only selected chats, both directions, and propagates message updates, deletions, and purges. A durable change checkpoint supports restart and backfill; unavailable or expired journal coverage is reported. The adapter fails closed when required archive capabilities are missing.
- C4: The workspace keeps current source text and checkpoints in SQLite, with a recoverable indexing queue and Qdrant vectors generated locally. Search and read return current source references and omit disabled, erased, or stale revisions. A restart preserves searchable content. Index failures retain pending work for retry. Removing a source erases its local retained text and derived vectors through an explicit command.
- C5: The public CLI supports configuration checks, mailbox sign-in, bounded sync, indexing, search, source-linked readback, and source erasure. A read-only MCP server exposes bounded search/read tools with retrieved content labeled as untrusted evidence. No ingestion or retrieval operation sends messages, marks mail read, or executes instructions found in imported text.

## Decisions and verification boundary

Use wacli for archive ingestion. Retain Baileys as a separately enabled bot component. Use local Qdrant and FastEmbed so initial retrieval needs no paid vector service or hosted embedding call. Keep this mutable retrieval store separate from the existing immutable second-brain event history so deletion can erase copied payloads. The existing reasoning/agenda skills can retrieve context through MCP.

Real local storage, indexing, CLI, and MCP behavior require executable proof. Graph and WhatsApp protocol fixtures exercise the real adapters at unavailable external boundaries. Live Microsoft consent, the selected mailbox, phone pairing, archive completeness, and unattended VM execution require operator activation and consumer readback; local fixtures do not establish those claims.
