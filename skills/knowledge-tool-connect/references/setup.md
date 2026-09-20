# Connection setup and profile commands

## Resolve and resume

Run "${CODEX_HOME:-$HOME/.codex}/skills/knowledge-tool-connect/scripts/knowledge_profile.py" resolve; use --profile NAME for an explicit operation/chat choice. Profiles live in ${CODEX_HOME:-$HOME/.codex}/knowledge.toml (a harness convention). Reuse an existing profile without asking again. Missing config/default yields exit 3, SETUP_REQUIRED: retain the pending request and perform setup here, rather than telling the user to invoke another skill. Invalid config requires repair; it is not missing setup. Explicit none is configured and disables storage. Unrelated work and explicitly targeted local notes/Zotero do not require remote setup.

If the request already names a provider, account, workspace or destination, reuse those choices. Ask only what remains ambiguous. An explicit target takes precedence over the optional saved destination within the verified workspace; a different account/workspace needs the matching connection. Missing a destination asks where to read/save, never for unrelated buckets. Read [the routing contract](secondbrain.md).

## First connection

Check the requested operation/provider against this skill’s provider reference **before** requesting a token or installation. If no usable connector exists, it determines actual plugin availability and supported API operations. Offer applicable paths in plain language, for example: “Vuoi installare/collegare il plugin ClickUp oppure usare un token API?” Do not present an unsupported API operation as a working alternative.

- **Plugin/MCP:** follow the main skill’s installation/connection guidance. Retain pending intent while the user installs or authorizes the plugin; refresh actual capabilities afterward. Do not claim readiness from an installation message alone.
- **API:** reuse a matching credential when present. Otherwise ask “Hai già un token o vuoi essere guidato a generarlo?” Follow the selected provider reference and [credential intake](credentials.md). Offer pasting the token in chat or supplying an environment-variable/private-file reference. Accept the chosen input without repeating its value; explain once that chat input remains in conversation history. A variable in another terminal may not exist in the agent process; verify availability without printing its value.
- **Markdown:** obtain the chosen absolute root and follow [local storage](markdown.md).
- **None:** save the explicit choice and return an unsaved proposal.

Run the selected provider’s discovery command before a profile exists; do not recursively resolve missing configuration during discovery. Ask the user to select among genuinely ambiguous accounts/workspaces. Save verified identity metadata and the credential in private knowledge.toml. Discovery before profile creation still takes an environment/private-file reference: use a scoped private temporary file for chat intake, then create the verified profile and import its credential with --import-current. Do not expose the token in command arguments. A connection needs no content destination to exist; request an optional default destination only when useful to the pending operation. Do not invent IDs or create containers.

## Persist configuration

Use this skill's knowledge_profile.py (Python 3.11+, POSIX). Global --config PATH selects an explicit alternate harness file.

- put NAME --provider clickup|notion --connection LABEL --account ID --workspace-id ID saves an MCP connection. Optional --destination REFERENCE remembers a user-chosen target. No task/deal/idea mapping is required.
- Add --transport api --token-env NAME OR --token-file ABSOLUTE_PATH for API as preferred transport. Auth defaults to ClickUp personal / Notion internal; --auth-type oauth means an existing OAuth token, not OAuth enrollment.
- credentials NAME --token-stdin reads a token through stdin and saves it as token in private knowledge.toml, replacing the credential binding while preserving preferred transport, destinations and defaults. This is the default storage for supplied tokens.
- credentials NAME --import-current imports the selected existing environment/file credential into token, preserving auth_type and leaving the original file intact. Optional --auth-type TYPE overrides its type.
- credentials NAME --token-env NAME OR --token-file ABSOLUTE_PATH remains available for users who prefer a reference. MCP can retain an unused API credential for later switching.
- resolve --profile NAME --transport api selects API temporarily; it changes no saved state. Missing credentials return SETUP_REQUIRED: complete credential setup and resume the same choice.
- transport NAME api|mcp changes the saved preference only when requested. default NAME selects a saved connection as default.
- put NAME --provider markdown --root ABSOLUTE_DIRECTORY and put NAME --provider none configure local/disabled storage.

put replaces one complete profile; preserve its intended fields when updating it. Add --default only for the chosen persistent default. Version-1 profiles and optional legacy aliases remain readable; they do not establish a taxonomy. Multiple profiles support separate accounts/workspaces. Config writes are atomic and owner-only (0600). Inline tokens are plaintext in this private, ignored file, never version-controlled. Public command output replaces tokens with [redacted]; never use that placeholder to rewrite credentials. Readback for display is redacted; API clients resolve the actual token internally.

Read back list/resolve, verify identity/access with the resolved profile and selected operation transport, then resume the retained request. Failed verification is a blocker, not a verified connection.

