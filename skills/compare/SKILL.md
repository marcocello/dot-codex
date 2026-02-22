---
name: compare
description: "Deep-dive compare my architecture/solution vs a provided reference (file/link/SOTA), recommend whether to change, and produce an implementation spec if yes. Read_when You have a draft architecture/solution and want to compare it to a reference and decide whether to migrate."
metadata:
  short-description: Optional user-facing description
---


Input:
- Mine: code / doc / architecture (partial ok)
- Reference: file(s) or link(s)
- Goal: what we optimize for (perf, cost, simplicity, scale, reliability)

If inputs are incomplete, ask only blocking questions (max 3).

Method:
1) Normalize both designs into the same model:
   - components
   - data flow
   - state/storage
   - failure modes
   - performance characteristics
   - operational complexity
   - testability

2) Diff:
   - identical
   - materially different
   - hidden assumptions

3) Decide:
   - KEEP / PARTIAL ADOPT / REPLACE
   - justify with concrete tradeoffs (not vibes)

4) If decision ≠ KEEP, produce a spec:
   - Spec v1 (bullets)
   - What changes (explicit)
   - What stays (explicit)
   - Migration steps (ordered)
   - Compatibility risks
   - Verification plan

Output (STRICT):

## Diff
- ...

## Tradeoffs
- ...

## Decision
- KEEP | PARTIAL ADOPT | REPLACE
- Why:

## Spec (only if change)
- Spec v1:
- Migration:
- Verification: