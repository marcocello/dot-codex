# Proof Scope

Passing command useful only when scenario matches claim.

## Risk Selection
Before choosing scenarios, identify the most plausible way the proof could pass while the real user or production consumer remains broken. Select only pressures relevant to the feature:

- allowed-size or admitted-volume boundaries;
- existing persisted states, migration, rollback, and idempotency;
- restart, recovery, cancellation, and concurrency;
- health and responsiveness during slow or blocking work;
- provider-native variability and real integration topology;
- permissions, precedence, and multi-owner state transitions;
- UI interaction topology, not only final appearance;
- compatibility read-back through affected consumers.
- exact consumption target: isolated source candidate, existing local runtime, or deployed runtime.

Do not turn this into a universal checklist. Use the smallest scenario set that attacks the central plausible failures and state honest gaps for important pressure that cannot be executed safely.

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
- Operational pressure matches admitted behavior and relevant production state.
- Existing consumers and interaction topology remain compatible when the feature claims preservation.
- Persisted configuration is read back after the relevant refresh, remount, close/reopen, or restart; a successful write response alone is not persistence proof.
- Proof against a fresh isolated runtime is intermediate source proof when an existing runtime is the named consumption target; it cannot produce `done` until that exact target is validated.
- Sampling/threshold explicit for probabilistic behavior.

## Weak Proof
- File exists for behavior claim.
- Source assertion for runtime claim.
- Mock replaces claimed boundary.
- Inner helper bypasses route/worker/browser/CLI/scheduler.
- Assistant prose replaces persisted/provider/rendered state.

Green + weak: return to user proof discussion. Evaluator never fills missing executable evidence with confidence.
