# Harness Operator Map

## Current Harness Workflow

The normal coding workflow is:

1. Turn intent into one `FEATURE.md`.
2. Turn that feature contract into one `PROOF.md` plus executable proof artifacts.
3. Run the primary proof through the real boundary that matters: UI, API, provider, database, CLI, migration, or workflow.
4. Capture the proof result in `FEATURE_DIR/proof/runs/<timestamp>/` when practical.
5. Repair implementation, setup, fixtures, or diagnostics until the primary proof passes.
6. Run the target repo gate.
7. Run `coding-feature-evaluator` as the skeptical done judge.
8. If a queue exists, update `docs/features/status.json` only after proof, gate, evaluator, and latest evidence are recorded.

Compact version:

```text
FEATURE.md -> PROOF.md -> realistic proof -> evidence bundle -> repair loop -> gate -> evaluator -> queue done
```

For explicit autonomous work, a Codex Goal keeps the run moving, but the Goal is only runtime state. It does not replace `FEATURE.md`, `PROOF.md`, the queue, proof output, gate results, or evaluator judgment.

## Harness Shape

The skills split responsibility instead of repeating one large workflow everywhere.

- `coding-feature-spec`: intent to feature contract.
- `coding-proof-author`: feature contract to executable proof and anti-gaming pressure.
- `coding-feature-execute`: implementation of a ready feature.
- `coding-repair`: concrete failure, bug, proof failure, lint failure, typecheck failure, gate failure, or evaluator failure.
- `coding-autonomous-execute`: explicit autonomous execution or queue completion across proof, gate, evaluator, and repair loops.

`AGENTS.md` owns the operating kernel. Skill files own local procedure. Harness docs own durable detail.

## Harness Docs

- Proof lifecycle and run evidence bundles: [`docs/harness/proof-lifecycle.md`](proof-lifecycle.md).
- Autonomous execution and recovery before `NEED_INPUT`: [`docs/harness/autonomous-execution.md`](autonomous-execution.md).
- Destructive-proof allowlists: [`docs/harness/destructive-proof-allowlist.md`](destructive-proof-allowlist.md).
- Concise handoffs: [`docs/harness/handoff.md`](handoff.md).
- Memory policy: [`docs/harness/memory-policy.md`](memory-policy.md).
- Harness evolution notes and change manifests: [`docs/harness/evolution`](evolution).

## Repo Helpers

- `scripts/proof_run_capture` wraps a proof command and writes a run evidence bundle.
- `scripts/validate_feature_queue` rejects `done` queue items without recorded proof, gate, evaluator, and latest evidence.
- `scripts/harness_review` summarizes proof bundles and harness change manifests.
- `scripts/gate_config` runs the dot-codex harness checks.

## Proof Evidence

Serious proofs should leave evidence behind when practical:

```text
FEATURE_DIR/proof/runs/<timestamp>/
  command.txt
  stdout.txt
  stderr.txt
  result.json
  screenshots/
  logs/
  provider-readback.json
  notes.md
```

Only real evidence belongs in that folder. Empty screenshots, invented logs, and fake provider read-back are worse than a clear note saying the evidence was unavailable.

For local proof commands, use:

```bash
scripts/proof_run_capture --feature-dir FEATURE_DIR -- <primary proof command>
```

The helper exits with the wrapped command's status, so it can be used directly as the primary proof command or inside a proof runner.

## Queue Completion

`docs/features/status.json` is a progress index, not a workflow engine. The authoritative contracts remain `FEATURE.md` and `PROOF.md`.

A queue item should be marked `done` only when it records:

```json
{
  "completion": {
    "primary_proof": "PASS",
    "gate": "PASS",
    "evaluator": "PASS",
    "latest_evidence": "docs/features/<feature>/proof/runs/<timestamp>"
  }
}
```

`scripts/validate_feature_queue` enforces this shape for `done` items when a status file exists.

## Harness Evolution

The harness should improve when repeated failures expose a weak instruction, weak proof, missing tool, or missing diagnostic.

```text
observed failure -> failure pattern -> change manifest -> harness change -> verification -> accepted or rejected pattern
```

This is intentionally lighter than a workflow engine. It is meant to stop random prompt tweaks and make harness changes explainable.

## Safety And Handoff

Some realistic proofs need cleanup, sends, writes, or provider mutations. Those actions need explicit approval unless a narrow, unexpired entry exists in `.codex/approvals/destructive-proof-allowlist.json`.

Default handoffs are short receipts:

```text
Done: <issue>
Outcome: <one to three lines>
Changed: <grouped bullets>
Verification:
- Primary proof: <command> -> PASS|FAIL|NOT RUN
- Gate: PASS|FAIL|NOT RUN
- Evaluator: PASS|FAIL|NEED_INPUT
Blockers: none | <exact user-owned input/action>
```

The final answer should summarize the real result, not dump the whole execution transcript.

## Current Limits

This config is strong enough to force contract-first, proof-first coding behavior. It is not yet a fully automatic harness-evolution system.

- Proof evidence capture exists, but app-specific proof runners still need to use it.
- Browser, provider, video, and log capture are supported by convention, but not yet automatically generated for every stack.
- `scripts/harness_review` summarizes evidence and manifests; it does not yet create or judge harness changes by itself.
- Queue completion validation applies when repos use `docs/features/status.json` with the completion shape above.
- Live validation still depends on credentials, safe targets, external services, and user approval for risky actions.

## Non-Coding Work

Not all useful Codex work is coding work. Personal operating workflows such as Notion activity tracking, Second Brain captures, Granola follow-up extraction, Gmail follow-up review, Zotero-derived ideas, deal tracking, and activity briefs live in [`docs/secondbrain.md`](../secondbrain.md).

The Second Brain skills use the `second-brain-*` namespace and the user-facing `SECOND BRAIN | ...` workflow names.
