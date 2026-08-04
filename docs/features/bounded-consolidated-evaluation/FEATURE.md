# Bounded Consolidated Evaluation

## Goal
Reduce evaluator time, implementation bias, and repair cycles in a long same-checkout run while preserving a complete semantic challenge of each active feature.

## Behavior
- The accountable parent maintains a transient active-feature surface containing files changed for the current feature plus directly relevant call paths.
- A fresh evaluator uses that surface as its entry point instead of treating the accumulated dirty diff as the feature diff, following outside call paths only when required to judge behavior or architecture.
- The same evaluator performs one review in two ordered reasoning passes:
  - evidence pass: before opening implementation files, compare the accepted goal and contracts with the retained passing attempt, inspect actual output, and identify what is demonstrated, missing, or still vulnerable to a central false green;
  - implementation pass: inspect the transient active-feature surface and relevant call paths, then challenge whether the implementation honestly produces the evidenced behavior or bypasses architecture, policy, validation, or proof boundaries.
- The evaluator completes the bounded review after finding a blocker and returns all supported material findings in one verdict.
- Preferences, style opinions, speculative improvements, and behavior outside the accepted contract are excluded from material findings.
- Autonomous execution resets the transient surface for the next feature and continues serially until no `ready` feature remains.

## Constraints
- The surface and evidence-pass conclusions exist only in evaluator context: no intermediate report is created. Do not add queue fields, intermediate reports, receipts, hashes, commits, branches, worktrees, another agent, or another completion stage.
- Proof-backed repair and a fresh evaluator `PASS` remain required after findings.

## Non-Goals
- Limiting the number of material findings.
- Preventing the evaluator from following a directly relevant call path outside the initial surface.
- Stopping autonomous execution after one feature.
- Pretending prompt instructions provide deterministic isolation between the two reasoning passes.
