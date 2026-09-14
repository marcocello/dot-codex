# Ship

Deliver one ready feature against fixed acceptance. Ship owns implementation, internal repair, target verification, and final review.

## Enter And Persist

Require implementation authorization, the specification, independently authored executable proof, and a matching `ready` entry. Read [status.md](status.md), [proof.md](proof.md), and [evidence.md](evidence.md). Claim `ready -> active` using this task's stable owner id. Coordinate overlapping writes and shared runtime use; independent tasks may continue.

Use native Goal tools according to their actual contract. Check for an existing Goal and explicit Goal authorization in the current user/runtime instructions, including a standing user request. A normal build request alone does not authorize Goal creation. If required authorization or native capability is missing, surface the exact need before dependent Ship work; never create a replacement loop or `GOAL.md`.

The Goal names outcome, scope, target, fixed proof, affected regression verification, and final review. Use the user/system-configured overall allowance; set a numeric token budget only when explicitly requested. Reuse an existing matching Goal. Do not replace an unfinished unrelated Goal, invent an allowance, or reset/extend its budget. Pause, resume, objective changes, and budget control belong to supported user/runtime controls; the agent uses only exposed operations it is authorized to perform.

## Implement And Repair

Keep `FEATURE.md`, `PROOF.md`, and acceptance requirements unchanged. Implementers cannot edit frozen proof inputs. The independent author may correct demonstrably faulty setup under [proof.md](proof.md#fixed-acceptance), preserving scenarios, assertions, outcomes, and test boundaries, retaining the correction, and rerunning proof without asking permission. This stays in Ship with the same claim, Goal, and allowance. Record and compare all proof input versions, including shared acceptance helpers. Use domain skills for application code and add internal tests for concrete risks alongside the feature they verify, separately from frozen acceptance; follow the organization in [proof.md](proof.md#separate-authorship).

The separate author establishes meaningful red evidence when practical. During repair, inspect the exact failure, distinguish implementation from environment/access or proof defects, reproduce the narrow boundary, and repair code. Run the narrow check while iterating; run complete feature proof on the final candidate. Repeated failures call for a different evidence-backed approach, not a fixed retry count.

Use the Shape compatibility note and actual changes to select affected existing tests or proofs. Update selection as impact changes. Run everything if cheap; broaden for shared or uncertain impact. An introduced regression is repaired inside this feature's existing task, Goal, and allowance, with no separate package or reviewer per affected feature. Reuse a failing test or add a focused regression outside fixed acceptance. Evidenced unrelated pre-existing failures are reported separately; investigate uncertain causes before labeling them old.

If acceptance itself needs correction or its meaning remains unresolved, pause dependent implementation, retain the failure, and ask the user about the concrete behavior decision once. Continue authorized work whose correctness is independent of every plausible answer. Only after the decision may Shape revise the specification, a separate author revise proof, and supported controls align the Goal. Freeze the revision before dependent work resumes. Never alter valid proof to accommodate implementation difficulty or use a mode transition to evade this rule.

## Stop And Resume

The overall allowance covers implementation, regression repairs, verification, and final review. At budget exhaustion or user interruption, stop substantive work. Missing necessary input/access pauses only dependent work; complete useful authorized work independent of the answer, then stop. Retain the task association, input versions, evidence, attempted approaches, exact remaining failure, and next useful action. Stopped work is unfinished. Do not mark success or silently restart with a fresh allowance.

Retain one pending question and what it blocks. An asynchronous question already counts as asked; do not duplicate it as `NEED_INPUT` in the final response. On automatic continuations, check for a reply or useful independent work without re-asking, repeating rule citations, or rechecking unchanged artifacts merely to fill the turn. If no progress is possible, use native blocked controls once their actual criteria are met. Until then, preserve the pending state without claiming success or simulating pause through a replacement loop. Explain again only when the user asks or new evidence materially changes the decision.

Feature ownership and native Goal state are distinct. An interrupted/budget-limited feature can retain its active claim while execution is stopped. Use feature `blocked` for a necessary external dependency or decision. Use a native Goal blocked operation only when its actual runtime criteria are met; budget exhaustion is not that operation. Before resuming, check changed contracts, source, evidence, and runtime. The user controls further allowance and acceptance changes.

## Verify And Review

Run realistic proof on the named consumption target plus selected regression checks against the final candidate. Capture both official proof and completion-supporting regression runs through the appropriate [capture mode](evidence.md#evidence-for-one-feature), and supply their retained paths to review. Source evidence is intermediate when an existing runtime is the target: continue authorized activation/read-back or report the exact pending action. Keep relevant code, acceptance inputs, and runtime stable through proof and review; any relevant mutation requires renewed verification.

After proof PASS and regression verification, invoke one fresh read-only final reviewer distinct from implementer and proof author. Supply the original request/corrections, specification, proof, changed surface, named target, and retained results. It checks accepted behavior, correctness, affected existing behavior, proof adequacy, and current evidence. Extra early review is discretionary for a concrete risk or user request.

The reviewer returns `PASS`, blocking `FINDINGS`, or `NEED_INPUT`, with evidence and the smallest next action. Accepted-behavior failures, introduced regressions, inadequate proof, and concrete correctness/safety defects block. It checks any independent setup correction against the unchanged contract and retained diff. Style preferences and unrelated improvements are suggestions. The reviewer does not edit, execute official proof, mutate status, or grant permission. Code findings return to code repair, setup findings to the independent proof author, and acceptance decisions to the user; rerun verification before fresh review.

## Complete

Complete only with target-valid proof PASS, passing selected checks except evidenced unrelated pre-existing failures, final-review PASS, and unchanged relevant inputs. A newer failed or unfinished official attempt invalidates an older PASS. Observed broken behavior overrides green evidence; diagnose and follow the same code-repair, independent setup-repair, or user-directed acceptance-correction rule.

Retain evidence and update `active -> done` with the latest valid official `proof_run`; then mark the matching Goal complete only when its objective is actually satisfied. A status-only completion write does not require another proof run. Run required repository checks and report outcome, changed surface, proof, review, runtime state, and gaps. Stop at analysis/specification when that was the requested deliverable; never treat proof success as deployment authorization.
