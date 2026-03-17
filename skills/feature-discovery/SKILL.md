---
name: feature-discovery
description: "Expand a rough feature idea into full problem-space coverage before coding: JTBD, user journey, use cases, edge/failure cases, roles, integrations, assumptions, and V1/V2/V3 scope cuts. Use when a user has an idea but lacks clarity on complete behavior."
metadata:
  short-description: Discovery workflow for feature completeness
---

Purpose: turn a partial feature idea into a discovery artifact that is ready to merge into `FEATURE.md`.

Use this before implementation when behavior coverage is unclear.

---

## Inputs

Ask only for missing essentials:

- feature idea/title
- target user/persona
- desired business or user outcome
- hard constraints (must/avoid)

If details are still missing, proceed with explicit assumptions.
Subsequent questions are not mandatory and should be asked only when direction is unclear or a missing detail is blocking progress.

---

## Workflow

1) Frame the job-to-be-done
   - Write one JTBD statement: `When ... I want ... so that ...`

2) Map the user journey
   - List the end-to-end journey in ordered steps
   - Keep steps user-visible and domain-focused

3) Expand use-case coverage
   - Happy path
   - Key variants
   - Edge cases
   - Failure and recovery cases

4) Identify opportunity areas
   - User pain/friction points along the journey
   - Candidate solution options for each high-impact pain

5) Define operating context
   - User roles interacting with the feature
   - Integration dependencies and external systems
   - Assumptions and unknowns that need validation

6) Slice delivery scope
   - V1: smallest valuable slice
   - V2: important capability expansion
   - V3: advanced/optimization scope

7) Prepare merge-ready output
   - If a feature directory is provided, map findings into `docs/features/<feature-id-slug>/FEATURE.md`
   - Preserve concise, behavior-first wording
   - Convert stable findings into Gherkin acceptance scenarios
   - Ask subsequent questions only when direction is unclear and the discovery cannot proceed safely

---

## Output

Return concise Markdown with this shape:

# <Feature title>

## Discovery Canvas
- JTBD: <statement>
- User journey: <step 1 -> step 2 -> ...>
- Use cases: <happy path + variants>
- Edge cases: <list>
- Failure and recovery: <list>
- Roles: <list>
- Integrations: <list>
- Assumptions to validate: <list>
- Scope cuts: V1 / V2 / V3

## Scenario Seeds
- <black-box scenario statement 1>
- <black-box scenario statement 2>
- <key error-path scenario statement>

Constraints:
- Keep language implementation-agnostic
- Focus on observable behavior
- Prefer completeness of behavior space over solution detail
