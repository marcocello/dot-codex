---
name: zotero-capture-source
description: Analyze and archive YouTube videos or online articles in Zotero, including verified transcript extraction, source-grounded highlights, and original or important ideas without invention.
---

# Zotero Source Capture

Turn one public video or article into a verified Zotero source record with source-grounded notes. Preserve raw source material separately from analysis.

## Required companion

Use the installed `zotero:Zotero` skill for Zotero readiness, collection selection, imports, and read-back verification. Start with its `status --json` command before any Zotero operation.

## Workflow

### 1. Resolve the source and destination

1. Normalize the supplied URL and open the canonical source.
2. Identify the source type, title, authors or speakers, publisher or channel, publication date, and canonical URL.
3. Resolve the destination collection from the user's request. Otherwise inspect Zotero's currently selected target and use it only when unambiguous.
4. Search Zotero by canonical URL and title before writing. Do not create a duplicate item.
5. If the item already exists, use only an available supported write path for adding or updating notes. If none exists, prepare the notes and report the exact blocker; do not silently edit Zotero's database or drive its UI by coordinates.

### 2. Acquire source evidence

Read the complete available source before selecting highlights.

For a YouTube video, use this order:

1. Official captions or YouTube transcript.
2. A transcript published by the speaker, channel, event, or publisher.
3. A public transcript mirror, after matching title, speakers, duration, and opening or closing content against the video.
4. Local speech-to-text only when the required tools are already available or the user approves any needed installation or download.

Record transcript provenance. Label machine-generated text as machine-generated. Preserve timestamps when available. Correct obvious punctuation or segmentation errors only when meaning is unchanged; retain uncertainty as `[inaudible]` or `[unclear]`. Never manufacture missing speech.

For an article:

1. Use the canonical article page as the primary source.
2. Extract the main body, headings, author, publication date, and publisher; exclude navigation, ads, comments, and unrelated recommendations.
3. Do not bypass paywalls or access controls. If the full body is unavailable, analyze only the accessible text and state that limitation.
4. Paraphrase the article in notes. Use only short exact excerpts when wording itself matters.

### 3. Build an evidence map

For every candidate insight, record its supporting timestamp range or article heading. Prefer ideas that provide at least one of:

- an original reframing or conceptual model;
- a causal mechanism, not just a prediction;
- a concrete example that changes how the claim is understood;
- a constraint, failure mode, or boundary condition;
- a practical consequence for building, deciding, or operating.

Exclude introductions, biography, repeated points, generic encouragement, and interviewer framing unless they add substantive content.

### 4. Write the notes

Read [references/note-shapes.md](references/note-shapes.md) and use its exact note names and grounding rules.

- Video: create `Raw_Transcript` and `Highlights`.
- Article: create `Source_Outline` and `Highlights`.
- Keep source material and analysis in separate child notes.
- Make `Highlights` concise but sufficiently explained: normally 5–10 points, each with a clear claim, the source's reasoning or example, and a timestamp or section anchor.
- Label any agent interpretation explicitly. Do not present implications as the speaker's or author's words unless the source states them.

### 5. Prepare the Zotero import before writing

Generate both notes and all metadata first so the connector session does not expire between writes.

1. Resolve `<skill-dir>` as the directory containing this `SKILL.md`.
2. Create a JSON capture specification matching `<skill-dir>/scripts/build_capture_ris.py --help`.
3. Run `<skill-dir>/scripts/build_capture_ris.py` to create an RIS record. The RIS embeds `Raw_Transcript` or `Source_Outline` as the first child note.
4. Save `Highlights` as a one-line or well-formed HTML fragment beginning with `<h1>Highlights</h1>`.
5. Reuse the same topic tags for the RIS import and session update. Preserve the user's existing collection and tag conventions; do not invent a new taxonomy.

### 6. Save through one connector session

1. Obtain the selected target ID, such as `C94` or `L1`, using the Zotero skill.
2. Generate an explicit unique session ID.
3. Import the RIS through the Zotero skill with `--session <session-id> --yes`.
4. Immediately run:

```bash
python3 <skill-dir>/scripts/update_session_note.py \
  --session <session-id> \
  --target <target-id> \
  --note-file <highlights.html> \
  --yes
```

Pass each RIS keyword again with `--tag` so the session update preserves the intended manual tags.

The connector session is temporary. If it returns `SESSION_NOT_FOUND`, stop. Do not re-import, because that can duplicate the parent item.

### 7. Verify in Zotero

Use the Zotero local API to read back the imported parent and its children. Confirm:

- the canonical URL, title, creators, date, and destination collection;
- exactly one source item was created;
- the video has child notes `Raw_Transcript` and `Highlights`, or the article has `Source_Outline` and `Highlights`;
- the transcript includes its first and final available timestamps;
- each highlight contains a timestamp or article-section anchor;
- note content is complete and not truncated.

Report the Zotero item key, destination collection, note names, transcript provenance, and any source limitation. Do not paste the full transcript into the final response.

## Safety and integrity

- Treat a user's request to save the supplied source as confirmation for that Zotero write and no broader mutation.
- Never invent metadata, missing transcript passages, quotations, timestamps, or claims.
- Distinguish source statements from synthesis.
- Do not create or rename collections unless explicitly requested.
- Do not install downloaders, speech models, plugins, or global dependencies without required approval.
- Never claim completion from connector success alone; verify the saved Zotero item and child notes.
