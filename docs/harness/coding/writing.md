# Clear coding writing

Apply this STE-inspired adaptation to coding specifications, acceptance tests, proof plans and reports, reviews, explanations, questions, progress updates, and handoffs. Read it once when a coding skill loads and reuse it during the task. It changes how the agent expresses meaning; existing skills and contracts still own behavior, authority, evidence, and completion.

This is a coding adaptation, not a claim of ASD-STE100 compliance. Use the user's requested language, style, and document conventions. For languages other than English, retain the clarity principles without imposing the English dictionary or grammar.

## Preserve meaning first

- Preserve the actor, action, condition, scope, quantity, timing, negation, permission, and evidence boundary. A shorter sentence that changes one of these is a worse sentence.
- Use one term for one concept. Keep established domain terms, including technical nouns and verbs such as `streaming`, `cache`, and `deploy`. Define unfamiliar terms when readers need them; do not add a mandatory glossary.
- Preserve requirement strength. Use `must` for accepted obligations, `should` for recommendations, and `may` for permission or an explicitly uncertain possibility. State which meaning applies when it is ambiguous. Use `can` for capability and `will` for a plan or established future behavior. Do not turn advice or uncertainty into a requirement or guarantee.
- Keep facts, observations, assumptions, recommendations, and open decisions distinct. Name an unknown instead of inventing a value, actor, cause, or product decision to make the sentence sound precise.
- Preserve code blocks, identifiers, commands, file paths, schema keys, official names, quoted source text, and exact errors. Improve the surrounding prose. Rewrite product copy only when that work is in scope and consistent with its audience and voice.

## Make prose easy to follow

Prefer active sentences with an explicit actor: “The API rejects the request.” Use the imperative for a reader's action: “Run the migration.” State the condition before a dependent action: “If the migration fails, stop the release.” If the actor is unknown, say so; passive voice is acceptable when it preserves that uncertainty.

Put one main idea in each sentence and one topic in each paragraph. Separate sequential instructions when their order matters. Keep conjunctions and qualifiers that express a real relationship; do not remove them to satisfy a length target.

Aim for instructions of about 20 words or fewer and explanations of about 25 words or fewer when practical. These are editing guides, not pass criteria. Keep necessary technical detail. Use a list for a sequence and a table for a comparison. Do not force every conversation into a template or count its words.

Use familiar words and stable names. Remove ornamental synonyms, idioms, filler, and long noun chains. Prefer a short sentence to a semicolon. Use full forms in formal artifacts when they improve clarity; ordinary conversation can remain natural.

## Specifications and acceptance criteria

Describe observable behavior with its starting condition, actor, action, and result. Split independent obligations so that each can be checked. Include necessary failure and permission behavior from the accepted scope. Give exact limits only when they are decided or justified.

Avoid promises such as “works correctly,” “handles errors gracefully,” or “is fast.” Replace them with the observable accepted result. If the result is undecided, record the open decision and ask through Product Partner before dependent work. A prose rewrite cannot supply missing acceptance.

Example with an established export contract:

> When the user selects orders and chooses Export, the app downloads a CSV file containing only those orders.

> If the export fails, the app shows an error message. The selected orders remain selected so that the user can retry.

The second criterion applies only if the error and retry behavior is accepted. Do not infer it from “handle errors gracefully.” Keep stable criterion IDs and the existing feature/coverage structure; style changes do not authorize acceptance changes.

## Proof plans and reports

For a proof plan, identify the starting state, public action, independent observation, and pass condition. Name the runtime, consumer, and real or fake external edges when they determine the claim. Refer to criterion IDs instead of repeating the whole specification. [The proof contract](proof.md) owns the required boundaries and capture procedure.

The examples are illustrative, not defaults for other tasks. Do not import their actors, controls, output formats, or actions into another contract. Label unconfirmed activation or observation details as assumptions and resolve them before relying on the plan.

Example plan for the export criterion:

> Select orders A and B in the browser. Choose Export and read the downloaded CSV file. Pass if the file contains A and B and excludes unselected order C.

For a report, use past tense for observations. State what ran, what it established, and what remains unverified. Separate an observed failure from a suspected cause. A passing local check cannot become a live-target success through a wording change.

Example report:

> The browser downloaded a CSV file containing A and B. The file excluded C. This run verified the selected-order export on the local app.

> The API used a fake payment provider. The run did not verify delivery to the real provider.

Preserve literal errors when reporting failures:

> The request returned `503`. The log contained `upstream timed out`. The cause is not confirmed.

## Questions, updates, and handoffs

Lead with the result, finding, or decision needed. Explain the consequence in concrete terms. Ask a direct question with a recommendation when a consequential choice is unresolved. Keep established authorization and pending questions intact; clearer language does not create permission.

Example question:

> Should the export include archived orders? I recommend excluding them because the current view contains active orders only.

Example update:

> The local check passed. Production verification is pending because this task has no access to the deployed worker.

At handoff, state what changed, the observed result and boundary, material gaps, and any remaining action and owner. Scale the detail to the task and existing reporting conventions. Avoid process narration or invented warnings merely to match a maintenance-manual style.

## Review before sending

Read the text for ambiguous actors, overloaded terms, missing conditions, vague results, and unsupported completion claims. Check that any simplification preserves the original meaning, especially modal verbs, negation, quantities, permissions, and uncertainty. Keep useful explanation and rationale; brevity alone is not quality.

Do not add a mandatory language checker or make style lint a condition of feature completion. Automated checks can suggest edits but cannot establish meaning, factual accuracy, acceptance, or formal STE compliance. When the user explicitly requires full STE, use the official standard and suitable review; report limits of any available checker.

## Sources and provenance

The inspected [0xpili skill](https://github.com/0xpili/simplified-technical-english/tree/1e148d670cba46685ad2b4c3f2354a637a7fdbbe) summarizes ASD-STE100 Issue 7 (2017). Its [notice](https://github.com/0xpili/simplified-technical-english/blob/1e148d670cba46685ad2b4c3f2354a637a7fdbbe/NOTICE.md) distinguishes the MIT-licensed skill text and scripts from ASD's dictionary and disclaims formal compliance.

[ASD's public overview](https://www.asd-ste100.org/about_STE.html) describes controlled vocabulary, writing rules, and permitted domain terminology. As checked on October 4, 2026, it lists Issue 9 (January 2025) as current. Use the [official download route](https://asd-ste100.org/STE_downloads.html) for the authoritative standard. This reference is original coding guidance informed by those sources; it does not reproduce the dictionary or vendor the upstream skill or checker.
