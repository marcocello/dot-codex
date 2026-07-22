---
name: coding-repair
description: "Fix a known defect or concrete failure with the smallest verified change."
---

# Repair

Purpose: identify the owning failure quickly, make the smallest correct change, and verify it at the narrow boundary before returning to the applicable completion lane.

## Entry
- Clear issue, failing command, or evaluator finding: proceed.
- Unclear expected behavior: use `coding-feature-spec`; ask the user only when a material choice cannot be inferred safely.
- Inherit the assurance lane from `AGENTS.md`.
- Exactly one owning `FEATURE_DIR`: read its contracts and use the tracked lifecycle.
- Multiple plausible owners: ask one focused ownership question.
- No owner for an isolated defect: use a focused local regression rather than creating ceremony.

## Fast Path
For a concrete failure, diagnose in this order:

1. Read the latest `result.json` or exact failing command result.
2. Read the relevant tail of `stderr.txt`; inspect stdout only when it carries the useful signal.
3. Classify the owner: implementation, proof, setup/environment, gate/tooling, or external dependency.
4. Reproduce the narrow failure when cheap and safe.
5. Inspect the owning code/configuration and adjacent tests only.
6. Make the smallest effective repair without weakening accepted behavior or proof.
7. Rerun the narrow check.
8. For tracked/autonomous work, rerun the full proof through capture and retain the attempt.

Same failure twice: change tactic or widen inspection. Do not repeat the same patch/retry loop without new evidence.

## Workflow
1. Establish root cause
   - Follow the real call path: entrypoint, parsing, routing, owner module, persistence, network, runtime boundary.
   - Quote exact evidence and state confidence: `clear`, `likely`, or `unknown`.
   - Unknown cause: add the smallest diagnostic before production edits.
   - Missing credentials, mounts, services, provider setup, or required configuration are failures; do not silently convert them into success or no-op behavior.

2. Locate existing logic
   - Search for the owning function/component before adding code.
   - Reuse and extend existing logic; avoid parallel helpers or duplicated policy.
   - Read adjacent tests and architecture constraints.

3. Establish red
   - Add or update the smallest regression that proves the defect.
   - Confirm it fails for the intended reason when practical.
   - Do not use an exact source string assertion for runtime behavior unless source shape is the contract.

4. Implement green
   - Keep the edit local.
   - Avoid refactoring unrelated paths.
   - Do not catch and downgrade required-runtime failures.
   - For semantic behavior, repair the structured invariant at the owning boundary rather than adding phrases, language gates, or tool hiding.

## Runtime Evidence
- Local application issue: inspect bounded recent runtime output before code.
- Docker/service issue: inspect relevant container/service state and recent logs.
- Browser issue: inspect visible behavior, console, and network when available.
- Database/provider issue: inspect persisted or provider read-back safely.
- Environment issue: use repository readiness/setup commands and `coding-prepare-environment`.
- Capture relevant lines only; redact secrets and customer data.

## Contract Boundary
- Missing behavior or changed goal: stop coding against the old contract; return to the feature decision flow.
- Changed proof strength, fake boundary, or known gap: stop coding against the old proof; return to the proof decision flow.
- Mechanical runner, fixture, or setup repair with unchanged proof meaning: note why and rerun.

## Verification
- `lightweight`: focused regression or narrow check; add broader checks only when risk warrants.
- `tracked`: captured realistic proof, useful gate or skip reason, fresh evaluator.
- `autonomous`: same tracked checks plus queue continuation.
- Re-check the runtime/browser/provider signal that exposed the issue when relevant.
- Evaluator `FAIL`: repair the specific finding, rerun full proof/gate, then use a new evaluator.
- Evaluator `NEED_INPUT`: ask only for the exact dependency after local recovery.
- During autonomous work, return control to `coding-autonomous-execute` until proof passes or its terminal condition is met.

## Handoff
Report outcome, root cause, changed surface, focused regression, broader proof/gate/evaluator when applicable, and blockers. Keep raw logs and internal attempts out unless needed for diagnosis or audit.
