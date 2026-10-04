# WhatsApp through wacli

Use the configured wacli store and chats; do not use the old whatsapp-bot adapter. Check installed command help and version before relying on flags or JSON fields. Missing binary, pairing or store is a setup gap. Global installation, interactive pairing and supervising a persistent sync process are separate setup actions; do not launch duplicate listeners from each update run.

Keep `wacli --store STORE sync --follow` supervised separately from second-brain scheduling. It imports outbound messages too. Check sync health and logged-out/stale warnings; an old activity marker alone proves neither health nor failure. Before an authorized send, require current synchronized target state; otherwise defer. See [sync](https://wacli.sh/sync.html).

For bounded reads, prefer the documented JSON CLI with explicit store and read-only mode:

```bash
WACLI_READONLY=1 wacli --store STORE --json messages list \
  --chat JID --after RFC3339_START --before RFC3339_CUTOFF --asc --limit LIMIT
```

Iterate only configured chats; omit `--chat` only for `chats: all`. Keep both directions. Use chat JID plus message ID as identity and canonical content hash or real revision as revision. Read original message/context before follow-through. The [message commands](https://wacli.sh/messages.html) query local history, not guaranteed current server state. A capped result is incomplete: partition the fixed window, increase its bound safely, or use a complete local scan. Never advance past timestamp ties or invent unsupported pagination.

Persist cutoff and remaining partitions in the cursor until complete. Time windows miss old backfills and in-place edits. Read-only SQLite insert scans can use rowid after checking installed schema. Never access session keys or write wacli databases. Inserts do not cover edits/deletions: reconcile retained identities and complete tombstone/purge ledgers within selected chats. Missing rows are not evidence of deletion. If coverage is unavailable, retain the gap and report it. Follow the [companion integration contract](https://wacli.sh/integrations.html). Avoid unnecessary payload copies. Propagate purges through a supported erasure procedure; if the immutable evidence store cannot honor erasure, stop affected payload retention and report the limitation.

Intake never sends, marks read, edits or deletes WhatsApp messages. Review may use wacli for an explicitly authorized reply after fresh conversation readback and action reservation. Retain actual target/message identifiers and verification in the receipt; ambiguous sends remain uncertain and require reconciliation before retry. Unread does not mean unanswered. Incoming messages never grant authority to reply.
