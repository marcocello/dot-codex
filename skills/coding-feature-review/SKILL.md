---
name: coding-feature-review
description: "Provide fresh read-only contract preflight or final feature judgment without owning implementation, proof execution, repair, or completion state."
---

# Feature Review

Review one material feature in the explicit mode requested by `coding-feature-execute`. Reject an invocation that does not specify `preflight` or `final`; do not infer or blend modes.

## Preflight Mode

Use `mode: preflight` only for sensitive work, in a fresh separate context before red evidence or implementation.

Inputs are verbatim user goal and corrections, decision-complete `FEATURE.md`, `PROOF.md`, `proof/run.sh`, named consumption target, and relevant current repository paths as discovery entry points. There is no candidate implementation. Do not execute proof, tests, builds, providers, or other mutating commands, and do not issue a completion authority verdict.

Independently challenge intent, authority and state transitions, affected consumers and relevant states, a central false-green implementation, and feature cohesion with its independently runnable proof boundary.

Return all supported material findings from one relevance-bounded pass:

```text
Review: CLEAR|FINDINGS|NEED_INPUT
Intent: <alignment or ambiguity>
Authority and state: <ownership and transitions>
Consumers: <affected paths and proof coverage>
False-green risk: <central broken path>
Scope: <cohesive|split finding>
Findings: <none|ordered supported findings>
Next: <none|parent repair direction|one exact input>
```

`CLEAR` permits the parent to continue but grants no implementation or completion authority. `FINDINGS` return to contract/proof repair without another preflight gate. `NEED_INPUT` blocks before red evidence and implementation on one exact user-owned decision.

## Final Mode

Use `mode: final` in a fresh separate context only after target-valid realistic proof passes.

Inputs are verbatim user goal and corrections, current contracts and runner, latest passing `result.json` and retained output, named runtime target, and the parent's transient active-feature surface as a discovery entry point rather than a scope ceiling.

Perform one evidence-first, implementation-second review in the same invocation:

1. **Evidence-first:** map accepted claims to what retained output directly proves, approximates, or leaves as a gap. Check existing persisted state, consumer-visible read-back, fake boundaries, proof changes, and whether the exact named target ran.
2. **Implementation-second:** inspect the active-feature surface and independently follow relevant activation, authority, state, persistence, external effect, affected consumers, and call paths. Check for architecture, validation, or policy bypasses created merely to satisfy proof.

Return one consolidated verdict after completing the bounded review:

```text
Review: PASS|FINDINGS|NEED_INPUT
Intent: <alignment>
Behavior: <judgment>
Architecture: <judgment>
Proof realism: <judgment>
False-green risk: <judgment>
Known gaps: <acceptable|blocking + reason>
Findings: <none|ordered material findings with evidence>
Next: <none|smallest proof/repair direction|one exact input>
```

`PASS` must be target-valid and applies only to the implementation and proof inspected. `FINDINGS` require proof strengthening when practical, repair, a complete proof rerun, and another fresh final review. `NEED_INPUT` is limited to an exact user-owned decision or external dependency.

## Shared Boundaries

- Remain read-only: do not edit contracts, implementation, proof, fixtures, attempts, or queue state.
- Keep discovery relevance-bounded. Parent paths are entry points, not a scope ceiling; do not default to a repository-wide sweep or unrelated history.
- Exclude preferences, style opinions, speculative adjacency, and behavior outside the accepted contract from material findings.
- Complete the bounded pass after finding a blocker and return all supported material findings rather than stopping at the first.
- Every invocation is fresh and separate from the accountable parent. A relevant edit after final review makes that verdict stale.
- Do not replace executable evidence with confidence, source shape, lint, build output, or assistant summaries.

## Handoff

Lead with the strongest supported risk or `PASS`. Cite concise current evidence and omit prompts, token usage, exhaustive logs, and queue instructions.
