# Independent knowledge-profile acceptance

## Done and command

Done requires the executable boundary to pass and an independent semantic assessment of the final instructions to pass the scenarios below. CLI green alone is insufficient. Author: independent agent `/root/knowledge_proof`, before implementation, from FEATURE.md and the approved user dialogue. Target: checked-out local harness, Python 3.11+, no deployed/live service claim.

Run `bash docs/features/knowledge-profiles/proof/run.sh` from the repository. All acceptance-determining executable inputs are `proof/acceptance.py` and `proof/run.sh`; configuration fixtures are embedded in acceptance.py. FEATURE.md, this document and those inputs are frozen in `proof/FROZEN.sha256`. Candidate-specific semantic findings and capture evidence live outside these frozen inputs.

## Executable scenarios

Every activation is a fresh real public CLI subprocess. The CLI owns selection and durable TOML state; subsequent resolve/list subprocesses are affected consumers and durable read-back. No behavior is faked. Temporary configuration prevents touching actual harness settings or external accounts.

| Scenario/test | Activation and read-back | Central defect caught |
| --- | --- | --- |
| first_use_then_persistent_default_and_override | Missing config resolve; put without default; explicit default; reopen using CODEX_HOME; per-operation Notion override; reopen ClickUp default; switch default | Invented default, repeated setup across processes, ignored override, override contaminating default |
| multiple_accounts_replace_isolated_profile | Put two ClickUp accounts; list and resolve; replace default profile with none; list/resolve again | Conflated accounts, stale provider fields, unrelated profiles/default lost |
| markdown_none_and_no_routing_side_effect | Configure absolute Markdown path; resolve; configure none; resolve; unknown profile/default | Implicit content creation, none fallback, unknown profile silently defaulting |
| invalid_put_preserves_durable_configuration | Unsupported provider, missing remote fields, relative root, placeholder connection; byte-for-byte configuration and resolve | Partial writes, unsafe placeholder destination, invalid input replacing good state |
| invalid_config_never_repaired_or_replaced_implicitly | Malformed TOML, unsupported version/provider, dangling default, relative root, incomplete remote profile; resolve/list/put; byte read-back | Invalid state silently repaired, bypassed, or overwritten |
| concurrent_writers_preserve_all_profiles | Parallel public put processes against one config; list and resolve | Read-modify-write losing unrelated saved profiles/default |

## Required semantic assessment

An independent reader assesses the final skill instructions and reachable provider references against these realistic user intents, explains the resulting decision path, and records pass/fail plus ambiguities. Judge outcomes across paraphrases, not literal phrases. Do not substitute wording searches for this assessment.

1. Fresh chat: “Segna che devo chiamare Luca domani” / “Aggiungi un promemoria per Luca”. Configured work ClickUp must resolve automatically, verify connector identity/workspace/schema before access, match complete candidate scope before creating, and read back the resulting record. No account-selection interview on every chat.
2. “Fammi il punto della settimana” / “Cosa è rimasto aperto?” scopes read-only review to the selected default. An explicit personal selection affects that operation/session without silently saving a new default. “Rivedi tutti i profili” enumerates configured profiles and retains provenance; connected but unconfigured accounts are not automatically included.
3. Missing config requests setup details once; complete explicit default setup saves configuration. Unavailable connector, mismatched account, unsupported capability, or invalid schema blocks at the exact boundary with the unsaved proposal where possible, and never silently falls back to another provider. Legacy Notion API must not provide a bypass before network access.
4. Two ClickUp accounts with similarly named workspaces/lists remain distinct through configured identities and IDs. ClickUp and Notion mapping describe schema discovery and capability checks for tasks, deals and ideas without assuming the schemas are equivalent or creating remote schemas.
5. Markdown capture has stable record identifiers, explicit root/path handling, complete matching before creation, update preserving record identity, and durable read-back. A repeated capture must not require a duplicate record. None performs no provider content reads/writes and communicates that persistence is disabled. Explicit direct Markdown notes and Zotero archival remain distinguishable modes.
6. Generic capture retains source evidence, scoped source collection, classification and conservative commercial edits; review retains brief/weekly behavior. Active routing/inventory refer to generic review and setup. The persistent file is local convention, excludes credentials and has no shipped real-account default.

## Proves, limitations and false-green risks

The executable suite proves routing persistence and errors at the actual local CLI boundary, including first use and concurrent updates. The semantic assessment proves that authored instruction paths direct the intended capture/review behavior without contradictions; it does not prove model compliance in future chats or live connector behavior. No remote account is selected, authentication performed, SaaS content accessed, provider schema created, or Markdown content writer implemented by this CLI. Such live operations remain unverified.

No external fake is needed because the accepted target ends at local routing and instruction adapters. Risks include untested platform-specific locking/permission failures and filesystem crashes; ordinary concurrency and failed-validation preservation are exercised, but power-loss durability is not. Hashes are audit records, not execution isolation. A shallow implementation that only returns fixed JSON fails profile variation and durable reopening; instruction-only success cannot replace CLI evidence. Evidence: captured runner output, exit status, frozen hash verification, independent candidate-specific semantic report and explicit remaining limitations.
