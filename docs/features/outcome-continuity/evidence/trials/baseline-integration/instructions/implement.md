---
name: coding-implement
description: Implement authorized features through a scoped native Goal, preparing drafts as needed and carrying delivery through independent proof, affected regressions, and final review.
---

# Implement

Deliver every authorized outcome in narrow useful slices against independent acceptance. Choose the order and tactics from dependencies and evidence; this skill defines responsibilities, not a script of mandatory ceremonies.

## Enter And Persist

- Resolve scope, dependencies, and claims from the request, accepted decisions, and feature inventory.
- For new/changed behavior or material structural changes, apply [product discovery and autonomy](../coding-product-partner/SKILL.md#discovery-and-autonomy). Check the intended outcome and scope against the request and evidence; do not rely on a `ready` label alone. Resolve routine choices yourself and proceed within existing authority. Return consequential user-owned gaps to Product Partner, pausing only dependent work.
- Include scoped drafts; exclude unrelated backlog and deferred work.
- Prepare the next useful slice through [Design Specs and Proof](../coding-design-specs-proof/SKILL.md); use [Product Partner](../coding-product-partner/SKILL.md) when the outcome or consequential product decisions remain unclear. Mark the slice `ready` before claiming implementation. Keep later drafts provisional instead of requiring the whole backlog to be specified first.
- Do not request build approval again or make optional questions a delivery gate.
- Use [status mechanics](../../docs/harness/coding/status.md), [proof rules](../../docs/harness/coding/proof.md), and [capture commands](../../docs/harness/coding/evidence.md).
- Start or resume the scoped implementation Goal under the policy below once the next slice is ready. A request to implement does not put unresolved product discovery or initial specification/proof design into Goal mode.

## Start The Goal

- Reuse or create the scoped native Goal when the intended outcome is understood and the next slice is ready and authorized for implementation. The standing request covers this transition; do not ask again.
- The Goal covers authorized implementation through independent proof, affected regressions, and final review, including necessary repairs and preparation of later agreed slices. Product discovery and standalone specification/proof design do not start Goals.
- Set budgets only when supplied. Honor overrides, interruptions, and tool/runtime limits. Never replace an unrelated Goal, extend limits, or create substitute persistence loops.
- If Goal tools are unavailable, report once and continue authorized work. Preserve other ownership; stopped is not complete.

## Implement And Repair

- Implement prerequisites first. Delegate independent features when files, contracts, runtimes, and agents permit.
- Keep each feature to one demonstrable outcome with its necessary end-to-end path. Preserve the shared journey and remaining scope; a completed slice is not automatically a completed application.
- Otherwise work serially. Never claim another worker's feature.
- Freeze acceptance, then implement with the relevant domain skills.
- Diagnose at the real boundary. Keep application regressions separate from acceptance.
- Send proof defects and unresolved acceptance choices through the proof contract's decision boundary.
- Select regressions from changed code, consumers, and compatibility. Broaden when justified or cheap.
- Repair introduced regressions within the existing feature/Goal; no extra package per affected behavior.
- Investigate before calling failures pre-existing. Report evidenced unrelated failures separately.
- Repeated failure requires new evidence or a different repair. Retry only for supported transient causes.
- Record what the next attempt will establish. Repetition alone does not make a blocker user-owned.
- Pause dependent work only. Stop substantive work at interruption or exhaustion.
- Keep one current checkpoint: ownership, inputs, attempts, remaining acceptance, blockers, runtime, next action.
- On resumption, recheck source, contracts, and runtime. Mark old observations historical.
- Do not repeat pending questions or poll unchanged artifacts. Use Goal controls only under their actual rules.

## Verify And Review

- Run complete proof and affected regressions against the final candidate; capture separately.
- Keep relevant source, acceptance, and runtime inputs stable. Relevant changes invalidate evidence.
- Compare observed behavior with the original request and accepted discovery cases. Passing tests cannot excuse missing outcomes.
- Obtain a fresh final reviewer distinct from implementer and proof author.
- Supply request/corrections, contracts, changed surface, target, and results.
- Use the [reviewer brief](../../docs/harness/coding/proof-guidance.md#final-reviewer) when useful. Reviewers challenge what a pass might miss, not merely whether files and labels exist.
- Review behavior, regressions, proof adequacy, input freshness, and author repairs.
- Reviewers stay read-only: no edits, official runs, status mutations, or permission grants.
- Use early review only for a concrete risk or user request.
- Resolve blockers, rerun affected verification, then obtain fresh review. Keep unrelated preferences optional.

## Complete

- Require latest target-valid official proof PASS, affected verification, reviewer PASS, and unchanged relevant inputs. Record the actual review through the [receipt command](../../docs/harness/coding/evidence.md#current-candidate-and-review); the status helper checks freshness and attribution, not semantic adequacy.
- Record `active -> done` with its proof pointer. Continue remaining scope.
- After integration changes, rerun affected proof/regressions and obtain fresh review.
- Complete the Goal only when its entire objective is met.
- Status-only completion needs the repository gate, not another proof run.
- Hand back feature/proof mapping, demonstrated boundary, runtime, gaps, and blockers.
- Proof success does not authorize deployment.
