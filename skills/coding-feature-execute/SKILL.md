---
name: coding-feature-execute
description: "Implement one decision-ready feature through captured proof, repository gate, fresh evaluation, and queue completion."
---

# Feature Execute

Purpose: deliver one accepted feature. One accountable parent owns its decisions, integration, queue transitions, and completion judgment. Other agents and feature parents may edit the same checkout concurrently while preserving unrelated work.

## Entry
Require one `FEATURE_DIR` containing:

- decision-complete `FEATURE.md`;
- decision-complete `PROOF.md`;
- executable `proof/run.sh`;
- `ready` queue item when `docs/features/status.json` exists;
- repository-relative `files` prefixes describing likely changes and `revalidate_on` prefixes describing proof dependencies.

A `revalidate` item does not enter this skill unless revalidation failed and the parent moved it to `ready`.

If behavior is missing, vague, or has unresolved material choices, return to `coding-feature-spec`. If proof is prose-only, static for runtime behavior, gameable, or decision-incomplete, return to `coding-proof-author`. Do not repair contract ambiguity through silent product choices during implementation.

## Workflow
1. Load contracts
   - Read `FEATURE.md`, `PROOF.md`, `proof/run.sh`, queue item, and required domain skills.
   - Read `docs/APP.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md` when present.

2. Prepare ownership
   - Confirm one accountable parent for this active feature; multiple agents or other feature parents may edit the same checkout concurrently.
   - Preserve unrelated work and re-read shared files before applying narrow edits. Do not start a competing proof while this feature's newest attempt is unresolved.
   - Validate queue `files` change prefixes and `revalidate_on` proof dependencies; broaden them before implementation when needed.
   - Run `"${CODEX_HOME:-$HOME/.codex}/scripts/invalidate_feature_status" --feature <id>` from the target repository before code and after prefix expansion.
   - Preserve unrelated dirty-tree changes.

3. Prepare environment
   - Reuse repository-native runtimes and tasks.
   - Use `coding-prepare-environment` when dependencies, services, local configuration, or tasks are missing.
   - Initialize Git only when required for a new project; never overwrite history.

4. Route implementation
   - Use the relevant frontend, backend, Laravel, PHP, WordPress, operations, or research skill.
   - When the feature or an evaluator finding exposes a concrete architectural boundary failure, use `coding-architecture-deep-dive` to select the smallest structural correction, then implement it inside the same feature when it remains within the declared goal and change surface.
   - Do not broaden into speculative architecture refactoring; every structural change must remove a concrete failure mode or restore an owning boundary.
   - Use bounded subagents for independent discovery, diagnosis, or implementation support only when useful.
   - Parent verifies and integrates all delegated work.

5. Establish red evidence
   - For new behavior or a known defect, run the decision-complete proof through `proof_run_capture` before substantial implementation when safe and meaningful. Retain the captured failing attempt.
   - If the attempt passes, determine whether the behavior already exists or the proof is too weak. An older PASS is not red evidence.
   - If a useful pre-change failure cannot safely or meaningfully be produced, state why in the first implementation attempt note.
   - Green-but-broken or proxy-only proof returns to `coding-proof-author` for a strengthened proof decision before implementation continues.

6. Implement
   - Make the smallest coherent change satisfying `FEATURE.md`.
   - Reuse existing paths and owning abstractions.
   - Add lower-level tests only when they reduce risk or localize defects.
   - Implement semantic behavior at the durable decision boundary, not through open-ended phrase lists.

7. Capture proof
   - Run `"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir FEATURE_DIR --timeout-seconds N --note "reason"` from the target repository.
   - Read the created `result.json` and relevant output.
   - Keep every failed, timed-out, interrupted, and passing attempt.
   - Immediately after `PASS`, initialize that attempt’s `completion.md` with gate and evaluator `NOT RUN` context before starting either stage. Update it as each stage finishes or fails.

8. Repair failures
   - Use `coding-repair` for the latest concrete failure.
   - Architecture failure: repair the owning boundary, not the symptom or proof expectation.
   - Run the narrow failing check when useful, then capture the full proof again.
   - Same failure twice: change tactic or widen inspection.
   - Contract/proof meaning changed: stop implementation and use Contract Repair below.

9. Run repository gate
   - After proof passes, run the canonical shared gate with `"${CODEX_HOME:-$HOME/.codex}/scripts/gate" --root <repo-root> --profile <profile>` using every applicable explicit profile.
   - Do not create or copy a target-repository `scripts/gate`; project-native build, test, lint, or health commands remain separate checks and may run in addition when useful.
   - Skip with a short reason only when the canonical profiles and repository-native health commands are not meaningful for the change.
   - Retain the command and outcome or skip reason in the final attempt's `completion.md`. A failed gate is retained there before repair begins.

10. Run managed evaluation
   - Rerun `"${CODEX_HOME:-$HOME/.codex}/scripts/invalidate_feature_status" --feature <id>` from the target repository immediately before evaluation so a feature that became overlapping and `done` during this work moves to `revalidate` before completion is judged.
   - Spawn a fresh read-only evaluator automatically.
   - Wait for the verdict and apply it through Managed Evaluator below.
   - Copy the evaluator's plain output verbatim into the final attempt's `completion.md` before queue mutation or repair.

11. Finalize queue
   - `PASS`: parent marks the item `done` with a short note.
   - `FAIL`: parent repairs, reruns proof/gate, and spawns a new evaluator.
   - `NEED_INPUT`: parent asks only for the exact user-owned or external dependency.

## Completion Learning
For every passing proof attempt considered for a repository gate or managed evaluator, the parent initializes plain `completion.md` before those stages and keeps it current:

```md
# Completion

Gate: <command + PASS|FAIL, SKIPPED + reason, or NOT RUN + pending/interruption reason>

Evaluator:
<verbatim plain output, or NOT RUN + reason>

Correction or repair context:
<material user correction, evaluator failure, gate failure, or repair lesson; none when absent>
```

Initialize the note before running the gate, then update it before repairing a failed gate/evaluator so pending, interrupted, and failed managed stages survive the current conversation. On resume, a prior passing attempt without this file is incomplete learning context and must be reconstructed when evidence is available or reported as missing. Do not create `completion.json`, validate a schema, calculate progress, or derive queue status from this file. It is learning context, not a receipt. Proof, gate decision, evaluator judgment, and parent queue mutation keep their existing authority.

## Managed Evaluator
- Use `spawn_agent` automatically; never ask the user to open or manage a second task.
- Every evaluation uses a new agent and `fork_turns: "none"` so implementation conversation is not inherited.
- Prompt the evaluator to read `coding-feature-evaluator`, the repository, feature directory, final run directory including initialized `completion.md`, gate result or skip reason, current implementation, and relevant attempts including earlier completion history.
- Supply the original user goal, material corrections, and the parent-owned change surface. Prefer exact non-secret wording; otherwise provide a faithful concise summary and identify unavailable intent context.
- Evaluator is read-only: no contract, implementation, proof, fixture, queue, or setup edits.
- Parent waits with the available agent-wait mechanism and reads the plain-language verdict.
- Parent preserves the verdict through Completion Learning; the evaluator remains read-only.
- No free slot: wait for an owned subagent to finish. Do not replace the fresh evaluation with same-context approval.
- Evaluator capability unavailable: mark `blocked` with the exact platform limitation.

Prompt shape:

```text
Read-only final evaluation. Read skills/coding-feature-evaluator/SKILL.md.
Repo: <absolute path>
Feature: <feature dir>
Final run: <run dir>
Gate: <PASS|SKIPPED + reason>
User goal and material corrections: <exact non-secret wording or faithful summary>
Parent-owned change surface: <paths and concise purpose>
Inspect current implementation, the final initialized completion.md, and relevant earlier attempts/completion history. Do not edit. Return evaluator output only.
```

## Contract Repair
Use when accepted behavior or proof meaning is wrong or incomplete after implementation begins:

1. Stop coding against the wrong contract.
2. Explain the defect and the behavior/proof consequence.
3. State the revised behavior or proof decision and continue when it remains within the user’s stated goal. Ask only when an unresolved choice would materially change behavior, scope, safety, cost, or external effects.
4. Strengthen proof and demonstrate the missed failure when practical.
5. Rerun the complete official proof with a note explaining the change and why scope was not weakened.

Preserve the material accepted correction in the resulting attempt's `completion.md` when that attempt reaches gate or evaluation.

Mechanical runner or setup fixes that do not change proof meaning need an attempt note and full rerun, not another product discussion.

## Handoff
Use the `AGENTS.md` receipt: outcome, changed surface, realistic proof, gate or skip reason, evaluator verdict, known gaps, blockers. Keep run internals and exhaustive file lists out unless audit/debug is requested.
