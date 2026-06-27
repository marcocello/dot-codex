---
name: coding-autonomous-execute
description: "Execute a feature queue, one feature, or a stubborn issue fix through a Codex Goal with explicit PROOF.md verification, evaluator judgment, bounded repair, and queue progress updates. Use when the user asks for autonomous execution, keep-going-until-done behavior, queue completion, or repeated repair after coding-feature-execute or coding-repair."
---

# Autonomous Execute

Purpose: use Codex Goals as the only runtime continuation mechanism for autonomous feature work. Do not introduce scheduler, daemon, or repo-local workflow-engine behavior.

## Runtime Contract
A Codex Goal is thread-scoped runtime continuation. It does not replace the durable
contracts, queue, checks, evaluator, or handoff rules in `AGENTS.md`.

Budget limit is not completion. Mark a Goal complete only by the universal lifecycle in
`AGENTS.md`.

Autonomous execution keeps working until the proof is satisfied. A failed proof, gate, or
evaluator result is the next work item, not a stopping condition.

## Goal Quality Checklist
Before starting or rewriting a Goal, make sure it includes:
- concrete outcome state;
- proof source, gate, evaluator, and queue expectations from `AGENTS.md`;
- starting context or suspected area when known;
- realistic environment requirements when relevant;
- anti-gaming constraints;
- queue or progress artifact for long-running work;
- final cleanup/review before marking complete.

## Goal Templates
Queue:

```text
/goal Complete all ready or repairing items in docs/features/status.json one feature at a time.
For each feature, ensure FEATURE.md and PROOF.md exist, run coding-feature-execute, apply the
AGENTS.md Universal Lifecycle, and keep working until the primary proof, gate, and evaluator
pass. Repair failures, prepare environment, and retry the narrow failing command after each
change. Freeze FEATURE.md, PROOF.md, and proof artifacts once implementation code changes
begin. If the contract is wrong, stop implementation, reset the item to contract repair, and
restart only after the contract is ready. Mark the item done only after the lifecycle passes.
Skip draft and needs_input items. Stop when no ready or repairing items remain, and report any
draft or needs_input items with concrete next input. Do not weaken proof, reduce scope, or
substitute assistant/tool claims for observable evidence.
```

Issue fix:

```text
/goal Fix the reported issue with a regression proof, verified by the failing proof turning green
and the relevant broader check passing. Keep the fix minimal, preserve current behavior outside the
failing path, do not weaken proof, exhaust local recovery attempts, and ask NEED_INPUT only when
the remaining prerequisite is user-owned or external.
```

## Recovery Ladder
Do not mark a queue item `needs_input` until the available recovery paths have been tried.

1. Read `FEATURE.md`, `PROOF.md`, proof artifacts, queue notes, recent run output, and repo
   docs that define setup or proof prerequisites.
2. Discover available tools before `NEED_INPUT`: inspect PATH, repo scripts, Makefiles,
   package scripts, Docker files, docs, MCP/app connectors, browser automation, and local
   app state when relevant.
3. Run available setup, login, readiness, or diagnostic commands that are safe in the
   current sandbox and do not expose secrets.
4. Use `coding-prepare-environment` when the failure is local environment setup.
5. Use `coding-proof-author` when proof lacks a readiness artifact, env template,
   deterministic fallback, or clear live-validation gap.
6. Use `coding-repair` when a setup, readiness, proof, gate, or evaluator failure is
   fixable in the checkout.
7. When a destructive primary proof requires approval, first check
   `.codex/approvals/destructive-proof-allowlist.json` if present.
8. Treat an allowlist entry as valid only when `enabled` is true, `expires` is still valid,
   and `cwd`, full `command`, and `target` exactly match the destructive proof being run.
   The simplified entry shape is:
   `{"id":"hubspot-base-test","enabled":true,"cwd":"...","command":"...","target":"hubspot:<portal-id>","expires":"YYYY-MM-DD"}`.
9. If no exact allowlist match exists, request approval for the exact command, target
   account/resource, expected effect, and proof reason.
10. Do not mark a Goal blocked because proof needs explicit approval; keep the run at
   `needs_input` only if approval is unavailable, denied, or cannot be requested in the
   current runtime.
11. Retry the narrow failing command after each concrete repair or approval.
12. Write the recovery attempts and remaining exact input into queue notes or the handoff.

## Queue Execution
Use this when `docs/features/status.json` exists or the user asks to complete multiple features.

1. Read `docs/features/status.json`.
2. Select the next repairing or ready item with `coding-feature-queue`.
3. Preflight the selected item's `FEATURE.md`, `PROOF.md`, primary proof command, and
   executable proof artifact before marking it `in_progress`.
4. If the contract or proof is missing, stale, weak, or waiting on live prerequisites, use
   the Recovery Ladder before changing status; mark the item `draft` or `needs_input` only
   after the attempted recovery is recorded; do not mark it `in_progress`.
5. Mark the item `in_progress` only after the preflight shows it is implementable.
6. After marking `in_progress`, freeze `FEATURE.md`, `PROOF.md`, and proof artifacts for
   the implementation pass.
7. Work on exactly one `FEATURE_DIR`.
8. Use `coding-feature-execute` for implementation.
9. Apply the `AGENTS.md` Universal Lifecycle.
10. Continue only while the Goal remains active and the next item is clear.

## Persistent Repair Loop
Use this loop when proof, gate, or evaluator judgment fails.

The loop must continue until the primary proof, gate, and evaluator pass.

1. Repair one concrete failure at a time with `coding-repair`.
2. Rerun the narrowest failing check first.
3. Rerun the checks required by the `AGENTS.md` Universal Lifecycle.
4. If the same failure repeats, change tactic: inspect runtime logs, shrink the
   reproduction, prepare missing local environment, or move the fix to the owning boundary.
5. Follow the tactic ladder before asking for input: inspect exact output/logs/state,
   add a diagnostic check around the failing boundary, identify whether the contract proves
   the wrong behavior, move the implementation fix to the owning layer, use the relevant
   domain skill, then retry.
6. Do not ask `NEED_INPUT` because the same non-external failure repeated. Ask only when
   the remaining prerequisite is user-owned or external and no honest local recovery path
   remains.
7. Continue until the primary proof, gate, and evaluator pass.
8. If the failure shows `FEATURE.md`, `PROOF.md`, or proof artifacts are wrong, stop the
   implementation pass. Return the item to contract repair (`draft` when a queue exists),
   update the contract there, then restart implementation from preflight.

## Green-But-Broken Handling
Use this when the primary proof, gate, and evaluator pass but observed product behavior still fails.

1. Treat the result as a proof-system failure, not as completed work.
2. Read the relevant run output, browser/runtime evidence, or agent trace to identify what the proof missed.
3. Do not edit `FEATURE.md`, `PROOF.md`, or proof artifacts while the implementation pass
   still contains code changes.
4. Stop implementation and return the item to contract repair (`draft` when a queue exists).
5. Use `coding-proof-author` in that contract-repair phase to add or strengthen a failing
   proof for the observed broken behavior.
6. Restart implementation only after the strengthened proof fails for the right reason.
7. Rerun the checks required by the `AGENTS.md` Universal Lifecycle before marking the item done.

## Boundaries
- Do not use Goals for one-line edits, simple explanations, vague improvement requests, or work without an auditable finish line.
- Do not run multiple autonomous Codex sessions against the same checkout.
- Use an isolated `codex/` branch or worktree for independent background tasks.
- Do not auto-approve destructive commands, force pushes, deploy actions, or secret edits.
- Use the proof and handoff terminology from `AGENTS.md`.
- Do not continue treating an item as done after credible green-but-broken evidence.

## Handoff
Report using the `AGENTS.md` short receipt format for completed feature or issue work.

Default autonomous output is a human receipt, not an execution transcript:
- lead with `Goal complete`, `Done`, or `Needs input`;
- summarize the outcome before file paths;
- keep verification to primary proof, gate, and evaluator status lines;
- mention queue and goal state only when relevant;
- omit token counts, run IDs, internal thread IDs, prompt text, tool metadata, and exhaustive
  skill lists unless the user asks for an audit/debug appendix or an explicit token budget
  requires usage reporting.
