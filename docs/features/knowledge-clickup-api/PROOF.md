# Independent acceptance proof

## Done and command

Done means the public resolver establishes explicit setup-required state without choosing a destination; persisted selections survive subsequent CLI processes; the direct ClickUp CLI authenticates the selected identity, confines access to its configured workspace/lists, completes pagination, and confirms supported writes by remote GET read-back. Integration instructions must ask/save/resume on missing setup while preserving explicit standalone capture. Execute `docs/features/knowledge-clickup-api/proof/run.sh` from the repository. No real credential or account is required.

## Boundary and scenario mapping

Producer is a user-selected profile and JSON input files; public activation is the production Python command-line entrypoint in a fresh subprocess. State owner is the canonical profile resolver and ClickUp client. Consumers are capture/review calling those commands. Durable read-back comes from the TOML file across processes and an independent simulated service state file. Only the unavailable/unsafe HTTPS edge (`urllib.request.OpenerDirector.open`) is replaced; no resolver, validation, client operation or success result is stubbed. The child runs the actual entrypoint through `runpy`, with its normal script import path established.

| Scenario | Dedicated test | Observable read-back / defect caught |
| --- | --- | --- |
| First use, absent default, configured none, restart, override, unknown profile, malformed file | `test_setup_signal_restart_none_and_override` | CLI exit/structured signal and later process resolution; catches fabricated defaults and misleading setup |
| Extended config, invalid credential combination, missing credential, MCP isolation | `test_credentials_configuration_and_isolation` | Saved config unchanged on failure, no secret persistence or HTTP; catches unsafe fallback |
| Preconfiguration discovery and verified personal/OAuth identity | `test_discover_and_check` | Recorded official HTTP paths/auth, verified receipt; catches wrong authentication/identity omission |
| Explicit private token file | `test_private_token_file` | Rejects world-readable and symlink credentials before HTTP |
| Account/workspace/list/task mismatch | `test_scope_stops_content_access` | No out-of-scope content or mutation requests |
| Multiple pages, archived tasks, missing last_page, repeated pages, failed page | `test_complete_pagination_and_failures` | Complete task IDs and outbound pagination; catches first-page-only and partial-success claims |
| Create/update preservation and invalid payloads | `test_mutation_and_readback` | Service state and final GET; catches write-only success and omitted-field loss |
| Field schema, supported custom fields and invalid options/types | `test_custom_fields_and_rejections` | Custom endpoint state/read-back; catches silent custom-field loss and permissive passthrough |
| HTTP/auth/rate limit/timeout/malformed/read-back/uncertain write | `test_failure_no_success_no_retry` | Bounded failure, known ID, one write maximum; catches secret leakage, false success, retry duplication |

Semantic assessment independently reads the resulting integration, capture, review and routing instructions against these journeys: (1) “save this task” with no config triggers knowledge-config, asks the destination, persists the response then resumes; (2) no default with multiple saved profiles asks selection; (3) explicit none does not reopen setup; (4) malformed/unknown config is repaired explicitly rather than fallback; (5) standalone Markdown/Zotero bypass setup; (6) temporary profile override does not alter default; (7) capture/review defer provider details to the single integration skill. Record findings in independent evidence, not as automated live-agent proof.

## Proves / does not prove

Proves real executable CLI behavior with a deterministic remote-service boundary and local persisted configuration. The fake observes and rejects incorrect host, timeout and relevant query/payload fields, and maintains state distinct from the client's result. Does not prove live SaaS connectivity, plan permissions, actual user credential availability, or an LLM's autonomous compliance in a fresh conversation. Instruction semantic assessment supports the routing claim but is not live conversation execution. Redirect refusal and exhaustive provider schema variants require code review and supporting regressions; these do not expand the CLI acceptance receipt.

False-green risks: fake API shape divergence, instruction compliance not exercised live, output receipts accepted without a real server. Mitigation: use official endpoint shapes, assert outgoing scope/auth/query/payload and service state, independently review request safety and instruction journeys, explicitly retain live-service gap. No real account/default is selected and no remote content changes.

## Frozen inputs and evidence

Acceptance inputs are FEATURE.md, this document, proof/run.sh, proof/test_acceptance.py and proof/http_edge.py. SHA-256 baseline is recorded in evidence/proof-freeze.sha256 before implementation. Run output and exit status are retained by feature evidence capture; meaningful failures and proof-only repairs remain in evidence. Implementation must not change these inputs. Environment is local Python 3.11+, repository CLI, synthetic environment credential, temporary config/state directories, no network.
