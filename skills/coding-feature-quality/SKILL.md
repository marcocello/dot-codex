---
name: coding-feature-quality
description: "Review FEATURE_DIR/FEATURE.md and FEATURE_DIR/PROOF.md before non-trivial implementation for ambiguity, edge cases, testability, proof quality, and architecture conflicts without adding framework phases."
metadata:
  short-description: Lightweight feature and proof review
---

# Contract Readiness Review

Purpose: decide whether a `FEATURE.md` + `PROOF.md` contract package is ready to drive
implementation.

## Workflow
1) Read the contracts
   - Treat `FEATURE_DIR/FEATURE.md` as the behavior description.
   - Treat `FEATURE_DIR/PROOF.md` as the completion proof contract when it exists.
   - Read `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md` when present.

2) Scan for quality gaps
   - Ambiguity: unclear actors, terms, outcomes, constraints, or unresolved assumptions.
   - Edge cases: missing error, empty, boundary, permission, concurrency, and recovery cases.
   - Testability: behavior that cannot be checked through public boundaries or deterministic tests.
   - External contract: missing API, CLI, file, event, provider, or UI-boundary contract
     where consumers need stable inputs, outputs, statuses, states, schemas, or messages.
   - Resolution rules: missing defaults, fallbacks, precedence, version-selection,
     conflict-handling, or selection logic where multiple interpretations are plausible.
   - Semantic invariants: duplicate prevention, routing, classification, extraction,
     permissions, intent handling, or similar behavior defined only by example phrases
     instead of structured decision rules.
   - Operational constraints: missing runtime, deployment target, storage, credentials,
     environment, or resource assumptions that affect implementation correctness.
   - Proof quality: missing primary proof command, primary proof not wrapped with
     `scripts/proof_run_capture`, missing declared `--source-path` inputs whose freshness authorizes completion, missing proof scope, weak evidence, mock-only proof for
     user-visible behavior, undeclared false-green risks, or provider writes without read-back.
   - Boundary mismatch: proof calls an inner worker, service, or helper while the behavior is
     really triggered by persisted state, queue polling, scheduler pickup, webhook delivery,
     CLI invocation, API routing, or another public activation path.
   - Activation coverage mismatch: `FEATURE.md` claims multiple producer classes or real
     system paths, but `PROOF.md` exercises only the new inner component, service, executor,
     or helper. Contract review must fail unless the feature is explicitly scoped to that
     inner boundary or the uncovered producer class is recorded as a manual gap/readiness blocker.
   - Fake boundary ambiguity: missing `Claimed Behavior Coverage` or unclear fake boundary
     ledger for non-trivial proofs that use mocks, fakes, monkeypatches, fake subprocesses,
     fake providers, or fake browser/API clients.
   - Architecture conflicts: behavior that violates authoritative repo architecture or layer rules.

3) Decide what to do
   - If feature gaps materially affect scope or correctness, update `FEATURE_DIR/FEATURE.md` before implementation or ask only the blocking question.
   - If proof gaps materially affect completion, use `coding-proof-author` before implementation.
   - If gaps are minor, record the assumption directly in `FEATURE.md` or `PROOF.md` and continue.
   - For larger brownfield changes, optionally create or update `FEATURE_DIR/notes.md`.

4) Keep the workflow lightweight
   - Do not create Spec Kit or OpenSpec command phases.
   - Do not create `.specify/`, `openspec/`, or another orchestration root.
   - Keep behavior in `FEATURE.md`.
   - Keep proof detail and executable proof artifacts under `FEATURE_DIR/PROOF.md`, `FEATURE_DIR/proof/`, or the repo's established testbed/E2E location.

## Output
- `Contract review: PASS` when `FEATURE.md` and `PROOF.md` are ready for implementation.
- `Contract review: FAIL` when material ambiguity, proof weakness, architecture conflict, or
  testability gaps must be repaired before implementation.
- `Contract review: NEED_INPUT` when a missing product decision, environment constraint,
  or unavailable source prevents a reliable contract review after local recovery attempts.
- Include findings only when there are material gaps.

## Rules
- Stay within the single `FEATURE_DIR` workflow.
- `FEATURE.md` remains the behavior description.
- `PROOF.md` remains the completion authority.
- Gate remains the repo-health guard, not the feature proof.
- This is the contract-readiness reviewer, not the completed-implementation evaluator.
