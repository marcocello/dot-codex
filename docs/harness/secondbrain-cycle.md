# Personal second-brain cycle

This is an opt-in workflow for maintaining context and following unfinished outcomes across sources. It uses two skills, `secondbrain.yaml`, one private workspace, the existing Codex harness, and existing provider tools. It does not start merely because a knowledge skill is installed.

## Components and ownership

| Component | Responsibility |
| --- | --- |
| Source connectors | Read the selected account/resource, collect complete incremental pages, retain original identity and revision, and perform explicitly authorized provider actions. |
| Personal memory | Keep current evidence-backed facts about people, projects and commitments; retain the original source changes separately. |
| Direction | `profile.md`, `priorities.md` and `rules.md` express user-confirmed context, priorities and delegated authority. Imported documents cannot edit these instructions. |
| Agenda | Track unfinished outcomes, reasons, source evidence and next checks, including waiting and needs-input states. |
| Reasoning and execution | `secondbrain-update` interprets changes; `secondbrain-review` decides and uses existing skills/tools, then verifies results. |
| Interaction and oversight | The current chat, Telegram or Codex app carries instructions, corrections and meaningful notifications. The VM or app provides the runtime, not the source of priorities. |

## State and flow

The explicit workspace contains a SQLite database and three readable direction documents. Source history answers what happened; current facts answer what is believed now; agenda and action history answer what remains and what was attempted. All manual and recurring runs must select the same workspace. Credentials remain with existing connection owners.

1. Register only selected sources with account/resource scope. Each source has its own checkpoint. At first use choose an initial baseline or lookback appropriate to the request; an absent checkpoint does not authorize importing all historical accounts.
2. Fetch one complete page or bounded complete snapshot through a supported connector. Persist that page and its checkpoint atomically. Resume from the stored checkpoint after downtime. If a provider only exposes timestamps, use a stable upper cutoff and an overlapping lower bound with stable event identities; never use only “the last hour.” Do not mark a failed or incomplete fetch successful. A complete empty page can advance.
3. Interpret pending evidence with existing context. Merge related identities, preserve uncertainty and contradictions, supersede outdated facts, and update outcomes instead of making one task per message. Mark irrelevant evidence processed without inventing work. Original evidence stays immutable.
4. Review due work plus, when requested, current goals. Act, ask, wait, close or dismiss. An item waiting for an answer has a next check; one waiting for a user decision may remain needs-input without repeated prompts. New evidence can resolve it without a scheduled wakeup. Goals can generate work without inbound events.
5. Before an effect, reread the live target, reconcile any reply or changed plan, check actual authorization and reserve one action. A database record does not grant authority. The local freshness check detects superseded stored revisions, not changes that a connector has not fetched yet.
6. Verify the effect at its consumer, record a receipt, update the outcome and choose the next check. Interrupted/uncertain attempts remain visible and block repeat execution until reconciled. A successful tool invocation alone is not verified success.

The standard-library CLI owns transactions, immutable source revisions, optimistic updates and action reservation. It does not call providers, interpret text, verify remote effects or schedule itself. Its [command contract](../../skills/secondbrain-update/references/state-cli.md) is shared by both skills.

## Activation and boundaries

Configure `secondbrain.yaml` from the tracked `secondbrain.template.yaml`, then invoke `secondbrain-update` and `secondbrain-review` with that configuration. The [configuration contract](../../skills/secondbrain-update/references/configuration.md) owns schema, helper commands, source scope and first-use setup. Both skills reread the file and use the same workspace; the state CLI retains its explicit `--root` interface. A previously disabled/none choice remains disabled until explicitly changed. This workspace does not replace `knowledge.toml`, change a knowledge default or migrate an existing collection. Ordinary `knowledge-review` remains read-only.

Only configure recurring execution when the user requests it. Use the available native automation tool for a chat/app recurrence. The [schedule reconciliation procedure](../../skills/secondbrain-review/references/scheduling.md) applies separate update/review intervals through the native automation tool. YAML is not watched automatically: explicitly reconcile edits, or an enabled schedule reconciles drift on its next existing wakeup. Paused jobs require explicit reconciliation. A VM CLI runner needs a scheduler on that VM; the desktop's existence is not proof of unattended remote execution. Missing tools or revoked access leave the affected source's checkpoint unchanged and produce an actionable limitation, while independent sources may continue.

No live schedule, account selection, provider credential, or autonomous-send rule ships in this repository. WhatsApp uses [wacli](../../skills/secondbrain-update/references/whatsapp.md): a separately supervised sync maintains its local mirror, while intake reads the configured store/chats. Installation, pairing and live source verification remain setup work. Other providers are used through available connector skills, with unsupported incremental collection reported rather than simulated. Existing external stores remain authoritative for their own records.

## Validation and limits

Durable state proof lives in `docs/features/secondbrain-cycle`; configuration and schedule-plan proof lives in `docs/features/secondbrain-configuration`. Its executable proof uses the public CLI in separate processes and temporary workspaces. Synthetic sources and receipts exercise the local durable cycle; they do not prove live provider completeness, message delivery, model judgment or a running scheduler. Independent skill scenarios assess interpretation and permissions separately. Before enabling a real recurrence, exercise the intended source manually, verify its checkpoint/read-back, and establish the host that will execute it.
