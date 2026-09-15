# Research

Purpose: gather the minimum external evidence needed to reduce speculative planning before findings are written into `docs/APP.md`, `docs/ARCHITECTURE.md`, or `FEATURE.md`.

Use directly for `coding-workflow` Analyze or as focused evidence gathering during Shape. Research findings do not authorize implementation or revision of fixed acceptance.

## Workflow
1) Start with the concrete question
   - Write down the exact uncertainty to resolve.
   - Prefer a narrow question over broad open-ended exploration.

2) Prefer authoritative sources
   - Use repository context and official documentation, including Context7 when it fits the question.
   - Prefer official docs, standards, vendor docs, or primary-source material over blog summaries.
   - Verify current external assumptions using available authoritative sources and follow the session's browsing requirements.

3) Keep the pass bounded
   - Collect only the evidence needed to make the planning decision.
   - Avoid sprawling market scans or implementation deep dives.

4) Return durable findings
   - Summarize the finding, the source, and the implication for the repo decision.
   - Incorporate stable conclusions into documentation when authorized. During Ship, report a contradiction to the workflow owner; do not rewrite the fixed specification or proof.

## Rules
- Do not turn research notes into a parallel planning system.
- Keep claims source-backed when they affect architecture, APIs, or feature proof.
- Respect explicit source and network restrictions; report unavailable evidence precisely.
- If evidence is weak or conflicting, state that clearly instead of pretending the question is settled.
