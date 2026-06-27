# AGENTS.md — Marco Dev Operating Contract

## Purpose
- AGENTS.md gives Codex the repo-wide operating contract: what to optimize for, where to route work, and when work is allowed to be called complete.
- Skills own detailed procedures, stack-specific choices, examples, scripts, and reference repos.
- Repo docs own durable project context when present: `docs/APP.md`, `docs/ARCHITECTURE.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md`.
- Do not copy full skill workflows into this file.

## Personal Context Memory
- Treat recurring user preferences, wording patterns, repeated corrections, and workflow
  habits as candidates for the right durable layer.
- Use Codex memories for stable personal context that should help future chats without
  becoming a hard rule.
- Use global or repo `AGENTS.md` guidance for instructions that must reliably apply.
- Use or update a skill when a repeated pattern becomes a reusable workflow with steps,
  references, scripts, or domain-specific judgment.
- Do not store secrets, credentials, or private sensitive details as memory candidates.

## Working Model
- Work one feature or issue at a time.
- For feature work, use one `FEATURE_DIR` at a time.
- Feature description: `FEATURE_DIR/FEATURE.md`.
- Proof contract: `FEATURE_DIR/PROOF.md`.
- FEATURE.md describes what to build. PROOF.md defines how done is proven.
- For non-trivial feature work, PROOF.md must include an anti-gaming review that names fake or incomplete implementations the proof should catch.
- For issue work, first check whether the bug clearly belongs to an existing `docs/features/*/FEATURE.md`.
- If exactly one feature matches an issue, use that `FEATURE_DIR`, run or inspect its `PROOF.md`, and strengthen the proof with a focused failing regression before fixing when the existing proof misses the bug.
- If no feature clearly matches an issue, do not create `FEATURE.md` by default; use the smallest local regression proof unless the expected behavior itself needs durable definition.
- If `FEATURE_DIR` is missing:
  - inspect `docs/features/*/FEATURE.md` for one clear match;
  - use that match when exactly one is clear;
  - otherwise create `docs/features/<request-slug>/FEATURE.md` and `docs/features/<request-slug>/PROOF.md`;
  - ask only when multiple plausible matches would materially change scope.
- Exception: `coding-app-to-features` may bootstrap `docs/APP.md`, `docs/ARCHITECTURE.md`, multiple feature specs, and `docs/features/status.json`; after that, return to one `FEATURE_DIR` at a time.

## Autonomous Work
- `docs/features/status.json` is only a durable progress queue.
- Use `coding-feature-queue` to add, select, and update queue items.
- Use a Codex Goal only for explicit autonomous execution, queue completion, or "keep going until done" work.
- A Goal is runtime state. It does not replace `FEATURE.md`, `PROOF.md`, `status.json`, checks, or evaluator judgment.
- Do not mark a Goal or queue item complete because the implementation looks plausible.
- Feature or queue-item completion requires the primary proof in `PROOF.md`, gate,
  `coding-feature-evaluator`, and queue progress evidence when a queue exists.
- Artifact-authoring work is not the same as feature completion; use the artifact-specific
  checks named by the active skill before claiming that artifact is done.
- Autonomous execution is proof-satisfaction work: while the primary proof is unsatisfied,
  keep working on the code, environment, fixtures, or diagnostics needed to make it pass
  honestly.
- Contract freeze: once implementation code changes begin for a feature, do not edit that
  feature's `FEATURE.md`, `PROOF.md`, or proof artifacts in the same implementation pass.
- If proof, gate, and evaluator pass but credible observed behavior is still broken, treat
  the proof as insufficient, stop implementation, return the item to contract repair, then
  restart implementation after the contract is ready.
- If `coding-feature-evaluator` returns `FAIL`, repair through `coding-repair` or
  `coding-autonomous-execute`.
- If `coding-feature-evaluator` returns `NEED_INPUT`, keep the item `needs_input` and
  report the exact user-owned input or external action needed.
- Use `coding-autonomous-execute` directly only when the user explicitly asks for
  autonomous execution, queue completion, repeated repair, or "keep going until done"
  work. Otherwise, report the repeated failure and recommend autonomous execution.

## Proof Loop
- Autonomous Proof Loop: keep working until the primary proof, gate, and evaluator pass.
- The primary proof is a realistic public-boundary check with a minimal deterministic
  fixture. It proves observable behavior, not source shape.
- Secondary guards support the primary proof; lint, typecheck, unit tests, and static
  checks do not replace it.
- Live validation is separate: use real provider, browser, or API evidence when live state
  matters, but keep a deterministic local proof when live state is user-owned or unstable.
- Before `NEED_INPUT`, inspect the feature/proof, run safe setup/readiness/diagnostics,
  discover tools, retry after each repair, and record what was tried.
- Codex may use any available local CLI, app connector, browser, desktop automation tool,
  MCP tool, repo script, package manager, container tool, cloud CLI, database client, or
  diagnostic command that can help satisfy the proof.
- If a useful tool is missing, suggest the exact install or enablement action and continue
  with any honest lower-fidelity local path.
- Any approval-risk action requires explicit approval: installing global tools, adding
  dependencies, paid/external services, destructive commands, deployments, force pushes,
  secret edits, credential entry, or external account changes.
- Approval-required proof is actionable, not blocked. Request approval for the exact
  destructive or external command with target, effect, and proof reason.
- Destructive proof allowlist: before requesting approval, check
  `.codex/approvals/destructive-proof-allowlist.json` when present. Use the simple shape:
  `{"approvals":[{"id":"...","enabled":true,"cwd":"...","command":"...","target":"provider:resource","expires":"YYYY-MM-DD"}]}`.
  A destructive proof may proceed only when an enabled, unexpired entry exactly matches the
  current `cwd`, full command string, and target. Do not infer approval from similar
  commands. Do not allow wildcards, shell chains, broad delete commands, or unknown targets.
  The allowlist guides repo policy only; platform/runtime approval prompts still take
  precedence when they appear.
- Use `NEED_INPUT` only when the remaining requirement is user-owned or external and no
  honest local path can satisfy the proof.
- Do not stop at the first failed repair. Change tactic and keep the loop tied to proof
  satisfaction.
- Proof Change Guard: if `FEATURE.md`, `PROOF.md`, or proof artifacts must change, make
  that a contract-repair phase before implementation. Record why the old contract was wrong
  or incomplete, what fake implementation the new proof catches, red/green evidence when
  practical, and why scope was not reduced.
- Repeated failures use a tactic ladder: inspect exact output/logs/state, add a diagnostic
  check, identify whether the contract is wrong, move the fix to the owning layer, use the
  relevant domain skill, then retry.

## Project Context
- If `docs/ARCHITECTURE.md` exists, treat it as authoritative and apply it.
- Do not override project architecture unless explicitly asked.
- Read only the current repo's architecture document.
- Keep implementation behavior aligned with `docs/APP.md`, `docs/CONVENTIONS.md`, and `docs/TESTING.md` when those files exist.
- For software project bootstrap or feature execution, make sure the project has a Git repository and use `coding-prepare-environment` to create VS Code run tasks when needed.

## Default Greenfield Architecture
When bootstrapping a greenfield application and no repo architecture overrides it:
- Use stack/domain skills before creating application folders or choosing starters.
- Prefer a React frontend that talks to backend APIs unless the user, repo docs, or selected stack skill points to a different architecture.
- Delegate backend framework, service layering, API details, and backend tree structure to the `coding-python-backend` skill.
- Delegate frontend starter, component system, UI baseline choices, and frontend tree structure to the `coding-frontend` skill.
- Delegate WordPress plugin, theme, full-site, and Bedrock-style tree structure to the `coding-wordpress` skill when WordPress is in scope.
- Keep repo-level docs focused on architecture decisions; do not define application folder structure outside the owning stack/domain skill.

## Skill Routing
- Use `coding-feature-spec` to create or refine `FEATURE.md` and invoke executable proof authoring for non-trivial features.
- Use `coding-proof-author` to create or refine `PROOF.md` and executable proof artifacts.
- Use `coding-feature-quality` before non-trivial implementation when `FEATURE.md` has ambiguity, missing edge cases, weak testability, or possible architecture conflicts.
- Use `coding-feature-execute` to implement a ready feature.
- Use `coding-repair` for a clear reported defect, runtime bug, failing command, gate,
  proof check, typecheck, lint result, or evaluator `FAIL`.
- Use `coding-autonomous-execute` only by the autonomous policy above.
- Use `coding-proof-author` when proof coverage is missing, vague, or weak.
- Use `coding-feature-evaluator` before marking feature or issue work complete.
- Use `coding-prepare-environment` for local setup, dependencies, `.env`, command prefixes, stack-specific preparation, and `.vscode/tasks.json`.
- Use `coding-commit` when the user asks to stage, commit, or draft a commit message.
- Use stack/domain skills for folder structure and implementation details instead of copying those rules here.
- Use reference repos only when the matching skill is active and the current repo lacks a pattern; state the repo and pattern reused in one line.

## Implementation Discipline
- Reuse existing code first.
- Make the smallest change that satisfies the feature or issue.
- Keep changes local; avoid unrelated refactors.
- Avoid backward compatibility work unless explicitly requested.
- Prefer explicit code over cleverness.
- Use red/green TDD for implementation and bug fixes.
- Do not delete, weaken, or bypass tests to get green.

## Universal Lifecycle
- Choose checks by the work product being delivered:
  - Product implementation or issue fix: run the primary proof from
    `FEATURE_DIR/PROOF.md`, the target app repo gate at `$HOME/.codex/scripts/gate`, and
    `coding-feature-evaluator` before calling the feature or fix done.
  - Contract, proof, fixture, or testbed authoring: run the artifact-specific parser,
    contract, lint, fixture, or readiness checks. Live app/provider validation is needed
    only when the task asks for it or claims product behavior now works.
  - Documentation, config, prompt, research, audit, skill, plugin, or message-only work:
    run the smallest relevant structural, factual, style, or syntax check when one
    exists. Do not invent a product proof for non-product artifacts.
- Use `coding-feature-quality` for `FEATURE.md`/`PROOF.md` readiness before
  implementation. Use `coding-feature-evaluator` only for completed implementation or
  issue-fix work.
- If a broader feature proof or repo gate still cannot run because of missing live environment,
  credentials, or unrelated pre-existing failures, report that separately as a
  live-validation or gate blocker. Do not convert a completed artifact-authoring task into
  `NEED_INPUT` unless the requested output was full feature completion and the recovery
  requirements above have been exhausted.
- Treat fixable proof, gate, evaluator, and contract-readiness failures as repair work, not
  input blockers. Use `NEED_INPUT` only for missing input, unavailable external state,
  unreproducible behavior, or a repeated blocker after the recovery requirements above
  have been exhausted.
- When editing this `dot-codex` config repo itself, do not run repo gate or feature
  proof commands unless explicitly asked.
- Do not claim done unless required checks pass or a concrete remaining input is reported.

## Hard Limits
- ≤100 lines per function.
- Cyclomatic complexity ≤8 where tooling exists.
- ≤5 positional parameters.
- 100-character line width unless project tooling is stricter.
- If a limit would make the design worse, state the reason and keep scope tight.

## Zero-Warning Standard
- Treat warnings as defects in touched scope.
- Fix warnings from linters, type checkers, compilers, and test runners.
- If a warning must remain, add a local ignore with a one-line justification.

## Review Order
- Review in this order: architecture → code quality → tests → performance.
- For findings, include concrete impact and file:line references.

## Dependency Hygiene
- When adding or upgrading dependencies, use current stable versions and pin explicitly unless ecosystem conventions prevent it.
- Run stack-appropriate dependency/security audits when dependencies change.
- Do not add dependencies when existing stdlib or repo patterns are sufficient.

## Secret-Bearing Deployment Files
- Preserve existing secret values when editing deployment YAML, Kubernetes manifests, Helm values, Kustomize overlays, `.env` files, and CI/CD deployment files.
- Do not replace them with placeholders such as `secret`, `REDACTED`, or `<secret>`.
- Do not print raw secrets in responses, logs, or summaries.

## Safety
- Do not force push, deploy, or run destructive commands unless explicitly requested and approved.

## Handoff
Default to a short human receipt, not an audit log.

For completed feature or issue work, report in this order:
- First line: `Goal complete: <feature-id>`, `Done: <issue>`, or
  `Needs input: <short reason>`.
- `Outcome`: one to three lines describing the user-visible result.
- `Changed`: grouped bullets, capped at five. Put unrelated required cleanup under
  `Incidental changes`.
- `Verification`: compact status lines only:
  - `Primary proof: <command> -> PASS|FAIL|NOT RUN`
  - `Gate: PASS|FAIL|NOT RUN`
  - `Evaluator: PASS|FAIL|NEED_INPUT`
- `Queue`: only when updated.
- `Goal`: only when a Goal was active; include status and duration. Omit token counts
  unless the Goal had an explicit token budget or the user asked for usage.
- `Blockers`: `none`, or the exact user-owned input/action.

Keep proof red/green evidence concise. Do not include run IDs, prompt text, token counts,
tool/search/command metadata, internal thread IDs, repo paths, or exhaustive skill lists in
the default handoff. Put those details in an optional `Technical appendix` only when the
user asks or an audit/debug handoff requires them.

Do not label gate, evaluator, or secondary checks as proof.

For completed artifact-authoring work, report:
- First line: `Done: <artifact>` or `Needs input: <short reason>`.
- `Outcome`: one to three lines.
- `Created/changed`: grouped bullets, capped at five.
- `Checks`: parser, contract, syntax, fixture, or other narrow artifact checks.
- `Live validation`: `PASS`, `NOT RUN`, or `NEED_INPUT`, only when the artifact is meant to
  run against a live app/provider.
- `Blockers`: `none`, or the exact user-owned input/action. Do not imply the artifact is
  incomplete when only live validation is unavailable.

## Output Token
- If the remaining requirement is user-owned after recovery: `NEED_INPUT: <question>`.
