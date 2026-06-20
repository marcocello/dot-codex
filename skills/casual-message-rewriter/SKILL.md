---
name: casual-message-rewriter
description: Rewrite text into casual, natural, human-sounding messages for chat, DMs, email snippets, social replies, or spoken-style notes. Use when the user asks to make wording less formal, less polished, more casual, more natural, less verbose, less punctuated, less capitalized, more like phone typing, more like a real person, or similar, regardless of topic.
---

# Casual Message Rewriter

## Goal

Turn structured or polished text into something that feels like a real person wrote it quickly. Preserve the core meaning, but reduce stiffness, over-explanation, formal punctuation, and unnecessary capitalization.

## Workflow

1. Identify the original intent, audience, and desired level of casualness from the user request.
2. Keep the same core point and any important constraints.
3. Compress large concepts into the shortest natural version that still makes sense.
4. Rewrite in plain, conversational language.
5. Prefer one usable version unless the user asks for options.
6. Do not explain the rewrite unless the user asks.

## Style Rules

- Use simple words and short phrases.
- Keep grammar understandable, but allow lighter punctuation, missing punctuation, and sentence fragments.
- Make it sound written by a person in a message thread, not a brochure or formal email.
- Remove corporate phrasing, abstract labels, and over-structured bullets unless needed.
- Avoid perfect symmetry, heavy transitions, and polished essay rhythm.
- Use lowercase by default for phone-style and very casual writing.
- Drop capital letters at sentence starts when the user wants a quick-texting feel.
- Remove punctuation when it makes the message feel more natural, especially commas, periods, and semicolons.
- Keep only punctuation that improves clarity or tone, such as a question mark when the message is a question.
- If the source is long, summarize the point instead of carrying every detail into the rewrite.
- Keep typos out unless the user explicitly asks for imperfect spelling.
- Do not add new claims, facts, promises, or emotional intensity that were not implied.

## Casualness Levels

If the user does not specify a level, use **casual but clear**.

- **Casual but clear**: natural, readable, suitable for LinkedIn, email, or a DM.
- **Phone-style**: lowercase, compact, little or no punctuation, sounds typed quickly.
- **Very casual**: shorter, chat-like, sometimes no punctuation, with small imperfections in rhythm.

## Examples

Formal input:

> I am looking for companies where sales are highly conversation-driven and where customer context often fails to reach the CRM.

Casual but clear:

> i’m looking for companies where sales happens through a lot of real conversations and the important context often never really makes it into the crm

Phone-style:

> basically i’m looking for companies where sales is very conversation driven and a lot of the important stuff stays in calls notes whatsapp or people’s heads instead of making it into the crm

Compressed phone-style:

> basically teams where sales happens in conversations and the important stuff gets stuck in notes whatsapp or people’s heads instead of the crm

Formal input:

> Could you provide your perspective on which customer segment would experience this problem most strongly?

Casual but clear:

> curious from your experience where do you think this problem shows up the most
