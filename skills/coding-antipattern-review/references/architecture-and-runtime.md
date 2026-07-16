# Architecture and Runtime Lenses

Use runtime evidence when available. Configuration or topology shape alone rarely proves an operational anti-pattern.

## Communication and load

### Chatty I/O

- Signal: one logical operation performs many sequential network, storage, or process-boundary calls.
- Confirm with: traces, request counts, latency decomposition, N+1 access, or rate-limit pressure.
- Reject when: calls are bounded, parallelized safely, cached appropriately, or required for consistency.

### Synchronous chokepoint

- Signal: independent or slow work is serialized through one blocking dependency or coordinator.
- Confirm with: queue growth, tail latency, thread or worker starvation, or throughput ceilings.
- Reject when: ordering is a required invariant and measured capacity has sufficient headroom.

### Unbounded fan-out

- Signal: one request, event, or retry can create work proportional to uncontrolled input or dependency count.
- Confirm with: missing concurrency limits, explosive queue growth, resource exhaustion, or cascading downstream load.
- Reject when: hard bounds, batching, backpressure, and admission control are enforced at the owning boundary.

### Extraneous fetching

- Signal: callers repeatedly retrieve or materialize substantially more data than they use.
- Confirm with: payload size, memory pressure, query plans, serialization cost, or repeated filtering after fetch.
- Reject when: prefetching measurably reduces total cost or preserves a required snapshot.

## Reliability and recovery

### Retry storm

- Signal: failures trigger synchronized or multiplicative retries without budgets, jitter, backoff, or admission control.
- Confirm with: retry multiplication, elevated downstream load during incidents, repeated side effects, or exhausted timeout budgets.
- Reject when: retries are bounded, idempotent, jittered, observable, and contained within an end-to-end deadline.

### Missing backpressure

- Signal: producers can outpace consumers indefinitely and the system accepts work it cannot finish within its contract.
- Confirm with: unbounded queues, memory growth, stale work, timeout cascades, or overload collapse.
- Reject when: explicit queue limits, load shedding, flow control, or durable capacity planning bounds the backlog.

### Non-idempotent redelivery

- Signal: at-least-once processing or client retries can repeat externally visible effects.
- Confirm with: absent idempotency keys, duplicated writes or charges, or crash windows between effect and acknowledgment.
- Reject when: the effect is naturally idempotent or deduplication is enforced by an atomic owner.

### Single point of failure

- Signal: one component or state owner can stop a critical capability without recovery or graceful degradation.
- Confirm with: topology, recovery procedures, failover evidence, and the actual availability requirement.
- Reject when: the accepted service objective permits the downtime or an independently verified recovery path exists.

## Data and resource ownership

### Busy database

- Signal: application logic, large transformations, contention-heavy coordination, or unrelated workloads accumulate in the database.
- Confirm with: query plans, lock waits, CPU saturation, coupling, or change bottlenecks.
- Reject when: set-based database execution is measured to be the simplest and most efficient owner of the operation.

### Monolithic persistence or shared mutable datastore

- Signal: independently changing domains or services directly mutate the same schema and depend on each other's storage internals.
- Confirm with: cross-domain transactions, migration coordination, ownership ambiguity, or failure coupling.
- Reject when: the system is intentionally monolithic with one deployment and one accountable data owner.

### Cache stampede or unsafe caching

- Signal: popular expiration causes concurrent recomputation, or caching breaks freshness and consistency invariants.
- Confirm with: synchronized misses, origin spikes, stale decisions, or invalidation gaps.
- Reject when: request coalescing, staggered expiry, bounded staleness, and ownership rules address the risk.

### Noisy neighbor

- Signal: one tenant, job, queue, or workload can exhaust shared resources and violate other consumers' service levels.
- Confirm with: shared-limit metrics, missing quotas, starvation, or correlated latency and error spikes.
- Reject when: isolation, fair scheduling, quotas, or reserved capacity enforce the required service objective.
