---
name: Feature
description: "Create or update FEATURE.md from a rough idea (user story + acceptance criteria). Read_when You want to define feature scope and user stories for this repo."
metadata:
  short-description: Optional user-facing description
---

Purpose: produce a high-quality FEATURE.md for this repo.

## Inputs
If the user did not provide them, ask only the minimum questions needed:
- target user/persona
- core workflow (happy path)
- key constraints (must/avoid)
- what “done” means

## Behavior
1) If FEATURE.md exists, update it (preserve useful sections; replace scope/stories as needed).
2) If ARCHITECTURE.md exists, skim it for constraints that affect the feature (do not quote it; just apply).
3) Write FEATURE.md using the template below.
4) Keep it specific, testable, and minimal. Avoid speculation.

## Output rules
- Output ONLY the contents of FEATURE.md (no commentary, no diffs).
- Use clear user stories and acceptance criteria that can be turned into tests.

## FEATURE.md template
# FEATURE.md

## Context
- Problem:
- Users:
- Why now:

## Scope
### In scope
- ...

### Out of scope
- ...

## User stories
### US-1: <title>
- As a <user>, I want <capability>, so that <benefit>.
- Acceptance criteria:
  - [ ] ...
  - [ ] ...

## Success criteria
- ...

## Open questions
- ...