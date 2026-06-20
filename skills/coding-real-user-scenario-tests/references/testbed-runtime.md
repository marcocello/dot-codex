# Testbed Runtime Reference

Use this reference when authoring real-user scenario test fixtures for Followups-style dev listener testbeds.

## Dev Listener Runtime

The current Followups runner is:

```text
backend/app/scripts/api_interaction_testbed.py
```

It sends each fixture turn to:

```text
POST /api/dev/listener/webhook
```

Required runtime inputs:

- `--fixture`: plain-text fixture file.
- `--output`: JSON result file.
- `--base-url`: backend API URL, usually local dev API.
- `--access-code`: dev listener access code.
- `--uid`: registered dev listener UID.
- `--thread-id`: recommended for repeatable isolated conversations.
- `--timeout-seconds`: per-turn timeout.
- `--hubspot-token`: required only for HubSpot real object checks.

The runner preserves order, waits for a final response before moving to the next turn, writes JSON evidence, and stops on the first timeout/failure/assertion failure.

## Fixture Format

Each user turn starts with `- `. Indented lines continue the same turn. Comment lines start with `#`.

```text
- User asks a realistic question or gives an update.
  expect_contains: stable phrase in final response
  expect_tool: expected_tool_name
  expect_tool_result: tool_name:path.to.field=expected value
  expect_tool_row: tool_name:field=value;other_field=value
  expect_hubspot_object: task:create_task
  expect_delivery_status: suppressed
```

Do not use exact full response equality. Prefer durable phrases, tool checks, and real-system checks.

## Supported Directives

- `expect_contains: <phrase>`
  - Checks the final assistant response contains a stable phrase.
  - Use sparingly for user-visible summaries.

- `expect_tool: <tool_name>`
  - Checks the tool/action trace contains a successful tool.
  - Good baseline for read/write routing, not sufficient alone for writes.

- `expect_hubspot_object: <task|deal>:<source_tool>`
  - Collects returned IDs from `source_tool`, then verifies the object exists in HubSpot.
  - Requires `--hubspot-token`.
  - Current support is task/deal only.

- `expect_tool_result: <tool>:<path>=<value>`
  - Checks a successful tool result has a field at a dotted path equal to a value.
  - Useful for provider write responses that include ids, status, subject, event id, draft id, spreadsheet row ids, or normalized payload fields.

- `expect_tool_row: <tool>:<field>=<value>;...`
  - Scans dict rows returned in a tool result and passes when one row matches all fields.
  - Useful for Google Sheet/CRM read-back checks after `get_objects` or write responses that return `record`.

- `expect_delivery_status: <status>`
  - Checks final delivery status, commonly `suppressed` in dev listener runs.

## Real-system Verification Patterns

### CRM / HubSpot

Use:

```text
expect_tool: create_task
expect_hubspot_object: task:create_task
```

or:

```text
expect_tool: create_deal
expect_hubspot_object: deal:create_deal
```

For contact/company writes, inspect the current runner. If no real object directive exists, use a read-back turn with `get_objects` plus `expect_tool_row`, or extend the runner.

### Google Sheets

For reads:

```text
expect_tool: get_objects
expect_tool_row: get_objects:Nome=Emanuela;Cognome=Bivio;Azienda=Progetto 5 cooperativa sociale
```

For writes, prefer a read-back assertion in the same tool result when available:

```text
expect_tool: edit_contact
expect_tool_result: edit_contact:record.Stato Lead=IN TRATTATIVA
```

If the write tool does not return the updated row, add the next turn as a read-back:

```text
- Mostrami la riga aggiornata di Emanuela Bivio.
  expect_tool: get_objects
  expect_tool_row: get_objects:Nome=Emanuela;Cognome=Bivio;Stato Lead=IN TRATTATIVA
```

Always include sheet interpretation instructions when column semantics are non-standard, especially owner columns.

### Email Drafts

Use tool trace plus result fields when the draft tool returns a provider id or subject:

```text
expect_tool: draft_email
expect_tool_result: draft_email:subject=Recap incontro
```

If the runtime cannot query the provider for the created draft, name the gap and add a runner task: verify draft existence through Gmail/Outlook API by returned draft id, recipient, and subject.

### Calendar / Meeting Creation

Use tool trace plus event id/status fields when returned:

```text
expect_tool: create_event
expect_tool_result: create_event:summary=Demo Progetto 5
```

Real verification should read the provider calendar by returned event id and assert title, time, attendees, and Meet/link state when relevant. If the runner lacks this, specify the missing calendar verifier.

### Documents / PDF Reports

Use:

```text
expect_tool: create_pdf_recap_report
expect_tool_result: create_pdf_recap_report:path=...
```

When possible, verify the artifact exists and contains stable text. If the runner does not support artifact checks, add proof coverage or a runner extension.

## Definition Of Done

A real-user scenario testbed is done only when:

- The fixture parses.
- Each write has a real-system verification path or a documented unsupported gap.
- The dev listener run command is documented.
- Result inspection commands are documented.
- Relevant proof tests pass.
- The repo gate or project-required checks pass, or a concrete blocker is reported.
