# Harness Operator Map

This document maps ownership. Operational detail belongs in the linked contract, skill, or script rather than being repeated here.

## Assurance Lanes

Choose one lane before work begins; `AGENTS.md` owns the authoritative definitions and completion bars.

- `lightweight`: isolated low-risk work; focused regression or narrow check.
- `tracked`: behavior-contract or higher-risk work; captured proof, gate, evaluator.
- `autonomous`: tracked work plus persistent recovery and queue state.

## Current Harness Workflow

Tracked delivery follows one compact state flow:

```text
FEATURE.md -> PROOF.md -> realistic proof -> evidence bundle -> repair loop -> gate -> evaluator -> queue done
```

If implementation exposes a wrong contract, enter contract repair, explain the revision, establish strengthened red evidence when practical, then resume. Final evidence must match the revised contracts, runner, and declared sources.

## Plain Inner And Outer Loops

The inner loop performs one feature or issue and records useful behavioral evidence. The outer loop reviews evidence later and separates local project lessons from reusable harness lessons.

```text
Inner loop: do the work -> prove it -> record useful evidence.
Outer loop: read the evidence -> find repeated patterns -> route the lesson to the right owner.
```

The inner loop is feature proof satisfaction. The outer loop is harness improvement from repeated evidence.

A Codex Goal may keep an autonomous run moving, but it is runtime state only. It does not replace contracts, proof output, the gate, evaluator judgment, or queue state.

## Responsibility Map

- `AGENTS.md`: assurance lanes, permissions, routing, completion invariants, handoff class.
- `coding-feature-spec`: intent to observable behavior contract.
- `coding-proof-author`: behavior contract to executable proof and anti-gaming pressure.
- `coding-feature-quality`: pre-implementation contract readiness.
- `coding-feature-execute`: tracked feature implementation.
- `coding-repair`: concrete defect or failing check under the inherited assurance lane.
- `coding-autonomous-execute`: persistent tracked execution and recovery.
- `coding-feature-evaluator`: skeptical done judgment for tracked and autonomous work.
- Harness docs: durable rationale, schemas, examples, and safety detail.
- Repository scripts: deterministic evidence, receipt, queue, and lint enforcement.

Shared completion, permission, and lane rules belong in `AGENTS.md`. Skills reference those rules and add only local decisions. Deterministic conditions belong in scripts.

## Target Repo Autonomy

- Autofix repairs a concrete target-repo failure and reruns the inherited completion checks.
- Autosuggestions turn evidence into proposed repo improvements without silently broadening scope.
- Auto-improve converts an accepted suggestion into ordinary feature, proof, repair, readiness, or queue work.

Harness self-improvement is separate. Promote a failure to harness evolution only when repeated evidence shows the harness itself allowed the pattern.

## Canonical Contracts

- Proof lifecycle, evidence bundles, revision identity: [`proof-lifecycle.md`](proof-lifecycle.md).
- Proof scope and false-green risk: [`oracle-scope.md`](oracle-scope.md).
- Target-repo autonomy: [`repo-autonomy.md`](repo-autonomy.md).
- Persistent recovery and `NEED_INPUT`: [`autonomous-execution.md`](autonomous-execution.md).
- Destructive proof approval: [`destructive-proof-allowlist.md`](destructive-proof-allowlist.md).
- Human receipts: [`handoff.md`](handoff.md).
- Memory boundaries: [`memory-policy.md`](memory-policy.md).
- Harness evolution: [`evolution/evolution-loop.md`](evolution/evolution-loop.md).

## Deterministic Helpers

- `scripts/proof_run_capture`: capture the primary proof and revision-bound evidence.
- `scripts/record_completion_evidence`: persist gate and evaluator receipts beside proof evidence.
- `scripts/validate_proof_bundle`: validate serious evidence shape and agent-observation requirements.
- `scripts/validate_feature_queue --feature <id>`: validate one active feature from current artifacts.
- `scripts/validate_feature_queue --all`: strict whole-queue audit.
- `scripts/harness_review`: summarize evidence and validate evolution manifests.
- `scripts/gate_config`: validate this dot-codex configuration.

## Harness Evolution

Harness changes should start from repeated observed failure, not model preference:

```text
observed failure -> failure pattern -> change manifest -> harness change -> verification -> accepted or rejected pattern
```

The manifest records before evidence, predicted fixes, predicted regressions, held-out checks, after evidence, rollback plan, and verdict basis. This keeps changes falsifiable and rollbackable.

## Current Limits

- Application-specific proof still needs domain-owned screenshots, provider read-back, logs, fixtures, or testbeds.
- Live validation still depends on credentials, safe targets, external services, and approval for risky actions.
- `scripts/harness_review` summarizes evidence; it does not independently authorize or apply improvements.
- Queue completion enforcement applies only where repositories adopt the documented queue and evidence contracts.

Non-coding operating workflows live in [`docs/secondbrain.md`](../secondbrain.md) and the `second-brain-*` skills.
