---
name: feature
description: "Create or update features/<id>/FEATURE.md from a rough idea (user story + constraints)."
metadata:
  short-description: Define a feature spec compatible with Press + gate workflow
---

Purpose: produce a high-quality `FEATURE.md` inside `features/<id>/`.

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
   - `features/<id>/`
   - If it exists -> update `FEATURE.md`
   - If not -> create directory and file

2) Convert rough idea into:
   - Clear title and description
   - Explicit, testable behavior
   - Optional user stories and Gherkin scenarios when helpful
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
- Include title and description at minimum
- If scenarios are provided, use valid Gherkin wording

---

## FEATURE.md Template

# <Feature title>

## Description
<Clear problem statement in user-story form>

## Acceptance Scenarios
Feature: <Behavioral capability>
  In order to <goal>
  As a <user>
  I want <capability>

  Scenario: <Scenario title>
    Given <context>
    When <action>
    Then <observable outcome>

## Constraints (optional)
- <constraint>
