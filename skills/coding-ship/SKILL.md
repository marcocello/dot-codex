---
name: coding-ship
description: Deliver one specified feature through implementation, independent executable proof, affected regressions, and final review, continuing the matching Shape Goal when available.
---

# Ship

Deliver one authorized ready feature against fixed independent acceptance.

## Enter And Persist

Require the specification, independently authored executable proof, and a matching `ready` entry. Use [status mechanics](../../docs/harness/coding/status.md) to claim it; read the [proof contract](../../docs/harness/coding/proof.md) and [capture commands](../../docs/harness/coding/evidence.md) for this run.

Continue the matching [Shape Goal](../coding-shape/SKILL.md#start-the-goal). Direct Ship without one proceeds normally: no new Goal inferred from a build request and no Goal-approval blocker. Honor separate explicit Goal requests through available tools. Missing Goal tools do not block ordinary execution. Never invent a Goal/budget, replace an unrelated Goal, extend limits, or use substitute persistence loops.

## Implement And Repair

Freeze specification and acceptance inputs under the proof contract. Implement the agreed behavior using selected domain skills. Diagnose failures at the real boundary; repair application code and keep implementer-authored regressions separate from acceptance. Proof setup defects go to the independent author; changed or ambiguous acceptance goes to the user. A mode change cannot bypass that distinction.

Select regressions from changed code, shared consumers, and Shape's compatibility notes; run all when cheap or justified by broad impact. Repair introduced regressions within this feature and its existing Goal/allowance, without another package/reviewer per affected feature. Investigate uncertain causes before labeling failures pre-existing; report evidenced unrelated failures separately.

Stop substantive work at interruption or configured exhaustion; no silently renewed allowance. Missing decisions/access pause dependent work only. Preserve task/ownership, input versions, attempts, remaining failure, and next useful action. On resumption inspect changed contracts/source/runtime; do not repeat pending questions or poll unchanged artifacts to simulate progress. Use native blocked controls only when their actual criteria hold. Align any existing Goal through supported controls after an authorized scope decision; never rewrite frozen acceptance to match implementation.

## Verify And Review

Run complete realistic proof on the named consumption target and affected regressions against the final candidate, captured separately through the evidence commands. Passing source checks are intermediate when the target is a live runtime. Keep relevant source, acceptance, and runtime inputs stable; relevant changes invalidate evidence, unrelated edits do not.

Compare the demonstrated user-visible result with the original request and accepted discovery cases, not just test totals. A requested result still missing is a gap even when scoped tests pass. Repair within the contract; omitted or ambiguous acceptance follows the existing user-decision and independent-proof process. Report limitations explicitly.

After proof and affected checks, obtain a fresh read-only final reviewer distinct from implementer and proof author. Supply original request/corrections, contracts, changed surface, target, and retained results. It checks behavior, correctness, affected regressions, proof adequacy, input freshness, and independent setup corrections. It does not edit, run official proof, mutate status, or grant permission. Extra early review is optional for a concrete risk or user request.

Blocking findings return to code repair, independent setup repair, or the user-owned acceptance decision; rerun affected verification before fresh review. Preferences/unrelated improvements are suggestions. Observed broken behavior overrides green evidence.

## Complete

Require target-valid latest official proof PASS, affected verification (with evidenced unrelated failures reported), final reviewer PASS, and unchanged relevant inputs. Record `active -> done` with that proof pointer, then complete a matching Goal only when its scoped objective is satisfied. A status-only completion write needs the repository gate, not another proof attempt. Report outcome, verification/review, runtime state, gaps, and blocker. Proof success never authorizes deployment.
