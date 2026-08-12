---
name: coding-feature-preflight
description: "Challenge one decision-complete tracked or autonomous feature and proof in fresh separate read-only context before implementation. Invoke from coding-feature-execute; do not use for lightweight work or final implementation evaluation."
---

# Feature Preflight

Purpose: expose correlated intent and proof assumptions before implementation without creating another completion verdict or repair loop.

## Inputs
Use bounded current evidence:

- original user goal and material corrections;
- current `FEATURE.md`, `PROOF.md`, and `proof/run.sh`;
- only relevant current app, architecture, conventions, testing, and existing behavior needed to identify authority or consumers.

Do not accept the authoring parent's rationale as evidence. Review no candidate implementation: implementation has not started. Do not load unrelated repository history or generated output.

## Review
Perform one bounded fresh read-only challenge:

1. Intent: identify the strongest materially different interpretation that could satisfy the wording but miss the requested outcome. Confirm the accepted contract rejects it when relevant.
2. Authority and state transitions: identify who decides, mutates, and observes each central state or effect, including precedence and failure/recovery transitions when relevant.
3. Affected consumers: identify the real paths that must remain compatible and whether the proof exercises the primary consumer or states an honest gap.
4. Central false-green: name a plausible broken or incomplete implementation that could pass the proposed proof.
5. Feature cohesion: identify independently valuable outcomes or independently runnable proof boundaries that should not share one feature package.

Return all supported material concerns from this pass, capped at no more than three findings. Do not add requirements outside the original goal, accepted corrections, or authoritative repository constraints.

## Boundaries
- Run for tracked and autonomous contract packages only. Lightweight work has no feature preflight.
- Do not edit contracts, proof, implementation, tests, retained attempts, or queue state.
- Do not execute proof, tests, builds, providers, or other mutating or completion commands.
- Do not issue an implementation verdict or inspect a candidate implementation.
- Do not create a durable receipt, score, counter, status field, or intermediate artifact.
- Run exactly once for the decision-complete package. The accountable parent resolves supported findings or rejects unsupported scope expansion with evidence; it does not invoke another preflight as an approval gate.
- `CLEAR` means no material contract/proof issue was identified in this bounded pass. It grants no implementation or completion authority.
- Return `NEED_INPUT` only for one exact unresolved user-owned decision that prevents an honest contract. It blocks red evidence and implementation until the accountable parent receives and incorporates that decision.

## Output
```text
Review: CLEAR|FINDINGS|NEED_INPUT
Intent: <alignment or ambiguity>
Authority and state: <ownership and transitions>
Consumers: <affected paths and coverage>
False-green risk: <central broken path>
Scope: <one coherent outcome and proof boundary|split finding>
Findings: <none|ordered list of no more than three material findings>
Next: <parent resolution direction|one exact input|none>
```

## Handoff
Lead with the strongest material contract or proof risk. Keep implementation suggestions, style preferences, lifecycle narration, and completion claims out.
