# Adaptive Feature Shaping

## Goal
Turn product input of any maturity into the smallest decision-ready app context and feature/proof set that supports the intended outcome, while acting as a proactive product and architecture partner before implementation.

## Behavior
- Accept a rough or detailed app idea, one rough or detailed feature, or a bundle of ideas. Determine the required shaping depth from material uncertainty and impact rather than the input label.
- Use the global operating kernel as the single intake router. Route one coherent accepted outcome to feature shaping; route multiple potential or accepted outcomes, mixed bundles, or app-level product/architecture authority to app shaping. Discovery may change that routing before artifacts are finalized.
- Expose only the canonical `coding-feature-spec` and `coding-app-to-features` skills as active feature/app shaping authorities. Retire undeclared legacy Codex entry links that encode conflicting mandatory artifact, fixed feature-count, or Gherkin-only workflows without deleting their external source content.
- Investigate current repository behavior, product authority, architecture, related contracts, and authoritative external facts before asking the user for facts that can be discovered.
- Before artifacts are finalized, explain the understood purpose, user benefit, important current constraints, materially different interpretations, and recommended product or architecture direction.
- When incomplete intent leaves materially different plausible product outcomes, ask one concise grouped shaping round even if a safe default exists. Each question explains why it matters, presents meaningful options and consequences, and recommends a default that the user may delegate back to the harness. Do not ask ceremonial questions when investigation and accepted decisions already resolve the outcome.
- A single feature investigation may discover adjacent capabilities. Classify each material discovery as current behavior, prerequisite, follow-up, alternative, or unrelated. Include it in the current artifact set only when it is required by the accepted outcome or explicitly selected; otherwise preserve only an architecture seam or concise deferred note when that prevents foreseeable rework.
- Select artifacts conditionally:
  - create or update `docs/APP.md` only for durable product identity, user, outcome, scope, or boundary decisions;
  - create or update `docs/ARCHITECTURE.md` only for durable cross-feature components, ownership, state, data flow, or integration decisions;
  - create one feature package per independently valuable, independently provable outcome accepted for the current scope;
  - leave weakly supported ideas in conversation instead of generating speculative specifications or backlog.
- Keep exploration and discarded alternatives in conversation. Durable files contain only accepted behavior, decisions, invariants, compatibility requirements, material risks, architecture seams, and non-goals.
- Before implementation, provide concise feature and proof decision summaries. Contract-authoring requests stop after the justified app/architecture documents and decision-complete feature/proof packages; implementation requires explicit authorization.
- Proof decisions derive from the feature's actual risk model and select only relevant operational pressure, including allowed-size limits, existing persisted states, restart/recovery, concurrency, provider-native variability, deployment topology, health under slow work, or UI interaction topology.

## Constraints
- Discovery may expand understanding freely; only accepted decisions may expand durable artifacts or implementation scope.
- Anticipate plausible adjacent capabilities in current architecture only when a small, concrete seam prevents foreseeable rework. Do not implement speculative adjacent product behavior.
- Questions scale with uncertainty and consequence, not a fixed count. Prefer one grouped round; ask a second round only when answers expose a new material decision.
- Every `FEATURE.md` sentence must contribute accepted behavior, a decision, an invariant, compatibility, material risk, or a non-goal.
- Preserve one accountable parent and serial implementation of one feature package at a time even when shaping produces several packages.
- Preserve realistic executable proof, final-candidate freshness, fresh final evaluation, the four queue states, and read-only preflight/evaluation.

## Non-Goals
- Generating a mandatory `APP.md`, `ARCHITECTURE.md`, roadmap, or fixed number of feature packages for every request.
- Implementing every plausible adjacent capability discovered during shaping.
- Requiring the user to approve written contracts after material decisions are resolved.
- Adding another reviewer, queue state, receipt, score, hash, dependency graph, or orchestration layer.
- Changing implementation preflight or final evaluation scope; independent lifecycle-review hardening is owned by a separate feature.
- Replacing product judgment with a universal question checklist or operational-risk checklist.
