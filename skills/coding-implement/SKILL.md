---
name: coding-implement
description: Implement authorized features through a scoped native Goal, preparing drafts as needed and carrying delivery through shared acceptance coverage, affected regressions, and final review.
---

# Implement

Read [Coding writing](../../docs/harness/coding/writing.md) once per task and apply it to specifications, proof, reports, and human interaction.

Deliver every authorized outcome in narrow useful slices. Choose tactics from dependencies and evidence; delegation and separate review are optional.

## Enter And Persist

Resolve scope, dependencies and ownership from the request, accepted decisions and feature inventory. Include authorized drafts, not unrelated backlog. Apply [Product Partner](../coding-product-partner/SKILL.md) to inspect surrounding behavior and raise useful proposals before dependent edits and [Design Specs and Proof](../coding-design-specs-proof/SKILL.md) to ensure one or more logical features cover the whole request, then prepare the next feature for implementation. A ready label does not replace checking intent; keep later implementation details provisional.

Once the next slice is ready and authorized, claim it through [status mechanics](../../docs/harness/coding/status.md) and start its Goal. Optional questions and skill transitions introduce no approval gate. [Proof rules](../../docs/harness/coding/proof.md) own acceptance boundaries and repairs; [capture commands](../../docs/harness/coding/evidence.md) own retained results.

## Start The Goal

Reuse or create a scoped native Goal for authorized implementation through verification, including necessary repairs and preparation of later agreed slices. Discovery and standalone specification do not start Goals. The standing request authorizes this transition without another approval.

Set budgets only when supplied. Honor interruptions and limits; never replace an unrelated Goal, extend its allowance, or create substitute persistence loops. If Goal tools are unavailable, report once and continue authorized work. Stopped is not complete.

## Implement And Repair

- Implement prerequisites first against the narrow spec and executable acceptance tests, using relevant domain skills. Run focused checks during development. Delegate only when useful and ownership permits; otherwise work serially without claiming another worker's feature.
- Group related features into a coherent [implementation round](../../docs/harness/coding/rounds.md). Use `implemented` when code and focused checks are finished but shared verification is pending; it releases the claim, not the verification obligation. A finished slice is not a finished application.
- Diagnose at the real boundary. Repair introduced regressions within the same feature and Goal; use proof rules for test defects. Select affected regressions from changed code and consumers, broadening when justified. Establish evidence before calling a failure pre-existing.
- Repeated failure needs new evidence or a different repair; retry unchanged only for supported transient causes. Continue independent work while dependent work waits. Do not repeat pending questions or poll unchanged artifacts.
- On interruption, retain one checkpoint with ownership, inputs, attempts, remaining acceptance, runtime and next action. On resumption, recheck source, contracts and runtime rather than treating historical observations as current.

## Verify And Review

Run outstanding acceptance checks and relevant shared journeys against the stable integrated result. Capture acceptance separately from supporting regressions. After repairs, [rerun only affected checks](../../docs/harness/coding/rounds.md#rerun-only-affected-checks), reusing current evidence and declared inputs.

Compare the actual result, changes and coverage with the original request and spec. The implementing agent can do this. Fix discrepancies and verify affected behavior; passing tests cannot excuse a missing outcome or justify weakening acceptance.

## Complete

Require current target-valid PASS evidence for every mapped criterion and affected verification. Check coverage and dependency scopes: scripts cannot infer omitted promises or dependencies. Record the [round or standalone result](../../docs/harness/coding/evidence.md), then mark verified features done through the status helper. Blocked features remain incomplete; continue the remaining authorized scope.

Historical completion does not establish current behavior; use `check-round` when claiming a retained whole round is current. Integration changes require affected verification. A status-only update needs the repository gate, not another proof run.

Complete the Goal only when its entire objective is met. Hand back the feature/proof mapping and the observed boundary and runtime. Match readiness claims to the changed version actually available at the user's intended entry point. If it is unavailable there, state the remaining activation step, authority or access needed, and owner. Separate availability from behavior still awaiting verification. Continue already-authorized delivery steps; proof success does not authorize deployment.
