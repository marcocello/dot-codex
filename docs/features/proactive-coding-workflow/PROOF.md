# Proactive coding workflow proof

## Done

All eleven bounded cases produce independently exercised and independently assessed forward responses/action traces consistent with the accepted contract. The candidate instruction hashes and frozen acceptance inputs remain unchanged through official proof and final review.

## Command

Run `"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture.py" --feature-dir docs/features/proactive-coding-workflow --timeout-seconds 60 --note "bounded blind proactive workflow exercises"` from the repository root. The runner is `proof/run.sh`; dedicated verifier is `proof/check.py`.

## Scenarios and boundary

The producer is each raw user request plus investigated repository/runtime context in `proof/cases.json`. Two fresh independent agents consume actual current on-disk harness instructions under `proof/executor.md`, without this document, the feature specification, oracle, other responses or evaluator hints. The consumer/read-back is their actual next user-visible response plus explicit external next-action, Goal disposition and stopping boundary, retained verbatim as JSON. No application implementation is claimed or performed in this isolated exercise. Unsafe external actions and real scenario Goal mutations are excluded; supplied runtime/project facts replace access to another project, not the instruction behavior being assessed.

`proof/oracle.json` defines behavioral assertions, assessed individually by the independent proof author after outputs arrive. The runner binds responses, assessment and candidate through SHA256 maps and requires all assertions. This is semantic assessment, not exact-prose matching or a token-presence test.

| Case | Activation and observation | Catches |
| --- | --- | --- |
| model_defaults | Original ambiguous booth/both prompt; inspect question, preserved role and Goal actions | Redundant role/Goal approvals, guessing consequential meaning, deliberate behavior mislabeled defect |
| animation | Reuse existing accessible animation; inspect next response/actions | Design/implementation reapproval, stopping at plan, loss of accessibility |
| roles | Explicit member editing request; inspect boundary and intended work | Overpreservation despite explicit change, unrelated permission expansion |
| fix | Known filename typo; inspect scope and checks | Material ceremony or Goal requirement for isolated maintenance |
| analysis | Architecture explanation only; inspect specialist and stopping condition | Unrequested Shape/implementation/Goal |
| spec_only | Explicit specification-only request; inspect Goal scope and stopping condition | Goal expanding requested scope or repeated known decisions |
| direct_ship | Ready accepted feature with no Goal request; inspect execution disposition | Goal approval blocker or unauthorized new Goal |
| missing_tools | Build with unavailable Goal API; inspect continuation | Fabricated Goal, substitute persistence, needless pause |
| shorthand_pr | Terse runtime symptom with supplied PR; inspect intake actions | Asking user to route, overlooking supplied context, unauthorized mutation |
| deep_shape | Underspecified reminders feature; inspect journey discovery and product questions | Guessing consequential behavior, superficial Shape, blanket one-question cap |
| occupied_goal | Build with unrelated unfinished Goal; inspect isolation and continuation | Replacing Goal/owner or process blocker |

## Evidence method

Proof author: `/root/proactive_proof`. Coordinator records candidate instruction hashes in `evidence/candidate-sha256.json`, including at least AGENTS, workflow, shared rules and all four lifecycle skills; include other changed instruction surfaces. Dispatch executors with `fork_turns=none` and only neutral protocol, assigned case IDs, candidate hash map and output path. Split cases across `evidence/executor-a.json` and `evidence/executor-b.json`. Executors cannot be the implementer or proof author. Independent proof author writes `evidence/assessment.json` with candidate hashes, response file hashes and one pass/evidence judgment per frozen oracle assertion. Final reviewer must be distinct from implementer and proof author.

`proof/acceptance-sha256.json` freezes FEATURE, PROOF, runner, verifier, cases, oracle and executor protocol before implementation. The runner fails on missing evidence, altered candidate/acceptance, missing cases, incomplete judgments or any failed assertion. It does not create or edit evidence. Demonstrate missing-evidence failure before implementation; final official proof requires actual blind outputs and assessment. Preserve unsuccessful attempts and failed judgments when candidate correction requires reruns.

## Proves

The named candidate instructions, actually consumed by independent agents, elicit the accepted observable response/decision behavior for these bounded scenarios. They distinguish useful clarification from process approval and preserve request scope, skill announcements, permission boundaries and Goal ownership.

## Does not prove

A fresh production Codex startup, real TWYD implementation, native Goal tool execution, full autonomous completion, all possible prompts, or a statistical guarantee of future model behavior. A described next action is evidence of a decision only, not proof that an application changed.

## False-green risks and known gaps

Agents share the same filesystem; blinding is instruction-based, not an access-control guarantee. Record executor identities and source-read declarations. Independent semantic judgment can be wrong; retain concrete output evidence for final review. Checks validate assessment integrity, not semantics themselves. Current native conversation capture may be partial. No source-reading summary or implementer-predicted response can substitute for actual independent outputs.

## Environment and target

Current local dot-codex checkout, Python 3, fresh bounded independent agent invocations, actual on-disk instructions at recorded hashes. Missing agents or evidence is a failed/incomplete proof, never silently downgraded to static wording checks.
