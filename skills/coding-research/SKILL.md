---
name: coding-research
description: "Gather authoritative external evidence for product, domain, library, or API assumptions before app planning or feature contracts commit to them."
metadata:
  short-description: External evidence gathering for planning
---

# Research

Purpose: gather the minimum external evidence needed to reduce speculative planning before findings are written into `docs/APP.md`, `docs/ARCHITECTURE.md`, or `FEATURE.md`.

## Workflow
1) Start with the concrete question
   - Write down the exact uncertainty to resolve.
   - Prefer a narrow question over broad open-ended exploration.

2) Prefer authoritative sources
   - Use Context7 first for library and framework documentation when it fits the question.
   - Prefer official docs, standards, vendor docs, or primary-source material over blog summaries.
   - Use live web search only when local context and Context7 are insufficient.

3) Keep the pass bounded
   - Collect only the evidence needed to make the planning decision.
   - Avoid sprawling market scans or implementation deep dives.

4) Return durable findings
   - Summarize the finding, the source, and the implication for the repo decision.
   - Fold stable conclusions back into `docs/APP.md`, `docs/ARCHITECTURE.md`, or `FEATURE.md`.

## Rules
- Do not turn research notes into a parallel planning system.
- Keep claims source-backed when they affect architecture, APIs, or feature proof.
- Respect the repo default that web search is disabled unless the run explicitly enables it.
- If evidence is weak or conflicting, state that clearly instead of pretending the question is settled.
