# Advisory-Only UI Improvement Skill

## Goal
Give a user a precise, reusable written plan for improving a web interface without changing the product during the UI review task.

## Behavior
- Every `coding-ui-improvement` invocation is read-only, including requests phrased as improve, fix, redesign, apply, build, or address feedback.
- The skill may inspect rendered UI, screenshots, repository source, Agentation feedback, and external design registries, but it does not mutate files, dependencies, annotations, services, or product state.
- The result prioritizes observed UI problems by user impact and confidence, and separates evidence-backed defects from taste-level suggestions.
- Every recommendation identifies the affected local component and file when discoverable, states the exact visual or interaction change, covers relevant states and viewport/accessibility behavior, and includes an acceptance check that a later implementation task can verify.
- When recommending an external component, the result cites the source or registry, component identifier, relevance, intended local target, and required adaptation to the product's existing tokens and conventions.
- When the user asks to apply the recommendations, the skill still completes the written brief and states that implementation requires a separate task using the appropriate frontend or repair workflow.

## Constraints
- Existing product context and the rendered interface take precedence over external inspiration.
- External components are recommendations, not installed dependencies or tested solutions.
- Agentation annotations remain pending and unmodified.
- Limitations caused by unavailable rendering, source, or authenticated design tools are stated explicitly.

## Non-Goals
- Editing application or test files.
- Generating or applying patches.
- Installing, copying, or scaffolding components.
- Changing dependencies or configuration.
- Acknowledging, resolving, or otherwise mutating Agentation feedback.
- Guaranteeing deterministic instruction compliance by every future model version.
