---
name: answer-job-application
description: Draft or revise job-application answers from company and role context, grounded in a supplied professional-profile dossier. Use for application forms and recruiter questions; not for job discovery, submission, or invented candidate facts.
---

# Answer Job Application

Produce copy-ready answers in the candidate's own credible voice. Optimize for relevance and truth rather than trying to cover an entire career.

## Inputs

Accept any combination of:

- company description or notes;
- role description or job URL;
- application questions;
- character or word limits;
- the candidate's rough draft or additional facts;
- a path to the candidate's `professional-profile` dossier.

The user may paste everything as one unstructured block. Separate the company context, requirements, questions, and constraints without asking them to reformat understandable material.

If the user supplies a job URL without the relevant text, read the listing using the available web or browser capability. Do not research the company more broadly unless the user asks or one current fact is necessary to answer accurately.

## Profile context

Locate `professional-profile` in the current workspace or use the path supplied by the user. If it is absent, ask for its location; do not search unrelated personal directories.

Read `README.md` and `PROFILE.md` completely. Read these when present and relevant:

- `CAREER_HATS.md` to select a coherent positioning;
- `JOB_SEARCH_CRITERIA.md` to respect role and practical constraints;
- `REPOSITORY_EVIDENCE.md` for technical depth, architecture, products, or recent project examples;
- `SOURCES.csv` when a precise date, title, metric, conflict, or source status matters.

Treat evidence labels, conflicts, and missing facts as binding. Never turn repository activity into unsupported claims about sole ownership, customers, commercial adoption, production scale, or business results.

## Choose the story before writing

Infer the company's immediate problem and the three to five requirements that matter most. Select one primary positioning and, only when useful, one supporting positioning from the dossier.

Read the material through two lenses:

- Recruiter: Is the answer immediately relevant, understandable, consistent with the requested seniority, and free of unexplained risk?
- Hiring manager: Does it show that the candidate handled a comparable problem, made consequential decisions, and produced an observable result?

Identify one evidence-backed differentiator that could make the candidate memorable. Notice screening concerns such as overlapping roles, founder-to-employee transitions, apparent overqualification, executive-to-individual-contributor moves, or missing domain experience. Address a concern briefly only when the question or role makes it relevant.

For each answer, choose the smallest relevant evidence set. Usually one concrete example and one result or lesson are enough. Prefer recent directly relevant work, then verified responsibilities and outcomes. Use older evidence only when it explains a real advantage for this role.

## Results and KPIs

Use a KPI only when its value and meaning come from the dossier or a fact supplied in the current conversation.

- Never create a plausible percentage, revenue figure, user count, time saving, SLA, adoption number, budget, or team size.
- Never convert repository commit counts into employer-facing impact.
- Do not present an industry benchmark as the candidate's result.
- Do not combine unrelated facts to imply causation.
- Preserve the original unit, baseline, timeframe, and scope when known.
- When a strong answer needs a missing KPI, draft with the strongest supported scope or outcome and add one concise `Check before submitting` question.
- Use no more metrics than the answer needs.

## Truth and missing information

- Never invent motivation, dates, team size, revenue, customer names, production scale, compensation, availability, work authorization, relocation preference, language ability, or personal history.
- Use the dossier's canonical fact when sources conflict. If an unresolved conflict is material, ask one focused question or omit the detail.
- Treat compensation, visa or work authorization, notice period, availability, relocation, and other user-owned facts as `NEED_INPUT` when unsupported.
- For a minor gap, write conservatively without false specificity.
- Do not mention source IDs, the dossier, or commit counts in employer-facing copy.
- Do not add citations unless requested.

## Writing voice

Follow voice guidance or writing samples supplied by the user or dossier. Otherwise use plain, natural language with first person, concrete verbs, short paragraphs, and proportional enthusiasm. Preserve useful phrasing from a rough draft while removing awkwardness and repetition.

Avoid canned application language, inflated adjectives, generic company praise, and conclusions that merely repeat the opening. Do not force every answer into the same template or list shape.

## Answer shapes

- Short factual field: answer directly in one to three sentences.
- Motivation or fit: connect one company or role need to one or two relevant experiences.
- Experience question: lead with the closest example, responsibility, action, and result.
- Behavioral question: use a natural situation-action-result arc without labeling it `STAR`.
- Technical question: explain the decision, important boundary or tradeoff, and observed outcome.
- Weak-fit question: answer honestly and use adjacent evidence instead of pretending direct experience.

Respect stated limits strictly. With no limit, use the shortest complete answer.

## Final pass

Check that every factual claim is supported, the positioning is coherent, the first sentence answers the question, the candidate's responsibility and outcome are clear, and no invented or stale fact remains. Return answers in question order without a strategy preamble. Add a brief `Check before submitting` note only when a material factual check remains.
