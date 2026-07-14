# Harness Operator Map

## Current Harness Workflow

The normal coding workflow is:

1. Turn intent into one `FEATURE.md`.
2. Turn that feature contract into one `PROOF.md` plus executable proof artifacts.
3. Run the primary proof through the real boundary that matters: UI, API, provider, database, CLI, migration, or workflow.
4. Capture the feature proof result in `FEATURE_DIR/proof/runs/<timestamp>/` through `scripts/proof_run_capture`.
5. Repair implementation, setup, fixtures, or diagnostics until the primary proof passes.
6. Run the target repo gate.
7. Run `coding-feature-evaluator` as the skeptical done judge.
8. If a queue exists, update `docs/features/status.json` only after proof, gate, evaluator, and latest evidence are recorded.

Compact version:

```text
FEATURE.md -> PROOF.md -> realistic proof -> evidence bundle -> repair loop -> gate -> evaluator -> queue done
```

## Plain Inner And Outer Loops

Inner loop means Codex is doing the actual feature or issue work and recording what happened. For serious work, the output is not only changed code; it is a proof run with evidence: command, result, proof scope, metadata, notes, and when repair was needed, agent observation.

Outer loop means Codex reviews those evidence records later and asks what should be learned. The review separates local project lessons from reusable harness lessons before suggesting an owner.

Example: if a PDF feature passes because the proof only checked that `invoice.pdf` exists, the inner loop records the proof and its evidence. The outer loop can later say the project needs a stronger PDF proof that reads totals from the rendered file, and only if this pattern repeats should dot-codex strengthen a skill, evaluator fixture, script, test, or harness doc.

```text
Inner loop: do the work -> prove it -> record useful evidence.
Outer loop: read the evidence -> find repeated patterns -> route the lesson to the right owner.
```

For explicit autonomous work, a Codex Goal keeps the run moving, but the Goal is only runtime state. It does not replace `FEATURE.md`, `PROOF.md`, the queue, proof output, gate results, or evaluator judgment.

## Target Repo Autonomy

Autofixing, autosuggestions, and auto-improving are primarily target-repo capabilities:

- Autofix: repair one concrete target-repo failure, rerun the failed check, then rerun the proof lifecycle.
- Autosuggest: turn failed proof bundles, weak proof-scope classifications, evaluator failures, missing readiness, or user corrections into concrete target-repo next steps.
- Auto-improve: convert accepted suggestions into ordinary repo work: feature/spec repair, proof repair, implementation repair, readiness checks, diagnostics, or queued product improvements.

Harness self-improvement is separate. Use `$coding-app-improvement-review` when you want Codex to manually inspect features, proofs, evidence, successful checks, and user corrections, then suggest app/project improvements or harness lessons. Promote a target-repo failure to harness evolution only when repeated evidence shows the harness instruction, proof policy, script, test, or config allowed the same failure pattern.

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
- Proof scope and false-green risk: [`docs/harness/oracle-scope.md`](oracle-scope.md).
- Target repo autofix, autosuggestions, and auto-improve: [`docs/harness/repo-autonomy.md`](repo-autonomy.md).
- Autonomous execution and recovery before `NEED_INPUT`: [`docs/harness/autonomous-execution.md`](autonomous-execution.md).
- Destructive-proof allowlists: [`docs/harness/destructive-proof-allowlist.md`](destructive-proof-allowlist.md).
- Concise handoffs: [`docs/harness/handoff.md`](handoff.md).
- Memory policy: [`docs/harness/memory-policy.md`](memory-policy.md).
- Harness evolution notes and change manifests: [`docs/harness/evolution`](evolution), especially [`docs/harness/evolution/evolution-loop.md`](evolution/evolution-loop.md).

## Repo Helpers

- `scripts/proof_run_capture` wraps a proof command and writes a run evidence bundle.
- `scripts/validate_proof_bundle` checks the minimum proof bundle shape and serious proof-scope metadata.
- `scripts/validate_feature_queue --feature <id>` rejects the selected executable item when `PROOF.md` lacks `scripts/proof_run_capture` or declared source inputs, and rejects `done` without artifact-backed proof, gate, evaluator, and latest evidence. `--all` applies the same rules to the full queue.
- `scripts/harness_review` summarizes proof bundles, missing run evidence, agent risk signals, and harness change manifests; `--check` validates manifest shape.
- `scripts/gate_config` runs the dot-codex harness checks.
- `docs/harness/evaluator-fixtures.json` calibrates evaluator judgment examples; it is not runtime feature evidence.

## Proof Evidence

Serious proofs should leave evidence behind when practical:

```text
FEATURE_DIR/proof/runs/<timestamp>/
  command.txt
  stdout.txt
  stderr.txt
  result.json
  run-metadata.json
  oracle-scope.md
  attempts.json
  repair-notes.md
  agent-observation.md
  agent-observation.json
  screenshots/
  logs/
  provider-readback.json
  notes.md
```

Only real evidence belongs in that folder. Empty screenshots, invented logs, and fake provider read-back are worse than a clear note saying the evidence was unavailable.

For local proof commands, use:

```bash
scripts/proof_run_capture \
  --serious \
  --feature-dir FEATURE_DIR \
  --source-path <implementation-or-proof-input> \
  --behavior-boundary "<producer -> activation -> consumer -> read-back>" \
  --oracle-scope "$(cat FEATURE_DIR/PROOF.md)" \
  --notes "<short proof result summary>" \
  -- <primary proof command>
```

The helper exits with the wrapped command's status, so it can be used directly as the primary proof command or inside a proof runner.

## Queue Completion

`docs/features/status.json` is a progress index, not a workflow engine. The authoritative contracts remain `FEATURE.md` and `PROOF.md`.

A queue item should be marked `done` only when it records:

```json
{
  "completion": {
    "latest_evidence": "docs/features/<feature>/proof/runs/<timestamp>"
  }
}
```

`scripts/validate_feature_queue --feature <id>` requires the selected queued item to use `scripts/proof_run_capture` plus at least one `--source-path` in `PROOF.md`; unrelated queue items are out of scope. `scripts/validate_feature_queue --all` performs the strict whole-queue audit.
For `done` items, validation derives proof, gate, and evaluator success from the referenced bundle, requires serious proof metadata and concrete proof scope, and rejects repeated repair evidence without `attempts.json`.

## Harness Evolution

The harness should improve when repeated failures expose a weak instruction, weak proof, missing tool, or missing diagnostic.

```text
observed failure -> failure pattern -> change manifest -> harness change -> verification -> accepted or rejected pattern
```

The inner loop is feature proof satisfaction. The outer loop is harness improvement from repeated evidence.

Target-repo autosuggestions sit between those loops. They recommend the next repo-level fix; they do not automatically rewrite harness policy.

The app improvement review skill is the manual analysis point between those loops. A recurring pattern can become a harness-evolution candidate only after repeated evidence, not from one failed proof or one model opinion.

Every harness change manifest should name before evidence, predicted fixes, predicted regressions, held-out checks, after evidence, and verdict basis. `scripts/harness_review --check` rejects manifests that cannot support that before/after claim.

This is intentionally lighter than a workflow engine. It is meant to stop random prompt tweaks and make harness changes explainable, falsifiable, and rollbackable.

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

- Proof evidence capture is required for `FEATURE_DIR` work, but app-specific proof runners may still need richer screenshots, provider read-back, logs, or domain artifacts.
- Browser, provider, video, and log capture are supported by convention, but not yet automatically generated for every stack.
- `scripts/harness_review` summarizes proof evidence and manifests; it does not create, apply, suggest, or judge harness changes by itself.
- Queue completion validation applies when repos use `docs/features/status.json` with the completion shape above.
- Live validation still depends on credentials, safe targets, external services, and user approval for risky actions.

## Non-Coding Work

Not all useful Codex work is coding work. Personal operating workflows such as Notion activity tracking, Second Brain captures, Granola follow-up extraction, Gmail follow-up review, Zotero-derived ideas, deal tracking, and activity briefs live in [`docs/secondbrain.md`](../secondbrain.md).

The Second Brain skills use the `second-brain-*` namespace and the user-facing `SECOND BRAIN | ...` workflow names.
