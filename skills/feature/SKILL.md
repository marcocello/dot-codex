---
name: feature
description: "Create or update docs/features/{feature-id-slug}/FEATURE.md from a rough or incomplete idea, including discovery (JTBD, user journey, use cases, and edge cases) before BDD scenarios. Use when the task is feature-spec authoring or refinement. Use the `research` skill when important product, domain, or API assumptions need external evidence."
metadata:
  short-description: Define a feature spec compatible with Press + gate workflow
---

Purpose: produce a high-quality `FEATURE.md` inside `docs/features/<feature-id-slug>/`.

This file is the source of truth for implementation and acceptance harness generation.

---

## Inputs

If missing, ask only the minimum necessary:

- short title
- user persona or core job-to-be-done
- core workflow (happy path)
- key constraints (must/avoid)
- definition of done (observable behavior)

Do NOT ask architecture questions unless strictly required.
Subsequent questions are not mandatory and should be asked only when direction is unclear or a missing detail is blocking progress.

---

## Behavior

1) Load repo-level context when present:
   - Read `docs/APP.md` if it exists.
   - Read `docs/ARCHITECTURE.md` if it exists.
   - Read `docs/CONVENTIONS.md` if it exists.
   - Read `docs/TESTING.md` if it exists.

2) Determine feature directory:
   - `docs/features/<feature-id-slug>/`
   - Slug format: lowercase words separated by hyphens (for example `docs/features/todo-api/`)
   - If it exists -> update `FEATURE.md`
   - If not -> create directory and file
   - no numbering or date prefixes; just a clear slug

3) Run a discovery pass when the idea is incomplete:
   - Write one JTBD statement (`When ... I want ... so that ...`)
   - Map the end-to-end user journey (key steps only)
   - Expand use-case coverage: happy path, key variants, edge cases, and failure/recovery cases
   - Identify user roles and external integrations involved
   - Record high-impact assumptions to validate
   - Use `research` when high-impact assumptions depend on external APIs, framework behavior,
     domain rules, or competitive/product evidence
   - Ask subsequent questions only when direction is unclear and discovery cannot continue safely

4) Convert discovery into `FEATURE.md` behavior:
   - Clear feature title
   - Explicit, testable behavior
   - BDD scenarios as the default acceptance format
   - Gherkin scenarios as the canonical BDD artifact
   - Minimal constraints

5) Keep acceptance behavior:
   - Observable
   - Black-box
   - Deterministic
   - Suitable for automated testing

6) Avoid:
   - Internal implementation details
   - Speculation without tagging assumptions
   - Over-engineering
   - Architecture decisions unless explicitly provided
   - Backward compatibility requirements unless explicitly requested

---

## Output rules

- Output Markdown content for `FEATURE.md`
- Keep it concise and human-readable
- Include title and `Acceptance Scenarios` at minimum
- Include `Acceptance Scenarios` in valid Gherkin
- Use black-box behavior wording in steps (no implementation details)
- Include at least one happy-path scenario plus key edge/error scenarios
- Use `Scenario Outline` + `Examples` when behavior is identical and only data varies
- Do not add a separate `## Description` section unless explicitly requested
- If discovery was needed, include `## Discovery Notes` with short bullets for:
  - JTBD
  - user journey coverage
  - edge/failure coverage
  - assumptions to validate

---

## FEATURE.md Template

# <Feature title>

## Discovery Notes (optional)
- JTBD: <when / want / so that>
- User journey: <step 1 -> step 2 -> ...>
- Edge/failure coverage: <bullet list>
- Assumptions to validate: <bullet list>

## Acceptance Scenarios
Feature: <Behavioral capability>
  In order to <goal>
  As a <user>
  I want <capability>

  Scenario: <Scenario title>
    Given <context>
    When <action>
    Then <observable outcome>

  Scenario Outline: <Variant behavior title>
    Given <context with <value>>
    When <action with <value>>
    Then <observable outcome <result>>

    Examples:
      | value | result |
      | ...   | ...    |

## Constraints (optional)
- <constraint>
