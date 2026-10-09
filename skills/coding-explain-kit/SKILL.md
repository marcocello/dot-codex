---
name: coding-explain-kit
description: Explain how a software kit works through its business purpose, design rationale, prior analysis, evidence sources, decision cases and runtime behavior. Use for conceptual onboarding or interpreting a creator's walkthrough; prioritize understanding over a file tour or numbered execution trace.
---

# Explain a Kit

Read [Coding writing](../../docs/harness/coding/writing.md) once per task and apply it to specifications, proof, reports, and human interaction.

Help a technically literate reader who is unfamiliar with the domain build a causal understanding of a kit. Explain why the system has this shape before walking through what executes. Remain read-only toward the assessed system unless changes are separately requested.

## Establish what is being explained

Start from the user's question, supplied conversation, README and kit entrypoints. Identify the version inspected and the boundary between the domain engine, the kit adapter and its host. Read only the code and evidence needed to substantiate the explanation. Do not claim the deployed version or live behavior from a local checkout alone.

If a creator's transcript is supplied, first reconstruct their explanation faithfully. Normalize obvious transcription errors from context, but leave ambiguous statements uncertain. Separate the creator's rationale, measured claims, intended design and implementation claims. Compare consequential claims with the current code without letting an implementation audit bury the conceptual explanation.

## Build the causal explanation

Use these lenses where relevant, combining them into a connected account rather than mechanically emitting a section for each:

- **Business purpose and acceptable answer.** What decision does the user need to make? What manual effort does this replace? Is an approximate answer useful, and when must an expert take over? Identify what the product deliberately leaves outside its scope.
- **Domain objects and identity.** Explain unfamiliar terms when first needed, using one small physical or business example. Distinguish a product identifier from a revision, transaction, production run or configuration. Finding the same identifier does not establish that its old parameters or outcomes remain applicable.
- **Prior analysis and design rationale.** What was studied before the kit was built? Which historical inputs and outcomes were available? How were required inputs, useful predictors, rules or similarity criteria selected? Distinguish feature selection, training and calibration performed offline from extraction and inference performed per request. If the rationale is not recorded, label it unknown rather than inventing a plausible design history.
- **Information groups and acquisition effort.** Distinguish information required to produce any answer, information that improves the answer cheaply, and information requiring specialist work. Check whether these are explanatory categories, actual model tiers or enforced input gates. Preserve the system's names without inventing a universal tier taxonomy.
- **Decision cases.** Organize around what the system knows: its strongest available evidence, weaker historical evidence, analogous cases, and unsupported cases, if those branches exist. For each branch explain why it is selected, what it reuses or estimates, the result it can support and the reason for lower confidence. Do not impose these branches on kits with a different design.
- **Mechanism and data location.** Name the actual source and access technique: local snapshot, live database, keyed lookup, filtered numerical neighbors, embedding search, rules, regression, LLM extraction or human input. Avoid vague verbs such as 'searches' or 'uses AI' when the distinction matters. Explain whether a value is read, computed, estimated, selected or refreshed.
- **Uncertainty and human input.** Explain where uncertainty originates, how the implementation measures or propagates it, and what validation supports it. Distinguish unknown-input uncertainty from model error, historical staleness and extrapolation. State when the system asks, defaults, estimates, qualifies or refuses, and what an answer changes on rerun. A wide band is not proof that an unsupported case is safe.
- **Kit integration.** After explaining the engine, show what packaging adds: receiving requests, extracting documents, invoking the engine, recording state, and delivering outputs. Distinguish runtime artifacts from development analysis and models included in the package. Explain host-provided capabilities separately from dependencies bundled in the kit.

Once the reader has this foundation, give a short runtime flow if useful. For an important transition, connect input → operation and rationale → output. Avoid repeating the entire explanation as a second exhaustive workflow.

## Explain at the right depth

Lead with the central idea in a few sentences. Prefer a compact case table and one running example to many implementation steps. Use hypothetical numbers only when labeled as illustrative. Introduce technical detail to answer a concrete question; offer file paths as evidence, not as the explanation itself. Answer follow-up questions at the requested layer without replaying the whole system.

For a transcript assessment, deliver three things at an appropriate length: what the speaker's account establishes, which points need correction or evidence, and the few questions that would most improve understanding. Credit sound rationale without treating the speaker's confidence as proof.

## Evidence discipline

- Distinguish current code, documented intent, measured results and inference. State the verification boundary; static inspection is not an executed end-to-end run.
- Correlation or feature importance supports predictive usefulness, not causality. Reproducing experts' choices does not independently establish cost accuracy.
- A nearest candidate always existing does not make it a valid comparable. Check eligibility filters, distance thresholds and behavior outside the observed range.
- Historical production parameters may be stronger evidence than old estimates, but availability, revision compatibility and rate freshness still require checking.
- Do not infer that a missing production record means a quote was rejected, or infer business outcomes from absence in a snapshot.
- Separate point prediction, quantile prediction, residual calibration and input-uncertainty propagation when the system uses them. Neighbor dispersion alone is not automatically the prediction error for a new case.
- Do not generalize a successful input, component or route to the whole system. Surface consequential gaps without expanding a conceptual explanation into an unsolicited refactor.
