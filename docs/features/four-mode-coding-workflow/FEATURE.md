# Four-Mode Coding Workflow

## Goal

Replace the decomposed coding lifecycle with one light, progressively disclosed workflow that helps Codex shape accepted behavior, ship it through realistic proof, fix clear defects, and operate real runtimes without losing durable state or completion truth.

## Behavior

- All coding change work routes through one `coding-workflow` skill. Its public modes are Shape, Ship, Fix, and Operate; the modes are semantic states, not separate skill owners.
- The workflow skill keeps shared invariants in one small entry document and loads only the reference for the active mode plus proof or status references when needed.
- `docs/features/status.json` is mandatory for every repository adopting the harness, including before it contains a feature. Every durable material feature package has exactly one queue entry.
- Version 2 queue entries contain `id`, `feature_dir`, `priority`, `status`, `owner`, `proof_run`, and `notes`. Supported states are `draft`, `ready`, `active`, `blocked`, and `done`. No legacy schema or evidence exception is accepted.
- Shape investigates the repository and asks focused questions only when materially different answers change observable behavior, durable ownership, existing-state compatibility, safety, cost, external effects, or proof feasibility.
- Shape creates one package per independently valuable observable outcome. Every material package always contains `FEATURE.md`, `PROOF.md`, and executable `proof/run.sh`; Shape stops before implementation unless implementation was already authorized.
- Ship claims one explicit or selected `ready` feature as `active`, establishes meaningful red evidence when safe and practical, implements with the relevant domain skills, repairs failures internally, proves the exact named consumption target, obtains one fresh read-only final oracle, and records the retained final passing run before `done`.
- Implementation and review failures inside Ship remain in Ship. A material correction to accepted behavior or proof returns the item to `draft`, updates the package through Shape, and then resumes through `ready` and `active`.
- Fix owns a clear defect with known expected behavior and uses the smallest failing regression and repair. A focused fix does not create a feature package; a defect that invalidates an existing completed feature reopens its entry, and ambiguous or materially new behavior returns to Shape.
- Operate starts with read-only observation of the actual runtime, performs only authorized remediation, and verifies the exact target. A code defect routes to Fix; a missing capability routes to Shape.
- Explicitly requested features take precedence over current-task work, resumable active work, and global priority. Global priority is used only when the user requests queue continuation.
- Multiple independent features may be active in parallel. Each active feature has one nonempty task owner; one task claims at most one material feature. Only that owner may transition its active entry. New tasks never displace another task's work. Same-task replacement releases its own feature; additive same-task work waits unless explicitly delegated. A material correction to the active contract still moves it to `draft`.
- A small `scripts/feature_status` command serializes read-modify-write using an OS lock and atomic replacement, checks expected state and active ownership, and preserves other entries. Shared identity, schema, priorities, and ownership remain validated; package files and proof evidence are validated only for the target feature during updates. Another feature's invalid or unfinished proof, missing package artifacts, or local notes cannot block the target update. Full internal validation still reports collection-wide problems. There is no scheduler, daemon, lease, automatic takeover, or compatibility path.
- Same-checkout parallel work is the default. Independent areas proceed concurrently; overlapping edits have one coordinated writer, and shared server/database changes are coordinated with affected tasks. Before proof through final review, keep the relevant code and runtime inputs stable without freezing the repository. If they change, invalidate and rerun affected proof. Worktrees are optional when explicitly chosen, not required to resolve overlap.
- Green proof followed by broken observed behavior is a proof defect: strengthen the missed activation, state, consumer, read-back, fake, or runtime boundary; demonstrate the miss when practical; repair; rerun; and reevaluate.
- No work category automatically triggers an early review. Use an extra read-only reviewer only when a concrete identified risk warrants it or the user requests it. Ordinary uncertainty is resolved through investigation and material questions, not mandatory review choreography.
- Official proof attempts remain reproducible evidence. Debugging checks are not official attempts; retain meaningful red, materially distinct failures, and final green. Every `done` entry requires a `proof_run` pointing to the latest official attempt inside its own feature, with a retained `PASS`. Missing, failed, malformed, foreign, stale, or unresolved newer evidence prevents completion. Non-done entries clear the pointer. Historical unsupported completion claims become blocked for evidence reconciliation; retained artifacts and previous notes are preserved.
- Fix regression proof exercises the actual risk boundary and required approvals remain intact. A standalone fix needs no package just for an optional early review.
- Ship owns fresh evaluation without a separate public review skill. After passing exact-target proof, Ship starts one fresh read-only final-oracle agent with the user goal, current contracts, retained evidence, named target, and changed surface; it returns `PASS`, `FINDINGS`, or `NEED_INPUT` and never edits or substitutes confidence for proof.
- `PROOF.md` defines the scenarios and tests created specifically to demonstrate them. `proof/run.sh` executes those purpose-built proof tests, not a generic test suite or gate as a substitute. Shared fixture, driver, and assertion utilities may be reused. Internal regression, lint, build, and gate checks remain the agent's responsibility, outside the user-facing proof contract and proof runner.
- After final-oracle `PASS`, Ship performs one completion-only metadata write that records the reviewed latest PASS and moves `active -> done`; this write does not stale the candidate, and the gate validates it without another proof attempt.

## State Transitions

```text
draft -> ready -> active -> done
                    |-> blocked

active|done -> draft   when accepted behavior or proof meaning changes
blocked -> ready       when the external or user-owned blocker is resolved
active -> ready        when a clearly replacing request preempts unchanged work
```

Independent task owners may each have one active feature. Every durable feature directory has all three package artifacts in every persisted state; `draft` describes unresolved decisions rather than an incomplete scaffold. `status.json` is a lifecycle index, not a task list: it contains no subtasks, percentages, implementation plans, requirements, proof explanations, or dependency graph.

## Architecture

- `AGENTS.md` is a compact constitution and routes coding work to `coding-workflow`.
- `skills/coding-workflow/SKILL.md` owns mode selection, shared invariants, transitions, and progressive disclosure.
- `skills/coding-workflow/references/{shape,ship,fix,operate,proof,status}.md` own focused procedures.
- Existing stack and domain skills remain implementation capabilities; they do not own delivery lifecycle state.
- `scripts/gate` validates the mandatory status schema and active workflow structure. `scripts/proof_run_capture` remains the official contained proof runner.
- Current decomposed lifecycle skills, compact duplicate lifecycle skills, their prompt metadata, and duplicated harness rationale are retired rather than kept as compatibility wrappers.

## Constraints

- Keep the installed Impeccable native plugin unchanged; remove only its separate Git-skill declaration and generated ignore entry. Verify the declaration is absent and the plugin remains installed.
- The current checkout is the active Codex home, so script changes apply immediately. Fresh-session skill discovery remains unproven in this already-running task. Stale evidence means an older attempt than the newest official run; relevant candidate edits still require demotion and rerun by workflow policy, not an inferred Git-fingerprint guarantee.

- Preserve explicit implementation authorization, dirty-tree protection, approval boundaries, red/green discipline, exact-target proof, final-candidate freshness, fresh final review, and honest known gaps.
- Preserve unrelated skill-inventory work already present in the working tree.
- Keep historical feature contracts as history even when their former lifecycle architecture is superseded.
- Do not create a workflow engine, todo system, YAML orchestration DSL, daemon, mandatory early reviewer, additional mandatory agents beyond the final review, or per-step status tracking.
- Do not use `coding-app-improvement-review` for this migration.
- The delivery target is this current checkout, which is also the installed Codex home. Executable boundaries are tested here. A currently running task cannot reload its boot-time skill catalog; fresh-session discovery is a separate boundary, not established by source proof.

## Non-Goals

- Replacing Codex task history, compaction, tools, permissions, or plugin runtime.
- Defining application-specific frontend, backend, framework, or deployment architecture.
- Guaranteeing subjective product taste that has not been converted into accepted observable behavior.
- Rebuilding external agent runtimes inside dot-codex.
