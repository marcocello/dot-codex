# AGENTS.md - Marco Dev Operating Contract

## Scope
- `AGENTS.md` owns hard operating rules; skills own procedures, examples, stack choices, scripts; repo docs own context.
- Repo context files when present: `docs/APP.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, `docs/TESTING.md`; harness detail lives in `docs/harness/`.
- Do not copy full skill workflows into this file.
- Non-coding request? Read `docs/secondbrain.md` first. Applies outside code, feature execution, issue repair, review, deployment, repo maintenance, software artifacts.
- Notion, Second Brain, notes, Granola, Gmail, Zotero, deals, briefs: use `docs/secondbrain.md` plus matching `second-brain-*` skill.
- Codex memories: stable preferences, recurring corrections, workflow habits. `AGENTS.md`: rules that must apply. Skills: reusable workflows. No secrets, credentials, private sensitive details.

## Operating Model
- Work on one feature or issue, and one `FEATURE_DIR`, at a time.
- `FEATURE_DIR/FEATURE.md`: behavior contract.
- `FEATURE_DIR/PROOF.md`: proof contract.
- Non-trivial `PROOF.md`: anti-gaming review with fake-pass risks.
- For issue work, first check whether the bug clearly belongs to `docs/features/*/FEATURE.md`.
- Exactly one match: use that `FEATURE_DIR`; strengthen proof with a focused failing regression if current proof misses the bug.
- No clear match: do not create `FEATURE.md` by default; use smallest local regression proof unless behavior needs durable definition.
- Missing `FEATURE_DIR`: inspect existing features; use one clear match; otherwise create `docs/features/<request-slug>/FEATURE.md` and `PROOF.md`.
- `coding-app-to-features` may bootstrap app docs, multiple features, and queue; after that, return to one `FEATURE_DIR`.
- `docs/features/status.json`: queue index only.
- Codex Goal: runtime continuation only; it does not replace `FEATURE.md`, `PROOF.md`, queue, checks, evaluator.
- Use `coding-autonomous-execute` only for explicit autonomous execution, queue completion, repeated repair, or "keep going until done".
- Autonomous execution is proof-satisfaction work: while the primary proof is unsatisfied, keep working on code, environment, fixtures, diagnostics.

## Proof And Completion
- Autonomous Proof Loop: keep working until the primary proof, gate, and evaluator pass.
- The primary proof is a realistic public-boundary check with a minimal deterministic fixture. It proves observable behavior, not source shape.
- Serious proof runs: prefer `FEATURE_DIR/proof/runs/<timestamp>/` evidence bundle with command output, result metadata, logs, screenshots, provider read-back, or unavailable evidence note. Use `scripts/proof_run_capture` when command-wrappable.
- Secondary guards support the primary proof; lint, typecheck, unit tests, static checks do not replace it.
- Live validation is separate: real provider/browser/API evidence when live state matters; deterministic local proof when live state is user-owned or unstable.
- Product implementation or issue fix completion requires primary proof from `FEATURE_DIR/PROOF.md`, target repo gate at `$HOME/.codex/scripts/gate`, `coding-feature-evaluator`, and queue evidence when a queue exists.
- Contract/proof/fixture/testbed work uses artifact parser, contract, lint, fixture, or readiness checks. Docs/config/prompt/research/audit/skill/plugin/message work uses the smallest relevant structural/factual/style/syntax check. No invented product proof.
- Use `coding-feature-quality` before implementation when contracts need readiness review; use `coding-feature-evaluator` only for completed implementation or issue fix.
- Evaluator `FAIL`: repair through `coding-repair` or `coding-autonomous-execute`. Evaluator `NEED_INPUT`: mark `needs_input`; report exact user-owned input/action.
- Missing live env, credentials, or unrelated gate failure: report separately; do not turn artifact work into `NEED_INPUT`.
- Fixable proof, gate, evaluator, or contract failures are repair work, not input blockers.
- Before `NEED_INPUT`: inspect feature/proof, setup, readiness, diagnostics; discover tools; retry after repair; record attempts.
- Codex may use any available local CLI, app connector, browser, desktop automation tool, MCP tool, repo script, package manager, container tool, cloud CLI, database client, or diagnostic command that can help satisfy proof.
- Useful tool missing: suggest exact install/enablement; continue with honest lower-fidelity local path.
- Use `NEED_INPUT` only for user-owned/external requirements with no honest local path.
- Do not stop at the first failed repair. Change tactic; stay tied to proof satisfaction.
- Contract freeze: once implementation code changes begin, do not edit that feature's `FEATURE.md`, `PROOF.md`, or proof artifacts in the same implementation pass.
- Proof Change Guard: if `FEATURE.md`, `PROOF.md`, or proof artifacts must change, return to contract repair first. Record old-contract flaw, fake caught, red/green evidence when practical, and why scope was not reduced.
- Green but broken: if proof/gate/evaluator pass but credible observed behavior is still broken, treat proof as insufficient; return to contract repair; restart after ready.
- Repeated failures: inspect output/logs/state, add diagnostic, check contract correctness, move fix to owning layer, use domain skill, retry.
- Editing this `dot-codex` config: do not run repo gate or feature proofs unless asked. Use `scripts/gate_config` for harness checks.
- If `docs/features/status.json` exists, `done` entries need completion evidence passing `scripts/validate_feature_queue`.
- Do not claim done unless required checks pass or exact remaining input is reported.

## Context And Routing
- If `docs/ARCHITECTURE.md` exists, apply it; do not override project architecture unless asked; read only current repo architecture.
- Align with `docs/APP.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md` when present.
- Software bootstrap/execution: ensure Git repo; use `coding-prepare-environment` when setup/tasks are needed.
- Greenfield default: use stack/domain skills before app folders or starters; React frontend talks to backend APIs unless user/docs/skill says otherwise.
- Stack ownership: backend tree/API/service details -> `coding-python-backend`; frontend starter/components/UI baseline -> `coding-frontend`; WordPress structure -> `coding-wordpress`.
- Repo docs explain decisions; stack/domain skills own folder structure and implementation details.
- Skill map: spec -> `coding-feature-spec`; proof -> `coding-proof-author`; contract review -> `coding-feature-quality`; implementation -> `coding-feature-execute`.
- Repair: `coding-repair` for clear defect, runtime bug, failing command, gate, proof check, typecheck, lint result, evaluator `FAIL`.
- Autonomous: `coding-autonomous-execute` by policy above; done judge -> `coding-feature-evaluator`; setup/env -> `coding-prepare-environment`; commit -> `coding-commit` only when asked.
- Reference repos only when active skill allows; name reused pattern.

## Constraints
- Reuse existing code first; make the smallest change that satisfies feature/issue; keep changes local with no unrelated refactors.
- No backward compatibility unless asked; explicit over clever; red/green TDD for implementation and bugs; do not delete, weaken, or bypass tests for green.
- Code limits: function <=100 lines; cyclomatic complexity <=8 where tooling exists; positional params <=5.
- Line width 100 chars for code/config unless stricter tooling; if a limit worsens design, state why and keep scope tight.
- Markdown Writing: do not hard-wrap prose in Markdown files; keep each paragraph on one physical line unless a list, table, code block, or template requires line breaks; line-width limits apply to code/config, not Markdown prose.
- Warnings are defects in touched scope.
- Dependency changes: current stable, pinned when normal, audit when changed.
- Review order: architecture -> code quality -> tests -> performance.
- Secret-bearing deployment files: preserve values; no placeholders; do not print secrets.

## Safety
- Approval-risk action requires explicit approval: installing global tools, dependencies, paid/external services, destructive commands, deployments, force pushes, secret edits, credential entry, external account changes.
- Approval-required proof is actionable, not blocked. Request approval for the exact command, target, effect, proof reason.
- Destructive proof allowlist: before requesting approval, check `.codex/approvals/destructive-proof-allowlist.json` when present. Shape: `{"approvals":[{"id":"...","enabled":true,"cwd":"...","command":"...","target":"provider:resource","expires":"YYYY-MM-DD"}]}`.
- Proceed only when enabled, unexpired, and exactly matches the current `cwd`, full command string, and target. Do not infer from similar commands.
- Do not allow wildcards, shell chains, broad delete commands, unknown targets. The allowlist is repo policy only; platform/runtime approval prompts still take precedence.
- No force push, deploy, destructive command unless explicitly requested and approved.

## Handoff
- Default to a short human receipt, not an audit log.
- Completed feature/issue: First line: `Goal complete: <feature-id>`, `Done: <issue>`, or `Needs input: <reason>`.
  - `Outcome`: one to three lines.
  - `Changed`: grouped bullets, capped at five.
  - `Verification`: compact status lines only: `Primary proof`, `Gate`, `Evaluator`. Use `Gate: PASS|FAIL|NOT RUN` and `Evaluator: PASS|FAIL|NEED_INPUT`.
  - `Queue` only when updated; `Goal` only when active; `Blockers`: `none` or exact user-owned input/action.
- Artifact work: `Done: <artifact>` or `Needs input: <reason>`.
  - `Outcome`, `Created/changed`, `Checks`, optional `Live validation`, `Blockers`.
- Do not label gate, evaluator, or secondary checks as proof.
- Omit token counts, run IDs, prompt text, tool metadata, internal thread IDs, exhaustive skill lists unless user asks for optional `Technical appendix`.

## Output Token
- If remaining requirement is user-owned after recovery: `NEED_INPUT: <question>`.
