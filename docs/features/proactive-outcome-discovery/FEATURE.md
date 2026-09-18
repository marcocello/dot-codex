# Proactive outcome discovery

## Outcome

Strengthen the existing concise harness so it helps infer, challenge, and complete the user's practical outcome rather than translating literal wording into a patch. AGENTS keeps routing; Shape owns discovery; Ship and the shared proof contract challenge outcome completeness; README explains the north star. No new skill, shared guide, rigid questionnaire, approval gate, or global checklist.

## Accepted behavior

- Form a concrete working interpretation of the desired user outcome and propose a direction grounded in inspected context. Clarify genuinely ambiguous terms only when context cannot resolve them. Do not require formal tickets or renewed build authorization.
- Investigate likely unmentioned cases that could defeat the outcome in the actual affected journey. Distinguish current implementation facts from desired policy: an empty existing default is a fact to address, not a reason to declare successful auto-selection.
- For relevant defaulting/automation requests, examine fresh or missing configuration, invalid/unavailable candidates, capability/eligibility, timing, saved overrides, repeat actions, and existing records. Select relevant cases, not a universal questionnaire. Never silently invent a provider, price tier, permission change, or arbitrary fallback when consequential.
- Ask concrete decision questions about unresolved consequences with options/tradeoffs and an evidence-supported recommendation. Resolve code-discoverable facts independently. Surface adjacent choices as proposals, preserving scope, permissions, explicit analysis-only requests, and progress independent of pending answers.
- Carry discovered cases and accepted decisions into specification and independent proof. Before freezing, compare scenarios to the original user outcome; the proof author must expose missing decisions rather than silently narrow the claim. Proof should include the relevant ordinary state that defeats the obvious shallow implementation, e.g. no configured default, not only a pre-populated happy path.
- At delivery compare actual visible behavior and supported cases with the original outcome, not merely test totals. Report unresolved limitations; a missing requested result cannot be called complete solely because scoped tests pass. Preserve independent authorship and fixed acceptance; missing behavior discovered during Ship returns to the authorized acceptance decision process.

## Motivating evidence and limits

User-supplied historical interaction in native task 01a0af8c-7363-7390-8e1f-a0d60b3d0d0e: auto-select both models after Kit association was reported complete, then vision remained empty because fresh setup had no vision default. A later correction introduced fallback selection. The transcript supports a missed fresh-state outcome and excessive user prompting; implementation/proof source for that project is not inspected here, so no claim about exact old test internals or current deployed behavior. The old Goal authorization gate has already been removed; preserve that fix.

## Scope and verification

Edit only AGENTS.md, README.md, coding-shape/SKILL.md, coding-ship/SKILL.md, and shared coding/proof.md as needed, with minimal owner-specific additions. Preserve all previous feature records and scripts/inventory. Independent executable proof must check current candidate identity/navigation and independently assess a motivating model-default case and held-out cases (at least first-use notification setup, destructive/costly fallback, and clear bounded repair or analysis-only scope). Evaluate concrete proposed behavior/questions, avoiding exact phrase matching and claims of universal future compliance. Final separate read-only review and repository gate required. No target application changes, external actions, commits, or pushes.
