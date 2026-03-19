---
name: feature-discovery
description: "Produce a lean, dry, breadth-first discovery document for a feature idea before coding. Use when the user needs fast clarity on journey coverage, key edge/failure paths, and a concise acceptance contract without bloated artifacts."
metadata:
  short-description: Lean discovery for feature completeness
---

Purpose: turn a rough feature idea into a lean, dry, actionable document that covers behavior breadth without unnecessary sections.

Use this before implementation when direction is partially clear but coverage is incomplete.

---

## Inputs

Ask only for missing essentials:

- feature idea/title
- target user/persona
- desired user/business outcome
- hard constraints (must/avoid)

If details are still missing, proceed with explicit assumptions.
Subsequent questions are not mandatory and should be asked only when direction is unclear or a missing detail is blocking progress.

---

## Workflow

1) Frame the job-to-be-done
   - Write one JTBD statement: `When ... I want ... so that ...`

2) Map user journey breadth
   - List only key user-visible steps end-to-end
   - Keep journey compact and outcome-focused

3) Expand coverage minimally
   - Capture core happy path
   - Capture highest-risk variants/edge cases/failure cases
   - Avoid duplicate phrasing across sections

4) Lock a concise behavior contract
   - Convert stable findings directly into Gherkin `Acceptance Scenarios`
   - Keep black-box wording and implementation-agnostic steps

5) Keep output lean
   - Discovery Canvas max 8 bullets total
   - Acceptance Scenarios max 6 scenarios total (4 core + 2 edge/failure)
   - One-line bullets when possible
   - Scenario Seeds are optional and only added when explicitly requested

---

## Output

Return concise Markdown with this shape:

# <Feature title>

## Discovery Canvas
- JTBD: <statement>
- User journey: <step 1 -> step 2 -> ...>
- Core use cases: <short bullets>
- Edge/failure focus: <short bullets>
- Roles/integrations (only if relevant): <short bullets>
- Assumptions to validate: <short bullets>
- Scope cut (V1 first): <one line>

## Acceptance Scenarios
Feature: <Behavioral capability>
  In order to <goal>
  As a <user>
  I want <capability>

  Scenario: <Core behavior>
    Given <context>
    When <action>
    Then <observable result>

Constraints:
- Keep language implementation-agnostic
- Focus on observable behavior
- Prefer breadth coverage over verbose prose
- Keep the document lean and dry
