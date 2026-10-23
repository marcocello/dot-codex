---
name: writing-ste
description: Draft or revise requested documentation, emails, specifications, reports, instructions, and other written deliverables with ASD-STE100-inspired clarity. Preserve meaning and the requested language and voice. Not for ordinary replies, questions, progress updates, or handoffs.
---

# Clear writing with STE

Use this guidance when the task asks for a written deliverable, including work outside coding. The deliverable can be a file, a document in an app, or a draft supplied directly in chat. Apply it when creating or revising that text; the user does not need to name STE. Do not load or apply this skill solely for ordinary conversation, questions, progress updates, or handoffs.

This is an adaptation of ASD-STE100 for general communication. It does not verify the official dictionary or establish formal compliance. Task instructions still own the deliverable, authority, evidence, and completion criteria.

## Preserve meaning

- Preserve the actor, action, condition, scope, quantity, timing, negation, permission, and evidence boundary. Keep a longer sentence if shortening it would change the meaning.
- Use one stable term for each concept. Keep established technical terms. Explain an unfamiliar term when the reader needs the explanation.
- Preserve requirement strength. Use `must` for obligations, `should` for recommendations, and `can` for capability. Use `will` for a plan or established future behavior. Distinguish permission from uncertainty when using `may`. Do not turn a possibility into a fact, or a plan into a verified result.
- Keep observations, assumptions, recommendations, and open decisions distinct. State an unknown instead of inventing an actor, cause, value, or decision.
- Preserve code, commands, identifiers, paths, schema keys, official names, exact errors, and source quotations. Edit the surrounding prose unless the user requests changes to those items.

## Write clearly

Lead with the answer, result, or decision needed. Add the explanation that the reader needs to understand or act. Keep useful rationale and evidence.

Prefer active voice and an explicit actor: “The API rejects the request.” Use an imperative for the reader's action: “Run the migration.” Put a condition before the action that depends on it: “If the migration fails, stop the release.” If the actor is unknown, preserve that uncertainty.

Give each sentence one main idea and each paragraph one topic. Separate instructions when their order matters. Keep the words that express conditions and relationships. Do not omit articles or subjects to save space.

Use familiar words, direct verbs, and consistent names. Remove filler, ornamental synonyms, idioms, and unsupported claims of quality. Break long noun chains into phrases. Prefer separate sentences to semicolons. Prefer simple tenses when they preserve the timing and meaning.

For technical instructions, aim for 20 words or fewer per sentence. For explanations, aim for 25 words or fewer. Treat these as editing guides, not hard limits. Do not sacrifice necessary precision.

Use lists for sequences or parallel items and tables for comparisons. Follow the requested document structure.

## Adapt to the task

- **Emails and messages:** State the purpose and any requested action clearly. Match the recipient and the user's requested tone. A casual draft can remain casual.
- **Documentation and specifications:** State who acts, under which condition, and with which observable result. Split independent obligations. A clearer sentence must not create new acceptance criteria or product decisions.
- **Procedures and instructions:** State prerequisites and conditions before dependent actions. Keep action order, limits, exceptions, and warnings intact. Prefer one instruction per sentence.
- **Reports and reviews:** State what was observed, where it was observed, and what remains unverified. Separate a failure from a suspected cause. A wording change cannot extend the evidence boundary.
- **Rewrite requests:** Return the revised text in the requested format. Explain edits or provide a comparison when requested. Flag material ambiguity that cannot be resolved from the supplied context.

Respect the user's requested language, tone, audience, and document conventions. For other languages, apply the clarity principles without imposing English grammar. For creative, personal, persuasive, or marketing text, preserve the requested voice and nuance.

For acceptance and proof examples in coding tasks, read [Coding writing](../../docs/harness/coding/writing.md). Reuse it if already read in this task.

## Check before sending

Read for unclear actors, inconsistent terms, missing conditions, vague results, and unsupported certainty. Check modal verbs, negation, quantities, timing, and permissions against the intended meaning. A readable sentence can still be wrong.

Do not add a mandatory checker or treat a style score as proof of correctness or completion. If the user requests formal ASD-STE100 compliance, use the official standard and dictionary with suitable review. State any verification limits.

## Sources and scope

This local skill adapts the repository's existing writing guidance for requested written deliverables. The reviewed [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill/tree/cd62d297d5ef7cf9f59718cadc233ab2876ea013) informed the distinction between drafting and a dedicated rewrite workflow. This skill does not vendor its text, examples, or linter.

Use [ASD's official site](https://www.asd-ste100.org/) and [standard request route](https://www.asd-ste100.org/STE_downloads.html) for the authoritative standard. This skill does not reproduce ASD's dictionary or claim certified compliance.
