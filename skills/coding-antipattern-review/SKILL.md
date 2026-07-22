---
name: coding-antipattern-review
description: "Review code, architecture, runtime, tests, proof, and function maintainability for evidence-backed anti-patterns. Use for recurring smells, fragile boundaries, false confidence, readability problems, or suspected practices needing false-positive checks."
---

# Anti-pattern Review

Purpose: identify harmful recurring practices without turning a catalog match, scanner alert, or style preference into a finding.

Read-only unless the user separately requests remediation.

## Inputs
- Repository, component, paths, or review question.
- Optional suspected patterns, incidents, failing behavior, performance concern, or test/proof weakness.
- Repository architecture, conventions, testing rules, and native analysis tools.

Determine the requested depth before scanning broadly. Review the smallest surface that can answer the question.

## Workflow
1. Bound the review
   - Read `AGENTS.md` and relevant app/architecture/convention/testing docs.
   - Map only the modules, state owners, I/O boundaries, runtime paths, and proof surfaces needed.
   - Confirm review-only versus requested implementation.

2. Select relevant lenses
   - Do not load every catalog by default.
   - Use Lens Routing below.

3. Generate candidates
   - Use repository-native linters, analyzers, tests, metrics, history, and runtime evidence before proposing new tooling.
   - Treat scanner/catalog output as candidate generation only.

4. Challenge each candidate
   - Trace callers, state, configuration, tests, runtime behavior, and ownership.
   - Search for the strongest counterexample or intentional constraint.
   - Reject candidates that are bounded composition roots, generated code, adapters, trust-boundary duplication, protocol requirements, or deliberate isolation.

5. Classify
   - `Confirmed`: evidence establishes the violated invariant and credible consequence.
   - `Suspected`: shape exists, but one material fact is missing.
   - `Rejected`: context or counter-evidence makes it intentional or harmless.

6. Prioritize
   - Rank by user/system impact, likelihood, breadth, and remediation risk.
   - Explain consequence before naming the pattern.
   - Recommend the smallest correction that restores the invariant.

## Lens Routing
Read only what the request needs:

- Code, responsibility, state, error handling, abstractions -> [code-and-design.md](references/code-and-design.md).
- Distributed/runtime/persistence/reliability/performance -> [architecture-and-runtime.md](references/architecture-and-runtime.md).
- Tests, mocks, fixtures, and proof false confidence -> [tests-and-proof.md](references/tests-and-proof.md).
- External catalogs and maintained sources -> [sources.md](references/sources.md) when attribution matters.
- Detailed finding records -> [finding-schema.md](references/finding-schema.md) for broad or formal reviews.

## Function Maintainability Lens
Use when the request concerns readability, verbosity, tangled functions, or safe refactoring.

1. Select critical, high-churn, high-defect, or high-fan-in/out functions. Do not inventory every function by default.
2. Inspect:
   - intent clarity from name/signature;
   - single responsibility and abstraction level;
   - nesting, branch count, guard clarity;
   - hidden mutation and side effects;
   - argument shape, boolean modes, primitive policy;
   - error semantics and broad catches;
   - duplicated setup or control-flow skeletons;
   - focused testability.
3. Classify verbosity:
   - `Lean`: each block serves behavior or explicit safety.
   - `Acceptable`: some ceremony, still predictable and readable.
   - `Bloated`: repeated scaffolding, unjustified defense, mixed concerns, or indirection obscures behavior.
4. Report only functions whose shape creates a concrete defect risk, delivery cost, or unsafe change boundary.

## Evidence Rules
- Require an exact file, component, command, trace, metric, test, history, or data-flow path.
- Distinguish observed fact, inference, and unknown.
- Static-analysis hit does not prove exploitability, runtime impact, or architectural intent.
- Famous pattern name does not prove harm.
- Style preference, framework disagreement, or hypothetical scale is not a finding without consequence.
- Check false-positive pressure explicitly: what evidence would make this pattern acceptable here?
- Preserve behavior unless the user requested a behavior change.

## Output
For compact reviews:

```text
Findings:
- P1|P2|P3 | Confirmed|Suspected | evidence | consequence | counter-evidence | smallest correction | confidence
Rejected candidates:
- <candidate + why rejected>
Validation: <checks needed before/after repair>
Unknowns: <material only>
```

For function findings, include purpose, current shape, verbosity classification, primary issue, rewrite direction, and test impact.

## Boundaries
- This is not a complete security audit.
- Do not copy external catalogs into the response.
- Do not prescribe a replacement pattern without repository fit.
- Do not infer systemic impact from one isolated example unless it crosses a critical boundary.
- Do not apply remediation during review-only work.
- Route a clear defect to `coding-repair`; route accepted behavior/architecture changes through the feature lifecycle.

## Handoff
Lead with confirmed findings and strongest counter-evidence checks. Include suspected candidates only when the missing fact is actionable. Prefer fewer high-confidence findings over a noisy catalog dump.
