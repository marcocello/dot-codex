# Code and Design Lenses

Use these entries as candidate lenses, not automatic findings. Confirm an observable consequence and reject the candidate when repository context makes the structure intentional and bounded.

## Responsibility and boundary candidates

### Mixed responsibility

- Signal: one unit owns unrelated policy, transformation, persistence, transport, or presentation decisions.
- Confirm with: independent reasons to change, cross-layer dependencies, fragile tests, or repeated partial edits.
- Reject when: the unit is a small composition root whose explicit job is orchestration.

### Divergent change and shotgun surgery

- Signal: one concept changes for many unrelated reasons, or one behavior change requires edits across scattered owners.
- Confirm with: version history, repeated coordinated edits, duplicated policy, or missed-change regressions.
- Reject when: generated code, protocol adapters, or intentionally duplicated isolation boundaries require synchronized shapes.

### Feature envy and inappropriate intimacy

- Signal: a unit primarily manipulates another unit's internal data or depends on unstable implementation details.
- Confirm with: accessor chains, private-shape knowledge, change coupling, or abstraction leakage.
- Reject when: the code is an explicit adapter translating between stable contracts.

### Generic dumping ground

- Signal: `utils`, `helpers`, manager, service, or base modules accumulate unrelated responsibilities and high fan-in.
- Confirm with: unrelated imports, naming that hides ownership, cycles, or frequent conflicts.
- Reject when: the module is a small, cohesive standard-library-style utility surface.

## Control and state candidates

### Boolean-mode or primitive-driven policy

- Signal: flags, strings, or loosely typed primitives secretly select distinct behavioral modes.
- Confirm with: branch multiplication, invalid combinations, unclear call sites, or repeated validation.
- Reject when: the value belongs to a closed protocol or enum and the branches remain small and exhaustive.

### Hidden global state

- Signal: behavior depends on mutable singleton, ambient context, process state, import order, or implicit configuration.
- Confirm with: order-dependent tests, concurrency risk, surprising callers, or difficult isolation.
- Reject when: the state is immutable after startup and has one explicit lifecycle owner.

### Temporal coupling

- Signal: valid behavior requires undocumented call ordering or partially initialized objects.
- Confirm with: state-transition gaps, defensive `None` checks, lifecycle bugs, or order-sensitive tests.
- Reject when: the ordering is enforced by a type, transaction, state machine, or framework lifecycle contract.

### Speculative abstraction

- Signal: indirection, configuration, extension points, or wrappers exist for hypothetical variation and obscure current behavior.
- Confirm with: one implementation, no current variation pressure, navigation cost, or repeated pass-through layers.
- Reject when: a real external boundary, test seam, compatibility contract, or near-term supported variant owns the abstraction.

## Error and data-flow candidates

### Swallowed or flattened errors

- Signal: broad catches, generic fallback values, logging-and-continuing, or one undifferentiated error channel hides failure semantics.
- Confirm with: false success, missing rollback, untraceable incidents, or callers unable to choose recovery behavior.
- Reject when: the boundary deliberately converts lower-level errors into a documented stable contract while preserving observability.

### Duplicated policy

- Signal: the same business decision or validation rule is encoded in multiple places with slight variation.
- Confirm with: inconsistent outcomes, coordinated edits, or one path bypassing the intended owner.
- Reject when: duplication is a deliberate availability, security, or trust-boundary defense with independent validation.

### Leaky abstraction

- Signal: callers must know storage, transport, framework, or vendor mechanics to use a domain capability correctly.
- Confirm with: low-level exceptions, repeated protocol setup, or implementation-driven branching in callers.
- Reject when: the low-level capability is itself the public abstraction and hiding it would remove necessary control.
