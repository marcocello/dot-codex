# AGENTS.md - Marco Dev Operating Kernel

## Authority

- `docs/harness/coding-workflow.md` is the coding design. `coding-workflow` owns lifecycle; domain skills own technique; scripts own command contracts; repository docs own product context.
- Invoke shared tools as `"${CODEX_HOME:-$HOME/.codex}/scripts/<tool>"`; do not copy them into target repositories.
- Route non-coding personal operations through `docs/harness/secondbrain.md` and the matching `second-brain-*` skill.
- `skills.toml` owns the desired skill inventory. Use `codex-manage-skills` through `skill_inventory.py`; `docs/harness/skill-management.md` defines ownership, reconciliation, and updates.
- `docs/harness/` describes current operating rules. `docs/features/` records dot-codex changes, accepted decisions, and verification evidence; earlier specifications remain change history.

## Start And Route

- Rename a task once on its first turn as `TYPE: concise outcome`, under 60 characters. Use `FEAT`, `FIX`, `REFACTOR`, `DOCS`, `TEST`, `CHORE`, `REVIEW`, `RESEARCH`, or `OPS`.
- Use `coding-workflow`: Shape new or unclear behavior; Ship an authorized ready feature; Fix known broken behavior or small maintenance; Analyze a question or architecture; Operate a runtime symptom. An explicitly invoked skill never bypasses this assessment.
- Read only the active mode reference and its relevant shared references. Direct analytical skills remain available.
- Shape uses conversation to resolve consequential journeys, corner cases, boundaries, and compatibility. Record accepted behavior and existing behavior to preserve in `FEATURE.md`. Human document sign-off is optional; existing build authorization carries through discovery. Analysis/specification-only requests stop at their deliverable.
- Organize tests with the features they verify. Keep dedicated acceptance in the feature's `proof/` directory and internal regression tests alongside the owning feature, separately from frozen acceptance; follow `skills/coding-workflow/references/proof.md` for placement and ownership.
- A separate agent writes `PROOF.md`, dedicated acceptance tests, and executable `proof/run.sh` from the specification, original conversation/corrections, and target before implementation. Missing decisions return to Shape; unavailable independent authorship must not be replaced by implementer-authored acceptance.
- Every material feature has one package and status entry; `docs/features/status.json` is mandatory after adoption. Automatically migrate an existing old-format index to the current schema without asking permission; follow `skills/coding-workflow/references/status.md`. A standalone focused Fix or Analyze needs no package. Use `feature_status` for atomic claims and transitions after migration.
- Independent tasks may share a checkout, with one owner per active feature and one active feature per task. Coordinate overlapping writes and shared runtime changes; never displace another task. Global priority applies only to requested queue continuation.

## Execution And Acceptance

- Apply relevant current `docs/APP.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md` sections. Investigate facts; ask when choices materially change behavior, ownership, scope, compatibility, cost, data, permissions, external effects, or proof feasibility.
- Use native Goals for material Ship within explicit user/runtime authorization and supported tool controls. A normal build request alone does not authorize Goal creation. Honor the user's configured allowance; never invent, reset, or extend a budget or emulate persistence with another loop. Stop at the runtime limit or user interruption. Missing input/access pauses dependent work; continue authorized independent work. Stopped is not complete.
- Keep `FEATURE.md`, `PROOF.md`, and acceptance requirements fixed. Only the independent proof author may repair demonstrably faulty test setup without approval, preserving scenarios, assertions, outcomes, and test boundaries; retain the correction and rerun proof under `skills/coding-workflow/references/proof.md`. Implementers cannot edit frozen proof inputs. Acceptance changes or unresolved meaning require a user decision; switching modes cannot bypass this rule.
- Normally complete the agreed feature before a later behavior request starts a new change cycle. Preserve previous specifications and evidence. After correction, restate the accepted direction before editing.
- During implementation, select regression checks from actual impact; run all when cheap or broadly justified. Repair introduced regressions inside the current feature's Goal and allowance. Do not create a package/reviewer per affected feature. Evidenced unrelated pre-existing failures are reported separately.
- Material completion requires realistic proof on the named consumption target, affected regression verification, and one fresh separate read-only final reviewer PASS on unchanged relevant inputs. The reviewer is distinct from the implementer and proof author. Early review is discretionary for a concrete risk or explicit request.
- A standalone focused Fix completes after its focused check and affected regressions. A defect invalidating delivered feature behavior reopens its existing proof/review obligations; regressions introduced during active Ship remain in that run.
- Observed broken behavior overrides green evidence. Preserve the failed claim and distinguish code repair, independent test-setup repair, and a user-owned acceptance decision. Generic tests, gates, builds, and lint support verification but never replace feature proof.

## Boundaries

- Stack/domain skills own application source structure. Sites is opt-in for application construction: use it only when explicitly requested or `.openai/hosting.json` existed before the task began. A platform manifest created during the current task cannot retroactively authorize that platform.
- Do not create `AGENTS.md` or `AGENTS.override.md` in target repositories. Preserve existing instructions; their absence must not be treated as a gate failure.
- Preserve unrelated dirty work. Repository-local setup and declared dependencies are authorized. Global installs, paid resources, destructive operations, deployments, force pushes, secret edits, credential entry, and external mutations require applicable explicit authorization. Review is not mutation permission.
- Do not hard-wrap Markdown prose. Validate this repository with `"${CODEX_HOME:-$HOME/.codex}/scripts/gate" --root "$PWD"`. The gate checks repository structure, feature-status records, skill metadata and references, configuration hygiene, and applicable runtime prerequisites. Run feature proof and affected regressions separately; gate PASS does not imply test-suite execution.

## Evidence And Handoff

- Retain relevant native dialogue/corrections, skill versions, role/Goal links, proof attempts, regressions, review, and outcome. Mark missing capture as partial; never fabricate history. `coding-app-improvement-review` proposes deliberate improvements from actual runs. Capture official proof and completion-supporting feature regressions through the separate modes of `proof_run_capture`. Follow `skills/coding-workflow/references/evidence.md` for the detailed evidence and learning procedure.
- Lead with outcome, changed surface, proof or focused regression, required final review, runtime state, gaps, and exact blocker. Local verification does not resolve a deployed incident; verify the original symptom after deployment.
- Ask each necessary question once and retain the pending decision. Use `NEED_INPUT: <question>` only if it has not already been asked; automatic continuations must not repeat it or unchanged rule explanations. Follow native blocked-state criteria when no independent work remains. Approval and operational details: `docs/harness/safety.md`.
