# Interaction Capture Integrity Proof

## Paginated-history repair, November 1, 2026

The live app migrated legacy JSONL history to its paginated store. All 103 distinct chats behind the 117 unavailable session entries have `history_mode=paginated`. The old exporter still attempted to open their removed JSONL paths. The app's read-only history API can read these chats.

The current executable proof is `proof/acceptance.py`. The previously referenced `tests/unit/test_interaction_capture_integrity.py` is absent from this checkout. The historical scenarios below describe earlier verification; the following current scenarios replace that unavailable executable boundary without changing the accepted dialogue rules.

- Run the production CLI against a fake outer app server that implements metadata reads and multiple full-history pages. Read back the persisted records and index. Verify completed dialogue, commentary, repeated messages, credential redaction, context/tool/reasoning exclusion, timestamps, incomplete turns, empty turns, duplicate session entries, and project filtering.
- Repeat the capture unchanged and verify byte and modification-time stability. Complete a pending turn, capture the exact current chat, and verify the updated history. Remove chats from the visible list and verify retained history.
- Make a history read fail and verify partial coverage plus preservation of the existing record. Reject summary-only pages and pagination cycles without publishing a truncated record.
- Capture empty and interrupted turns. Verify empty-session suppression and exclusion of interrupted dialogue.
- Capture legacy JSONL through the same CLI. Verify mirrored response/event messages appear once and injected context is excluded.

Only the outer app server and temporary source data are fake. The capture CLI, parser, writer, lock, and persisted read-back are real. A separate authorized live recapture and aggregate read-back verify recovery in this project's `docs/interactions/` store. No real chats are resumed or modified.

Paginated records add `capture.source_format=app-server-paginated`. Their event counts describe the normalized parser events, including an `other` placeholder for each excluded API item. Raw tool and reasoning payloads are never included in those normalized events. Legacy JSONL provenance remains unchanged.

## Done

- Empty completed and empty unfinished lifecycle turns cannot appear as dialogue or falsely make a record partial.
- Nonempty records preserve timestamps, compact event provenance, app-visible metadata, analysis counts, and strengthened credential redaction without storing excluded event payloads.
- The real capture CLI skips new empty sessions, preserves an existing historical record when its visible source is empty, and still adds, updates, and retains normal project/worktree chats.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture.py" --feature-dir docs/features/interaction-capture-integrity --timeout-seconds 90 --note "verify clean analysis-ready interaction capture"
```

## Scenario: Parser excludes lifecycle noise and retains safe provenance

- Dedicated test: `test_record_omits_empty_turns_and_retains_safe_provenance` in `tests/unit/test_interaction_capture_integrity.py`.
- Producer/activation: pytest feeds realistic JSONL session metadata, empty lifecycle turns, completed visible turns, an empty active turn, timestamps, recognized fake credential forms, unknown event-type strings, and non-dialogue event payloads through the production parser.
- Consumer: an analyst reading a generated interaction record.
- Read-back: assertions inspect completed turns, completeness state, omitted IDs, timestamps, count totals, safe allowlisted event keys, originator redaction, dialogue redaction markers, and absence of excluded payload text.
- Fake: deterministic local JSONL only; parser and record builder are real.
- Catches: empty turns counted as interactions, empty active turns producing false partial state, timestamps flattened away, arbitrary event values becoming output keys, provenance requiring raw sensitive payload storage, or recognized credentials leaking.

## Scenario: CLI skips new empty sessions but preserves history

- Dedicated test: `test_cli_skips_empty_sessions_in_project_and_current_modes` in `tests/unit/test_interaction_capture_integrity.py`.
- Producer/activation: pytest invokes the production capture CLI in project mode against the fake outer app-server boundary with one new empty session, one existing record whose current session is empty, and one normal app-visible session; it then invokes current mode for the new empty task.
- Consumer: `docs/interactions/index.json`, managed records, and the CLI summary.
- Read-back: the new empty task has no file or index entry in either mode, the historical record remains byte-identical and indexed, the normal task has counts, redacted title, update metadata, and title redaction count, and both summaries report `empty` accurately.
- Fake: only the outer Codex app server and temporary source sessions; capture selection, parser, writer, lock, and index are real.
- Catches: destructive cleanup, new zero-dialogue clutter, current/project divergence, title credential leakage, summary lies, or metadata that exists only in an inner helper.

## Scenario: Current response-item dialogue reaches the persisted store

- Dedicated test: `test_cli_captures_response_items_and_updates_completed_history` in `tests/unit/test_interaction_capture_integrity.py`.
- Producer/activation: invoke the production CLI with the response-item envelope observed in local app-visible sessions, including injected context, user text, image metadata, commentary, final answers, and a pending turn. Invoke it again unchanged, then complete the pending turn and invoke current mode.
- Consumer/read-back: inspect the actual JSON record and index for exact message order, counts, redaction, image metadata without image payloads, completed-history boundaries, updates, and byte/mtime stability on unchanged capture.
- Fake: only the outer app server and synthetic sessions; selection, parser, writer, and persisted read-back are real.
- Catches: falsely empty current sessions, role-only filtering that saves injected instructions or environment context, missing commentary, unfinished dialogue leakage, inconsistent current/project modes, or unnecessary rewrites.

## Scenario: Mixed source representations preserve dialogue once

- Dedicated test: `test_mixed_formats_deduplicate_mirrors_but_preserve_repeated_messages` in `tests/unit/test_interaction_capture_integrity.py`.
- Producer/activation: pass mixed legacy and response-item messages, a repeated response ID, intentional same-text messages, and an aborted turn through the production record builder.
- Consumer/read-back: assert exact completed message order and multiplicity, with the aborted turn listed only as incomplete.
- Fake: synthetic local source objects only.
- Catches: double capture from mirrored formats, deletion of intentional repeats, replay duplication, and incorrectly completing an aborted turn.

## Scope

Proves:
- Clean v1-compatible records and index entries at the real parser and CLI boundaries.
- No persistence of non-dialogue payload contents in the new provenance surface.

Does not prove:
- Live app-server compatibility beyond the existing protocol boundary.
- Removal of empty records already retained in a target repository.
- Detection of every possible secret format.

False-green risks:
- Direct parser checks alone could miss writer behavior, so one scenario invokes the complete CLI.
- Text absence can be weak, so fixtures place unique excluded payload markers and assert they are absent from serialized records.
- Legacy-only fixtures previously passed while live sessions stored dialogue solely as response items; the dedicated CLI scenario now uses that observed envelope. Live project recapture and aggregate persisted read-back additionally verify this invocation's real target without storing source logs in proof evidence.

Evidence method:
- deterministic

Known gaps:
- Existing stores need a later explicit recapture or migration if historical empty files should be removed.

## Environment

- Repository-local Python and pytest.
- Temporary Git repository, worktree, JSONL sessions, app state, fake outer app server, and interaction store.
- No credentials, network, external account, or production-data mutation.
- Consumption target for this repair: the installed local capture entrypoint and this project's `docs/interactions/` store, activated by the explicitly requested live project capture after deterministic proof.
