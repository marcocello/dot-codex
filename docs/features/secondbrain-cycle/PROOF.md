# Second-brain cycle acceptance

## Done and target

The dot-codex CLI provides durable, explicit-root state for a skills-driven collect → understand → agenda → review → act → verify loop. Dedicated acceptance activates real public CLI processes and reads their persisted results through public query commands. Skill behavior also requires the independent semantic forward exercise described below; a database-only pass does not establish an autonomous live assistant.

## Command

From the dot-codex repository root: `bash docs/features/secondbrain-cycle/proof/run.sh`.

Use `scripts/proof_run_capture.py --feature-dir docs/features/secondbrain-cycle --timeout-seconds 180` for official captured attempts. Python 3 with the standard library, SQLite support, writable temporary storage, and the checked-out `scripts/secondbrain.py` are the only runtime requirements. The runner emits the boundary, fails on assertions, does not edit acceptance or implementation, and leaves no service running. Fixtures contain invented messages and permissions only.

## Acceptance mapping

All executable scenarios are in `proof/acceptance.py`. Inputs are JSON sent to `python3 scripts/secondbrain.py --root ROOT COMMAND`, including documented file-based query input. The CLI is the real state owner; pending/context/events/sources/due are the affected consumers and durable read-back boundary. Each command is a new process, so an in-memory implementation cannot pass.

| Scenario / test | Activation and observable read-back | External fake and central defect caught |
| --- | --- | --- |
| `test_first_use_explicit_root_and_preservation` | Uninitialized query fails; init creates real storage and documents; repeat init preserves authored profile; context remains empty; malformed commands/JSON fail structurally. | No provider configured. Catches implicit setup and overwritten user direction. |
| `test_durable_journey_due_resolution_and_irrelevant_evidence` | Ingest request, apply sourced fact and waiting outcome, restart queries show cursor and versions; due boundary; outbound response and irrelevant evidence close outcome without losing original evidence. | Synthetic inbound/outbound message boundary. Catches disappearing state, wrong due timing, lost evidence or unresolved reply. |
| `test_replays_revisions_empty_pages_and_atomic_cursors` | Replay exact event, ingest new revision, empty page advance, malformed mixed batch and stale cursor failure; read-back unchanged after failures; source identity binding and disable/re-enable; normalized times and bounded pending. | Opaque synthetic page cursors. Catches duplicate events, partial batches, missed catch-up and scope crossover. |
| `test_apply_atomic_versions_and_evidence` | Invalid evidence and stale versions reject entire interpretation; exact event remains pending until valid apply; a mixed agenda batch cannot partly commit; irrelevant event consumed without derived work. | Interpretation payload is explicit test input, not an emulated persistence layer. Catches lost pending evidence and silent overwrite. |
| `test_goals_states_and_due_order` | Goal-driven outcomes with no events, validated state/next-check/reason, deterministic due ordering, non-due needs-input/terminal items. | Synthetic user priority. Catches inbox-only architecture, repeated prompting and invalid future checks. |
| `test_freshness_action_claim_and_uncertain_reconciliation` | New stored revision invalidates old checked evidence; latest coverage and current version required; started/uncertain actions prevent repeat and agenda mutation; read-back after restart; reconciliation, terminal immutability, explicit agenda closure. | No remote send; synthetic receipts stop at unsafe external edge. Catches stale or double effects and inferred success. |
| `test_concurrent_action_and_interpretation` | Concurrent independent CLI processes compete for the same action item, then same pending event; exactly one winner and one durable result. | Synthetic target only. Catches race windows hidden by sequential testing. |

## Independent semantic forward exercise

After the new skills and references exist, the independent acceptance author must read and follow them against synthetic scenarios, documenting steps, resulting proposed state/actions, source routing, and remaining gaps in feature evidence. Required situations: a fresh missing workspace; embedded source instructions demanding sending or changing rules; an irrelevant update; a request already answered; a goals review without inbound events; missing connector access; absent sending authority; a provider timeout with unknown effect. Interpret equivalent message paraphrases by their outcomes, never exact phrasing. Verify skill discoverability in skills.toml, source batching/checkpoint ownership, read-only knowledge-review preservation, and one scheduled update-then-review prompt sharing a root. This semantic exercise checks instructions and decision paths; it does not claim nondeterministic model reliability or a real provider execution.

## Proves / does not prove

Proves the actual public local state API, transaction/restart/conflict behavior and independent skill decision walkthrough within the configured boundaries. Does not prove live provider pagination semantics, connected account access, WhatsApp ingestion implementation, remote sends, VM uptime, schedule activation, or deployment. The user requested dot-codex capability installation; those external activations remain separate setup.

## False-green risks and evidence

A raw database query or mocked CLI would bypass the target and is intentionally absent. Source and receipt fixtures cannot prove provider success; the output must retain that distinction. Automated persistence assertions alone cannot prove source instruction isolation or goal judgment, hence separate semantic evidence. Pending queries and context are implementation output; cross-process journeys, immutable original evidence read-back, distinct conflict probes and competing processes reduce internally consistent but ineffective behavior risks. CLI errors must be structured and nonzero. Assertions target behavior, not implementation layout.

Freeze this document, FEATURE.md, proof/run.sh and proof/acceptance.py before implementation. Official attempts retain logs and contract hashes through the shared capture tool; root records author/reviewer roles and freeze inputs. Any proof setup correction belongs to the independent proof author under the unchanged contract and must retain failure, diff, rationale and revised hashes in evidence. No live accounts or private source data enter fixtures.
