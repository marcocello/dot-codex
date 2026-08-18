# Harness Design

## Objective

Turn product input of any maturity into accepted, lean behavior and then deliver it through realistic evidence. Optimize for fewer user corrections and working outcomes, not artifact volume or internal ceremony.

## Seven Pillars

1. **Understand before producing.** Investigate the user, purpose, benefit, current repository, and material uncertainty before creating artifacts.
2. **Questions deepen understanding without becoming ceremony.** Ask focused grouped questions when answers can materially clarify or expand the problem, user implications, product, architecture, safety, cost, or proof. Continue across turns when answers expose consequential new unknowns; resynthesize after each round and stop on decision readiness rather than a fixed round count.
3. **Enrich without speculative scope.** Classify adjacent capabilities as current behavior, prerequisites, follow-ups, alternatives, or unrelated. Only accepted decisions expand scope; use a small future seam only when it prevents foreseeable rework.
4. **Record lean authority.** Create `APP.md`, `ARCHITECTURE.md`, feature packages, and queues only when they own durable decisions. Keep exploration and rejected ideas in conversation.
5. **Prefer simple modular architecture.** Separate real responsibilities and durable ownership while avoiding abstractions, orchestration, and documents created only for hypothetical flexibility.
6. **Prove the real lifecycle.** Exercise the public activation and consumer read-back, including relevant existing state, reopen/restart behavior, failures, affected consumers, and the actual runtime target. A fresh isolated environment proves source, not an already-running app.
7. **Own truthful completion.** One parent completes one feature before selecting the next and drives it through implementation, proof, repair, and fresh evaluation. When an existing runtime is the named consumption target, source proof is intermediate and cannot produce `done`.

## Flow

```text
input
  -> investigate and clarify material choices
  -> classify adjacent outcomes
  -> write only earned product, architecture, feature, and proof authority
  -> for sensitive work, fresh preflight
  -> implement and capture realistic proof
  -> fresh final review
  -> repair and repeat when needed
  -> truthful source/active-runtime handoff
```

Product input of any maturity or cardinality routes to `coding-product-partner`, which adapts investigation and artifact depth to uncertainty and consequence. Contract authoring stops before implementation unless implementation was explicitly requested.

## Independent Challenge

For sensitive work, `coding-feature-review` preflight mode receives verbatim goal and correction excerpts before implementation. Parent paths are an entry point, not a scope ceiling: the reviewer independently follows relevance-bounded current authority, state, affected consumers, persistence, runtime, and interactions. It returns all supported material findings in one pass and has no implementation or completion authority.

After realistic proof passes, `coding-feature-review` final mode is evidence-first and implementation-second. The parent's transient changed-file surface is an entry point, not a scope ceiling. The reviewer follows relevance-bounded authority and consumers, returns all supported material findings, and checks contract mismatch, architecture bypass, missing real usage states, environment mismatch, and central false greens. Supported findings strengthen proof, drive repair, require a complete proof rerun, and receive another fresh review.

## Completion Integrity

Realistic proof and final-review `PASS` apply only to the unchanged final candidate. Relevant edits make both stale. Retained attempt generation and the narrow queue completion write are bookkeeping, not candidate changes. Rerunning executable proof replaces freshness hashes, receipts, dependency graphs, commit pins, worktrees, and coordination machinery.

When an existing local or deployed runtime is the named consumption target, the queue cannot record `done` until that exact runtime passes. Safe local activation continues autonomously. `Source proven; activation required` is an intermediate or blocked handoff; deployment and other approval-risk actions remain approval-gated.

## Ownership

| Concern | Owner |
| --- | --- |
| Routing, lanes, safety, completion truth | `AGENTS.md` |
| Product and architecture shaping | `coding-product-partner` |
| Proof design and real usage states | `coding-proof-author` |
| Implementation and repair loop | `coding-feature-execute` |
| Preflight and final semantic judgment | `coding-feature-review` |
| Queue continuation and state | `coding-autonomous-execute`, `coding-feature-queue` |
| Run containment and retained output | `proof_run_capture` |

Each procedure lives at its owner. Other files route or explain; they do not restate full workflows.

## Threat Boundary

The harness reduces hallucinated intent, speculative scope, proof weakening, lost failures, architecture bypass, stale evidence, environment confusion, and shallow green results. It is not a formal correctness proof or a secure trust root against deliberate self-deception. Host crashes and deliberately detached descendants may escape cleanup; proof runners may not detach.
