---
name: no-bullshit-technical-writing
description: >-
  Write and revise direct, useful website content that demonstrates technical
  competence without assuming specialist readers. Use when Codex needs to draft
  or edit technical blog posts, engineering essays, service pages, project
  writeups, founder notes, newsletter pieces, or website copy that should sound
  specific, clear, evidence-based, and human instead of generic AI prose.
---

# No-Bullshit Technical Writing

Purpose: produce publishable pieces that demonstrate competence through clarity, concrete evidence,
and usefulness rather than dense jargon or performative hype.

Read `references/anti-ai-rhetoric.md` before drafting or revising any substantive piece. Use it as
the style checklist, especially when the requested output is for a public website.

## Workflow

1. Identify the content job:
   - Surface: blog post, website page, case study, product note, newsletter, LinkedIn post, or
     technical explanation.
   - Reader: non-specialist buyer, founder, operator, technical manager, engineer, peer reviewer, or
     general website visitor.
   - Point: the claim the piece must prove or the useful thing the reader should understand, decide,
     or do after reading.
2. Gather concrete material:
   - Use user-provided facts, repo context, source documents, code, metrics, names, dates, incidents,
     constraints, and tradeoffs.
   - Never invent personal anecdotes, customers, benchmarks, studies, production incidents, or
     numbers.
   - If a needed fact is missing, either ask for it when it changes the piece materially or label the
     gap as an assumption.
3. Build the outline around the argument:
   - Open with the specific claim, observation, example, or technical problem.
   - Explain why it matters in operational, business, product, user, or technical terms.
   - Develop the reasoning with plain language, mechanisms, tradeoffs, concrete examples, and
     evidence.
   - Translate technical detail into reader consequence: cost, risk, speed, quality, maintainability,
     confidence, or decision criteria.
   - Close with a concrete implication, decision, or next step.
4. Draft in the target language requested by the user. Apply the same anti-rhetoric rules in English,
   Italian, or any other target language by removing equivalent filler and hype.
5. Revise hard:
   - If the first paragraph can be deleted without losing essential meaning, delete it.
   - Replace vague claims with named systems, measured behavior, dated events, or explicit caveats.
   - Cut decorative bold, generic headings, forced lists, fake punchlines, and throat-clearing.
   - Scan for banned patterns from the reference, including "Not X, but Y" structures and weak
     intensifiers.

## Voice

- Sound like a competent practitioner explaining what they know, what they tested, and what remains
  uncertain.
- Prefer precise technical nouns over inflated adjectives.
- Use jargon only when it is the exact term a serious reader would expect, and explain it in plain
  language when a non-specialist may need the bridge.
- Use short sentences for force. Use long sentences to connect causation, context, and consequences.
- Avoid motivational tone, generic business language, clickbait, and theatrical framing.
- No em dashes, emojis, hashtags, or multiple punctuation.

## Substance Without Over-Technicality

Show expertise through decisions, tradeoffs, examples, and implications. Include enough detail to
make the piece defensible, but keep each detail useful to the reader:

- What problem the reader has and what changes after they understand the point.
- Interfaces, data flows, failure modes, constraints, dependencies, and operational costs when those
  details affect a real decision.
- Alternatives considered and why they were rejected.
- What changed after a decision, migration, incident, launch, or measurement.
- Known unknowns and limits of the evidence.

Do not make the piece longer to look smarter. Add length only when it improves the reader's ability
to make a decision, understand a risk, or use the idea.

## Output

- For drafting: return a ready-to-publish piece with a title only when useful.
- For revision: return the revised text first, then a short note listing the most important edits.
- For strategy help: return a tight outline, key claims, reader payoff, missing evidence, and
  suggested angle.
- Keep Markdown minimal. Use lists for comparisons, steps, or distinct checks; use prose for
  continuous argument.
