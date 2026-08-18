# Decomposed Delivery Lifecycle Proof

## Done

- Active routing and inventory expose separate proof-authoring, feature-execution, review, repair, queue, and autonomous-continuation skills.
- One review skill owns risk-triggered preflight and required final review without merging those modes or delivery responsibilities.
- Feature execution owns standard-versus-sensitive assurance classification; autonomous execution remains a continuation mode.
- Final-candidate freshness, proof strengthening and rerun after findings, named-runtime truth, queue completion, and public-boundary proof remain active.
- Affected active tests migrate from retired reviewer names and the complete harness gate remains green.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/decomposed-delivery-lifecycle --timeout-seconds 60 --note "verify decomposed delivery and proportional review"
```

## Scenario: Delivery responsibilities remain separate and discoverable

- Producer/activation: pytest parses `skills.toml`, delivery skill frontmatter and agent metadata, `AGENTS.md`, and current harness design.
- Consumer: Codex proof authoring, implementing one feature, independently reviewing it, repairing a failure, or continuing an accepted queue.
- Read-back: assertions require the separate active skills and reject the retired preflight/evaluator directories and references.
- Fake: none.
- Catches: a single delivery skill, duplicate reviewer authorities, stale routing, or undiscoverable metadata.

## Scenario: Assurance is proportional and operationally owned

- Producer/activation: pytest inspects feature execution, review, and autonomous contracts.
- Consumer: standard feature work, sensitive feature work, and explicit keep-going execution.
- Read-back: structured policy checks require feature execution to classify assurance, sensitive triggers to activate preflight, every material feature to receive final review, and autonomous execution to reuse rather than redefine assurance.
- Fake: none.
- Catches: mandatory preflight for all feature work, no preflight for sensitive work, or treating autonomous execution as a higher-risk tier.

## Scenario: Completion safeguards survive reviewer consolidation

- Producer/activation: pytest inspects execution, review, repair, proof authoring, queue, autonomy, and runtime-completion contracts; mutation canaries hollow each core section in memory.
- Consumer: proof failure, final finding, green-but-broken observation, relevant final edit, isolated source proof, and an existing named runtime.
- Read-back: assertions require proof strengthening, complete rerun, fresh final review, freshness invalidation, and target-valid queue completion.
- Fake: none.
- Catches: a renamed two-heading reviewer that loses evidence-first judgment, repair sequencing, freshness, or runtime truth.

## Scenario: Active compatibility remains green

- Producer/activation: the official feature runner executes focused lifecycle checks, proof-capture subprocess tests, and the complete repository gate.
- Consumer: all active harness mechanics and instruction consumers.
- Read-back: every command exits successfully and retained output reports the actual repository Python runtime.
- Fake: localhost fixture servers remain real local subprocess boundaries.
- Catches: focused policy checks passing while proof capture or another active consumer is broken.

## Scope

Proves:
- The active checkout exposes the accepted decomposed delivery topology, assurance transitions, review modes, and completion safeguards.

Does not prove:
- Deterministic reviewer judgment on every future feature.
- Product-partner behavioral evaluation, which has a separate owner.

False-green risks:
- Static policy checks cannot guarantee semantic compliance, so the fresh final reviewer independently inspects the current contract, evidence, and implementation.

Evidence method:
- deterministic active-surface, mutation-canary, subprocess, and full-gate validation plus fresh semantic final review

Known gaps:
- Reviewer quality remains probabilistic.

## Environment

- Repository-local Python and pytest; no credentials, deployment, paid resources, or external service mutation.
- The full gate uses a temporary localhost fixture server for existing inventory tests.
