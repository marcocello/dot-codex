---
name: capture-note
description: "Capture raw or loosely structured material into dated markdown notes while preserving the collection's filename, frontmatter, and organization conventions."
---

# Capture Note

Purpose: add personal knowledge, diary, journal, meeting, or second-brain notes to the right markdown location with minimal friction and no forced folder convention.

## Workflow

1. Identify the note material and any explicit target:
   - Treat spoken transcripts, rough bullets, pasted fragments, and polished prose as valid input.
   - Extract only the user's intended meaning, dates, people, decisions, tasks, and links.
   - Do not invent facts, summaries, dates, tags, or context that the user did not provide or that cannot be inferred from the target collection's local convention.
2. Find the note collection:
   - If the user gives a folder, inspect that folder first.
   - If the user only says "notes", "diary", "journal", "second brain", or similar, inspect the current workspace for likely markdown note roots before asking.
   - Prefer `rg --files` or `find` to list markdown files, then sample nearby files before editing.
3. Inspect folder structure before choosing a destination:
   - Look for directories with similar markdown files, such as daily notes, journals, inbox notes, meetings, people, projects, or topic folders.
   - Compare filename patterns, dates, title casing, frontmatter keys, heading levels, tag style, and whether notes are one file per day or one file per topic.
   - Choose the folder that already contains similar markdown notes.
   - Ask for clarification when multiple destinations are equally plausible or when writing would materially change a personal organization system.
4. Decide whether to append or create:
   - Append to an existing dated daily note when the collection clearly uses daily files and the target date already exists.
   - Create a new markdown file when the collection uses one file per entry, topic, meeting, or when no dated file exists.
   - Never overwrite unrelated notes. Preserve existing content order and local separators.
5. Write the note:
   - Use the target collection's existing filename and frontmatter conventions when present.
   - Include a date and title. Use frontmatter if similar notes use frontmatter; otherwise use a markdown heading with the date nearby.
   - Keep the body readable: short paragraphs, bullets for lists, and sections only when they add clarity.
   - Preserve uncertainty from the source text. Mark unclear items as unclear instead of resolving them by guesswork.

## Destination Heuristics

Prefer the strongest local convention over a generic preference:

- Daily note folders: filenames like `2026-06-08.md`, `2026-06-08 Monday.md`, or `Journal/2026/06/2026-06-08.md`.
- Diary or journal folders: dated entries with reflective prose and simple headings.
- Meeting folders: filenames with people, company, project, or meeting titles.
- Inbox or capture folders: unprocessed notes, rough transcripts, or short dated captures.
- Topic folders: notes grouped by domain, project, person, or source.

If no convention is discoverable, create a conservative markdown file near the requested folder: `YYYY-MM-DD-title-slug.md`, with a top-level title and date.

## Markdown Shape

Match existing notes first. When there is no clear pattern, use:

```markdown
---
date: YYYY-MM-DD
title: Note title
---

# Note title

Source note content rewritten clearly, without adding new facts.
```

For daily-note append operations, prefer:

```markdown
## Note title

- Captured: YYYY-MM-DD HH:MM
- ...
```

Use the user's local timezone when known from context. If the date is ambiguous, use today's date only for capture metadata and keep any event date uncertainty in the body.

## Safety Rules

- Do not print sensitive personal note content in the final response unless the user asks.
- Do not normalize private folder structures into a new system.
- Do not create tags, categories, backlinks, or aliases unless similar notes already use them.
- Do not move or rename existing notes unless explicitly requested.
- After editing, summarize the file path changed and whether the note was appended or created.
