# Acceptance proof: knowledge tool connection and task deletion

## Done and command

Done means the renamed public integration remains compatible with persisted profiles and historical CLI entrypoints; explicit scoped task/subtask deletion crosses the real client and transport, persists deletion at the simulated remote edge, and reports verified only after the successful DELETE followed by HTTP 404. Scope/auth failures prevent mutation; uncertain writes/read-back never retry or claim success.

Run `docs/features/knowledge-tool-delete/proof/run.sh`. Acceptance inputs are this document, FEATURE.md, proof/run.sh, proof/test_acceptance.py and proof/api_edge.py. Author: independent agent `/root/tool_delete_proof`. Freeze these inputs before implementation. Official attempts use proof_run_capture.py with this feature directory.

## Boundary and scenarios

Input is public CLI arguments, synthetic credentials, and an initially absent temporary CODEX_HOME. Real producer is knowledge_profile.py put/credentials; real state owner is the private version-1 TOML. Real activation uses separate Python processes and the requested canonical or historical script; api_edge.py uses runpy only to install the unsafe network edge, leaving parser, configuration resolution, credential loader, client, scope checks and HTTP transport real. The only fake is urllib OpenerDirector.open. It validates endpoint/authentication, models provider responses and persists request history and remote existence in a temporary JSON file. No provider network calls occur.

| Scenario/test | Consumer and read-back | Central defect caught |
| --- | --- | --- |
| first_use_routes_to_new_skill | Canonical, prior skill and shared profile CLI report setup owner from absent config | Old/missing setup routing after rename |
| discoverability_and_compatibility | Inventory, sole SKILL.md, scripts symlink, canonical/legacy/config/shared resolver restarts, raw config unchanged and mode0600 | Duplicate discoverable skills; broken old entrypoint; lost profile/token state or leaked credential |
| verified_task_subtask_and_legacy_success | Canonical and legacy delete through real parser/client/transport; durable remote absence and exact GET/DELETE/GET sequence; context receipt | No actual deletion; no preflight or read-back; empty204 failure; unsupported subtask; broken alias/old script |
| mcp_preference_requires_explicit_override_and_is_preserved | Existing MCP profile rejects API without override; explicit temporary override succeeds; config bytes unchanged | Silent transport switch or persistent profile mutation |
| preflight_failures_never_mutate | Identity/auth, workspace, list, task identity/home-list/workspace/access, initial404 and malformed IDs fail; durable request log contains no DELETE | Foreign or nonexistent task deleted; unsafe resource interpolation; not-found incorrectly treated as success |
| failed_or_uncertain_deletion_never_retries_or_claims_verified | DELETE rate limit/server/timeout/malformed response and post-delete visible/auth/permission/rate/server/timeout/malformed responses return identifying unverified error, exactly one DELETE | Retried destructive request, false success on permission failure, success without decisive read-back |

Independent semantic inspection before completion checks active routing/UI/reference names, workflow entrypoints, MCP capability guidance, concrete user authorization/scope, Docs/page unsupported API deletion explanation, and a typed numeric HTTP status exception without response body leakage or status-string parsing. This is mandatory supporting judgment for instruction behavior; executable checks do not simulate an assistant obeying prose.

## Proves / does not prove

Proves local public CLI and persistent-profile compatibility, deletion decisions, receipt/error behavior and normal real HTTP request construction against controlled outer-edge responses. Does not prove live ClickUp permission availability, provider eventual consistency, cascade behavior beyond selected task, a live MCP delete tool, Docs/page deletion, bulk/container deletion, Notion deletion, or a live account operation. No real credentials/data are used.

## False-green risks and evidence

A fake that deletes before a DELETE, invents verification output or implements scope checks would hide the central behavior; this edge only changes durable existence on observed DELETE and never supplies CLI output. A source-only check cannot establish deletion; successful scenarios require the exact request sequence plus independent persisted-state inspection. HTTP404 is accepted only following success; initial404 must fail without mutation. Fake behavior is deterministic and cannot establish SaaS guarantees. Preserve full official output and hashes; no scenario skipping or mutable expected outcomes. Existing task/Docs/Notion regressions remain separate supporting checks, not this acceptance runner.
