---
name: coding-real-user-scenario-tests
description: Create real-user scenario tests for agent workflows that run realistic user prompts through an automatable dev/API listener and verify outcomes against real systems. Use when Codex needs to author or update saved prompt fixtures, demo-readiness testbeds, conversation E2E tests, live integration checks, CRM/Google Sheet/email/calendar write verification, or test definitions that validate actual external side effects instead of only mocked behavior.
---

# Real-user Scenario Tests

## Purpose

Create repeatable tests that behave like a real user talking to the product, while still being
automatable through the dev API listener. The output is usually a plain-text fixture plus docs and
acceptance coverage that proves the fixture is parseable and has real-system verification.

## Core Workflow

1. Load local context.
   - Read the relevant feature contract if one exists.
   - For Followups, inspect `backend/app/scripts/api_interaction_testbed.py` before authoring
     checks; the runtime directives may evolve.
   - Read [references/testbed-runtime.md](references/testbed-runtime.md) for the current fixture
     and verification model.

2. Decide scenario source.
   - If the user provides exact questions, preserve them unless they are untestable.
   - If the user provides context but no questions, generate 3-7 realistic user questions that
     cover the core workflow, important writes, and one prioritization/read-only turn.
   - If neither questions nor enough context exists, ask for the minimum missing information:
     product surface, connected systems, and target workflow.

3. Gather real system context.
   - Inspect provided URLs, sheets, CRM records, mailbox/calendar examples, or repo demo data.
   - If a source is private, use available authenticated connectors or browser skills only when
     permitted. If still blocked, ask for an export or pasted rows; do not invent object names.
   - Identify stable row/object identifiers, owner fields, statuses, and existing write rules.

4. Design verification before writing the fixture.
   - For every turn, define at least one machine-checkable outcome.
   - Prefer durable checks in this order:
     1. Real-system object existence or read-back from the provider.
     2. Tool result row/value checks proving the written/read data.
     3. Successful tool/action trace.
     4. Short response phrases only for user-visible summaries.
   - Do not use exact full-response equality.
   - Do not call a scenario complete if the verification only proves the model said it did work.

5. Write artifacts.
   - Use the repo’s existing testbed layout when present.
   - For Followups demos, prefer `demo/<scenario-slug>/api-testbed-fixture.txt`,
     `README.md`, `questions-and-expected-results.md`, and connection instructions when needed.
   - Keep fixtures plain text, versionable, and manually readable.
   - Include setup requirements: dev listener UID/access code, backend URL, connected provider,
     needed tokens/scopes, active CRM backend, and any sheet-specific instructions.

6. Add or update acceptance coverage.
   - Assert the fixture parses.
   - Assert the fixture contains the intended real-system checks and avoids unsupported checks.
   - Assert live URLs/instructions are referenced when the scenario depends on them.
   - If runtime support is missing for the requested verification, either extend the runner in the
     feature scope or report the precise unsupported verification gap.

7. Validate.
   - Run the narrowest parser/acceptance test first.
   - Run the feature acceptance wrapper when a `FEATURE_DIR` is in scope.
   - Run the repo gate unless the repo contract says not to or a concrete blocker exists.

## Fixture Authoring Rules

- Treat the prompt sequence as a real user journey, not isolated API unit tests.
- Preserve turn order and shared conversation context.
- Include realistic phrasing, ambiguity, and business context, but make expected outcomes precise.
- Use real names and records only after reading the real source.
- Make write turns explicit enough that the agent should mutate the correct object without guessing.
- For owner-filter questions, include the owner semantics in setup/instructions and assert the
  fixture names the owner column or owner value.
- Avoid destructive live-system operations unless the user explicitly wants them and the testbed can
  isolate or reset data.

## Verification Checklist

For each scenario turn, record:

- User question.
- Expected provider(s): CRM, Google Sheet, mailbox, calendar, document/PDF, etc.
- Expected tools/actions.
- Expected real-system proof: object id exists, row has fields, draft exists, event exists,
  attachment/report path exists, or read-back turn returns updated data.
- Fixture directive(s) used.
- Remaining manual check, if any, with the reason it cannot be automated yet.

If a test claims a CRM/Google Sheet/email/calendar write, it must include a real-system check or a
clearly named runtime gap. A successful tool call alone is not enough when the runtime can verify
the provider state.
