---
name: write-product-posts
description: "Write natural Italian and adapted English social posts about product work in a technical, founder-led, lightly ironic voice. Use for launches, features, fixes, validation, recognition, and building reflections."
---

# Write Product Posts

## Prepare

Read [references/style-examples.md](references/style-examples.md) completely before drafting. Treat its product facts as style examples only; never transfer them into the user's post.

Accept a topic as the only required input. Use any optional context the user provides:

- what was difficult or wrong before;
- what changed and for whom;
- evidence, measurements, sources, limitations, or tradeoffs;
- release status, product name, preferred point of view, and call to action.

Do not research unless asked. Do not invent metrics, sources, validation, user behavior, availability, release status, or a plausible explanation the user did not give. When a fact is missing, omit it and build the post from what is known. With sparse input, state the supplied point directly once instead of padding it through negation, paraphrase, or metaphor. Ask one focused question only when the topic is too ambiguous to describe truthfully.

When the input supplies only one change and one motive, treat it as a sparse micro-post: write one cohesive factual paragraph in each language and skip the story template, analogy, playful expression, and ornamental closing.

## Find the Story

Identify the most concrete narrative available:

1. Name the previous friction without inflating it.
2. Explain the change in observable product terms.
3. Show the consequence for the user.
4. Add evidence or an honest limitation when supplied.
5. End with one human observation, dry aside, or direct invitation only when it adds something.

Prefer `problem → change → consequence → proof → human close`. Compress or reorder it when the topic is small. Do not force every component into every post.

Use first-person singular for a solo builder and first-person plural for a team. Preserve the point of view implied by the input; if none is available, avoid claims about team structure.

## Shape the Prose

Write connected prose that sounds spoken rather than a sequence of captions:

- let related sentences share a paragraph and use transitions, clauses, and references to connect them;
- start a new paragraph only when the idea, time, or emphasis genuinely changes;
- vary sentence length, including occasional longer sentences that carry context or causation;
- use a one-sentence paragraph only when it earns real emphasis, never as the default rhythm;
- do not turn every sentence into a miniature slogan or arrange the whole post as `statement. newline. statement. newline. punchline.`;
- avoid rhetorical scaffolding that exists only to make the writing sound important, such as an invented false contrast, a meta-announcement, or a summary restated as a punchline;
- never use a `not just X` contrast unless the user actually supplied X;
- delete a sentence that only repeats the previous point through a metaphor or a more abstract noun;
- do not force a tidy moral, mirrored contrast, metaphor, or aphorism at the end.

Use the fewest paragraph breaks the thought needs, normally one to three. Default a micro-post to one cohesive paragraph unless the subject genuinely turns. A plain ending is valid; do not add a sentence merely to make the post feel finished. Read the draft aloud: if the pauses feel more designed than spoken, join or rewrite the sentences.

## Write the Italian Post

Write as a native Italian product builder speaking to intelligent people:

- prefer specific nouns and verbs over marketing adjectives;
- mix technical precision with ordinary spoken Italian;
- explain specialist terms through their practical consequence;
- preserve the connective flow of ordinary Italian instead of copying social-media fragments;
- allow one playful expression or everyday analogy when it feels earned;
- keep imperfections human without introducing deliberate spelling errors;
- use numbers, named sources, and limitations exactly when provided;
- default to prose, no hashtags, no emoji chain, and no generic engagement bait;
- avoid “siamo entusiasti”, “rivoluzionario”, “game changer”, “soluzione innovativa”, and similar corporate filler.

Choose the length from the material:

- micro-post: 20–90 words;
- normal update: 100–180 words;
- launch or evidence-heavy explanation: 160–260 words.

Do not pad a small update to reach a longer range.

## Write the English Post

Write a second post from the same facts. Do not translate line by line.

- sound like a native English-speaking technical founder;
- preserve product claims, numbers, sources, qualifications, and call to action;
- replace Italian wordplay with a natural English dry aside or omit it;
- keep the same level of informality without importing Italian syntax;
- avoid startup clichés, excessive slang, and inflated claims;
- keep the English post independently publishable.

The two posts may differ in rhythm, analogy, and sentence order. They must not differ in factual meaning.

## Check

Before returning the answer, verify:

- every product claim comes from the input;
- no plausible detail was invented merely to create a stronger before-and-after contrast;
- every sentence adds a fact, consequence, qualification, or genuinely useful bit of voice instead of restating the previous sentence;
- the benefit is concrete enough to understand;
- the Italian reads as written in Italian, not translated into it;
- the English reads as an adaptation, not a literal translation;
- humor appears at most once per post and does not obscure the update;
- paragraphs group related thoughts instead of isolating each sentence;
- the ending sounds like something the builder would naturally say, not a manufactured quote card;
- for a sparse micro-post, the last sentence does not introduce a new metaphor, comparison, or contrast;
- no source-example fact leaked into the new topic;
- no hashtags, emojis, CTA, or invented metric was added without a reason.

## Return

Return only the two finished posts unless the user asks for commentary:

```markdown
## Italiano

<post>

## English

<post>
```
