# Independent acceptance: unified knowledge skill

## Done and command

Done requires the dedicated subprocess proof below plus independent semantic inspection of the final instructions against FEATURE.md and the user's requested setup experience. Run `bash docs/features/knowledge-unified/proof/run.sh` from the repository. Python 3.11+ and a local POSIX filesystem are required. Target is this harness checkout; no live service or credential setup is claimed.

## Boundary and scenarios

Real producer is a user/agent invoking the public profile CLI; activation is a fresh Python subprocess at the canonical knowledge-connect path or either retained legacy path. The profile resolver owns state and decisions. Consumers are capture/review/connect agents reading JSON routing and the persisted version-1 TOML. Read-back occurs in fresh processes through all paths and by parsing the durable TOML. No fakes are used: no network or credentials are needed by this boundary. Every scenario uses an isolated temporary configuration.

| Scenario | Dedicated test | Read-back and central break caught |
| --- | --- | --- |
| First use with no config | `test_missing_configuration_routes_every_entrypoint_to_unified_skill` | All entrypoints return exit 3 and SETUP_REQUIRED naming knowledge-connect; stale owner or missing canonical CLI fails. |
| Legacy creation, canonical and compatibility reads | `test_creation_readback_and_restart_through_all_entrypoints` | Same resolved profile after process restart, preserved account/workspace, no forced task taxonomy, valid persisted version 1. |
| Config without default or API credentials | `test_missing_default_and_missing_api_credentials_route_setup` | Explicit unified setup referral instead of invented default/transport credentials; no implicit default mutation. |
| Credential references and transport lifecycle | `test_credential_binding_and_temporary_transport_preserve_identity_and_default` | Environment reference attaches without altering identity; temporary override leaves file byte-identical; explicit persisted API selection survives restart; file reference replacement removes old reference. |
| Local/disabled providers | `test_none_and_markdown_remain_usable` | none and Markdown resolve through retained paths without changing default during explicit per-call selection. |

## Semantic acceptance

Independent inspection must establish one active knowledge-connect entrypoint owning setup and execution, linked detailed setup, current consumers routed to it, removal of knowledge-config from active inventory, and compatibility-only old code. Judge instructions by outcome rather than exact wording: distinguish missing/disconnected plugin, absent/invalid credential, ambiguous account/target, insufficient permission, and unsupported operation; explain the next applicable action. ClickUp generation must point to Settings → ClickUp API → API tokens. A user may paste a token in chat or supply an existing environment/private-file reference; acknowledge conversation retention briefly, avoid echo/command/repository inclusion, do not demand rotation merely for voluntary chat input, save only by suitable private tools with applicable authorization, and accurately offer private terminal setup if secure storage is unavailable. Assess currently implemented ClickUp Docs capability accurately and preserve explicit limits for unsupported operations, including Notion page-body/block APIs, before credential setup. No implication that a token bypasses every MCP limit. The original user request, FEATURE.md and final affected instruction files are the semantic inputs; document the independent assessment separately as evidence.

## Proves, limits and false greens

Proves local profile continuity, new setup owner, compatibility activation and instruction semantics within this checkout. Does not prove live SaaS permissions, plugin installation, token provisioning in a real chat, secret storage availability, or provider API behavior; those clients remain subject to separate regressions. A passing CLI suite alone cannot establish conversational behavior or inventory routing; the independent semantic assessment is mandatory. No real token may enter proof files or output. Claims of secure storage require actual suitable tools at use time and cannot be inferred from this proof.

## Evidence and freeze

Freeze FEATURE.md, this contract, proof/run.sh and proof/test_cli.py using SHA-256 before implementation. Save hashes and independent semantic assessment outside the frozen contract. Official attempts use proof_run_capture.py. Preserve failing evidence; only the independent proof author may repair demonstrably faulty fixtures without changing accepted outcomes.
