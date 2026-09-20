# Notion connections

For MCP, inspect actual tools and their account/workspace identity binding before content access. Use the exact requested page/data source and existing properties; follow the user’s structure, never invent categories or schema. Missing plugin/connection and MCP limits follow knowledge-tool-connect’s guided recovery.

The bundled API handles data-source page properties only, not page body/block editing, arbitrary pages or every provider endpoint. Confirm operation support before proposing API setup. DESTINATION below is an explicit data-source UUID or configured legacy alias.

## Credential setup

Reuse the selected profile’s credential. Otherwise ask whether the user already has a compatible integration token. This client requires bot identity with workspace metadata; a personal user token is not interchangeable. Consult the current official [authorization guide](https://developers.notion.com/docs/authorization) for creating an internal connection and granting the requested content access, then guide [private token storage](credentials.md). Accept a user-selected chat token through credential intake, or a private reference; do not assume all pages become accessible after connection. Existing OAuth tokens are accepted; this helper does not implement OAuth enrollment. Explain incompatible credential/capability limits before setup.

## Direct API

For `transport=api`, use `"${CODEX_HOME:-$HOME/.codex}/skills/knowledge-tool-connect/scripts/notion_api.py"`. Global `--config PATH`, `--profile NAME` and optional `--transport api` precede the command. The override changes no saved preference. The canonical profile resolver is in this skill’s scripts directory.

Configure an integration bot account UUID and workspace UUID. Content operations take a data-source UUID (not a database ID); no data sources are required just to connect. Compact UUIDs are accepted. Use exactly one inline `token`, existing `token_env`, or private `token_file` reference and optional `auth_type=internal|oauth`; both use Bearer authentication. Never use the former fixed token path. Personal user tokens lacking bot workspace identity are unsupported. The client verifies `/users/me` bot/workspace identities before data-source access, refuses redirects and never automatically retries writes.

- `discover --token-env NAME` or `--token-file PATH`: identity/workspace metadata only; no profile mutation or content search. Setup may invoke this before a profile exists.
- `check`: authenticated identity and exact source metadata/schema verification for configured legacy aliases, if any. Without aliases this verifies identity/workspace only.
- `fields DESTINATION`: actual source property schema, including existing options.
- `list DESTINATION`: paginated accessible pages, checking scope and cursor/completeness signals. Notion’s 10,000-result/query cap and incomplete responses produce an error instead of a partial success; this helper does not implement time-window partitioning.
- `get DESTINATION PAGE_ID`: exact scoped page.
- `create DESTINATION --data-file PATH`, `update DESTINATION PAGE_ID --data-file PATH`: JSON object mapping existing property names to simple values. Title/rich_text accept plain strings up to 2000 characters; select/status accept existing option names or null; URL accepts HTTP(S) or null; number accepts finite numbers or null; checkbox accepts boolean. Create requires title. Update checks page scope first and sends only supplied properties. Use a fresh read and merge when replacing an existing text value to preserve unrelated evidence. No blocks, relations, people, dates or other property types are implemented.

Writes use typed Notion payloads and a separate GET read-back checking identity, parent and requested values. An unverified write reports a known page ID when available; inspect before retrying. Unsupported API operations remain explicit limitations; a transport switch requires explicit user choice, using a temporary override unless a lasting preference was requested.

## Sources

Official contracts: [bot workspace identity](https://developers.notion.com/reference/user), [data sources](https://developers.notion.com/reference/retrieve-a-data-source), [page creation and property updates](https://developers.notion.com/guides/data-apis/working-with-databases), and [query completeness limits](https://developers.notion.com/guides/data-apis/query-large-data-sources). The client pins `Notion-Version: 2026-03-11`. Live credentials and SaaS state require separate verification.
