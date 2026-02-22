---
name: feature
description: "Create or update features/<id>/feature.yaml from a rough idea (user story + constraints)."
metadata:
  short-description: Define a feature spec compatible with Press + gate workflow
---

Purpose: produce a high-quality `feature.yaml` inside `features/<id>/`.

This file is the source of truth for implementation and acceptance harness generation.

---

## Inputs

If missing, ask only the minimum necessary:

- feature id (e.g., FEAT-001)
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
   - If it exists → update `feature.yaml`
   - If not → create directory and file

2) Convert rough idea into:
   - Clear description
   - Explicit, testable acceptance criteria
   - Minimal constraints

3) Keep acceptance criteria:
   - Observable
   - Black-box
   - Deterministic
   - Suitable for automated testing

4) Avoid:
   - Internal implementation details
   - Speculation
   - Over-engineering
   - Architecture decisions unless explicitly provided

---

## Output rules

- Output ONLY valid YAML for `feature.yaml`
- No commentary
- No Markdown
- No diffs
- Must be machine-parseable

---

## feature.yaml Template

id: <FEAT-ID>
title: <Short title>
description: |
  <Clear problem statement in user-story form>

acceptance:
  - id: AC-1
    text: "<Observable behavior>"
  - id: AC-2
    text: "<Observable behavior>"

constraints:
  backend: "<if relevant>"
  frontend: "<if relevant>"
  storage: "<if relevant>"
  testing: "<if relevant>"
  avoid: "<optional>"

notes:
  - "<Optional clarifications>"