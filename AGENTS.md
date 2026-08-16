# AGENTS.md - Marco Dev Operating Kernel

## Role
- This file is the navigation contract for Codex in this repo.
- `AGENTS.md` owns global authority, assurance lanes, completion, safety, and handoff rules.
- Shared harness executables are owned by dot-codex and invoked from any checkout through `"${CODEX_HOME:-$HOME/.codex}/scripts/<tool>"`. Do not create, copy, or wrap these tools in target repositories.
- Non-coding or personal operating work routes first through `docs/secondbrain.md` and matching `second-brain-*` skills.
- Skill descriptions own the shortest unique routing trigger or exclusion. Skill bodies own task-specific procedure, examples, stack choices, decision rules, and domain judgment.
- Scripts own command arguments, outputs, exit semantics, and mechanical guarantees.
- Harness docs own durable rationale, threat models, and detailed proof, autonomy, safety, and handoff design.
- Repo docs own app context when present: `docs/APP.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, `docs/TESTING.md`.
- State each instruction once at its owner. Cross-reference the owner instead of copying defaults or full workflows.

## Task Naming
- At the beginning of every task, rename the current task with the task-title tool using `TYPE: concise outcome`.
- Use uppercase types: `FEAT` for new user-facing behavior, `FIX` for broken behavior, `REFACTOR` for internal restructuring without behavior changes, `DOCS` for documentation-only work, `TEST` for tests or proof-only work, `CHORE` for configuration, dependencies, tooling, or maintenance, `REVIEW` for code, architecture, or security review, `RESEARCH` for investigation without implementation, and `OPS` for deployment, infrastructure, or operational work.
- Keep the outcome under 60 characters and omit trailing punctuation.
- Prefer `FIX` over `FEAT` when restoring previously intended behavior.
- If the primary outcome changes, rename the task again.
- Perform the rename; do not merely suggest a title.

## Work Kernel
- Work on one issue, one feature, and one `FEATURE_DIR` at a time. One accountable parent owns decisions, implementation, proof, evaluation, queue state, and completion.
- Select one assurance lane before editing and keep downstream skills aligned with it.
- `lightweight`: isolated, low-risk edit or bug fix with no durable behavior contract; use the smallest regression or narrow check. No `FEATURE_DIR`, captured proof, evaluator, or queue mutation required.
- `tracked`: feature work, behavior-contract work, or repairs involving queues, safety, data, migrations, external services, multiple modules, or repeated failures; use the normal feature lifecycle.
- `autonomous`: explicit keep-going, queue, or repeated-repair work; use the tracked lifecycle plus persistent recovery and queue state.
- `FEATURE_DIR/FEATURE.md`: behavior contract.
- `FEATURE_DIR/PROOF.md`: realistic proof contract.
- For non-trivial work, use two decision passes before substantial implementation: feature challenge/decision summary, then proof challenge/decision summary. Each pass may contain zero user questions. Ask only when an unresolved user-owned choice has no safe default and its answer can materially change behavior, scope, safety, cost, data, permissions, or external effects. After the user answers, proceed without asking them to approve the written contract. When repository context, the request, or safe defaults resolve the choices, state the decisions and proceed directly.
- Route scope from the requested deliverable, not isolated verbs. A request for feature, proof, specification, or planning artifacts is contract-authoring work and ends after decision-ready `FEATURE.md`, `PROOF.md`, and executable `proof/run.sh` artifacts are written. Answers to discovery or proof questions do not authorize implementation. Contract authoring must not invoke `coding-feature-execute`; implementing the described product behavior requires a separate explicit request.
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
- Tracked and autonomous work require a passing realistic proof and a fresh read-only `coding-feature-evaluator` `PASS` for the current implementation and proof.
- Every tracked and autonomous feature invokes the evaluator after proof passes. Lightweight work does not invoke the evaluator.
- Completion applies only to an unchanged final candidate. Any relevant edit after the latest official proof `PASS` makes that proof stale; any relevant edit after evaluator `PASS` also voids the verdict. Follow `coding-feature-execute` to rerun the complete proof and obtain a fresh evaluator before marking `done`.
- `coding-feature-execute` owns evaluator findings, proof-backed repair, fresh reevaluation, and the parent-owned completion transition.
- `coding-proof-author`, `docs/harness/proof-lifecycle.md`, and `proof_run_capture` own executable proof design, retained attempts, timeouts, and process containment.
- `coding-feature-queue` owns queue schema and status; `coding-autonomous-execute` owns serial priority selection and continuation.
- Artifact work uses artifact-specific parsers, renderers, contract checks, fixtures, syntax checks, or readiness checks.
- One accountable parent owns the active feature, contracts, queue state, implementation, official proof, evaluation, and completion. On resume, inspect the feature's newest run directory; never start a competing proof or fall back to an older PASS while a newer attempt is incomplete.
- `NEED_INPUT` only after safe local recovery is exhausted and the remaining requirement is user-owned or external.
- Green-but-broken means proof is insufficient. Return to proof design, state the strengthened proof decision, demonstrate the missed failure when practical, and rerun.
- Contract revision guard: after implementation begins, explain why `FEATURE.md`, `PROOF.md`, or `proof/run.sh` changed. Continue autonomously when the revision remains within the user’s stated goal; ask only when an unresolved choice would materially change behavior, scope, safety, cost, or external effects. Never silently reduce scope or weaken proof. Show the missed failure when practical and rerun the complete proof. Saved attempt copies provide comparison; no freshness hash or receipt graph is required.
- A proof runner must not edit implementation or harness inputs, daemonize, call `setsid`, or escape its capture process group.
- `proof/run.sh` prints relevant non-secret facts about the actual application runtime and readiness into captured output. Generic capture records only its own runtime context and never dumps the full environment.

## Routing
- App idea -> `coding-app-to-features`.
- Spec -> `coding-feature-spec`.
- Proof -> `coding-proof-author`.
- Implement -> `coding-feature-execute`.
- Repair -> `coding-repair` for a clear defect, runtime bug, failing proof, evaluator finding, setup failure, test, typecheck, lint, or build.
- Autonomous queue, repeated repair, or keep-going work -> `coding-autonomous-execute`.
- Final semantic judgment for every tracked or autonomous feature -> `coding-feature-evaluator`.
- Queue schema/status -> `coding-feature-queue`.
- Setup/env/tasks -> `coding-prepare-environment`.
- Commit -> `coding-commit` only when asked.
- Stack/domain details live in the relevant frontend, backend, Laravel, PHP, WordPress, operations, or research skill.

## Context
- If `docs/ARCHITECTURE.md` exists, apply the relevant current sections; do not override project architecture unless asked.
- Align with the relevant current sections of `docs/APP.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md` when present. Do not load superseded history by default unless the active migration needs it.
- Greenfield app-shape selection and defaulting belong to `coding-app-to-features`; stack/domain skills own concrete folders, starters, and code layout.
- `coding-app-to-features` may bootstrap app docs, the complete lean feature set, executable proof packages, and `docs/features/status.json`; after preparation, return to one feature.
- Project-owned interaction records hold explicitly captured dialogue history; `AGENTS.md` holds hard rules; skills hold reusable workflows. Interaction records remain historical evidence, not automatic context.

## Scaffold And Instruction Boundaries
- Stack/domain skills own application source structure, framework starter, and code layout before hosting or deployment capabilities are selected.
- Sites is opt-in for application construction: use it only when the user explicitly requests Sites or `.openai/hosting.json` existed before the task began.
- A platform manifest created during the current task cannot retroactively authorize that platform, replace the selected stack skill, or redefine the application structure.
- Resolve and state the structure owner before running an initializer, installing dependencies, or creating application files.
- Do not create `AGENTS.md` or `AGENTS.override.md` in target repositories. The global operating kernel lives at `"${CODEX_HOME:-$HOME/.codex}/AGENTS.md"`; preserve pre-existing project instruction files without creating new ones.
- A missing project-local `AGENTS.md` or `AGENTS.override.md` is valid and must not be treated as a gate failure.

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
- Editing this dot-codex config: use `"${CODEX_HOME:-$HOME/.codex}/scripts/gate" --root "$PWD"` for repository-local harness validation. It is read-only and includes common, Python, harness, unit-test, and diff checks. It is not a product-feature completion stage; run the active feature proof separately when the tracked lifecycle applies.

## Handoff
- Default to a short human receipt, not an audit log.
- Product work: outcome, changed surface, realistic proof, evaluator verdict, known gaps, blockers.
- Lightweight work: outcome, changed surface, focused regression or narrow check.
- Artifact work: created/changed artifacts, relevant parser/render/contract validation, live validation only when relevant, blockers.
- Do not label an evaluator, lint, build, generic validation, or source inspection as feature proof.
- If the remaining requirement is user-owned after recovery: `NEED_INPUT: <question>`.
