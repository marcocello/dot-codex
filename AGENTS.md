# AGENTS.md - Marco Dev Operating Kernel

## Role
- This file is the navigation contract for Codex in this repo.
- Non-coding or personal operating work routes first through `docs/secondbrain.md` and matching `second-brain-*` skills.
- Skills own procedures, examples, stack choices, scripts, and domain judgment.
- Harness docs own durable proof, autonomy, safety, memory, and handoff detail.
- Repo docs own app context when present: `docs/APP.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, `docs/TESTING.md`.
- Do not copy full skill workflows into this file.

## Work Kernel
- Work on one feature or issue, and one `FEATURE_DIR`, at a time.
- Select one assurance lane before editing and keep every downstream skill aligned with it.
- `lightweight`: isolated, low-risk edit or bug fix with no durable behavior contract; use the smallest regression or narrow check, and do not require `FEATURE_DIR`, captured proof, the repo gate, or the evaluator.
- `tracked`: feature work, behavior-contract work, or repairs involving queues, safety, data, migrations, external services, multiple modules, or repeated failures; require the normal feature proof lifecycle.
- `autonomous`: explicit keep-going, queue, or repeated-repair work; use the tracked lifecycle plus persistent recovery and queue state.
- `FEATURE_DIR/FEATURE.md`: behavior contract.
- `FEATURE_DIR/PROOF.md`: proof contract.
- Do not claim done from plausibility, source shape, assistant claims, or tool-call success.
- For issue work, first check whether the bug clearly belongs to `docs/features/*/FEATURE.md`.
- Exactly one match: use that `FEATURE_DIR`; strengthen proof with a focused failing regression if current proof misses the bug.
- No clear match: do not create `FEATURE.md` by default; use smallest local regression proof unless behavior needs durable definition.
- Missing `FEATURE_DIR`: inspect existing features; use one clear match; otherwise create `docs/features/<request-slug>/FEATURE.md` and `PROOF.md`.
- Semantic or natural-language behavior must be fixed by defining the invariant and owning decision boundary, not by adding open-ended keyword, phrase, or language-specific lists. Hardcoded lists are acceptable only for closed vocabularies from a protocol, enum, provider contract, product taxonomy, or explicit spec. For lightweight semantic fixes, add paraphrase or non-English regression pressure, or promote to the repair harness.
- Ambiguity checkpoint: before editing, when a request has multiple plausible implementation strategies, touches auth/secrets/deployment/runtime/data, asks to use an exact file/path/source, or follows a user correction of the current direction, state the concrete behavior you are about to implement, the main alternative you are not implementing, and the material consequence or tradeoff. If any part is unclear or high-risk, ask one targeted question before editing.
- Correction checkpoint: if the user corrects the agent's approach once, pause further edits and restate the new intended behavior plus the rejected previous approach before changing more files.
- Promote lightweight work to the normal feature or repair harness when it touches behavior contracts, queues, safety, data, migrations, external services, multiple modules, or repeated failures.

## Completion Kernel
- Lightweight work is complete after its focused regression or narrow check passes; use stronger checks only when the touched surface makes them relevant.
- Tracked and autonomous work is complete only after the primary proof, gate, and `coding-feature-evaluator` pass.
- If a `FEATURE_DIR` exists, its primary proof must create a captured evidence bundle with `scripts/proof_run_capture`; do not treat raw test output as the feature proof.
- Queue work also needs `docs/features/status.json` completion evidence; validate the active item with `scripts/validate_feature_queue --feature <id>`, while the repo gate audits all items.
- Artifact work uses artifact-specific parser, contract, fixture, lint, syntax, or readiness checks.
- Autonomous Proof Loop: while proof is unsatisfied, keep repairing code, setup, fixtures, diagnostics, or contract owner routing.
- `NEED_INPUT` only after local recovery is exhausted and the remaining requirement is user-owned or external.
- Green-but-broken means proof is insufficient; return to contract repair before more implementation.
- Contract revision guard: after implementation begins, a wrong or incomplete contract must enter an explicit contract-repair state. Record why it changed, strengthen the proof, demonstrate the new proof fails against the current implementation when practical, then resume implementation. Final evidence must match the final contract, proof runner, and declared source revisions.

## Routing
- App idea -> `coding-app-to-features`.
- Spec -> `coding-feature-spec`.
- Proof -> `coding-proof-author`.
- Contract review -> `coding-feature-quality`.
- Implement -> `coding-feature-execute`.
- Repair -> `coding-repair` for clear defect, runtime bug, failing command, gate, proof check, typecheck, lint result, or evaluator `FAIL`.
- Autonomous queue, repeated repair, or keep-going work -> `coding-autonomous-execute`.
- Done judge -> `coding-feature-evaluator`.
- Setup/env/tasks -> `coding-prepare-environment`.
- Commit -> `coding-commit` only when asked.
- Stack/domain details live in stack skills: frontend, backend, Laravel, PHP, WordPress, operations, research.

## Context
- If `docs/ARCHITECTURE.md` exists, apply it; do not override project architecture unless asked.
- Align with `docs/APP.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md` when present.
- Greenfield default: use stack/domain skills before choosing folders or starters.
- `coding-app-to-features` may bootstrap app docs, multiple features, and `docs/features/status.json`; after that, return to one `FEATURE_DIR`.
- Codex memories hold stable preferences and habits; `AGENTS.md` holds hard rules; skills hold reusable workflows. No secrets in memories.

## Harness Docs
- Proof lifecycle and evidence bundles: `docs/harness/proof-lifecycle.md`; use `scripts/proof_run_capture` when command-wrappable.
- Proof scope and false-green risk: `docs/harness/oracle-scope.md` (compat filename).
- Target repo autofix, autosuggestions, and auto-improve: `docs/harness/repo-autonomy.md`.
- Autonomous execution and recovery: `docs/harness/autonomous-execution.md`.
- Destructive proof allowlist: `docs/harness/destructive-proof-allowlist.md`.
- Handoff receipt: `docs/harness/handoff.md`.
- Memory policy: `docs/harness/memory-policy.md`.
- Reference background lives in `README.md`; optional evolution notes live in `docs/harness/evolution/*`.

## Safety And Style
- Approval-risk action requires explicit approval: installing global tools or global dependencies, paid resource creation, destructive commands, deployments, force pushes, secret edits, credential entry, and external account or service mutations.
- Repo-local setup is pre-authorized when required by the user's requested coding task: `git init` in a new project, cloning a skill-prescribed starter or reference into the workspace, creating a local virtual environment, and installing project-declared dependencies into repo-local `.venv`, `node_modules`, or `vendor` directories. Do not ask the user for approval for these actions.
- Runtime or platform sandbox approval requirements still take precedence; request only the platform escalation that cannot be performed inside the current workspace permissions.
- No force push, deploy, destructive command, global dependency install, secret edit, credential entry, paid resource creation, or external account mutation unless requested and approved.
- Reuse existing code; make the smallest effective change; keep changes local; avoid unrelated refactors.
- Explicit over clever; red/green TDD for implementation and bugs; do not delete, weaken, or bypass tests for green.
- Code limits: function <=100 lines; cyclomatic complexity <=8 where tooling exists; positional params <=5.
- Markdown Writing: do not hard-wrap prose; keep each paragraph on one physical line unless structure requires line breaks.
- Editing this `dot-codex` config: use `scripts/gate_config` for harness checks; do not run repo gate or feature proofs unless asked.

## Handoff
- Default to a short human receipt, not an audit log.
- For product work, include primary proof, gate, evaluator, and blockers.
- For lightweight-lane work, include the narrow check and state that the full proof, gate, and evaluator path is available if the user wants stronger assurance.
- For artifact work, include created/changed files, narrow checks, live validation only when relevant, and blockers.
- Do not label gate, evaluator, or secondary checks as proof.
- If remaining requirement is user-owned after recovery: `NEED_INPUT: <question>`.
