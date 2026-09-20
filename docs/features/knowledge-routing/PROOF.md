# Independent routing acceptance

## Done and target

A user can configure a connection without a prescribed knowledge taxonomy, attach an API credential reference later, temporarily select API after MCP failure, and continue against an explicit destination without changing the saved preference or other accounts. The target is the checkout public CLI and final agent instructions; no live service target is claimed.

## Command and boundary

Run `bash docs/features/knowledge-routing/proof/run.sh`. Profile operations execute in fresh subprocesses and read persisted TOML through subsequent public commands. API commands execute through their public argument parsing with runpy; only urllib.request.OpenerDirector.open is replaced. All profile resolution, token loading, request construction, identity and destination checks and response processing remain production behavior. Synthetic HTTP replies describe external accounts, workspaces and destination contents, never decide client success. The runner is fail-fast and performs no external access or token creation.

## Scenarios

| Dedicated test | Input, visible read-back and break caught |
| --- | --- |
| first_use_connection_only_and_credential_recovery | Missing configuration returns setup signal; save connection and opaque document destination without aliases, attach unset credential reference, resolve API temporarily then reopen saved MCP preference; catches mandatory buckets, secret reads during config and silent default changes. |
| isolated_profiles_credential_replacement_and_persist_rejection | Distinct ClickUp/Notion profiles, rejected API preference before credential binding, replace env reference with nonexistent absolute file reference, reopen both profiles; catches destructive credential attachment, cross-account/default mutation and token-file creation. |
| legacy_aliases_and_local_profiles | Shared legacy destination aliases remain accepted alongside Markdown and none, default is stable; catches invented discriminator requirements and compatibility loss. |
| provider_connection_only_override_and_explicit_destination | Both clients reject saved MCP before HTTP, explicitly override to API, verify connection without metadata, then list an explicit ID and consume returned task/page; missing alias fails before HTTP and wrong account/workspace fail before content access. Catches ignored transport choice, mandatory taxonomy and lost scope checks. |

## Semantic assessment

After implementation the independent author assesses final config/connect/capture/review guidance across these paraphrases: “save this in my existing project” without configuration must retain intent and ask only missing connection/destination; “I do not have the plugin” offers actual available installation/connection or supported API with capability checked first; “I installed it” rediscovers then resumes; “MCP quota exhausted, use API” reuses matching credentials or guides first token creation and private storage, applies a temporary switch and preserves destination; “make API my default” explicitly persists it; “save this transcript in a ClickUp Doc” states the unsupported bundled operation before requesting a token; uncertain prior write reads back/deduplicates before retry; permissions failure is not treated as quota; none/unrelated work does not initiate setup. No required Tasks/Deals/Ideas, fixed states or Markdown directories. Evaluate meaning, not exact strings. Record assessment separately in evidence.

## Proves, limits and false-green risks

The automated proof establishes fresh-process configuration durability and synthetic service boundary routing. Semantic inspection establishes instructional completeness, not actual future model compliance. It does not demonstrate live plugins, installation, SaaS permissions, quota reset, token enrollment, Docs support or every endpoint. Existing API proofs are separate regressions for previously accepted write/read-back, pagination and error behavior. Compact HTTP fixtures may omit server variations; they are not server contract substitutes. Profile state is isolated in temporary directories; synthetic credentials are never sent to a network.

## Freeze and evidence

Freeze FEATURE.md, PROOF.md, proof/run.sh and proof/test_acceptance.py before implementation; compare hashes before completion. Capture official attempts via shared proof_run_capture.py. The independent author owns these acceptance inputs. Preserve baseline failures and any contract-grounded fixture repair separately; implementers must not edit proof. Independent semantic evidence is required in addition to automated pass.
