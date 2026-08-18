# AGENTS.md - Marco Dev Operating Kernel

## Authority
- This file is the compact router for Codex work in this repository. Skills own task procedures; scripts own command contracts; harness docs own rationale and threat models; target-repository docs own product and architecture context.
- Shared harness executables are invoked from any checkout through `"${CODEX_HOME:-$HOME/.codex}/scripts/<tool>"`. Do not copy or wrap them in target repositories.
- Non-coding or personal operating work routes through `docs/secondbrain.md` and the matching `second-brain-*` skill.
- State a rule once at its smallest owner. Cross-reference it instead of repeating workflows here.

## Start
- Rename every task with the task-title tool as `TYPE: concise outcome`, under 60 characters and without trailing punctuation.
- Use `FEAT`, `FIX`, `REFACTOR`, `DOCS`, `TEST`, `CHORE`, `REVIEW`, `RESEARCH`, or `OPS`. Prefer `FIX` when restoring intended behavior. Rename again if the primary outcome changes.
- Select one assurance category before editing:
  - `focused`: clear isolated reversible repair; use a focused regression or narrow check.
  - `standard`: material product behavior; use realistic proof and fresh final review.
  - `sensitive`: standard assurance plus fresh preflight for data/migrations, authorization/security, destructive or paid external effects, durable cross-component ownership, or material proof-target ambiguity.
- Autonomous work is a continuation mode, not an assurance category; apply the selected feature assurance serially.
- One accountable parent owns one active issue or `FEATURE_DIR`, its decisions, implementation, proof, evaluation, queue state, and completion.

## Route
- Product input of any maturity or cardinality, including app-level decisions -> `coding-product-partner`.
- Proof -> `coding-proof-author`.
- Implementation -> `coding-feature-execute`.
- Clear defect or failing check -> `coding-repair`.
- Autonomous queue or repeated repair -> `coding-autonomous-execute`.
- Queue state -> `coding-feature-queue`; environment -> `coding-prepare-environment`; commit -> `coding-commit` only when asked.
- Use the relevant frontend, backend, Laravel, PHP, WordPress, operations, or research skill for stack details.
- Route by the requested deliverable. Shaping, specification, planning, and proof authoring stop after their decision-ready artifacts; discovery answers preserve the request's existing authorization but do not expand it. Building product behavior requires an explicit implementation request.
- New or materially changed product behavior without a clear owner receives `docs/features/<slug>/FEATURE.md`, `PROOF.md`, and executable proof. A clear defect uses its existing feature owner or the smallest local regression; do not create a feature package merely because the harness exists.

## Context And Decisions
- Apply relevant current sections of `docs/APP.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md` when present. Do not load superseded history unless the active migration needs it.
- Before a consequential edit, state the accepted behavior, the material alternative rejected, and the consequence. After a user correction, restate the corrected direction before editing again.
- Ask for unresolved user-owned context or choices when the answers materially improve problem understanding, user implications, behavior, architecture, scope, safety, cost, data, permissions, external effects, or proof feasibility. Otherwise decide, disclose, and proceed.

## Completion
- Focused work is complete after its focused regression or narrow check passes.
- Standard and sensitive work require passing realistic proof followed by fresh read-only `coding-feature-review` final `PASS` on the unchanged candidate. Any relevant edit makes that evidence stale; `coding-feature-execute` owns reruns and repair.
- A green proof followed by observed broken behavior is a proof defect. Strengthen the owning scenario around the missed activation, existing state, visible read-back, affected consumer, or runtime boundary; demonstrate the miss when practical; repair; rerun proof; reevaluate.
- Name the consumption target before proof. When it is an existing local or deployed runtime, isolated source proof is intermediate and the feature cannot reach `done` until that exact runtime works. Continue safe local rebuild, restart, and verification autonomously; if approval or an external dependency remains after recovery, mark `blocked` with the exact action instead of converting it to source-only completion.
- `NEED_INPUT` is valid only after safe local recovery is exhausted and the remaining requirement is user-owned or external.
- Proof execution and retained attempts follow `coding-proof-author`, `docs/harness/proof-lifecycle.md`, and `proof_run_capture`. Queue completion follows `coding-feature-queue`.

## Scaffold Boundaries
- Stack/domain skills own application source structure, framework starter, and code layout before hosting or deployment capabilities are selected.
- Sites is opt-in for application construction: use it only when the user explicitly requests Sites or `.openai/hosting.json` existed before the task began.
- A platform manifest created during the current task cannot retroactively authorize that platform, replace the selected stack skill, or redefine application structure.
- Do not create `AGENTS.md` or `AGENTS.override.md` in target repositories. Preserve pre-existing project instruction files. Their absence must not be treated as a gate failure.

## Safety
- Explicit approval is required for global installs, paid resources, destructive commands, deployments, force pushes, secret edits, credential entry, and external account or service mutations.
- Repository-local setup needed for requested work is pre-authorized: `git init`, skill-prescribed starter/reference cloning, local virtual environments, and project-declared dependencies in `.venv`, `node_modules`, or `vendor`.
- Preserve unrelated dirty-tree work. Reuse existing code, make the smallest coherent change, and use red/green TDD for implementation and defects. Never weaken proof for green.
- Unless the repository is stricter: keep functions within 100 lines, cyclomatic complexity within 8 where tooling exists, and positional parameters within 5. Do not add tooling solely to enforce these guidelines.
- Do not hard-wrap Markdown prose.
- Validate dot-codex changes with `"${CODEX_HOME:-$HOME/.codex}/scripts/gate" --root "$PWD"`. The gate validates the harness; it is not product proof.

## Handoff
- Keep the receipt short: outcome, changed surface, realistic proof or focused check, final review verdict when required, active-runtime status, known gaps, and blockers.
- Do not label lint, build, a generic gate, source inspection, or a reviewer as feature proof.
- If blocked after recovery, end with `NEED_INPUT: <question>`.

## Reference
- Design: `docs/harness/deep-dive.md`
- Proof and false-green risk: `docs/harness/proof-lifecycle.md`, `docs/harness/oracle-scope.md`
- Autonomy and learning: `docs/harness/autonomous-execution.md`, `docs/harness/repo-autonomy.md`
- Destructive proof and handoff: `docs/harness/destructive-proof-allowlist.md`, `docs/harness/handoff.md`
