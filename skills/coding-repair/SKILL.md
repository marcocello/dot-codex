---
name: coding-repair
description: Repair known defects or small maintenance, distinguishing standalone fixes from reopened feature obligations and active implementation regressions.
---

# Repair

Restore known expected behavior with the smallest verified change. Use [AGENTS.md](../../AGENTS.md#understand-and-route) when discovery changes the route.

## Classify And Explain The Scope

Before editing, state the expected behavior and evidence, whether it invalidates a delivered feature, and the verification needed. Apply [Product Partner](../coding-product-partner/SKILL.md) to inspect neighboring actions and recovery, surfacing useful proposals even for clear fixes without expanding their scope. Clear new behavior goes to Design Specs and Proof; an unlocated runtime symptom goes to Runtime Ops.

Use available feature context to identify an owning contract; inspect a clearly relevant contract before classifying the repair as standalone. Do not require an exhaustive feature search or create a feature package solely for a bug.

- **Standalone Repair:** no delivered feature contract is invalidated. Focused check plus affected regressions; no package, Goal, independent acceptance author, or mandatory reviewer. Sharing a feature's source file alone does not reopen it.
- **Reopened feature:** read the existing contracts, identify the violated scenario, and reopen through [status mechanics](../../docs/harness/coding/status.md). Preserve realistic feature proof and fresh final review regardless of patch size.
- **Regression during active Implement:** repair within that feature's existing task, Goal/allowance, and review; no separate package per affected behavior.

Explain a changed classification before continuing. For example, restoring an already-required status mapping is Repair; deciding that a new status should count as completed is a product decision.

## Repair

1. Reproduce the symptom with a focused executable check at the narrowest boundary that observes the reported outcome; read the error, call path, neighboring tests, and runtime evidence. Name what the check observes and any fake or unavailable external edge. A selected API operation or successful request does not establish the downstream consumer result.
2. Establish the cause and confirm that the check exposes the reported failure before changing the implementation. If reproducing it is unsafe or unavailable, retain the observed failure evidence and state the verification gap; do not claim a red run or a resolved outcome. Keep the check as a regression in the repository, with the owning feature when one exists, and separate from frozen acceptance.
3. Make the smallest effective repair using existing logic. Preserve unrelated work; coordinate overlapping edits/shared runtimes without blocking independent work.
4. Rerun the exposing check and affected regressions, broadening only when impact warrants it. Do not hide runtime failures, weaken assertions, or perform unrelated refactoring.

Follow newly exposed prerequisites within the authorized repair through to the original expected behavior. Fixing setup only to encounter the next guard is partial progress. Investigate and repair the supported recovery path, preserving its validation; do not stop at “the scripts need a fix” or bypass state checks to obtain a passing command. Continue local work while any separately required runtime permission remains pending.

When a previous repair passed checks but the reported bug persists, inspect why those checks missed it and strengthen the relevant coverage before relying on another pass. For a violated feature contract, rerun the mapped affected acceptance checks and relevant composed journeys (or the owning standalone proof); route missing acceptance coverage through the shared proof procedure rather than creating a substitute fix-only proof or weakening accepted behavior.

Restore broken acceptance machinery under the [proof contract](../../docs/harness/coding/proof.md), preserving accepted outcomes and recording material test corrections. The same agent may do this; no separate author or reviewer is required.

## Complete

Standalone work completes with its focused check and proportional regressions, using native task evidence. Reopened features follow [Implement verification and completion](../coding-implement/SKILL.md#verify-and-review), capture official proof and supporting checks through [evidence commands](../../docs/harness/coding/evidence.md), and return to `done` only with required proof/review PASS. A narrow regression pass cannot replace failing feature proof; retain failures and report unrelated pre-existing issues without broadening product scope to get green. Relevant changes require renewed checks.

Limit completion claims to the behavior and boundary actually observed. If only local request construction was verified, say so and keep external delivery verification pending. Carry any original runtime symptom through the repair; local success does not close an operational issue without the affected consumer read-back required by Runtime Ops.

If the outcome remains blocked, hand back the exact remaining action, who must perform it, why it cannot be performed here, and how recovery will be verified. Provide a runnable command and target context when the user must execute it, or a specific approval/access request when that is the missing prerequisite. Do not assign agent-owned implementation work to the user or end a turn while that authorized work can still proceed.
