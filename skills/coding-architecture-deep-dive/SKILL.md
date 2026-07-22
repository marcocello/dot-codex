---
name: coding-architecture-deep-dive
description: "Assess one component's architecture, logic, implementation risks, bottlenecks, and tradeoffs before refactoring or reliability, performance, scaling, and migration decisions. Also compare the current design against a concrete reference when provided."
---

# Architecture Deep Dive

Purpose: produce a precise, evidence-based architectural assessment for one component or one current-versus-reference decision.

Read-only unless the user separately asks for implementation.

## Inputs
Required or inferable:

- component scope: service, module, package, path, workflow, or system slice;
- decision goal: simplicity, reliability, latency, throughput, scale, cost, maintainability, migration;
- current contracts and architecture decisions;
- constraints, rejected directions, and non-goals.

Useful when available:

- reference design or implementation;
- SLO/SLA and workload shape;
- incidents, regressions, traces, profiles, metrics;
- deployment topology and operational constraints.

Infer from repository artifacts first. Ask only when a missing answer can change the architectural decision.

## Workflow
1. Establish authority
   - Read `AGENTS.md`, feature/app contracts, architecture, conventions, testing, and relevant runtime/deployment docs.
   - Treat accepted goals, constraints, and non-goals as the comparison frame.
   - Distinguish actors/authority from procedure, document, or module ownership.

2. Map the component
   - Define inputs, outputs, state, data flow, dependencies, entrypoints, external boundaries, and failure paths.
   - Identify synchronous/asynchronous transitions, queues, locks, caches, persistence, and provider calls.
   - Note coupling, cycles, fan-in/fan-out, and lifecycle ownership.

3. Inventory decisions and assumptions
   - Identify choices affecting performance, reliability, security, operability, evolvability, testability, or cost.
   - Separate explicit decisions from accidental implementation shape.
   - Record assumptions that need workload/runtime evidence.

4. Analyze flaws and limits
   - Architecture: boundary leaks, wrong abstraction, coupling, shared ownership, hidden topology.
   - Logic: broken invariant, state-transition gap, concurrency race, retry/idempotency error.
   - Implementation: duplicated policy, unsafe error handling, synchronous choke point, unbounded work.
   - Operations: missing timeout, backpressure, observability, rollback, recovery, capacity limit.
   - Tie every finding to a concrete failure mode or maintenance consequence.

5. Analyze performance when relevant
   - Define the workload and metric before claiming a bottleneck.
   - Decompose CPU, I/O, serialization, network, database, lock/queue, cache, and provider time.
   - Look for N+1 work, unbounded fan-out, retry storms, cache stampede, hot locks, repeated parsing, or large copies.
   - Use measurements when available; label code-path estimates as inference.

6. Recommend
   - Prefer the smallest change that restores the violated boundary or quality attribute.
   - Include impact, likelihood, effort, migration risk, rollback, and validation.
   - Do not recommend broad refactoring for style or theoretical future scale.

## Reference Comparison
When the user supplies a concrete reference:

1. Normalize both designs across components, data flow, state, failure behavior, performance, operations, testability, and cost.
2. Identify identical behavior, material differences, and hidden assumptions.
3. Judge the reference against current accepted goals; do not assume newer or external means better.
4. Decide:
   - `KEEP`: current design fits better or differences do not justify migration.
   - `PARTIAL ADOPT`: adopt specific mechanisms while preserving current boundaries.
   - `REPLACE`: reference direction materially better and migration risk is justified.
5. For non-`KEEP`, state what changes, what stays, ordered migration, compatibility risk, rollback, and proof.

Do not recommend an explicit non-goal or rejected direction without new evidence that invalidates the earlier decision. Record the tradeoff instead.

## Evidence Rules
- Use exact paths, call/data flow, configuration, tests, traces, logs, or metrics.
- Separate observed fact, supported inference, and unknown.
- State confidence for each material finding.
- Do not convert a pattern name or reference preference into evidence.
- Do not claim capacity or latency limits without workload assumptions.
- Check counter-evidence that may make an apparent flaw intentional and bounded.

## Output
```text
Scope: <component and goal>
Findings:
- P0|P1|P2|P3 | evidence | root cause | impact | smallest correction | confidence
Decision: <none|KEEP|PARTIAL ADOPT|REPLACE>
Tradeoffs: <material only>
Migration: <none|ordered steps>
Validation: <focused proof/benchmark/checks>
Unknowns: <blocking only>
```

## Rules
- Findings first, ordered by impact.
- No generic architecture advice.
- No mandatory framework or pattern replacement.
- No backward-compatibility work unless required by user or authoritative contract.
- No implementation edits during review-only work.
- Route a clear defect to `coding-repair`; route accepted structural change through the normal feature lifecycle.

## Handoff
Lead with the decision and highest-impact evidence. Keep the remediation staged and testable. Ask for input only when one missing product/workload/operational fact can change the decision.
