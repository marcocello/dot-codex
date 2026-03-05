---
name: review-code-architecture
description: Analyze code snippets/files/diffs for architecture quality_ boundary violations, duplication, unnecessary verbosity, and maintainability risks. Use for targeted technical review, not feature implementation.
---

# Review Code Architecture

Purpose: run a focused architecture and maintainability review on a bounded code scope.

## Input
- Required: code snippet, file path, or diff.
- Optional: language/framework, module role, constraints.

If context is missing, infer from code. Ask only blocking questions.

## Checks
1. Boundaries and layering
   - Responsibility separation is clear.
   - Layer crossings are explicit and valid.
2. Duplication
   - Repeated logic/validation/mapping/branching.
   - Copy-paste candidates for extraction.
3. Verbosity and structure
   - Unnecessarily long functions.
   - Deep nesting or indirection without value.
4. Maintainability hygiene
   - Dead code or obsolete abstractions.
   - Inconsistent local patterns that increase cognitive load.

## Severity
- P1: design risk likely to cause defects or major maintenance cost.
- P2: maintainability issue with clear impact.
- P3: minor cleanup with low impact.

## Output contract
1. Report findings first, ordered P1 -> P3.
2. Each finding must include:
   - title
   - impact
   - location (file/line when available)
   - minimal corrective action
3. If no findings, state "No findings" and list residual risks.

## Constraints
- Do not propose broad refactors unless required for correctness.
- Do not report style-only issues without maintainability impact.
