# Coding workflow

Understand the request, implement the agreed behavior, prove it works, and retain evidence to improve future work. Codex supplies the runtime; the harness organizes how its capabilities are used.

This guide explains the workflow and its purpose. [`AGENTS.md`](../../AGENTS.md) sets the operating constraints, and [`coding-workflow`](../../skills/coding-workflow/SKILL.md) owns the detailed procedures linked below. Domain skills supply implementation technique.

## Pillars

- **Spec-driven:** accepted behavior gives implementation and verification a shared target.
- **Proof-driven:** realistic executable checks establish whether the intended behavior works.
- **Persistent execution:** explicitly authorized native Goals carry material implementation through verification within the configured allowance.
- **Evidence and reflection:** retained decisions and results support diagnosis and deliberate improvement. Capture automation depends on the available runtime integration.

## Workflows

The depth of work follows the behavior being requested. A rough idea needs investigation; a small correction needs a focused change and check.

| What the user needs | Procedure |
| --- | --- |
| New or changed behavior | [Shape](../../skills/coding-workflow/references/shape.md), then [Ship](../../skills/coding-workflow/references/ship.md) |
| Implementation of a ready feature | [Ship](../../skills/coding-workflow/references/ship.md) |
| Repair of known behavior or small maintenance | [Fix](../../skills/coding-workflow/references/fix.md) |
| Explanation, assessment, or architecture review | [Analyze](../../skills/coding-workflow/references/analyze.md) |
| Investigation of a running-system problem | [Operate](../../skills/coding-workflow/references/operate.md) |

For example, adding CSV export changes capability and needs Shape and Ship. Restoring an export that stopped working is Fix. Changing a button label can remain a standalone Fix. A defect that invalidates a delivered feature reopens its verification obligations; the [Fix scope criteria](../../skills/coding-workflow/references/fix.md#classify-and-explain-the-scope) define that distinction.

## From intent to completion

1. **Understand and agree.** Conversation and repository investigation establish the user's journey, boundaries, consequential decisions, and existing behavior to preserve. `FEATURE.md` records the accepted outcome. [Shape](../../skills/coding-workflow/references/shape.md) governs discovery, authorization, and when the specification is ready.

2. **Define independent proof.** A separate author turns the accepted scenarios into `PROOF.md`, executable acceptance tests, and `proof/run.sh`. Tests follow the features they verify, with acceptance and implementer-authored regressions kept separate. The [proof procedure](../../skills/coding-workflow/references/proof.md) owns test placement, authorship, realistic boundaries, and recorded attempts.

3. **Implement and repair.** The implementer works against fixed acceptance, using domain skills and an explicitly authorized native Goal. [Ship](../../skills/coding-workflow/references/ship.md) governs continuation, affected regression checks, stopping, and resuming. Proof defects follow the [fixed-acceptance procedure](../../skills/coding-workflow/references/proof.md#fixed-acceptance), which distinguishes code repair, independent setup repair, and decisions about required behavior.

4. **Verify where the result is consumed.** Proof exercises the intended runtime and reads back the relevant behavior. Supporting regressions check affected existing behavior. A fresh reviewer, separate from the implementer and proof author, challenges the completion claim. [Ship verification and completion](../../skills/coding-workflow/references/ship.md#complete) defines the evidence required to finish.

Analysis ends at its requested explanation or assessment. Runtime investigation begins with the observed symptom and follows the evidence to an authorized remedy; a local repair still needs verification on the affected runtime. The [Analyze](../../skills/coding-workflow/references/analyze.md), [Operate](../../skills/coding-workflow/references/operate.md), and [safety guide](safety.md) provide the corresponding procedures and boundaries.

## Feature records and ownership

`docs/features/` holds feature descriptions, accepted decisions, and verification evidence. Its `status.json` records ownership and completion references. The [status procedure](../../skills/coding-workflow/references/status.md) owns the schema, migration, transitions, concurrent work, and handoff rules.

When required historical proof no longer runs, the [restoration procedure](../../skills/coding-workflow/references/proof.md#restore-unrunnable-proof) recovers executable checks in the current feature structure through an independent author while preserving accepted behavior and old evidence.

A feature record preserves the history of a change. Current operating instructions live in `AGENTS.md` and the workflow skills; earlier specifications remain evidence of what was accepted at the time.

## Saving work and learning

Retain enough evidence to explain the request, decisions, implementation attempts, verification, and remaining gaps. [Evidence and reflection](../../skills/coding-workflow/references/evidence.md) defines what to record, how to protect private dialogue, and how to report missing capture.

Official proof and every supporting regression run used to justify feature completion go through `proof_run_capture`, with separate result kinds and evidence directories. Investigation commands and conversation context follow the [per-feature evidence procedure](../../skills/coding-workflow/references/evidence.md#evidence-for-one-feature).

Complete automatic lifecycle capture is not configured by this repository. Use supported capture where available and identify partial or unavailable evidence. Current proof capture also has limited write protection; its [documented boundary](../../skills/coding-workflow/references/proof.md#fixed-acceptance) explains what it can establish.

The [improvement-review skill](../../skills/coding-review-workflow/SKILL.md) examines actual runs and proposes corrections supported by recurring failures or a demonstrated harness defect. Retaining evidence supports that review; changes to global instructions remain deliberate decisions.
