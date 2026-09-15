# Interaction Capture Integrity Proof

## Done

- Empty completed and empty unfinished lifecycle turns cannot appear as dialogue or falsely make a record partial.
- Nonempty records preserve timestamps, compact event provenance, app-visible metadata, analysis counts, and strengthened credential redaction without storing excluded event payloads.
- The real capture CLI skips new empty sessions, preserves an existing historical record when its visible source is empty, and still adds, updates, and retains normal project/worktree chats.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/interaction-capture-integrity --timeout-seconds 90 --note "verify clean analysis-ready interaction capture"
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
