# Proof Scope

Passing command useful only when scenario matches claim.

## Required
```text
Proves:
- <observed behavior/invariant>

Does not prove:
- <live/scale/timing/provider/UI gap>

False-green risks:
- <broken implementation that may pass>

Evidence method:
- deterministic | probabilistic

Known gaps:
- none | live | manual | scale | timing | provider | environment
```

## Strong Proof
- Real producer/activation/consumer.
- Durable/visible read-back.
- Unsafe outer fake only.
- Central break fails.
- Sampling/threshold explicit for probabilistic behavior.

## Weak Proof
- File exists for behavior claim.
- Source assertion for runtime claim.
- Mock replaces claimed boundary.
- Inner helper bypasses route/worker/browser/CLI/scheduler.
- Assistant prose replaces persisted/provider/rendered state.

Green + weak: return to user proof discussion. Evaluator never fills missing executable evidence with confidence.
