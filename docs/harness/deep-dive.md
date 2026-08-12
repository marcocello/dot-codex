# Harness Design

## Objective
Reach accepted behavior one feature at a time. Use realistic executable proof to drive implementation and fresh semantic evaluation to find contract, architecture, and false-green gaps. Convert every supported evaluator finding into durable proof pressure before repair.

## Pillars
- Intent: `FEATURE.md` owns observable behavior and material boundaries.
- Evidence: `PROOF.md` and `proof/run.sh` activate the real boundary and read back durable or visible effects.
- Retention: `proof_run_capture` preserves meaningful failures, timeouts, interruptions, contract/runner copies, and final passes.
- Semantic challenge: every tracked or autonomous feature receives fresh final evaluation; only evaluator `PASS` permits parent-owned completion.
- Repair: proof or evaluator failures return to the owning code, architecture, setup, fixture, or proof boundary without weakening the goal.
- Serial autonomy: one parent completes one feature before selecting the next.
- Lean preparation: app-level work creates the complete non-speculative set of small, independently provable features.
- Independent contract challenge: one fresh separate bounded read-only preflight challenges tracked and autonomous feature/proof assumptions on the real implementation entry path without becoming a completion stage.
- Bounded evaluation: the parent supplies the active feature's transient changed-file surface and relevant call paths instead of making an accumulated same-checkout diff the default review scope. One evaluator reasons evidence-first and implementation-second so retained behavior is judged before implementation shape can bias the review.

Script precision cannot make a weak proof realistic, and evaluator confidence cannot replace executable evidence.

## Contract Preflight
After feature and proof decisions are complete and implementation is explicitly authorized, `coding-feature-execute` starts a fresh separate reviewer context before red evidence. The reviewer challenges intent forks, authority and state transitions, affected consumers, central false-green pressure, and feature cohesion. The review is contract-only: it may inspect relevant existing behavior needed to identify authority or consumers, but it does not inspect a candidate implementation or execute proof.

The reviewer returns at most three material findings in one pass. The accountable parent owns every contract/proof revision, evidence-based rejection, user question, and readiness transition. Preflight output is transient and grants no implementation or completion authority; final executable proof and fresh implementation evaluation remain unchanged.

## Evaluator Loop
A passing proof is a finite set of known scenarios. The evaluator first maps accepted claims to actual retained output, then inspects the implementation and relevant call paths against that evidence map. Both passes occur in the same bounded review with no intermediate report or extra stage. It returns all material findings it can support, including whether an important broken implementation could still pass. Supported findings first strengthen proof, demonstrate the missed failure when practical, repair the owning behavior, rerun the complete proof, and receive another fresh evaluation. This repeats until `PASS`.

The evaluator is read-only and cannot mutate contracts, implementation, proof, or queue state. The parent owns every repair and transition.

Final-candidate freshness is a serial parent invariant: relevant edits after proof or evaluation invalidate that evidence and return to complete proof followed by fresh evaluation. Retained attempt generation and the narrow queue completion write are bookkeeping, not candidate changes.

## Ownership
| Concern | Owner |
| --- | --- |
| Global lanes, completion, safety | `AGENTS.md` |
| App decomposition | `coding-app-to-features` |
| Behavior contract | `coding-feature-spec` |
| Proof contract | `coding-proof-author` |
| Fresh contract challenge | `coding-feature-preflight` |
| One-feature lifecycle | `coding-feature-execute` |
| Failure repair | `coding-repair` |
| Fresh semantic judgment | `coding-feature-evaluator` |
| Queue continuation | `coding-autonomous-execute` |
| Queue schema/status | `coding-feature-queue` |
| Run containment/artifacts | `proof_run_capture` |

Each procedure lives at its owner. Prompts and other documents route rather than restate it.

## Deliberate Tradeoffs
- Fresh evaluation after every supported repair can lengthen difficult features; the user selected evaluator-confirmed assurance over a fixed review bound.
- One fresh preflight adds implementation-entry latency to tracked and autonomous work; its bounded contract-only scope targets later contract/proof repair loops without duplicating final evaluation.
- Rerunning executable proof replaces freshness hashes and dependency graphs.
- Plain retained attempts replace receipts, progress scores, managed completion notes, and evidence schemas.
- Serial execution removes coordination overhead and moving-checkout ambiguity.
- No historical proof sweep gates feature completion; each proof must honestly own the feature claim.

## Threat Boundary
Resists accidental hallucination, rationalization, lost failures, proof weakening, architecture bypass, and shallow green evidence.

It is not a secure trust root against an agent rewriting both implementation and proof dishonestly. Hard kill, host crash, or deliberately detached descendants can escape cleanup; proof runners may not detach.
