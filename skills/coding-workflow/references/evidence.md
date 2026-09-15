# Evidence And Reflection

Retain enough context to explain what was requested, accepted, attempted, verified, and learned. Codex's native task history is the dialogue source; do not build another conversation store.

## Record

For material work, link the task and Goal, requested/effective workflow, actual proof-author/reviewer identities, and skills actually used with their versions or content digests. Retain relevant original dialogue, corrections, interruptions, fixed specification/proof versions, selected regressions and results, review verdict, target/candidate, outcome, and remaining gaps. Record model/time/usage only when available. Retain run context alongside the feature's proof attempts; source dialogue is stored once and referenced.

For independent test-setup repairs, retain original inputs/failure, author identity, exact diff, contract-grounded rationale, revised input versions, and rerun results outside the fixed `PROOF.md`. Keep pending questions and their dependent work in the existing run context; automatic continuation does not create a new question or decision.

For package-free Fix and Analyze, use scoped native task history and linked test/review output. Logging must not create a feature package or trigger a second-brain mutation.

Use supported lifecycle capture where the host has it configured. Native completion/interruption events and later reconciliation should include failed and interrupted runs, not only successful finals. This repository does not currently configure a complete automatic capture integration. Mark unavailable or partial capture explicitly; do not fabricate missing interactions, roles, usage, or timestamps. Native transcript formats are not a stable application contract, so do not add alternate parsers or compatibility readers to conceal unsupported capture.

Keep source dialogue private, redact sensitive content in retained extracts, and exclude hidden reasoning and unrelated conversations. Missing official proof evidence blocks completion; incomplete dialogue capture is reported and retried through supported capture without blocking otherwise valid development.

## Evidence For One Feature

Use `proof_run_capture` for every verification run used to support a material feature's completion. Choose the kind explicitly for supporting regressions; the default remains official proof. Each invocation creates a separate directory and records the kind, exact command arguments, actual working directory, note, start/runtime metadata, stdout/stderr, duration, and final result when execution reaches finalization. An abrupt host or process loss can leave a started attempt without a final result; retain it as incomplete.

Official proof executes the owning feature's `proof/run.sh` from the repository root and stores its attempts in `proof/runs/`. It snapshots `FEATURE.md`, `PROOF.md`, and `run.sh`:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/FEATURE --timeout-seconds 60 --note "verify accepted behavior"
```

Supporting regression capture executes the command after `--` as an argument vector, without implicit shell interpretation. It stores attempts under the owning feature's `tests/runs/` and snapshots `FEATURE.md` and `PROOF.md`. The working directory defaults to the repository root; optional `--cwd` selects an existing directory within that repository:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/FEATURE --kind regression --timeout-seconds 60 --note "check affected behavior" -- .venv/bin/python -m pytest docs/features/FEATURE/tests -q
```

Use actual relevant commands and the required timeout, rather than assuming this example's Python layout. Regression PASS records supporting verification and cannot satisfy `proof_run` or replace feature acceptance. Regression attempts do not supersede the latest official proof attempt. Link relevant run directories in the feature evidence supplied to the final reviewer, including failures and interrupted attempts. Store generated run evidence with the same local/private retention policy as proof attempts.

Direct commands are not monitored automatically. Commands used only for investigation may remain in native conversation; a verification command used to justify completion must run through the appropriate capture mode. Package-free fixes and analyses continue to use scoped native task evidence without creating a feature solely for capture.

Keep user corrections and discussions in the native conversation. Record accepted durable behavior in `FEATURE.md` and link the relevant conversation from feature evidence. During implementation, updates to accepted behavior follow the workflow's user-decision and fixed-acceptance procedures; intermediate discussion does not silently rewrite the specification. Avoid duplicating the full conversation into feature documents.

## Learn Deliberately

Use `coding-review-workflow` on selected real runs. Compare the original request and corrections with current code, accepted contracts, failed/passing attempts, reviews, and outcomes. Current verified evidence outranks historical assistant claims. Distinguish product decisions, discovery mistakes, code/proof defects, environment issues, and reusable harness problems.

Propose the smallest change supported by recurring evidence or a demonstrated harness defect. Pick one owner for the correction: a skill, document, script, test, or configuration. Validate it on the motivating case and a separate case before promoting it; keep, revise, or revert it based on the results. Retained attempts, the diff, checks, and a short rationale suffice; no separate evolution manifest or transition schema is needed. Automatic recording does not authorize automatic global prompt changes. No extra reviewer or learning loop is required on every small fix.

## Native Boundaries

[Codex Goals](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex) own persistent continuation and user/runtime budget controls. [Codex hooks](https://learn.chatgpt.com/docs/hooks) provide lifecycle integration points; their presence in documentation does not establish that this host records every event. The workflow must report actual capability and evidence rather than emulate missing native controls.
