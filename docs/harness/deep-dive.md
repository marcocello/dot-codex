# Harness Design

## Objective
Reach user intent autonomously across one or more features. Use realistic feedback to repair code, proof, setup, and architecture without weakening the feature or manufacturing green. Retain useful attempts with minimal harness overhead.

## Pillars
- Intent and decisions: focused questions improve `FEATURE.md` and `PROOF.md`; the LLM records decisions and proceeds without contract-approval gates.
- Real-boundary proof: the LLM chooses activation, consumer, durable or visible read-back, fake boundary, and failure pressure that match the claim.
- Reliable retained attempts: scripts guarantee what ran, how it ran, what returned, and whether mechanical requirements passed.
- Autonomous repair: failures drive the next diagnosis and owning repair across code, architecture, setup, fixtures, diagnostics, or proof.
- Contract and proof integrity: revisions stay aligned with the user goal and cannot narrow behavior or weaken proof merely to pass.
- Fresh completion judgment: a read-only evaluator judges intent, behavior, architecture, proof realism, false-green risk, gaps, and gate outcome.
- Learning without ceremony: attempts, completion notes, evaluator findings, and corrections inform the smallest project, proof, or repeated harness improvement.

Script precision cannot make weak proof realistic.

## Lifecycle
1. Inspect the request, repository context, architecture, related features, and current behavior.
2. Ask a compact set of feature questions only when answers can materially improve the result. Challenge edge cases, state decisions, write `FEATURE.md`, and proceed without requesting contract approval.
3. Discover the real proof boundary. Ask only material proof questions, state activation/read-back/fakes/gaps/timeout, then write `PROOF.md` and `proof/run.sh` without a second approval gate.
4. Mark the package `ready`, invalidate overlapping completed work to `revalidate`, and capture a failing proof before substantial implementation when meaningful.
5. Implement at the owning boundary. On proof, gate, or evaluator failure, inspect the newest evidence, repair the owning problem, and repeat with a changed tactic when evidence does not improve.
6. After realistic proof passes, run a useful repository gate or record a proportionate skip, then spawn a fresh read-only evaluator with the user goal, corrections, and parent-owned change surface.
7. Evaluator `FAIL` returns to repair and a new proof/gate/evaluator cycle. `NEED_INPUT` is valid only for an exact user-owned or external dependency after local recovery. `PASS` permits `done` and the next `ready` feature.

Material unresolved choices about behavior, scope, safety, cost, data, permissions, or external effects still require user input. Approval-risk actions remain separately approval-gated by `AGENTS.md` and platform policy.

## Ownership
| Concern | Owner |
| --- | --- |
| Behavior contract | `coding-feature-spec` |
| Proof contract | `coding-proof-author` |
| Per-feature lifecycle | `coding-feature-execute` |
| Failure repair | `coding-repair` |
| Run containment + artifacts | `proof_run_capture` |
| Semantic judgment | Fresh read-only evaluator subagent |
| Queue continuation | `coding-autonomous-execute` |
| Queue fields + overlap | `coding-feature-queue` |

Each owner contains its procedure. Other files route to it.

## Deliberate Tradeoffs
- Focused user questions and visible decision summaries replace contract-approval and pre-implementation review ceremony.
- Rerun replaces source freshness calculation.
- Plain retained attempts and completion notes replace manifests, hashes, receipts, structured evaluator records, progress scores.
- Fresh evaluator context reduces rationalization; same model/shared filesystem still share bias.
- Multiple feature parents may edit one checkout concurrently. Accountability remains per feature, overlap compares active change prefixes with completed proof dependencies rather than filename categories, and same-feature proof attempts do not compete.
- Overlap invalidation creates a separate `revalidate` backlog. Default build autonomy never consumes it. An explicit proof-only pass either restores `done` after fresh evaluation or moves the feature to `ready` for later repair.

## Threat Boundary
Resists accidental hallucination, rationalization, lost failures, stale related status, shallow proof.

Not a secure trust root against an agent rewriting code + proof. Strong assurance needs protected infrastructure.

Raw output secret redaction and size limits: deferred.

Hard kill, host crash, or deliberately detached process can escape cleanup. Proof runners may not detach or create a new session.
