---
name: review-architecture
description: "Review the architecture of a specific codebase component with a state-of-the-art deep-dive method: analyze architectural, logical, and implementation choices to identify weaknesses, flaws, limitations, and performance bottlenecks. Use when precise, evidence-based component assessment is requested before refactoring or scaling decisions."
metadata:
  short-description: Deep component architecture and performance analysis
---

# Review Architecture

Purpose: produce a precise, evidence-based architectural assessment for one component of a codebase.

## Input
- Required:
  - component scope (module/service/package/path)
  - analysis goal (for example: scale, reliability, maintainability, latency)
- Optional:
  - SLO/SLA targets
  - peak load profile
  - known incidents or regressions

If context is incomplete, infer from repository artifacts first and ask only blocking questions.
Subsequent questions are not mandatory; ask them only when direction is unclear or blocked.

## State-of-the-art analysis method
1. Scope and boundary model
   - Define component scope and external boundaries.
   - Map dependencies and coupling (incoming/outgoing, sync/async, data contracts).
   - Detect boundary violations and cyclic dependencies.

2. Decision inventory
   - Extract architectural, logical, and implementation choices that materially affect quality attributes.
   - Record intended tradeoffs and implicit assumptions.

3. Quality attributes assessment (ATAM-inspired)
   - Evaluate impacts on: performance, scalability, reliability, security, operability, evolvability, testability, and cost efficiency.
   - For each choice, rate fitness and highlight constraint violations.

4. Weakness and flaw analysis
   - Identify flaws by category:
     - architectural: layering leaks, wrong abstraction level, high coupling
     - logical: incorrect invariants, state-transition gaps, hidden branching complexity
     - implementative: hot-path inefficiencies, duplicated logic, unsafe concurrency, error-handling gaps
   - Link each flaw to root cause and concrete failure mode.

5. Performance bottleneck analysis
   - Define a benchmark protocol for reproducible measurement (workload shape, concurrency, warm/cold runs, percentile targets).
   - Build latency decomposition (I/O, CPU, memory, lock/queue contention).
   - Inspect hot paths and complexity growth under load.
   - Flag common bottleneck patterns: N+1 queries, unbounded fan-out, synchronous chokepoints, retry storms, serialization overhead, cache stampede.
   - Estimate impact using available evidence (profiling traces, logs, metrics, code-path cost).

6. Security and resilience deep checks
   - Build a focused threat model for the component (entry points, trust boundaries, abuse/failure cases).
   - Inspect degradation and recovery behavior: backpressure, circuit breaking, retry policy, timeout budget, idempotency, and rollback safety.

7. Limitation and risk modeling
   - Identify current scalability ceilings and operational fragility.
   - Produce a simple capacity model (steady-state vs peak, saturation points, queue growth risk).
   - Distinguish known fact vs inference vs unknown.
   - Provide confidence level per finding.

8. Prioritized remediation plan
   - Prioritize by impact x likelihood x implementation effort.
   - Provide minimal, staged actions: immediate stabilization, next hardening, later optimization.
   - Include counterfactual alternatives (why this remediation is preferred over at least one alternative).
   - Include rollback criteria for each high-risk change.

## Output contract
1. Findings first, ordered by severity (P0, P1, P2, P3).
2. Each finding must include:
   - title
   - affected component scope
   - evidence
   - root cause
   - user/system impact
   - recommended change (minimal viable fix)
   - confidence
3. Return a single main section:
   - `## Deep Dive Findings`
4. Keep findings concise and technical. Include only the highest-value evidence and actions.

## Constraints
- Be precise and technical; avoid generic advice.
- Do not report style-only issues without architectural or operational impact.
- Do not prescribe broad refactors unless justified by high-severity risk.
