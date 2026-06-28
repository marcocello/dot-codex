## dot-codex

Around December 2025, I stopped writing code and stopped reading the code AI produced.

The product still matters. The code still matters. What changed is the control point: reading every generated line became less useful than shaping the work before generation and proving behavior after generation. This repo focuses on sharper feature contracts, stronger proof, runtime checks, skeptical evaluation, and a harness that refuses to call plausible output done.

This repo is my current Codex configuration. Most of it also applies to Claude Code and other agentic coding systems, but this checkout is tuned for Codex App, Codex Goals, local skills, and the way I build software.

It mixes roughly twenty years of software work with what is now called harness engineering. Vibe coding was the trial phase. Feature-driven coding made the work describable. Ralph-style loops made agents persistent. Goals made long runs controllable. Proof and evaluators decide whether the output is worth trusting.

When AI writes most of the code, the old pipeline is incomplete. Issues, PRs, human-style review, and CI were designed for a world where humans produced most of the output. This repo is my attempt to adapt that pipeline to bounded agentic workflows.


## Core Idea

This repo treats AI coding as a harness problem. The useful control surface is not a
longer prompt; it is a small set of durable artifacts around the model.

`FEATURE.md` says what the feature is supposed to do. It is the product and behavior
contract.

`PROOF.md` says how the feature earns trust. It keeps proof central by naming evidence,
runtime checks, and the ways a fake or half-working implementation should be caught.

The repo gate protects general project health. It is useful, but it is not the same thing
as feature proof.

The evaluator is the skeptical read-only judge. It exists because a green command is not
always enough; the evidence has to match the behavior being claimed.

A Codex Goal keeps runtime moving during autonomous work. It is coordination state, not
the source of truth.

If everything is green but the product is still broken, the harness treats that as a
proof-system failure. Strengthen the proof first, then fix the implementation.

## Current Harness Workflow

The normal coding workflow is:

1. Turn intent into one `FEATURE.md`.
2. Turn that feature contract into one `PROOF.md` plus executable proof artifacts.
3. Run the primary proof through the real boundary that matters: UI, API, provider,
   database, CLI, migration, or workflow.
4. Capture the proof result in `FEATURE_DIR/proof/runs/<timestamp>/` when practical.
5. Repair implementation, setup, fixtures, or diagnostics until the primary proof passes.
6. Run the target repo gate.
7. Run `coding-feature-evaluator` as the skeptical done judge.
8. If a queue exists, update `docs/features/status.json` only after proof, gate,
   evaluator, and latest evidence are recorded.

The compact version is:

```text
FEATURE.md -> PROOF.md -> realistic proof -> evidence bundle -> repair loop -> gate -> evaluator -> queue done
```

For explicit autonomous work, a Codex Goal keeps the run moving, but the Goal is only
runtime state. It does not replace `FEATURE.md`, `PROOF.md`, the queue, proof output, gate
results, or evaluator judgment.

## Harness Shape

The skills split responsibility instead of repeating one large workflow everywhere.

`coding-feature-spec` turns intent into a feature contract.

`coding-proof-author` is central: it turns the contract into executable proof and
anti-gaming pressure.

`coding-feature-execute` implements a ready feature.

`coding-repair` fixes a concrete failure, bug, proof failure, lint failure, typecheck
failure, gate failure, or evaluator failure.

`coding-autonomous-execute` keeps going across proof, gate, evaluator, and repair loops
when the user explicitly asks for autonomous execution or queue completion.

`AGENTS.md` owns the operating contract. Skill files own local procedure. README is the
map: it explains the moving parts without replacing the detailed harness docs.

Detailed harness procedures live under [`docs/harness`](docs/harness):

- proof lifecycle and run evidence bundles;
- autonomous execution and recovery before `NEED_INPUT`;
- destructive-proof allowlists;
- concise handoffs;
- memory policy;
- harness evolution notes and change manifests.

Repo-local harness helpers:

- `scripts/proof_run_capture` wraps a proof command and writes a run evidence bundle.
- `scripts/validate_feature_queue` rejects `done` queue items without recorded proof,
  gate, evaluator, and latest evidence.
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

Only real evidence belongs in that folder. Empty screenshots, invented logs, and fake
provider read-back are worse than a clear note saying the evidence was unavailable.

For local proof commands, use:

```bash
scripts/proof_run_capture --feature-dir FEATURE_DIR -- <primary proof command>
```

The helper exits with the wrapped command's status, so it can be used directly as the
primary proof command or inside a proof runner.

## Queue Completion

`docs/features/status.json` is a progress index, not a workflow engine. The authoritative
contracts remain `FEATURE.md` and `PROOF.md`.

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

`scripts/validate_feature_queue` enforces this shape for `done` items when a status file
exists.

## Harness Evolution

The harness should improve when repeated failures expose a weak instruction, weak proof,
missing tool, or missing diagnostic.

The evolution area is:

```text
docs/harness/evolution/
  change-manifest-template.json
  failure-patterns.md
  accepted-patterns.md
  rejected-patterns.md
```

Use `scripts/harness_review` to summarize current proof bundles and pending harness change
manifests before changing the harness itself.

The expected evolution loop is:

```text
observed failure -> failure pattern -> change manifest -> harness change -> verification -> accepted or rejected pattern
```

This is intentionally lighter than a workflow engine. It is meant to stop random prompt
tweaks and make harness changes explainable.

## Safety And Handoff

Some realistic proofs need cleanup, sends, writes, or provider mutations. Those actions need
explicit approval unless a narrow, unexpired entry exists in:

```text
.codex/approvals/destructive-proof-allowlist.json
```

The allowlist must match the exact working directory, command string, target, and expiry.
It is repo policy only; platform approval prompts still take precedence.

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

This config is strong enough to force contract-first, proof-first coding behavior. It is not
yet a fully automatic harness-evolution system.

Current limits:

- Proof evidence capture exists, but app-specific proof runners still need to use it.
- Browser, provider, video, and log capture are supported by convention, but not yet
  automatically generated for every stack.
- `scripts/harness_review` summarizes evidence and manifests; it does not yet create or
  judge harness changes by itself.
- Queue completion validation applies when repos use `docs/features/status.json` with the
  completion shape above.
- Live validation still depends on credentials, safe targets, external services, and user
  approval for risky actions.

## Non-Coding Work

Not all useful Codex work is coding work. Personal operating workflows such as Notion
activity tracking, Second Brain captures, Granola follow-up extraction, Gmail follow-up
review, Zotero-derived ideas, deal tracking, and activity briefs live in
[`docs/secondbrain.md`](docs/secondbrain.md).

The Second Brain skills use the `second-brain-*` namespace and the user-facing
`SECOND BRAIN | ...` workflow names.

## Fundamental References

See [`docs/harness/references.md`](docs/harness/references.md).
