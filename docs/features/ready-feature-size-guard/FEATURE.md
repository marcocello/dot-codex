# Ready Feature Size Guard

## Goal
Prevent oversized feature packages from entering implementation while preserving lean vertical features that legitimately span several files or layers.

## Behavior
- Before a queue item becomes `ready`, app decomposition, feature specification, and the queue transition require one coherent observable outcome and one proof boundary.
- A package with multiple independently valuable observable outcomes or independently runnable proof boundaries is split before readiness.
- Touching multiple files or layers is not by itself evidence that a feature is oversized.

## Constraints
- Keep the existing five-field queue schema and four statuses.
- Do not add scores, estimates, dependency graphs, approval gates, or another lifecycle stage.

## Non-Goals
- Splitting one vertical outcome into component-only tasks.
- Automatically measuring feature size.

