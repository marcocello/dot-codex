---
name: knowledge-tool-connect
description: Set up and manage knowledge connections, profiles and tokens; use ClickUp/Notion MCP or APIs and recover from unavailable transports while preserving user choices.
---

# Knowledge Tool Connections

Own setup, profiles/defaults, credential intake, provider capabilities, authentication, operations and read-back. Use [setup and profile commands](references/setup.md) when configuration or credentials are missing or changing. Capture/review own the requested content work. Use the user's existing organization; no mandatory categories or schemas.

## Establish scope and capability

Accept a resolved profile from the workflow, otherwise run this skill’s scripts/knowledge_profile.py resolve. Reuse explicit provider/workspace/destination choices. SETUP_REQUIRED means perform [setup](references/setup.md) here, retain the request, ask only missing details and resume; invalid state requires repair. Discovery can run before a profile exists. No handoff to a separate configuration skill is needed.

Check the **requested operation** against actual callable tools and the selected provider reference before promising execution or requesting credentials. Read [ClickUp](references/clickup.md) or [Notion](references/notion.md). Bundled clients are limited; ClickUp supports list tasks (including deletion) and v3 Docs/pages; Notion page-body/block operations are not implemented here. Explain an unsupported operation before offering token setup as its solution.

Verify actual account/workspace binding, then the exact operation target and existing schema. A saved destination is optional; an explicit target overrides it within verified scope. A connection-only check verifies identity/workspace without asking for content containers. Markdown returns to [local storage](references/markdown.md); none does not access remote content.

## Missing plugin or connection

Inspect available tools/connections before saying the plugin is absent: installed, connected, accessible to this task and capable of the operation are different states. When available, use the plugin-management skill/tools to search by provider, discover exact plugin IDs and suggest the relevant installation/connection. Honor each tool's authorization/availability rules; never invent a plugin ID or claim installation. If no installation tool is available, explain the manual plugin/settings route supported by the current host.

Present usable options: install/connect the plugin, or supported direct API using a token. No automatic installation or arbitrary connector substitution. Keep supplied content and pending action while waiting. After the user connects, refresh tools and verify identity/access before resuming. If the current session cannot see newly installed tools, report that exact limitation and retain the resume context.

This procedure can guide future provider adapters, but bundled scripts currently implement only ClickUp and Notion. Other services need an actually available connector or implemented API adapter.

## Transport selection and recovery

Saved transport defaults to MCP when omitted. A profile may also hold an API credential. That does not authorize an automatic switch or mean the token is valid.

Distinguish missing plugin, disconnected account, unsupported capability, quota/rate limit, authentication failure, permission denial and uncertain write outcome. For an MCP quota or temporary failure, check whether API supports the exact pending operation. If so, offer “Il collegamento MCP ha raggiunto il limite. Vuoi usare l’API con un token oppure riprovare quando sarà disponibile?” Reuse a saved token if present; otherwise follow [setup](references/setup.md), the provider reference and [credential intake](references/credentials.md). API has its own limits and permissions; do not promise a quota bypass. Authentication/permission failures need relevant access repair, not another transport to evade permissions.

An explicit “usa l’API” authorizes the pending operation's transport choice. Resolve --transport api and pass that override to the API client; do not persist a new preference unless requested. Stay on the same verified account/workspace and target. If a write may already have happened, inspect its identity or complete matching candidates through an available read path before retrying. If the outcome cannot be established, report it as unverified and do not repeat it. Even an approved switch is not permission to duplicate a write.

## Execute and verify

Use the applicable MCP capability schema or "${CODEX_HOME:-$HOME/.codex}/skills/knowledge-tool-connect/scripts/clickup_api.py" --help / notion_api.py --help in the same directory. Global --config PATH, --profile NAME and optional --transport api precede the command. Scripts reuse this skill’s resolver. Task/data-source commands take explicit list/data-source IDs or existing legacy aliases. ClickUp Docs commands take Doc and page IDs; parse these from the supplied URL and verify their workspace. Do not pass a Doc URL to a list command.

Preserve unrelated content and existing schema. Obtain sufficiently complete candidates when matching is needed, and separately read back identity, target and intended values after writes. No automatic write retries or schema creation. Unsupported operations yield the limitation and an unsaved proposal; apply ordinary user authorization to destructive actions, messages and sharing. Tokens may be pasted in chat at the user’s choice: follow [credential intake](references/credentials.md), do not echo their values or commit them; store them only in private, ignored configuration or a private credential file, and do not read unrelated credential stores. Report selected scope, verified changes and uncertainty without exposing private content.

## Explain what is missing

State the specific missing prerequisite and the next applicable action: unavailable plugin → install/connect a discovered plugin or choose a supported API; absent credential → guide token generation/intake; invalid token → correct that binding; ambiguous account/workspace/target → ask only that choice; permission denial → obtain the required access; unsupported operation → describe the actual missing capability. Do not present token setup as a fix for missing endpoint support. Preserve current ClickUp task and Docs/page support; Notion page-body/block operations, ClickUp comments/attachments, container and Docs/page deletion and browser OAuth enrollment are not implemented by these clients. Report other limits from the current provider reference, not historical feature notes.
