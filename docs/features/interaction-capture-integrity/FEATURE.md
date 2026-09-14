# Interaction Capture Integrity

## Goal

Produce clean, analysis-ready interaction records from app-visible Codex sessions without treating lifecycle noise as dialogue or exposing additional sensitive content.

## Behavior

- Human-visible dialogue is recognized in both legacy `event_msg` messages and `response_item` messages. Mirrored representations and replayed message IDs do not duplicate dialogue; distinct repeated messages remain intact. Response-item context blocks, selected skill instructions, inter-agent messages, reasoning, and tool traffic are excluded. Aborted and unfinished turns remain outside completed history.
- A captured completed turn contains at least one human-visible user or assistant message. `task_started`/`task_complete` pairs with no human-visible messages are omitted and listed under `capture.omitted_empty_turn_ids` when the session otherwise produces a record.
- An unfinished turn is reported under `incomplete_turn_ids` only after it contains human-visible dialogue. Empty started turns do not make an otherwise complete interaction partial.
- A newly visible session with no completed or in-progress human-visible dialogue is counted as `empty` and does not create a record or index entry. If an existing record's current source is unexpectedly empty, synchronization preserves the historical record.
- Retained messages add `timestamp`; completed turns add `started_at` and `completed_at`. These are optional opaque source timestamp strings and are omitted when absent.
- `capture.source_event_count` counts every parsed JSONL object once. `capture.event_type_counts` has the same total and uses only allowlisted keys: `session_meta`, `response_item`, `turn_context`, `compacted`, `event_msg.task_started`, `event_msg.task_complete`, `event_msg.user_message`, `event_msg.agent_message`, `event_msg.turn_aborted`, `event_msg.other`, and `other`. Unknown source values are bucketed under the applicable `other` key and never become output keys.
- `task.title` and `task.updated_at` retain app-visible `title` and `updatedAt` strings when supplied by `thread/list`. `task.originator` remains the existing allowlisted session metadata. Originator and title use the same credential redaction as dialogue; timestamps remain opaque strings.
- Index entries add integer `turn_count` and `message_count`, plus optional redacted `title` and opaque `updated_at`. Older retained entries without these additive fields remain valid.
- Credential redaction additionally covers recognized Slack, GitLab, Google API, and bearer-token forms. Redaction counts remain explicit without retaining original values.
- Existing add/update/retain, project/worktree selection, atomic-write, locking, and partial-coverage behavior remains unchanged.

## Constraints

- Keep schema version 1 backward-readable: new record and index fields are additive, and older retained index entries remain accepted.
- Do not automatically delete or rewrite historical empty records that are no longer app-visible.
- Keep capture manually invoked and project-owned. Do not add background ingestion, a database, a raw-event archive, or automatic prompt injection.
- Preserve only allowlisted session/app metadata and event-type counts from non-dialogue events; never persist other payload contents.

## Non-Goals

- Reconstructing hidden reasoning, tool inputs or outputs, system/developer instructions, or command logs.
- Cross-host capture or automatic migration of existing interaction stores.
- Classifying product decisions or harness failures during capture.
