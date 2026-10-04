# Export active members to CSV

Status: specification complete; implementation and proof authoring are outside this task.

## Outcome

Local staff can save the active members from the existing Python CLI into a selected CSV file for their local workflow.

## Observable behavior

- Add the command `python3 members.py export --destination PATH`. The destination is required; relative paths resolve from the current working directory.
- Read the existing `members.json` beside `members.py`, using its current record fields: `name`, `email`, and Boolean `active`.
- Include only records whose `active` value is `true`, ordered by `name` ascending. Use ordinary case-sensitive string ordering, with source order retained for equal names.
- Write UTF-8 CSV with exactly two columns, in this order: `name,email`. Preserve the name and email values and use standard CSV quoting, including for commas, quotation marks, and embedded newlines. Do not include the `active` field.
- If no members are active, produce the header row with no member rows.
- Create the selected local file, or replace its contents if it already exists. Do not create missing parent directories.
- After a successful write, exit zero and report the destination path so staff can locate the saved file.
- If the parent directory is missing or the members source cannot be read, exit nonzero and give a useful error identifying the affected path and reason. Other source-reading or destination-writing failures must likewise report failure rather than success.

## Compatibility and boundaries

- Preserve `python3 members.py list`: print all members in source order with their name, email, and active value, as it does today.
- Preserve the members source and its existing location; exporting does not modify records.
- Use the Python standard library, consistent with the repository. No new dependencies, network access, UI, source-selection option, filtering options, or alternate export formats are in scope.
- File replacement is explicitly requested. Backup files, overwrite prompts, and transactional write guarantees are not additional requirements.

## Decisions and dependencies

The command, columns, active-only selection, ascending name order, CSV quoting, UTF-8 encoding, local file replacement, path reporting, and required failure behavior are settled by the request. Relative-path resolution, ordinary string ordering, stable ties, and a header-only empty result are routine defaults recorded here to remove ambiguity.

The feature depends only on the existing CLI and local members source. No external service or unresolved product decision is required. This document defines the behavior; it does not claim implementation readiness or completed runtime verification.
