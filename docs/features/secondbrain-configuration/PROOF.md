# Second-brain configuration acceptance

## Done, target and command

A private secondbrain.yaml determines normalized workspace/source configuration and two independently configurable desired native heartbeat schedules. The public configuration CLI safely validates that file, reconciles the real durable source registry atomically, and produces plan payloads without activating remote work. The existing state CLI remains the registry/evidence read-back consumer.

Run `bash docs/features/secondbrain-configuration/proof/run.sh` from the repository root. The runner uses the repository `.venv/bin/python` with PyYAML plus Python standard library and SQLite. It fails on assertions, emits a concise boundary statement, starts no daemon and makes no network/provider/scheduler call. Official capture: `scripts/proof_run_capture.py --feature-dir docs/features/secondbrain-configuration --timeout-seconds 180`.

## Public boundary and independent authorship

The independent proof author `/root/secondbrain_proof` wrote `proof/acceptance.py` and `proof/run.sh` before the configuration implementation. Test producers are synthetic YAML files in temporary directories. Every activation is a fresh public `scripts/secondbrain_config.py --config PATH show|sync-sources|schedule-plan` process; state setup and read-back use the existing public `scripts/secondbrain.py --root ROOT` API. There is no mocked configuration parser, database writer or read-back layer. Source messages are synthetic fixture inputs at the unavailable provider edge. Desired native heartbeat payloads are the terminal consumer boundary; invoking automation_update and live wacli access are outside executable proof.

## Scenario mapping

| Scenario / dedicated test | Real activation and durable/visible read-back | Central defect caught |
| --- | --- | --- |
| `test_missing_invalid_first_use_and_read_only_show` | Missing/invalid file errors through all relevant public commands; inspect absent storage; valid show and paused schedule-plan return normalized data without initializing. | Silent default scanning/creation, invalid-first-use initialization, planning side effects. |
| `test_path_resolution_is_config_relative_and_home_expansion` | Invoke same config from distinct caller directories and read absolute workspace/wacli/repository paths; show home expansion without writing there. | Dependence on caller cwd or unresolved adapter paths. |
| `test_real_registry_cursor_preservation_disable_remove_reenable` | Sync fresh registry, ingest synthetic message through existing state CLI, resync/restart, disable/remove/add/re-enable sources, read registry and pending evidence after each transition. | Reset cursors, deleted evidence, missing disable semantics and non-durable reconciliation. |
| `test_unconfigured_placeholders_can_be_selected_later` | Sync all-disabled empty placeholders into an empty registry; select WhatsApp later, ingest evidence, return to disabled placeholder and reselect while preserving scope/cursor. | Permanently binding empty placeholder scope or losing checkpoint during temporary deconfiguration. |
| `test_scope_provider_conflicts_are_atomic_and_require_new_identity` | Place addition before conflicting scope/provider and imply a removal; assert entire real registry and evidence unchanged after rejection; a new identity succeeds while old data remains. | Partial registration or removal on conflict and checkpoint reuse under a new source scope. |
| `test_validation_duplicate_unknown_and_unsafe_yaml` | Mutate schema/types/fields/provider/scope, duplicate nested/root YAML keys and IDs, unsafe YAML tag; all errors are JSON exit 1, omit sentinels/tracebacks, and preserve real registry. | Partial writes before full validation, unsafe loader, ambiguous duplicate configuration and private error leakage. |
| `test_independent_native_schedule_payloads_and_scope_gate` | Read exactly update/review heartbeat plans; compare statuses, stable names, absolute config/skill prompt references, independent 7/90-minute cadence changes, alternate config identities, no-enabled-source rejection and paused recovery. | Coupled intervals, duplicate/nonstable schedule identity, enabled jobs with no selected source, plan mistaken for activation. |
| `test_tracked_template_is_valid_paused_and_safe_to_copy` | Copy real tracked template to a temporary config; use public show/plan; verify paused 15/60-minute jobs, disabled sources and Git ignore coverage for private configuration. | Unusable default template, implicit account selection or tracked private configuration. |

Every assertion-determining fixture is authored inside proof/acceptance.py. The tracked template is implementation under test, not a seeded expected answer. The implementation's existing state CLI is activated directly; no prior feature's tests/proof are imported or executed. RRULE checks parse frequency/interval semantics rather than prescribing a particular equivalent minutes-versus-hours spelling.

## Semantic integration review required before completion

The independent final reviewer should verify new skill paths actually reread this configuration; handle disabled jobs; use wacli for the selected store/chats with initial lookback, complete checkpoints and explicit sync/backfill/edit/delete coverage; and retain incoming plus outgoing evidence. Verify generated prompts require rereading configuration, stop when the corresponding job is disabled, preserve quiet unchanged behavior and existing authority, and do not imply collection or effect verification from stale local data. Native schedule reconciliation must use actual automation IDs/tools, avoid duplicates and preserve current notification preferences. Do not infer scheduler activation from plan generation. No real account or wacli send is required or permitted by this proof.

## Proves, limits and false-green risks

Proves real local configuration validation/path normalization, transactionally reconciled durable registry, preserved cursor/evidence, independent desired native schedule payloads, safe default template and private-file ignore. It does not prove a running native automation, live wacli synchronization, account authentication, remote source completeness, live sends, or Mac uptime. Existing provider-specific validation beyond WhatsApp/repos is connector-owned and therefore not invented by these tests.

A plan-only success cannot establish scheduler reconciliation; the semantic review boundary above remains explicit. SQLite persistence is verified through separate public processes and failure read-back, not a code-shape test. Broad validation combinations and a conflict after an apparent addition catch implementations that merely perform independent source-put calls. Native output checks do not fake an automation server or assert a nonexistent live schedule.

## Fixed inputs and evidence

Freeze FEATURE.md, this document, proof/run.sh and proof/acceptance.py before implementation; the proof author records SHA-256 values in evidence/acceptance-freeze.json. Retain official failing/passing attempts under proof/runs through the shared capture tool. Only the independent author may repair demonstrably faulty proof setup under the unchanged contract, preserving original failure, exact diff/rationale and revised hashes outside this document. Relevant private conversation remains in native task history; fixtures contain no real messages or credentials.
