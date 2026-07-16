---
name: coding-antipattern-review
description: Review a codebase for recurring anti-patterns and failure-prone smells across design, runtime behavior, tests, and proof, with evidence and false-positive checks.
---

# Anti-pattern Review

Perform a read-only, evidence-first review. Treat every catalog match or tool alert as a candidate until repository evidence establishes the violated invariant, concrete failure mode, and affected scope.

## Workflow

1. Bound the review.
   - Identify the requested repository, component, paths, and review goal.
   - Read `AGENTS.md` and available app, architecture, convention, and testing docs.
   - Determine whether the user wants review-only output. Do not implement remediation unless explicitly asked.

2. Build the system map needed for the review.
   - Identify major modules, dependency directions, state owners, I/O boundaries, runtime paths, and proof surfaces.
   - Inspect repository-native linters, analyzers, tests, metrics, and operational evidence before proposing new tooling.

3. Select only relevant lenses.
   - Read `references/code-and-design.md` for module, function, dependency, state, and error-handling candidates.
   - Read `references/architecture-and-runtime.md` for distributed-system, persistence, reliability, and performance candidates.
   - Read `references/tests-and-proof.md` for test-suite and verification candidates.
   - Read `references/sources.md` when grounding a candidate in an upstream catalog or executable rule corpus.

4. Gather and challenge evidence.
   - Trace each candidate across callers, tests, configuration, runtime behavior, and ownership boundaries.
   - Search for the strongest counterexample or design constraint that would make the apparent smell intentional.
   - Use static-analysis output as candidate-generation evidence only. Confirm the behavior in the reviewed repository.
   - Do not infer systemic impact from one isolated example unless the example crosses a critical boundary.

5. Classify the candidate.
   - `Confirmed`: repository evidence establishes the invariant violation and credible failure mode.
   - `Suspected`: the shape is present, but runtime, ownership, or intent evidence is incomplete.
   - `Rejected`: counter-evidence or context shows the pattern is intentional, bounded, or harmless.
   - Report confirmed findings first. Include suspected candidates only when the missing evidence is material and actionable.

6. Prioritize and route.
   - Rank by user/system impact, likelihood, breadth, and remediation risk, not by famous pattern name.
   - Prefer the smallest remediation that restores the violated invariant.
   - Route implementation to `coding-maintainability-review` for clarity and boundary refactors, `coding-architecture-deep-dive` for structural or performance analysis, `coding-operational-issue-diagnostics` for live runtime investigation, or `coding-repair` for a clear defect.

## Evidence Rules

- Require an exact file, component, command output, trace, metric, test, or data-flow path for every finding.
- Explain the behavior or maintenance consequence before naming the anti-pattern.
- Distinguish observed fact, supported inference, and unknown.
- Do not report style preference, framework convention disagreement, or theoretical scale risk as an anti-pattern without a concrete consequence.
- Do not claim that a scanner proves exploitability, runtime impact, or architectural intent.
- Do not prescribe a pattern merely to replace an anti-pattern; show why the proposed direction fits this repository.
- Use `references/finding-schema.md` for evidence records and final output.

## Review Boundaries

- Keep security coverage to supported secure-design invariants and existing scanner evidence; do not present this skill as a complete security audit.
- Keep language-specific catalog entries subordinate to current language and framework documentation.
- Avoid copying upstream catalogs into the response. Cite the precise upstream source only when it materially supports a finding.
- Preserve existing behavior unless the user explicitly requests a behavior change.

## Example Triggers

- "Find the anti-patterns in this service and show which ones are actually harmful."
- "Audit this architecture for retry storms, chatty I/O, and shared-state problems."
- "Review these tests for test smells and false confidence."
- "Which recurring bad practices are making this codebase fragile?"
