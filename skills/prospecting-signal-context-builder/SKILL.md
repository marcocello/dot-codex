---
name: prospecting-signal-context-builder
description: Build product-agnostic GTM signal context files for signal detection. Use when Codex needs to turn user-provided text or files into a normalized `signal-context.md` containing product context, sector context, ICP, competitors, alternatives, pain points, trigger events, disqualification rules, signal criteria, search seeds, and engagement constraints for use by the prospecting-signal-detector skill.
---

# Signal Context Builder

Use this skill to create or update `signal-context.md` for `prospecting-signal-detector`.

This skill is product, project, and sector agnostic. All product context, sector context, ICP,
competitors, alternatives, signal criteria, and engagement constraints must come from
user-provided text or files.

## Inputs

Accept source material from:

- The user's current message or pasted notes.
- Workspace files named by the user.
- Product briefs, positioning docs, website copy, sales notes, ICP notes, CRM exports, competitor
  notes, market research, call transcripts, campaign plans, or existing `signal-context.md`.
- Links or live research only when the user asks for current external evidence.

If source material is missing or too thin, ask for the smallest missing high-impact input. Do not
invent product claims, sectors, ICPs, competitors, alternatives, or signal definitions.

## Output

Write a human-editable markdown file named `signal-context.md` at the workspace root unless the
user asks for another path.

Use `references/context-template.md` as the output structure. Keep unknowns explicit with
`Unknown` or `Needs input`, and include a short `Open Questions` section when important gaps remain.

## Workflow

1. Gather source material.
   - Read user-named files first.
   - Preserve the source-of-truth order the user provides.
   - If existing `signal-context.md` exists, update it instead of starting over unless the user asks
     for a rebuild.
2. Extract context.
   - Product context: what it is, who it helps, outcomes, proof, pricing or delivery model if
     supplied.
   - Sector context: market, submarkets, geography, regulation, seasonality, and communities.
   - ICP: account types, roles, buying committee, users, qualification rules, and disqualification
     rules.
   - Competitors and alternatives: named competitors, incumbent workflows, internal substitutes,
     agencies, consultants, spreadsheets, manual process, or "do nothing" if supplied.
   - Pain points and triggers: urgent problems, trigger events, objections, adoption barriers, and
     timing signals.
   - Signal criteria: CRITICAL, HIGH, MEDIUM, and LOW definitions that map to the provided context.
   - Search seeds: keywords, phrases, queries, communities, hashtags, job titles, company types,
     events, and competitor terms.
   - Engagement constraints: approved positioning, banned claims, tone, channels, compliance notes,
     and approval requirements.
3. Normalize the output.
   - Convert vague inputs into concrete bullets without adding unsupported facts.
   - Keep labels stable so `prospecting-signal-detector` can scan the file quickly.
   - Separate facts from assumptions.
   - Mark inferred items as `Inference:` only when the inference is directly supported.
4. Validate before handoff.
   - Confirm every signal class has at least one criterion or is marked `Needs input`.
   - Confirm ICP includes both fit and disqualification guidance or marks missing parts.
   - Confirm search seeds are tied to context, not generic filler.
   - Confirm engagement constraints include "do not post without explicit user approval".
5. Handoff.
   - Tell the user where `signal-context.md` was written.
   - Suggest using `prospecting-signal-detector` with that file for scanning, reporting, or engagement.

## Quality Rules

- Do not invent competitors, ICPs, sectors, signal criteria, proof points, or claims.
- Prefer exact phrases from source material for search seeds.
- Keep the file concise enough to load before every scan.
- Redact sensitive values in chat summaries, but preserve non-secret context in the file.
- If source files conflict, ask which source wins before overwriting important context.
