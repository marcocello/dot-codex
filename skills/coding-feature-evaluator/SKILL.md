---
name: coding-feature-evaluator
description: "Judge one implemented feature and its proof for intent, behavior, architecture, and false-green gaps."
---

# Feature Evaluator

Purpose: provide the fresh read-only semantic judgment required after realistic proof passes for every tracked or autonomous feature. The evaluator does not edit artifacts or queue state, but completion requires its fresh `PASS`.

Lightweight fixes do not invoke this skill.

## Inputs
Use bounded current evidence:

- original user goal and material corrections;
- current `FEATURE.md`, `PROOF.md`, and `proof/run.sh`;
- latest passing attempt and relevant evaluator-driven failing attempt when one exists;
- the parent-supplied transient active-feature surface: files changed for this feature plus directly relevant call paths;
- only relevant current app, architecture, conventions, and testing context.

Treat the transient active-feature surface as the review entry point. Do not derive feature scope from the accumulated dirty diff or load unrelated repository history and generated output by default. Follow a call path outside that surface only when needed to judge the accepted behavior or architecture.

## Review
Perform one evidence-first, implementation-second review in this order. The same evaluator owns both passes and returns one final verdict. Keep the first pass's claim map in working context only: no intermediate report, second agent, or additional lifecycle stage.

### Pass 1 — Evidence
Before opening implementation files:

1. Compare the accepted feature contract with the supplied user goal and corrections.
2. Inspect the latest `result.json` and actual retained output rather than trusting the status label or a summary.
3. For each claimed behavior, record what the executable attempt directly demonstrates, what it only approximates, and which declared gaps affect the claim.
4. Identify a central broken or incomplete behavior that the current proof could still permit.
5. Verify proof changes strengthened evidence rather than narrowing accepted behavior.

Do not use parent implementation summaries as evidence. The parent may supply paths that define the transient surface, but implementation explanations cannot replace retained runtime output.

### Pass 2 — Implementation
After the evidence claim map exists:

1. Open the transient active-feature surface and trace the real activation, decision boundary, persistence or external effect, and consumer read-back.
2. Challenge the evidence-pass claim map against the implementation and directly relevant call paths.
3. Check whether implementation bypasses policy, architecture, validation, or ownership to satisfy the proof.
4. Check whether a fake, fixture, source assertion, route inventory, or inner helper replaces behavior being claimed.
5. Follow a relevant path outside the supplied surface when required to judge the accepted behavior or architecture.

Complete the bounded review after identifying a blocker. Do not stop at the first material finding; consolidate all material findings supported by both passes in one final verdict.

## Rules
- Read-only: do not edit implementation, contracts, proof, fixtures, setup, retained attempts, or queue state.
- The two passes are ordered reasoning inside the same evaluator. Create no intermediate report and invoke no second evaluator or completion stage between them.
- Do not replace executable proof with confidence, source shape, lint, build output, or assistant claims.
- Do not add behavior outside the accepted contract or promote preferences into blockers.
- Findings must identify a contract mismatch, implementation defect, architecture bypass, or central false-green path.
- Exclude preferences, style opinions, speculative improvements, and behavior outside the accepted contract from material findings.
- After `FINDINGS`, the parent must strengthen proof when practical, repair, rerun proof, and request a fresh evaluation. The prior verdict cannot authorize completion.
- `PASS` applies only to the candidate it inspected. A relevant edit after inspection makes the verdict void; the parent must rerun the complete proof and another fresh evaluator before completion.
- Return `NEED_INPUT` only for an exact user-owned decision or external dependency that prevents an honest judgment.

## Output
```text
Review: PASS|FINDINGS|NEED_INPUT
Intent: <alignment>
Behavior: <judgment>
Architecture: <judgment>
Proof realism: <judgment>
False-green risk: <judgment>
Known gaps: <acceptable|blocking + reason>
Findings: <none|ordered list of all material findings with concise evidence>
Next: <none|smallest proof/repair direction covering the findings|one exact input>
```

`PASS` means the supplied current implementation and proof have no identified blocking mismatch or central false-green path. It authorizes the accountable parent to complete the queue item; the evaluator never mutates it directly.

`FINDINGS` requires proof-backed repair and fresh evaluation. `NEED_INPUT` blocks only on the exact missing input.

## Handoff
Lead with the strongest finding and cite concise repository evidence. Do not include prompts, token usage, exhaustive logs, or queue instructions.
