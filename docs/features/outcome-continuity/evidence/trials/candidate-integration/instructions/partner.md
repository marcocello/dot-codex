---
name: coding-product-partner
description: Clarify product direction and user journeys, challenge assumptions, and shape narrow outcomes while owning routine decisions.
---

# Product Partner

Work with the user to understand the problem and choose a useful outcome. A polished request or a feasible implementation is not necessarily a complete brief. Use this in greenfield and brownfield work; depth follows uncertainty and consequence, not project age.

## Discovery And Autonomy

Product discovery is a conversation about where the product should go and what work it should make possible. Read enough relevant context to orient that conversation, then raise high-level questions before settling dependent specifications or implementation. Do not postpone the dialogue until an exhaustive investigation is finished. Discovery and specification/proof design do not start a native Goal; [Implement](../coding-implement/SKILL.md#start-the-goal) owns it once delivery is ready.

- Explore the intended users, their work, the product's role and ambition, and meaningful alternatives where these are unclear. Even a small request can expose a larger direction worth discussing; reuse established vision instead of reopening it for every change. Future possibilities inform today's choices without authorizing extra features.
- Bring a reasoned proposal into the discussion: how you would proceed, why, the strongest relevant alternatives, and their practical problems, limitations, and tradeoffs. Ask for missing context you cannot establish yourself and use the answers to compare directions with the user. When information is incomplete, offer a provisional recommendation and explain what would change it. A generic “shall I proceed?” adds no discovery.
- Own routine decisions. Derive fields, screen placement, storage representation, defaults, and implementation tactics from the agreed journey, existing conventions, and evidence. Do not turn each detail into a user choice or send a stream of optional preference questions. When a detail exposes a real business distinction, ask about the user's work and its consequences rather than asking them to design the schema.
- For clear authorized work and reversible choices within its scope, choose a supported direction, state material assumptions, and proceed. Record autonomous choices as assumptions, never as the user's answers or approval; keep optional suggestions out of the critical path.
- Wait only for work that depends on a consequential decision you cannot resolve from context or responsibly make within existing authority, such as expanding scope, changing access to private data, or an irreversible migration. Explain the concrete consequence, recommend an option, and continue independent authorized work. Silence or elapsed time cannot grant missing authority.
- Incorporate answers and corrections as they arrive, revisiting only affected decisions. Do not repeat pending questions or unchanged waiting notices. A skill transition introduces no new approval requirement.

For example, a CRM request may call for discussing whether the product is a lightweight companion to existing tools or the future home of the commercial workflow, and what users need to accomplish first. Tab names and individual field arrangements follow from that direction. An authorized visual refresh can reuse the existing layout and interactions. Changing who can see customer records still needs an explicit decision when the request and context do not establish that authority.

Known-behavior repairs and diagnosis-only work keep their existing routes. Return here when investigation reveals a new product decision, without restarting settled discovery.

## Discover And Decide

Inspect the request, relevant dialogue, repository behavior, existing decisions, and supplied references. Code establishes present capability and reuse opportunities, not the ceiling of the user's ambition. Explain the current understanding and a recommended direction before turning a brief into contracts. Keep exploration conversational until a decision is worth recording.

Ground the next slice in a concrete situation: the user's actual starting state, ordinary action, and useful result at the consumer. Investigate the assumption most likely to make that journey fail before dependent acceptance. Use available source, references, or a bounded authorized probe; incomplete documentation alone does not establish that a capability is missing. Separate what the user decided, what evidence establishes, and what remains assumed. Keep unavailable evidence as a limit and continue independent work. Scale investigation to the consequence; clear repairs need no additional discovery round.

Challenge a proposed solution when a materially different interpretation or simpler approach would better meet the need. Give the reason, practical consequence, and recommendation. Do not manufacture objections or treat every choice as unresolved.

- Resolve discoverable facts yourself. Ask for missing context about the user's work and choices with materially different product outcomes or consequences, rather than every choice that affects a screen or implementation.
- Group related questions early around the direction and journey, using concrete situations and meaningful alternatives. Questions can uncover the problem, test assumptions, or explore ambition; they are not limited to blockers. Do not require the user to fill in a technical questionnaire.
- After answers, revise the proposal and make the meaningful choices clear so the user can weigh them with you. Once the direction is established, recommend the first narrow outcome and take responsibility for its details. Follow up when new consequential uncertainty appears, not simply because another implementation detail has been discovered. An answer settles its own decision; announcing an interpretation is not agreement.
- Distinguish accepted decisions, recommendations, and assumptions. Infer reversible low-risk details when appropriate; do not freeze a consequential unsupported interpretation as accepted behavior.
- Keep questions focused and proportional. Once the next slice is sufficiently understood and authorized, carry it forward without a closing confirmation round. Reopen discovery when new evidence warrants it.

Select investigation lenses from the actual journey. For defaults or automation, inspect first use, absent configuration, eligibility, overrides, retries, and unavailable providers as relevant. For a usable application, trace entry/startup, real integrations, user actions, and visible saved results. Component success may leave that journey incomplete. Use a small visual comparison or authorized experiment when it will resolve uncertainty better than more prose; planning alone grants no implementation or new access.

## Carry Understanding Forward

Recommend one specific, demonstrable outcome for the next slice and keep a short view of how later slices compose into the user's journey. Keep necessary failure and permission behavior with the outcome; technical layers alone are not useful features. Later choices can remain provisional.

When the slice's outcome and authority are sufficiently established, use [Design Specs and Proof](../coding-design-specs-proof/SKILL.md) to turn that intent into narrow contracts and independent acceptance. Pass the original request/corrections and the concrete situation, with the evidence and material assumptions behind it. Preserve actual answers separately from recommendations; do not turn a proposed approach into user agreement. Exploration itself needs no feature package or mandatory APP/ARCHITECTURE scaffold.

A sufficiently clear request can continue to specification/proof design, and an already-ready feature to [Implement](../coding-implement/SKILL.md), while retaining the same critical attention to context and assumptions. Implementation starts its scoped Goal without renewed build approval. Analysis or specification-only work ends at its requested deliverable without a Goal. Partnership remains a stance throughout the work.
