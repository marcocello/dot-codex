# Separate provider interaction skill

## Outcome and ownership

Create knowledge-connect, the single operational entrypoint for authorized ClickUp/Notion interactions using MCP or direct API. knowledge-config retains setup questions, profile storage/default selection and the resolver. Capture/review retain their workflows. Missing config invokes knowledge-config, asks and resumes; none/Markdown do not invoke remote connections. Config may delegate selected metadata discovery/access checks to knowledge-connect without an infinite setup loop. Direct provider requests also use knowledge-connect; an operation beyond bundled API capabilities uses an available explicitly selected MCP capability or reports a limitation, never fabricates support or switches transport automatically.

Move ClickUp code and provider references to skills/knowledge-connect; keep old ClickUp command as a thin compatibility launcher. Reuse profile resolution from config without duplicating it. Retain existing MCP/ClickUp API/Markdown/none profile and public CLI behavior. All remote auth checks, permissions, matching, read-back, no auto-retry/provider fallback and secret boundaries remain.

## Notion direct API

Add skills/knowledge-connect/scripts/notion_api.py with global --config PATH and --profile NAME before commands. Extend version-1 profiles so Notion supports transport=api and exactly one token_env/token_file, optional auth_type=internal|oauth (default internal). MCP remains the default, with no credential references. Notion API account is the bot user UUID, workspace_id and tasks/deals/ideas are UUIDs (hyphenated or compact accepted). Check bot account and workspace against GET /v1/users/me before data-source access; absent workspace identity fails closed. Use integration bot credentials; personal tokens without bot workspace identity are explicitly unsupported.

Fixed HTTPS api.notion.com/v1, Bearer authorization, Notion-Version 2026-03-11, finite timeout, no redirects, no error-body/credential printing or automatic write retries. Reuse private token loading/redirect refusal from connection-owned code. Missing config/default returns existing SETUP_REQUIRED exit 3; wrong provider/transport stops before credential access. Missing/invalid credentials, 401/403/429, malformed/partial responses and timeouts are bounded errors.

Public operations:

- discover --token-env NAME|--token-file PATH: return bot account/workspace identities only; no profile persistence or arbitrary content discovery.
- check: verify bot/workspace plus exact configured data-source IDs and property schemas (GET /data_sources/ID); reject shared destination IDs until a discriminator exists. Return verified=true.
- fields KIND: return configured source schema.
- list KIND: POST /data_sources/ID/query with page_size=100 and start_cursor until has_more=false; reject missing/repeated cursor, truncated flag/request_status or excessive pagination (100 pages / 10,000 results cannot imply completeness). Return pages and complete=true only for complete accessible results. Validate each page belongs to the configured data source; do not claim hidden/private pages are absent.
- get KIND PAGE_ID: GET /pages/ID, validate returned ID and parent.data_source_id before returning.
- create KIND --data-file PATH and update KIND PAGE_ID --data-file PATH: JSON object mapping existing property names to simple values. Supported types title/rich_text (plain strings, max 2000 chars), select/status (existing option name or null), url (HTTP(S) or null), number (finite number or null), checkbox (boolean). Unsupported types/properties/invalid options fail before mutation; no schema changes. Create requires the title property. Build typed properties and parent data_source_id for POST /pages. Update checks existing page scope before PATCH /pages/ID, only supplied properties. Separate GET verifies resulting identity, scope and requested values; mutation response alone is not success. Unknown or mismatched read-back reports unverified with known page ID; no automatic retries. Semantic matching/dedup belongs to invoking workflow.

General MCP guidance covers capability discovery, selected account/workspace scope, existing schema, pagination and authorized operation read-back. No claim that bundled APIs implement every provider endpoint; comments/messages, destructive actions, blocks and schema changes require a specifically available tool and applicable user authorization. No new live connection, token creation, external content mutation or deployment in this task.

## Verification

Independent CLI proof uses synthetic credentials and replaces only the unsafe external HTTP edge; exercise canonical Notion public CLI and profile persistence, identity mismatch and wrong transport, complete pagination and bad cursor, page scope before update, schema checks, create/update plus read-back and failures/no retries/no secrets. Existing ClickUp/profile proof runs as affected regression through compatibility paths, with direct canonical CLI smoke equivalence. Independent semantic assessment verifies config/connect/workflow boundaries and missing-config resume without loops. Frozen proof before implementation, final read-only review. Live SaaS unverified.
