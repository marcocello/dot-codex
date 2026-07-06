# Harness Evolution Loop

Harness evolution is for repeated harness failures, not ordinary feature repair.

Use it when proof bundles, evaluator failures, user corrections, or rollout evidence show that the harness itself allowed a recurring failure pattern.

For other software repos, do not confuse target-repo auto-improve with harness evolution. A failed proof usually means autofix the repo. A weak proof or missing readiness check usually means autosuggest repo work. Change the harness only when repeated evidence shows the repo-level loop failed because the harness guidance, script, test, or config was too weak.

## Loop

```text
run evidence -> failure pattern -> app improvement review -> component choice -> change manifest -> harness edit -> held-out regression -> accept/reject
```

## Component Choice

Choose the smallest owning layer that can prevent the failure:

- `AGENTS.md`: hard operating rule that must always apply.
- `skill`: reusable workflow or domain judgment.
- `script`: executable enforcement, validation, capture, or classification.
- `docs`: durable explanation or operator map.
- `test`: regression for harness behavior.
- `config`: model/tool/runtime setting.
- `memory`: stable user preference, recurring correction, or project pitfall.

If the same failure repeats after one component-level fix, do not keep adding text to the same place. Reclassify the owner.

## Change Manifest

Every harness change should declare:

- before evidence showing the old harness behavior;
- observed failure evidence;
- failure pattern;
- root cause;
- component level;
- why this component is the owner;
- observation signal: component, experience, or decision signal expected to improve;
- predicted fixes;
- predicted regressions;
- held-out checks;
- after evidence showing what changed after the harness edit;
- rollback plan;
- verification result.

The manifest is a falsifiable prediction, not a rationale essay.

## App Improvement Review

Use `$coding-app-improvement-review` when you want Codex to manually inspect feature specs, proof plans, proof evidence, successful checks, evaluator output, and user corrections, then suggest app/project improvements or harness lessons.

This review is not an auto-editor. Use it to see repeated target-repo failure patterns before changing skills, scripts, docs, tests, config, or memory.

## Held-Out Checks

Harness changes should run at least one check that did not directly motivate the change. This protects against prompt-only or policy-only edits that improve one scenario while weakening another.

Useful held-out checks include:

- proof-contract unit tests;
- `scripts/lint_harness`;
- `scripts/validate_feature_queue`;
- `scripts/validate_proof_bundle` on sample evidence;
- one unrelated feature proof when the user explicitly asks for broader validation.

Run `scripts/harness_review --check` before accepting a manifest. A final `accepted`, `rejected`, or `rollback` verdict needs concrete after evidence, verification, and verdict basis.

## Accept Or Reject

Accept a harness pattern only after repeated use, tests, rollout evidence, or real proof results show it improves behavior without unacceptable regression.

Reject or roll back a pattern when it adds ceremony, weakens proof, hides failures, increases unsafe autonomy, or shifts judgment from executable evidence to model confidence.
