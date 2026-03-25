---
name: maintainability-review
description: Review a full codebase for verbosity, tangled responsibilities, weak module boundaries, and readability debt; produce prioritized improvements that make code lean and clear for humans. Use when users ask for maintainability audits, code simplification, structure review, refactor planning, or “make this codebase cleaner/less intertwined.”
---

# Maintainability Review

Review for clarity-first maintainability. Minimize accidental complexity, reduce cognitive load, and recommend the smallest high-impact changes. Treat function-writing quality as a first-class review axis.

## Workflow
1. Scope the review.
- Read repository layout, tech stack, and architecture docs if present.
- Confirm whether the user wants review-only output or implementation + tests.

2. Build a structural map.
- Identify domains, layers, and dependency directions.
- Flag cross-layer imports, cycles, and over-centralized modules.

3. Audit code at module and function level.
- Measure readability risk: long functions, deep nesting, boolean branching chains, mixed abstraction levels, and duplicated logic.
- Detect intertwined concerns: domain + IO in one function, validation mixed with persistence, orchestration mixed with transformation.
- Check naming clarity, argument shape, side effects, and error handling consistency.
- Score function-writing quality with the Function Deep-Dive Checklist.

4. Run function deep-dive on critical paths.
- Prioritize high-churn, high-defect, and high-fan-in/out functions first.
- For each target function, assess:
  - intent clarity from name and signature
  - single-responsibility fit
  - abstraction consistency (policy vs mechanics mixed together)
  - control-flow complexity (nesting depth, branch count, early-return hygiene)
  - state mutation and side-effect visibility
  - argument design (primitive obsession, boolean flags, overloaded params)
  - error semantics (silent failures, broad catches, leaked low-level errors)
  - verbosity quality (essential detail vs incidental ceremony)
- Classify verbosity as:
  - Lean: concise and expressive; no repeated ceremony
  - Acceptable: mildly verbose but readable and predictable
  - Bloated: repetitive, indirect, or over-defensive without risk reduction

5. Evaluate test signal and safety.
- Verify whether behavior-critical paths are protected by focused tests.
- Flag refactor risk where code is fragile and test coverage is missing.

6. Produce a prioritized improvement plan.
- Rank findings by impact and effort.
- Propose concrete refactors as small, composable steps.
- Include at least one fast-win change and one structural change.

7. Suggest implementation order.
- Sequence changes to preserve behavior and reduce risk.
- Tie each change to validation strategy (tests, smoke checks, gate commands).

## Review Heuristics
- Prefer explicit and boring over clever and dense.
- Prefer small pure functions for transformation-heavy code.
- Prefer single-responsibility modules with stable interfaces.
- Prefer dependency direction from high-level orchestration to low-level utilities, never the reverse.
- Prefer deletion and consolidation over adding wrappers when wrappers do not remove complexity.

Use this rubric file when needed: `references/review-rubric.md`.

## Function Deep-Dive Checklist
For each function reviewed, report:
- `Purpose`: one-sentence behavioral intent.
- `Current Shape`: inputs/outputs, side effects, and branch profile.
- `Verbosity Assessment`: Lean / Acceptable / Bloated + why.
- `Primary Issues`: maximum 3 highest-impact issues.
- `Rewrite Direction`: the smallest safe rewrite strategy.
- `Test Impact`: tests needed before/after refactor.

## Output Contract
Return results in this exact section order:
1. `Findings`
2. `Function Deep Dive`
3. `Refactor Plan`
4. `Validation Strategy`
5. `Open Questions`

For `Findings`:
- Order by severity then confidence.
- Include file paths and focused line references whenever possible.
- Describe risk in behavior and maintainability terms.

For `Function Deep Dive`:
- Include 3-10 critical functions (depending on codebase size).
- Use one compact block per function containing:
  - function name + location
  - purpose and signature quality
  - verbosity classification
  - complexity symptoms
  - concrete rewrite direction

For `Refactor Plan`:
- Provide minimal change sets with rationale.
- Mark each step as `Quick Win`, `Medium`, or `Structural`.
- Estimate risk and expected readability impact.

For `Validation Strategy`:
- List tests to add/update before large refactors.
- Prefer narrow tests first, then broader project checks.

## Constraints
- Avoid style-only churn unless it directly improves readability.
- Avoid broad rewrites unless structural flaws justify them.
- Preserve existing behavior unless user requests behavior changes.
- Reuse existing project patterns unless those patterns are the core issue.

## Example Triggers
- "Review this backend and tell me how to make it leaner."
- "This code is verbose and intertwined. Give me a cleanup plan."
- "Audit functions and module structure for maintainability."
- "Find where responsibilities are mixed and propose better boundaries."
