---
name: coding-autonomous-execute
description: "Execute a feature queue, one feature, or a stubborn issue fix through a Codex Goal with explicit PROOF.md verification, evaluator judgment, bounded repair, and queue progress updates. Use when the user asks for autonomous execution, keep-going-until-done behavior, queue completion, or repeated repair after coding-feature-execute or coding-repair."
---

# Autonomous Execute

Purpose: Codex Goal = runtime continuation. No scheduler, daemon, workflow engine.

## Contract
- Goal does not replace contracts, queue, checks, evaluator, handoff rules in `AGENTS.md`.
- Budget limit is not completion.
- Failed proof/gate/evaluator output is next work item, not stopping condition.

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

Issue:

```text
/goal Fix the reported issue with a regression proof, verified by the failing proof turning green
and the relevant broader check passing. Keep the fix minimal, preserve current behavior outside the
failing path, do not weaken proof, exhaust local recovery attempts, and ask NEED_INPUT only when
the remaining prerequisite is user-owned or external.
```

## Recovery Ladder
Do not mark a queue item `needs_input` until available recovery paths have been tried.

1. Read `FEATURE.md`, `PROOF.md`, proof artifacts, queue notes, recent run output, setup docs.
2. Discover available tools before `NEED_INPUT`: inspect PATH, repo scripts, Makefiles,
   package scripts, Docker files, docs, MCP/app connectors, browser automation, local app state.
3. Run available setup, login, readiness, or diagnostic commands when safe and non-secret.
4. Use `coding-prepare-environment` for local environment failure.
5. Use `coding-proof-author` for missing readiness artifact, env template, deterministic fallback, or live-validation gap.
6. Use `coding-repair` for fixable setup/readiness/proof/gate/evaluator failure.
7. When a destructive primary proof requires approval, first check
   `.codex/approvals/destructive-proof-allowlist.json` if present.
8. Allowlist valid only when `enabled`, unexpired, and `cwd`, full `command`, and `target` exactly match the destructive proof.
   Example:
   `{"id":"hubspot-base-test","enabled":true,"cwd":"...","command":"...","target":"hubspot:example-portal","expires":"YYYY-MM-DD"}`.
9. No exact match: request approval for exact command, target, effect, proof reason.
10. Do not mark a Goal blocked because proof needs explicit approval; use `needs_input` only if approval unavailable/denied/unrequestable.
11. Retry the narrow failing command after each repair or approval.
12. Record attempts and remaining exact input in queue notes or handoff.

## Queue Execution
- Read `docs/features/status.json`.
- Select the next repairing or ready item with `coding-feature-queue`.
- Preflight the selected item's `FEATURE.md`, `PROOF.md`, primary proof command, executable proof artifact before marking it `in_progress`.
- Missing/stale/weak/live-blocked contract: use Recovery Ladder; mark `draft` or `needs_input` only after recorded recovery; do not mark it `in_progress`.
- Mark the item `in_progress` only after the preflight shows it is implementable.
- Then freeze `FEATURE.md`, `PROOF.md`, and proof artifacts.
- Work exactly one `FEATURE_DIR`.
- Use `coding-feature-execute`.
- Apply `AGENTS.md` Universal Lifecycle.

## Persistent Repair Loop
Use when proof, gate, or evaluator judgment fails.

The loop must continue until the primary proof, gate, and evaluator pass.

1. Repair one concrete failure at a time with `coding-repair`.
2. Rerun narrowest failing check first.
3. Rerun lifecycle checks.
4. Same failure repeats: change tactic.
5. Follow the tactic ladder: inspect exact output/logs/state, add a diagnostic check, verify contract,
   move fix to owning layer, use relevant domain skill, retry.
6. Do not ask `NEED_INPUT` because the same non-external failure repeated. Ask only when
   remaining prerequisite is user-owned/external and no honest local recovery path remains.
7. Continue until the primary proof, gate, and evaluator pass.
8. Contract/proof wrong: stop the implementation pass. Return the item to contract repair
   (`draft` when queue exists), update contract, restart from preflight.

## Agent Observation
Write or update `FEATURE_DIR/proof/runs/<timestamp>/agent-observation.md` when a current proof bundle exists and one of these happens: proof fails more than once, tactic changes, `NEED_INPUT` is reported, evaluator returns `FAIL`, green-but-broken handling starts, or contract repair is needed after implementation started.

Also write `agent-observation.json` when the observation exposes a reusable signal: asked user too early, skipped local recovery, fake proof attempted, repeated same tactic, ignored repo architecture, or contract changed after code. Use schema version 1 from `docs/harness/proof-lifecycle.md`.

If there is no current proof bundle, put the same short note in queue notes or handoff.

Keep it concise, not a transcript. Include: context loaded, routing decision, failure pattern, repairs attempted, tactic change, contract status, and remaining risk. Do not include prompts, token counts, exhaustive file lists, or long logs.

## Green-But-Broken Handling
Use this when primary proof, gate, evaluator pass but observed product behavior still fails.

1. Treat as proof-system failure.
2. Inspect run output, browser/runtime evidence, or trace; identify what proof missed.
3. Do not edit `FEATURE.md`, `PROOF.md`, or proof artifacts while implementation pass has
   code changes.
4. Stop implementation. Return the item to contract repair.
5. Use `coding-proof-author` in that contract-repair phase to add or strengthen a failing
   proof for the observed broken behavior.
6. Restart only after strengthened proof fails for right reason.
7. Rerun `AGENTS.md` Universal Lifecycle before done.
8. Record the proof-system failure and contract status in `agent-observation.md` or queue notes.

## Boundaries
- No Goals for one-line edits, simple explanations, vague improvement requests, no finish line.
- Do not run multiple autonomous Codex sessions against same checkout.
- Use isolated `codex/` branch or worktree for independent background tasks.
- No auto-approval for destructive commands, force pushes, deploys, secret edits.
- Use proof/handoff terms from `AGENTS.md`.
- Do not treat green-but-broken item as done.

## Handoff
Report using the `AGENTS.md` short receipt format for completed feature or issue work.

Default autonomous output is a human receipt, not an execution transcript.
- lead with `Goal complete`, `Done`, or `Needs input`;
- outcome before file paths;
- verification only primary proof, gate, evaluator;
- queue/goal only when relevant;
- omit token counts, run IDs, internal thread IDs, prompt text, tool metadata, exhaustive
  skill lists
  unless user asks for audit/debug appendix or explicit token budget requires usage.
