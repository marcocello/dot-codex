# Lean Review Rubric

Use this rubric to score findings and prioritize recommendations.

## Scoring Axes
- Readability: How hard the code is to understand on first read.
- Cohesion: Whether a module/function has one clear responsibility.
- Coupling: How tightly modules depend on internal details of others.
- Testability: How easy it is to verify behavior with focused tests.
- Change Risk: How likely modifications are to cause regressions.
- Verbosity Quality: Whether code volume is justified by risk/clarity, or is incidental ceremony.
- Function Integrity: Whether function name, signature, control flow, and side effects form a coherent unit.

## Severity Guide
- High: Likely to cause defects, slow delivery, or block safe changes.
- Medium: Clear maintainability drag with moderate delivery impact.
- Low: Local readability issue with low systemic risk.

## Effort Buckets
- Quick Win: <= 30 minutes; local rewrite, naming, extraction, or dedup.
- Medium: 0.5 to 1 day; module-level cleanup or dependency inversion.
- Structural: > 1 day; cross-module boundary redefinition or decomposition.

## Typical Smells to Flag
- Function performs parsing, validation, persistence, and response mapping.
- One module imports from multiple architectural layers.
- Conditionals encode business policy scattered across files.
- Repeated transformation logic with slight variance.
- "Utility" modules become generic dumps for unrelated logic.
- Function names that describe mechanism instead of behavior.
- Boolean flag arguments that create hidden multi-mode behavior.
- Multiple return shapes or mixed error channels in one function.
- Long guard/if chains that conceal policy priorities.
- Repeated setup/teardown or logging boilerplate across sibling functions.

## Function-Level Severity Signals
- High:
  - behavior-critical function with mixed concerns and poor testability
  - hidden side effects or broad exception handling that can mask defects
  - bloated control flow that blocks safe modification
- Medium:
  - consistent verbosity bloat and duplicated function skeletons
  - unstable signatures (too many args, ambiguous names, boolean switches)
  - abstraction leakage between domain logic and transport/persistence details
- Low:
  - local naming or structure issues with clear behavior and low regression risk

## Verbosity Classification Guide
- Lean:
  - each block contributes directly to behavior or explicit safety
  - little or no repeated ceremony
- Acceptable:
  - moderate ceremony but still easy to scan and maintain
  - some duplication or indirection without major maintenance harm
- Bloated:
  - repeated scaffolding, defensive code without evidence of risk, or layered indirection that obscures intent
  - function body length and branch shape exceed what behavior complexity requires
