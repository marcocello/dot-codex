---
name: coding-design-specs-proof
description: Turn sufficiently understood product intent into narrow feature specifications and acceptance tests through focused checks and shared journeys, preserving decisions and explicit assumptions.
---

# Design Specs and Proof

Read [Coding writing](../../docs/harness/coding/writing.md) once per task and apply it to specifications, proof, reports, and human interaction.

Proof and acceptance test mean the same realistic check through UI, API, or CLI. Read the original request, corrections, existing contracts and relevant repository context. Apply [Product Partner](../coding-product-partner/SKILL.md) to inspect surrounding behavior and surface useful adjacent proposals before fixing scope, including when the request is clear. Derive routine details yourself and distinguish accepted decisions from assumptions.

## Specify A Small Outcome

Define one demonstrable vertical outcome with its necessary failure and permission behavior. Split independently useful outcomes, not technical layers. For example, exporting selected orders includes the real download and correct contents; separate API, button and test features would not deliver it.

Once the full request is understood, create one feature or several logical features that together cover every requested outcome. Do not leave requested outcomes only in a future-work outline. Keep each specification proportional; later implementation details and executable proof can be prepared before their dependent implementation.

Use `docs/features/<id>/FEATURE.md` for the outcome, observable acceptance criteria, boundaries and material decisions or assumptions. Keep cross-feature product and architecture context in existing repository documents; create no mandatory scaffolding. A short contract is sufficient when it is precise.

## Connect It To Proof

- Reuse existing tests and journeys that establish the criteria. Add missing assertions rather than duplicate full suites. Write or reuse executable acceptance checks before dependent implementation; assertions may initially fail.
- In mapped features, `COVERAGE.json` links criterion IDs to shared check packages. FEATURE owns the promise, COVERAGE owns the links, and the shared PROOF owns execution and observation details. Do not repeat the feature specification in PROOF. See [coverage and rounds](../../docs/harness/coding/rounds.md) for layout and input reuse.
- Preserve a working standalone proof when useful. The same agent may specify, author, implement and verify. [Proof rules](../../docs/harness/coding/proof.md) own real boundaries, evidence and acceptance repairs; use [examples](../../docs/harness/coding/proof-guidance.md) only when needed.
- Resolve pivotal engineering assumptions before relying on them. A provider fake follows an evidenced contract; writing the fake does not establish that contract. Keep unavailable real boundaries explicit rather than narrow the promise.
- Check coverage against the original outcome, including necessary negatives. Setup checks establish runnable machinery, not successful application behavior.

Register useful drafts through [status mechanics](../../docs/harness/coding/status.md). Mark ready when the outcome and authority are clear, consequential choices are resolved, assumptions are justified and acceptance coverage is executable. Exploration needs no package or confirmation round.

Specification-only work ends at the requested deliverable without a Goal. An authorized build continues through [Implement](../coding-implement/SKILL.md), which owns its scoped Goal and delivery without renewed approval.
