---
name: feature
description: "Create or update docs/features/{feature-id-slug}/FEATURE.md from a rough idea (user story plus constraints). Use when the task is feature-spec authoring or refinement."
metadata:
  short-description: Define a feature spec compatible with Press + gate workflow
---

Purpose: produce a high-quality `FEATURE.md` inside `docs/features/<feature-id-slug>/`.

This file is the source of truth for implementation and acceptance harness generation.

---

## Inputs

If missing, ask only the minimum necessary:

- short title
- user persona
- core workflow (happy path)
- key constraints (must/avoid)
- definition of done (observable behavior)

Do NOT ask architecture questions unless strictly required.

---

## Behavior

1) Determine feature directory:
   - `docs/features/<feature-id-slug>/`
   - Slug format: lowercase words separated by hyphens (for example `docs/features/todo-api/`)
   - If it exists -> update `FEATURE.md`
   - If not -> create directory and file
   - no numbering or date prefixes; just a clear slug

2) Convert rough idea into:
   - Clear feature title
   - Explicit, testable behavior
   - BDD scenarios as the default acceptance format
   - Gherkin scenarios as the canonical BDD artifact
   - Minimal constraints

3) Keep acceptance behavior:
   - Observable
   - Black-box
   - Deterministic
   - Suitable for automated testing

4) Avoid:
   - Internal implementation details
   - Speculation
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

---

## FEATURE.md Template

# <Feature title>

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
