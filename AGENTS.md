# AGENTS.md - Marco Dev Operating Kernel

## Role
- This file is the navigation contract for Codex in this repo.
- `AGENTS.md` owns global authority, assurance lanes, completion, safety, and handoff rules.
- Non-coding or personal operating work routes first through `docs/secondbrain.md` and matching `second-brain-*` skills.
- Skill descriptions own the shortest unique routing trigger or exclusion. Skill bodies own task-specific procedure, examples, stack choices, decision rules, and domain judgment.
- Scripts own command arguments, outputs, exit semantics, and mechanical guarantees.
- Harness docs own durable rationale, threat models, and detailed proof, autonomy, safety, and handoff design.
- Repo docs own app context when present: `docs/APP.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, `docs/TESTING.md`.
- State each instruction once at its owner. Cross-reference the owner instead of copying defaults or full workflows.

## Work Kernel
- Work on one feature or issue, and one `FEATURE_DIR`, at a time.
- Select one assurance lane before editing and keep downstream skills aligned with it.
- `lightweight`: isolated, low-risk edit or bug fix with no durable behavior contract; use the smallest regression or narrow check. No `FEATURE_DIR`, captured proof, repository gate, evaluator, or queue mutation required.
- `tracked`: feature work, behavior-contract work, or repairs involving queues, safety, data, migrations, external services, multiple modules, or repeated failures; use the normal feature lifecycle.
- `autonomous`: explicit keep-going, queue, or repeated-repair work; use the tracked lifecycle plus persistent recovery and queue state.
- `FEATURE_DIR/FEATURE.md`: behavior contract.
- `FEATURE_DIR/PROOF.md`: realistic proof contract.
- For non-trivial work, use two decision rounds before substantial implementation: feature questions/challenge/decision summary, then proof questions/challenge/decision summary. Ask only questions whose answers can materially improve the result. After the user answers, proceed without asking them to approve the written contract. When repository context or the request already resolves the questions, state the decisions and proceed directly.
- Do not claim completion from plausibility, source shape, assistant claims, tool-call success, a gate, or an evaluator without realistic executable proof.
- For issue work, first check whether the defect clearly belongs to `docs/features/*/FEATURE.md`.
- Exactly one match: use that `FEATURE_DIR`; add a focused regression when current proof misses the defect.
- No clear match: use the smallest local regression unless expected behavior needs durable product definition. Do not create a feature package merely because the harness exists.
- New or materially changed product behavior without a clear owner: create `docs/features/<request-slug>/FEATURE.md`, `PROOF.md`, and executable proof.
- Semantic behavior must be fixed at the owning invariant, not through open-ended keyword, phrase, or language lists. Hardcoded lists are valid only for closed vocabularies from protocols, enums, provider contracts, product taxonomies, or explicit specs.
- Ambiguity checkpoint: before editing, state the intended behavior, rejected material alternative, and consequence when multiple strategies, auth/secrets/deployment/runtime/data, exact paths/sources, or a user correction could change the result. Ask focused questions when unresolved.
- Correction checkpoint: after a user correction, restate the accepted behavior and rejected previous direction before editing again.
- Promote lightweight work to tracked or autonomous when it touches behavior contracts, queues, safety, data, migrations, external services, multiple modules, or repeated failures.

## Completion Kernel
- Lightweight work is complete after its focused regression or narrow check passes; add broader checks only when the touched surface justifies them.
- Tracked and autonomous work require a passing realistic proof, a useful existing repository gate or explicit skip reason, and a fresh managed `coding-feature-evaluator` `PASS`.
- `FEATURE_DIR/proof/run.sh` contains the complete executable proof sequence. Its exit code is the suite result.
- Capture every official attempt with `scripts/proof_run_capture --feature-dir FEATURE_DIR --timeout-seconds N --note "reason"`.
- The LLM chooses a scenario-appropriate timeout. There is no default.
- Keep failed, timed-out, interrupted, and passing attempts Git-trackable. Scripts record execution; the LLM judges meaning and progress.
- Queue state lives in `docs/features/status.json` with only `draft`, `ready`, `revalidate`, `blocked`, and `done`, short notes, repository-relative `files` change prefixes, and `revalidate_on` proof-dependency prefixes.
- Before implementation, whenever change prefixes broaden, and immediately before managed evaluation, run `scripts/invalidate_feature_status --feature <id>` so completed features whose proof dependencies overlap the active changes move to `revalidate` even if queue state changed during the active work.
- Default autonomous implementation selects only `ready` work and ignores `revalidate`. Revalidation is an explicit, separate pass: rerun the existing proof without changing implementation, setup, contracts, or proof; after proof passes, run a fresh evaluator. Evaluator `PASS` returns the item to `done`; proof or evaluator failure moves it to `ready` for the normal repair lifecycle. Do not repair or recursively execute invalidated work during revalidation.
- Queue prose never authorizes completion. The parent marks `done` only after the current proof, optional gate decision, and fresh evaluator pass.
- Artifact work uses artifact-specific parsers, renderers, contract checks, fixtures, syntax checks, or readiness checks.
- For new behavior or a known defect, retain a captured failing proof before substantial implementation when safe and meaningful. If useful red evidence cannot be produced, retain the reason and do not present an older PASS as red pressure.
- Autonomous Proof Loop for `ready` implementation work: while proof is unsatisfied, inspect the latest result, repair the owning problem, and capture another attempt. This loop never applies to explicit revalidation.
- Multiple agents and feature parents may edit one checkout concurrently. Keep one accountable parent per active feature for decisions, integration, queue transitions, and completion judgment; preserve unrelated work. On resume, inspect that feature's newest run directory; an `attempt-start.json` without `result.json` is unresolved until its recorded process is checked. Never start a competing proof for the same feature or fall back to an older PASS while a newer attempt is incomplete.
- `NEED_INPUT` only after safe local recovery is exhausted and the remaining requirement is user-owned or external.
- Green-but-broken means proof is insufficient. Return to proof design, state the strengthened proof decision, demonstrate the missed failure when practical, and rerun.
- Contract revision guard: after implementation begins, explain why `FEATURE.md`, `PROOF.md`, or `proof/run.sh` changed. Continue autonomously when the revision remains within the user’s stated goal; ask only when an unresolved choice would materially change behavior, scope, safety, cost, or external effects. The evaluator rejects silent scope reduction or proof weakening. Show the missed failure when practical and rerun the complete proof. Saved attempt copies provide comparison; no freshness hash or receipt graph is required.
- A proof runner must not edit implementation or harness inputs, daemonize, call `setsid`, or escape its capture process group.
- `proof/run.sh` prints relevant non-secret facts about the actual application runtime and readiness into captured output. Generic capture records only its own runtime context and never dumps the full environment.
- After a proof attempt passes and before it enters gate/evaluation, the parent initializes plain `completion.md`; it then updates the file with gate outcome, evaluator output, and material correction or repair reason. Missing managed-stage history is a proof/evaluator failure. The file is never parsed as a completion receipt or queue authority.

## Routing
- App idea -> `coding-app-to-features`.
- Spec -> `coding-feature-spec`.
- Proof -> `coding-proof-author`.
- Implement -> `coding-feature-execute`.
- Repair -> `coding-repair` for a clear defect, runtime bug, failing proof, gate, test, typecheck, lint, build, or evaluator `FAIL`.
- Autonomous queue, repeated repair, or keep-going work -> `coding-autonomous-execute`.
- Done judge -> `coding-feature-evaluator`, normally spawned automatically by `coding-feature-execute`.
- Queue schema/status -> `coding-feature-queue`.
- Setup/env/tasks -> `coding-prepare-environment`.
- Commit -> `coding-commit` only when asked.
- Stack/domain details live in the relevant frontend, backend, Laravel, PHP, WordPress, operations, or research skill.

## Context
- If `docs/ARCHITECTURE.md` exists, apply it; do not override project architecture unless asked.
- Align with `docs/APP.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md` when present.
- Greenfield work uses stack/domain skills before choosing folders or starters.
- `coding-app-to-features` may bootstrap app docs, multiple features, and `docs/features/status.json`; after preparation, return to one `FEATURE_DIR`.
- Project-owned interaction records hold explicitly captured dialogue history; `AGENTS.md` holds hard rules; skills hold reusable workflows. Interaction records remain historical evidence, not automatic context.

## Harness Docs
- Canonical design and threat model: `docs/harness/deep-dive.md`.
- Proof capture and retained attempts: `docs/harness/proof-lifecycle.md`.
- Proof scope and false-green risk: `docs/harness/oracle-scope.md`.
- Target repo learning: `docs/harness/repo-autonomy.md`.
- Autonomous execution and recovery: `docs/harness/autonomous-execution.md`.
- Destructive proof allowlist: `docs/harness/destructive-proof-allowlist.md`.
- Handoff receipt: `docs/harness/handoff.md`.
- Reference background lives in `README.md`; optional evolution notes live in `docs/harness/evolution/*`.

## Safety And Style
- Approval-risk action requires explicit approval: global installs, paid resource creation, destructive commands, deployments, force pushes, secret edits, credential entry, and external account/service mutations.
- Repo-local setup required by requested work is pre-authorized: `git init`, skill-prescribed starter/reference cloning, local virtual environments, and project-declared dependencies inside `.venv`, `node_modules`, or `vendor`.
- Platform sandbox approval rules still apply; request only the escalation that cannot be completed inside current permissions.
- Reuse existing code; make the smallest effective change; keep edits local; avoid unrelated refactors.
- Explicit over clever. Use red/green TDD for implementation and defects. Never delete, weaken, or bypass proof for green.
- Code guidelines unless the repository defines stricter rules: function <=100 lines, cyclomatic complexity <=8 where tooling exists, positional parameters <=5. Do not add tooling only to enforce these numbers.
- Do not hard-wrap Markdown prose.
- Editing this dot-codex config: use `scripts/gate` as the repository gate. It is read-only and includes common, Python, harness, unit-test, and diff checks. Run the active feature proof separately when the tracked lifecycle applies.

## Handoff
- Default to a short human receipt, not an audit log.
- Product work: outcome, changed surface, realistic proof, gate or skip reason, evaluator, known gaps, blockers.
- Lightweight work: outcome, changed surface, focused regression or narrow check.
- Artifact work: created/changed artifacts, relevant parser/render/contract validation, live validation only when relevant, blockers.
- Do not label a gate, evaluator, lint, build, or source inspection as feature proof.
- If the remaining requirement is user-owned after recovery: `NEED_INPUT: <question>`.
