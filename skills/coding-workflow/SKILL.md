---
name: coding-workflow
description: "Route coding requests through Shape, Ship, Fix, Analyze, or Operate with independent proof authorship, fixed acceptance, native Goals, proportional regression checks, and retained evidence."
---

# Coding Workflow

Own the lifecycle while domain skills supply implementation or analytical expertise. Read only the active mode reference and relevant shared references; read the new reference when the mode changes.

## Route

| Request | Path and reference |
|---|---|
| New capability, changed behavior, unresolved scope, or material structural change | [Shape](references/shape.md), then Ship when implementation is authorized |
| One specified feature with independently authored executable proof ready | [Ship](references/ship.md) |
| Known defect or small maintenance | [Fix](references/fix.md) |
| Explanation, architecture assessment, or review | [Analyze](references/analyze.md) |
| Symptom in a running system | [Operate](references/operate.md) |

An invoked skill does not determine scope. Restoring a broken export is Fix, adding export is Shape → Ship, and a typo or small cleanup stays light. A complex repair can still be Fix. Explain a changed route and discuss unresolved behavior; do not add approval when authorization already exists.

Choose the route from expected behavior, not the ticket wording (“implement”), estimated effort, or patch size. When entering Fix, state whether it is standalone or reopens an existing feature, why, and which verification is required for completion; see [Fix](references/fix.md). A small patch does not remove an existing feature's proof obligations.

## Shared Rules

- Apply relevant repository product, architecture, convention, and testing context. Investigate facts and ask only questions whose answers materially change accepted behavior or consequences.
- Material features own `FEATURE.md`, `PROOF.md`, executable `proof/run.sh`, and a mandatory adopted-repository status entry. Use [status.md](references/status.md) for automatic old-format migration, registration, ownership, and transitions. Migration is authorized local setup, not a permission question. Standalone fixes and analyses remain package-free.
- Organize tests with the features they verify. Dedicated acceptance lives in the feature's `proof/` directory; implementer-authored regression tests stay alongside the owning feature, separately from frozen acceptance. Follow [proof.md](references/proof.md) for framework placement, ownership, and maintenance.
- Shape establishes behavior through conversation. A separate proof author works from the specification and relevant original dialogue before implementation; use [proof.md](references/proof.md). Human document sign-off is optional.
- Material Ship uses explicitly authorized native Goal execution and user/runtime limits. Follow actual tool authority; no substitute loops, invented budgets, or silent budget extension.
- Keep `FEATURE.md`, `PROOF.md`, and acceptance requirements fixed. Only the independent proof author may correct demonstrably faulty test setup under [proof.md](references/proof.md), preserving scenarios, assertions, outcomes, and test boundaries. Implementers repair application code and can add internal regression tests. Acceptance changes or unresolved meaning need a user decision before dependent work resumes.
- Regressions introduced during Ship stay within that feature's task, Goal, allowance, and final review. Run checks proportional to actual impact; report evidenced unrelated pre-existing failures separately.
- Name the consumption target. Relevant candidate/runtime changes invalidate proof and final review. Observed broken behavior overrides green claims; distinguish code repair, independent setup repair, and a user-owned acceptance decision.
- Preserve unrelated work, applicable approvals, and one owner per active feature. Coordinate shared writes/runtime resources; never take over another task. Queue priority applies only when the user asks to continue the queue.
- Retain contextual evidence through [evidence.md](references/evidence.md). Capture official proof and completion-supporting feature regressions separately with `proof_run_capture`. Missing dialogue capture is explicit, not invented, and does not block otherwise valid coding.

## Steering

Ordinary repair, independent setup corrections, and compatible guidance stay in the current run. A later behavior request normally begins a new Shape → Ship cycle after completion. Honor explicit interruption. A necessary acceptance decision pauses dependent work and preserves its evidence; ask once and continue authorized work independent of every plausible answer. Revise specification, independently authored proof, and Goal together only after that decision. Automatic continuations must not repeat unanswered questions or unchanged explanations; use native blocked controls only when their criteria are met and no independent work remains. Mode changes cannot bypass fixed acceptance.

An analysis or specification request ends at its requested deliverable. Already authorized implementation continues in the same task when ready. Independent analytical skills remain directly invocable; a skill name never authorizes unrelated changes.

## Review And Completion

Use an early read-only reviewer only for a concrete risk or explicit request. Material delivery requires one fresh separate final reviewer after successful proof and affected regression verification. It is distinct from implementer and proof author. A standalone focused Fix has no mandatory reviewer.

Report outcome, changed surface, proof or focused check, final reviewer when required, runtime state, known gaps, and exact blocker. Review never grants mutation permission. A missing required capability or external dependency is surfaced explicitly; no fallback or backward-compatibility path is part of this workflow.
