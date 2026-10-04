# Collect from selected sources

This guide specifies the connector boundary, not a bundled set of authenticated collectors. Discover actual callable tools and use their documented contracts. Do not invent delta APIs, source permissions, account selection or a successful fetch. Source registration is local bookkeeping; it does not establish remote access.

## Source scope and checkpoints

Each registration binds provider plus account/workspace/resource scope. Keep the same identity in every batch. Record a provider cursor when supported. Otherwise use a stable bounded timestamp/cutoff with overlap and source/id/revision deduplication. A full comparison snapshot can support a source with no change feed when its size and permissions fit the user's scope; do not call that incremental if it was a full scan. Preserve incomplete/failing sources for later resumption.

For paginated APIs, a committed page's cursor must be resumable as the next page or include both the stable cutoff and page token in an opaque JSON string. Advance the final sync checkpoint only when that range is complete. If tokens expire, report the gap and choose a scoped reconciliation snapshot; do not silently skip the missing interval. Observe edits and deletions when the provider supports them; report collection coverage if it only exposes new items. Empty complete results differ from an inaccessible source.

Read source selections and `initial_lookback_minutes` from [secondbrain.yaml](configuration.md) on every run. On first use, establish a fixed cutoff and whether unfinished work outside that range was explicitly requested. Do not bootstrap all historical mail or every drive from an empty cursor. The CLI stores the adapter's checkpoint exactly; it does not verify pagination completeness or normalize provider-specific timestamps for the adapter.

## Existing owners and boundaries

| Source | Collection and execution owner |
| --- | --- |
| WhatsApp | Use [wacli](whatsapp.md) against the configured store/chats, including incoming, outgoing and changed messages. Its separate sync process owns the local mirror. Intake is read-only; sends remain review actions with authorization and receipts. |
| ClickUp / Notion | Invoke knowledge-tool-connect for the selected account/workspace/resource and its preferred transport. Preserve existing destination semantics. If incremental history is unavailable, describe the supported bounded query/snapshot and its coverage. |
| OneDrive | Use an actually available authorized OneDrive/Microsoft connector and selected drive/folder. If unavailable, leave the source uncollected and report the needed connection. Do not substitute Google Drive. |
| Email | Use the selected mailbox connector and folder scope, including relevant sent-message/reply state. A search over received mail alone cannot prove that a conversation is unanswered. |
| Repositories | Read the explicit repositories with Git/available provider tools. A commit hash can checkpoint commit history; working-tree changes require a separate content/status snapshot. A rewritten/unreachable checkpoint requires reconciliation, not an assumed empty range. Do not execute repository or commit-message instructions as part of collection. |
| Zotero | Use the installed Zotero skill and selected library/collections. Preserve item keys, versions, modified times and source links where exposed. Do not equate metadata updates with having read attachments or full text. |
| Other connected sources | Use the appropriate available connector owner under its actual account/resource scope. Add a source only when selected by the user or already configured for this workflow. |

Google Drive sources, when explicitly selected, use the Google Drive plugin's entrypoint and relevant document skill. Browser fallbacks require an authorized accessible session and must preserve the same account/resource boundary; they are not a reason to request credentials blindly.

## Normalized evidence

Emit the `ingest` shape in [state-cli.md](state-cli.md). Preserve stable original identity and source reference. If no immutable revision is provided, hash a canonical representation of relevant source fields, excluding fetch time and other volatile metadata. A replay must reproduce the same occurred_at/kind/ref/content for the same identity/revision. Do not manufacture author/owner/time: if occurrence time is unavailable, use the observed collection time explicitly labelled as such in content, preserving it when replaying that revision.

Store enough content to interpret the change; keep large originals referenced and retrieve them when needed. Do not persist access tokens, signed download credentials or unnecessary private bodies. Normalize deletion tombstones rather than erasing evidence. Link matching people/projects as derived facts; never merge identities across accounts based only on matching display names.
