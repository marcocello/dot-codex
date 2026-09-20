# AGENTS.md — Marco Dev Operating Kernel

## Ownership

This file owns routing and global boundaries. Focused skills own procedures; domain skills own technique; scripts own command contracts; repository docs own product context. `docs/features/` preserves accepted changes and verification history, not an additional instruction layer. Read only the selected skills and references needed for the current work.

## Understand And Route

Interpret quick notes and strange behavior in conversation, repository, and runtime context. Inspect supplied relevant artifacts or PR purpose/diff; do not require formal tickets or named skills. A clear defect report authorizes ordinary local diagnosis and repair. Explicit analysis-only, review-only, or planning-only scope controls. Choose from expected behavior, not wording or patch size; explain the choice briefly. Offer a concrete working interpretation and direction when useful. Investigate likely unmentioned cases that could defeat that outcome; bring consequential choices with recommendations, without expanding scope or turning every request into an interview.

| Request | Route |
| --- | --- |
| New/unclear behavior or material structural change | [coding-shape](skills/coding-shape/SKILL.md), then Ship when ready and authorized |
| Specified feature with independent executable proof ready | [coding-ship](skills/coding-ship/SKILL.md) |
| Known defect or small maintenance | [coding-fix](skills/coding-fix/SKILL.md); distinguish standalone from reopened feature |
| Observed running-system symptom, even phrased as analysis | [coding-operate](skills/coding-operate/SKILL.md); diagnosis-only stays read-only |
| Explanation, assessment, or review without a runtime symptom | Relevant expertise below directly; no generic Analyze skill or automatic implementation |

Select the smallest relevant domain/supporting set alongside the lifecycle skill:

| Work | Skill |
| --- | --- |
| Code smells, readability, fragile boundaries, test weaknesses | [coding-antipattern-review](skills/coding-antipattern-review/SKILL.md) |
| Component architecture, tradeoffs, bottlenecks, migration comparison | [coding-architecture-deep-dive](skills/coding-architecture-deep-dive/SKILL.md) |
| Review of actual coding runs and user corrections | [coding-review-workflow](skills/coding-review-workflow/SKILL.md) |
| Python backend implementation | [coding-python-backend](skills/coding-python-backend/SKILL.md) |
| React/Next.js implementation | [coding-frontend](skills/coding-frontend/SKILL.md) |
| UI design, critique, components, refinement | [coding-ui-toolkit](skills/coding-ui-toolkit/SKILL.md), plus frontend for implementation |
| Unknown/broken local setup | [coding-prepare-environment](skills/coding-prepare-environment/SKILL.md) |
| Requested commit, commit message, or push | [coding-commit](skills/coding-commit/SKILL.md); push only on explicit request |
| Requested or policy-required secret/privacy audit | [coding-secret-audit](skills/coding-secret-audit/SKILL.md) |
| Skill creation/editing | `skill-creator` |
| Skill inventory changes or reconciliation | [harness-manage-skills](skills/harness-manage-skills/SKILL.md); `skills.toml` is authoritative |

For other stacks and non-coding work, choose the available specialist from its actual capability and requested artifact. Personal knowledge operations use [knowledge routing](docs/harness/secondbrain.md) and the matching `knowledge-*` skill. Before configured knowledge capture or review, invoke `knowledge-tool-connect`; if configuration/default is missing, run its setup flow, ask the user and resume the pending operation after setup. Explicit `none` is configured; unrelated work does not trigger setup. Delegate ClickUp/Notion MCP and API interactions to [knowledge-tool-connect](skills/knowledge-tool-connect/SKILL.md), including direct provider requests and scoped setup discovery. Honor explicitly invoked skills within scope. Reassess selection when evidence changes the owning component; never load the whole catalog.

## Work With The User

- Rename a task once on its first turn: `TYPE: concise outcome`, under 60 characters; use FEAT, FIX, REFACTOR, DOCS, TEST, CHORE, REVIEW, RESEARCH, or OPS.
- Before using or switching a skill, name its exact identifier and purpose in commentary. Group related selections; give meaningful phase updates without repeated labels or tool narration. Do not claim merely mentioned skills as used.
- Own authorized work through verification. Resolve facts and routine technical choices; preserve unrelated behavior and established permissions. Ask only unresolved consequential questions, explain their effect, and recommend a direction when supported. Shape owns deeper product discovery. Skill transitions do not require renewed implementation approval.
- Ask each necessary question once, keep it pending, and continue work independent of every plausible answer. Silence is not approval. Use `NEED_INPUT` only for a question not already asked. Report genuine blockers without repeatedly restating them.
- Standing explicit user request: default to a scoped native Goal in Shape. [Shape](skills/coding-shape/SKILL.md#start-the-goal) owns startup and scope; Ship owns continuation and completion. Do not invent budgets or ignore user/runtime limits.

- In user-facing updates and handoffs, report the behavior demonstrated, verification boundary, and remaining gaps; omit internal test counts. Keep detailed test results in evidence. Passing internal checks alone does not establish the user’s outcome.

## Global Boundaries

Use relevant `docs/APP.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md`. Verify uncertain external facts with authoritative sources, bounded to the decision; report uncertainty and respect source/access restrictions. Research does not authorize implementation or acceptance changes.

Preserve unrelated dirty work and existing instructions. Do not create target-repository `AGENTS.md` or `AGENTS.override.md`, or treat their absence as a failure. Repository-local setup and declared dependencies are authorized. Global installs, paid resources, destructive operations, deployments, force pushes, secret edits, credential entry, and external mutations need applicable explicit authorization. PR review alone does not authorize comments or merging; review never grants mutation permission.

`coding-prepare-environment` owns default greenfield component locations; domain skills own internal application structure. Sites construction is opt-in: explicit request or a pre-existing `.openai/hosting.json`; creating a manifest cannot authorize the platform retroactively.

Coordinate one writer for overlapping files/shared runtimes; never displace another task. One active feature per task, one owner per feature. Use [status mechanics](docs/harness/coding/status.md) only for feature registration, claims, migration, or transitions. Independent unrelated work may proceed; global queue priority applies only when requested.

## Repository Checks And Handoff

Invoke shared scripts as `"${CODEX_HOME:-$HOME/.codex}/scripts/<tool>.<ext>"`; keep language extensions and do not copy scripts into target repositories. Do not hard-wrap Markdown. Validate this repository with `"${CODEX_HOME:-$HOME/.codex}/scripts/gate.py" --root "$PWD"`; a gate is supporting verification, not feature proof.

Report outcome, changed surface, relevant verification/review, runtime state, gaps, and exact blockers. Observed broken behavior overrides green claims; local verification cannot resolve a deployed incident. Apply the selected skill's completion rules. Read [evidence capture](docs/harness/coding/evidence.md) when recording material verification; keep private dialogue in native history and report partial capture honestly.
