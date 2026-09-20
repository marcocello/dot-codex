# Provider-neutral knowledge setup and transport recovery

## User outcome

Remove mandatory Second Brain organization from config/connect and their capture/review consumers. Knowledge operations preserve the user's destination and existing structure; no automatic Tasks/Deals/Ideas classification, lifecycle states, directory hierarchy or commercial workflow. Setup may be invoked by capture or a direct provider request, and asks only missing information. Existing profiles and aliases remain readable without migration; legacy task/deal/idea keys are optional shortcuts, never mandatory setup questions.

A connection profile still scopes a provider, connection label, account and workspace. Optional destination is a user-chosen default reference (list/data source/document URL or ID); an explicit operation target takes precedence within the verified workspace. Missing destination asks where to save/read, not for three buckets. Markdown root and none stay supported. Scripts support ClickUp and Notion; the workflow pattern is extensible to other provider adapters without claiming unimplemented support.

## Connection and transport contract

Keep version-1 TOML and existing put/list/default/resolve behavior. Remote required fields: provider, connection, account, workspace_id. Optional: destination, legacy tasks/deals/ideas, transport (default mcp), token_env OR token_file, auth_type. MCP may retain an API credential reference without using it. API selection requires a credential reference. Credentials remain references, not values. Numeric ClickUp IDs and Notion UUID account/workspace/legacy aliases are required when API credentials are configured or API selected; destination is a nonempty opaque reference, checked by the requested operation.

CLI additions to knowledge_profile.py:
- resolve [--profile NAME] [--transport mcp|api]: temporary transport override, no file/default mutation. API override with absent credentials emits SETUP_REQUIRED exit 3; invalid profile remains error.
- credentials NAME (--token-env NAME|--token-file PATH) [--auth-type TYPE]: update only credential binding, preserving transport, defaults, destination and other profiles. Default auth personal for ClickUp/internal for Notion. No file/token creation or token reads.
- transport NAME mcp|api: explicitly persist preferred transport; selecting API without credentials fails without mutation.
- put remote profiles accepts optional --destination and no task/deal/idea aliases.

Both API clients accept global --transport api to explicitly override an MCP preference for one invocation via the canonical resolver. No override means honor saved preference; fail before credential/network use when mcp selected. check on a connection-only profile verifies account/workspace and returns verified=true without requiring destination metadata. Existing configured aliases may still be checked. fields/list/get/create/update (and ClickUp set-field) accept an explicit destination ID in the existing positional target slot or a configured legacy alias; missing alias fails clearly before HTTP. No mandatory unrelated destinations. Exact target scope checks and read-back remain. Notion source metadata on these operations validates requested data source; ClickUp list metadata validates workspace membership. Shared legacy aliases can be used as caller-selected destinations without requiring fixed kinds/discriminators in a generic client.

## Agent setup/recovery journey

knowledge-config owns questions, connection/default persistence and transport preference; knowledge-connect owns capability discovery, provider setup references, authentication verification, MCP/API operations and failure diagnosis. Avoid recursion by explicit setup discovery and resolved-profile handoff.

Before asking for a token or installation, check whether the desired operation is available through each candidate transport. ClickUp task API is bundled; Docs is not, and this must be stated before proposing an API token as a solution to a Docs operation. Notion supports only documented page property operations. This change does not implement Docs endpoints, arbitrary APIs or OAuth enrollment.

If plugin/MCP capability is absent, explain and offer an available plugin connection/install path or supported direct API. Do not invent plugin IDs or imply installation when tools cannot perform it. Use the actual plugin-management tooling/availability rules; user can install/connect manually. Once user reports completion, refresh capability discovery and resume retained intent. Do not reprompt about a provider/workspace already selected. No automatic plugin installation.

For MCP quota/rate-limit/unavailability, identify the actual reason and offer API when that exact operation has support, or wait/reconnect as appropriate. API has independent limits and permissions; no bypass guarantee. User choice authorizes the transport switch for the pending operation. Reuse matching saved API credentials; if absent, ask whether user already has a token, guide generation and private storage, then save its reference with credentials command. No token values in chat/args/config; do not search unrelated token stores. Operation transport override never silently changes default preference. Persist preference only on user request.

After API identity/workspace verification, preserve destination/content and resume. Before retrying any uncertain write, read back/deduplicate via stable identity; if impossible do not repeat the write. Authentication/permission failures aren't quota; do not offer a different transport as a permissions workaround. Explicit none or unrelated tasks do not trigger setup.

## Verification and limits

Independent acceptance exercises real public profile CLI across fresh processes and persisted read-back: connection-only setup, credential attach, immutable temporary override, persisted preference, multiple-account isolation, missing credential setup signal, legacy config compatibility, Markdown/none. Independent synthetic HTTP-edge public API checks establish connection-only check and explicit ID operation with same workspace/identity protection and override semantics. Independent semantic assessment of user paraphrases checks guided installation/token onboarding/quota switch, no repeated choice, no opinionated taxonomy, no unsupported capability promises, no blind retry. No live service credentials, installations, token creation or external mutations required. Existing applicable ClickUp/Notion API proofs remain regressions; old profile assertions requiring three destinations are deliberately superseded, not edited.
