---
name: coding-design-specs-proof
description: Turn sufficiently understood product intent into narrow feature specifications and independent executable acceptance proof, preserving decisions and explicit assumptions.
---

# Design Specs and Proof

Translate understood intent into observable behavior and a realistic way to prove it. Apply [product discovery and autonomy](../coding-product-partner/SKILL.md#discovery-and-autonomy): establish the outcome, authority, and consequential decisions from the request, dialogue, and evidence. Return unresolved user-owned choices to Product Partner; a clear authorized slice needs no additional question-and-answer round before specification.

Read the original request, answers, existing contracts, and relevant repository evidence. Distinguish accepted decisions from recommendations and assumptions. Resolve discoverable engineering facts yourself; return material product uncertainty to [Product Partner](../coding-product-partner/SKILL.md#discover-and-decide). Continue settled work while independent questions remain pending.

Specification/proof design does not start a native Goal. Derive routine details from the established direction and evidence; do not reopen discovery for individual fields or technical choices. Specification-only scope ends at the requested deliverable and grants no implementation authority. [Implement](../coding-implement/SKILL.md#start-the-goal) starts the Goal when the next slice is ready for authorized implementation.

## Design Narrow Slices

Prefer one specific, independently demonstrable outcome per feature. Include the minimal end-to-end path and necessary failure/permission behavior. Split when outcomes can be accepted separately, decisions remain independent, or one uncertain integration would hold unrelated value hostage. Do not split merely by files or layers, or omit essential cases to make a spec look small.

For a broad request, maintain a short journey outline showing how slices connect, their dependencies, and deferred choices. Prepare the next useful slice in detail; keep later slices provisional until their decisions are ready. Do not require a complete backlog of executable proofs before delivering a settled slice. Continue toward every authorized outcome rather than quietly dropping later scope.

For example, order search, saved filters, and scheduled exports can be separate outcomes. The selected order export still needs its real download and correct contents; separate “API,” “button,” and “test” features would not each deliver that outcome. Refactors use a narrow responsibility with explicit preserved invariants.

## Record Earned Decisions

Place durable content by what it describes. General app descriptions, vision, journey overviews, and broader future direction belong in `app.md` or equivalent product documentation. System structure, visual architecture, and cross-feature technical decisions belong in `architecture.md` or equivalent architecture documentation. Feature-specific outcomes, contracts, and proof belong in their owning package under `docs/features/`, including drafts with open decisions. Keep future possibilities clearly provisional wherever they are recorded.

Reuse existing product and architecture documents and their naming conventions; create them only when durable context needs a home. Neither filename is a universal prerequisite. Update the relevant document or feature package when reviewing decisions, so the result stays with the content it explains. Add conventions/testing guidance only when it prevents repeated decisions.

Use one directory per feature at `docs/features/<feature-id>/`, with a stable lowercase hyphenated identifier. Reuse the owning directory when refining an existing feature. Use these exact filenames and paths:

```text
docs/features/
├── status.json                # shared lifecycle index
└── <feature-id>/
    ├── FEATURE.md             # outcome and behavior contract
    ├── PROOF.md               # acceptance contract and scenario mapping
    └── proof/
        ├── run.sh             # executable acceptance runner
        └── runs/              # retained execution evidence, created on runs
```

A durable draft requires a nonempty `FEATURE.md`; add `PROOF.md` and executable `proof/run.sh` before marking it ready. Do not create empty proof files or run directories merely to fill the tree. Keep acceptance tests and determining fixtures/helpers under `proof/`, documenting framework-required alternative paths in `PROOF.md`. Create the package files before registering the draft; the status helper records and validates them, rather than scaffolding them. Follow [status mechanics](../../docs/harness/coding/status.md) for index changes.

Record each settled slice in its `FEATURE.md`: intended outcome, observable behavior, material decisions, assumptions, boundaries, dependencies, and compatibility. Connect decisions to the request, actual answers, or supporting context; distinguish agent assumptions from user agreement and never invent a question-and-answer record. Use schemas only where they resolve ambiguity; keep commands and fixtures in proof. Link the whole journey when useful. Drafts may retain open decisions; only implementation dependent on an unresolved consequential user decision waits.

## Prepare Independent Acceptance

- Register durable drafts using [status mechanics](../../docs/harness/coding/status.md). Exploration itself needs no package.
- Supply the independent author with FEATURE, original intent/corrections, relevant context, and the named consumption target under the [proof contract](../../docs/harness/coding/proof.md). Use its [role briefs and examples](../../docs/harness/coding/proof-guidance.md) when designing an unfamiliar boundary. This skill does not merge implementer, acceptance-author, and final-reviewer responsibilities.
- Establish critical provider capabilities, permissions, and observation paths through existing evidence or bounded authorized probes. An unsupported integration assumption is not readiness.
- Reconcile scenarios and proof with the original outcome. Resolve missing decisions rather than narrow the promise. Author setup checks establish that the proof machinery works; application assertions may correctly remain red.
- Mark a slice ready when its outcome and authority are clear, consequential user-owned decisions are resolved, remaining assumptions are justified, and its independent proof is executable. This is an accountable judgment, not a document-count test or another build-approval round.
- Retain prior evidence on interruption or revision. During delivery, acceptance repairs follow the proof contract; routine setup repair does not reopen product discovery.

Specification-only work ends at the requested deliverable without a Goal. An authorized build continues through [Implement](../coding-implement/SKILL.md), which starts or resumes its implementation Goal without renewed approval. Later slices can be prepared as needed; this skill is not a compulsory stop for small repairs or already-ready work.
