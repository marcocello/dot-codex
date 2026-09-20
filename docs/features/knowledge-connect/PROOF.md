# Independent acceptance proof

## Done and target

The user can retain configuration/setup in knowledge-config and delegate provider interaction to knowledge-connect. Canonical Notion API commands resolve an unchanged persisted profile, validate identity and scope, return complete accessible results, reject unsafe writes and separately verify successful writes. Automated target is this checkout's public CLI with synthetic credentials and an HTTP edge replacement. No live SaaS target is claimed.

## Command

`bash docs/features/knowledge-connect/proof/run.sh`

The runner invokes dedicated Python unittest cases via real CLI argument parsing/runpy. Only urllib.request.OpenerDirector.open is replaced; profile parsing, credential loading, HTTP request construction, scope/schema validation, pagination and mutation verification remain production code. The response object implements read/getcode/context management. The fake stores accepted typed properties and serves them back through a separate real GET request; it does not decide validity, scope, pagination or success.

## Scenarios

| Test | Public activation, consumer/read-back and central break caught |
| --- | --- |
| setup_required | list with absent TOML must emit SETUP_REQUIRED exit 3 before HTTP; catches invented defaults |
| identity_check_fields_and_wrong_transport | check/fields use persisted account/workspace/source IDs; schema output and identity mismatch/mcp rejection catch ignored routing |
| pagination_and_broken_cursor | list traverses two query pages and exposes completeness only on terminal response; catches first-page-only success and invalid cursor acceptance |
| create_update_and_separate_readback | create/update typed properties through HTTP, separate GET and returned verified page; mismatched read-back fails with page identity and one mutation; catches trusting mutation response or retrying writes |
| scope_and_invalid_schema_block_writes | update foreign-source page and create unknown fields/options/wrong types; no mutation reaches HTTP; catches cross-scope writes and implicit schema creation |
| http_failure_no_retry_or_body_leak | check under 401/403/429 edge failures; one request, bounded failure and no synthetic token/body printed |

Every invocation also verifies fixed HTTPS origin, Bearer header, pinned version, finite timeout, no token output and unchanged profile bytes. These assertions share constants and fixtures only within proof/test_acceptance.py; no implementation internals are imported as the oracle.

## Semantic assessment

The independent author reads the final config/connect/capture/review instructions, inventory and provider references after implementation. Assess ordinary paraphrases: “save this task” with no config must invoke config, ask and retain pending intent; “use none” must prevent remote calls; configured capture/review must pass resolved context to connect; metadata discovery during setup must not recursively restart setup; direct “update a ClickUp task” must route through connect with applicable scope; unspecified/unavailable capability must report the limitation, never silently switch account/transport. Record assessment separately in evidence. Exact instruction wording is not the oracle.

## Proves and limits

This establishes bounded local CLI behavior and, with the semantic assessment, operational instruction ownership. Existing ClickUp/profile regressions and compatibility-launcher smoke checks remain supporting verification, not this proof. It does not establish real account authentication, server permissions, every Notion property type, every endpoint, actual agent tool-selection performance, real network redirect behavior or hidden/private-page coverage. Synthetic schema and compact fixtures risk missing server variation; authoritative schema references and read-only final review supplement them. A missing canonical CLI is an expected initial red, not permission to change acceptance.

## Freeze and evidence

Freeze FEATURE.md, this document, proof/run.sh and proof/test_acceptance.py hashes before implementation. Capture official attempts using shared evidence tooling; keep semantic assessment and any independent fixture repair records outside frozen proof. The implementer must not edit proof inputs. No live credentials, daemon processes or external writes are required.
