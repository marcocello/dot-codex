## dot-codex

Around December 2025, I stopped writing code and stopped reading the code AI produced.

The product still matters. The code still matters. What changed is the control point: instead of manually inspecting every generated line, I shape the work before generation and make the AI produce proof that its work matches the intended behavior.

This repo is my current Codex configuration. It is tuned for Codex App, Codex Goals, local skills, and a harness that refuses to call plausible output done.

## Core Idea

This repo treats AI coding as a harness problem. The useful control surface is not a longer prompt; it is a small set of durable artifacts around the model.

The harness does not replace the model. It surrounds Codex with contracts, proof commands, evidence capture, repair loops, and done judgment.

The harness turns Codex work into a loop: define behavior, define proof, make Codex run it, collect evidence, repair failures, and only then judge done.

In other software repos, the same loop provides three repo-facing capabilities: autofix concrete failures, autosuggest improvements from proof evidence, and auto-improve accepted suggestions as normal feature, proof, repair, or readiness work.

## Current Approach In Plain Terms

The current harness has three loops.

The feature loop is: `FEATURE.md` -> `PROOF.md` -> real boundary proof -> evidence bundle -> repair until proof passes -> evaluator.

The agent loop is: observe whether Codex used the right context, skill, recovery path, and proof discipline while getting to green.

The learning loop is: turn repeated evidence into project improvements first, and only promote a lesson into the harness when it is clearly cross-project and repeatable.

The harness is not trying to make Codex creative by adding more ceremony. It is trying to make Codex accountable by making claims of completion expensive to fake.

## Pillars

### Feature Spec Is The Source Of Truth

`FEATURE.md` is the behavior contract. It defines the expected behavior, user-visible outcome, constraints, scope, and non-goals before implementation starts.

Current harness: good. It forces Codex to shape the work before coding.

Weak point: Codex can still under-question the user when ownership, data model, user-visible behavior, or external boundaries are ambiguous.

Next step: make "ask before spec" sharper only for ambiguity that would make the contract wrong.

### Proof Is A Separate Contract

`PROOF.md` defines how correctness will be proven. It stays separate from `FEATURE.md` so the feature says what must be true and the proof says how reality will be checked.

Current harness: strong. It keeps proof central instead of treating tests as an afterthought.

Weak point: proof quality still depends on choosing the right boundary.

Next step: keep forcing proof plans to name the real boundary they touch and the boundary they do not touch.

### Fake Proof Is Not Allowed

Passing source shape, mocked-only assertions, assistant claims, or convenient green commands is not enough. Proof has to exercise a meaningful public boundary: API, browser, DB, queue, provider readback, persisted state, logs, or another realistic contract.

Current harness: strong. This is one of the core protections.

Weak point: some projects do not yet have easy real-boundary proof infrastructure, so Codex may be tempted to fall back to narrow checks.

Next step: make weak proof explicit instead of hidden by requiring proof-scope limits to be written down.

### Evidence Bundle Is The Audit Object

Proof should leave inspectable artifacts: command, result, metadata, proof scope, attempts, repair notes, logs, screenshots, provider readback, or other concrete traces.

Current harness: good. `scripts/proof_run_capture` and proof-bundle validation already support this shape.

Weak point: browser traces, provider readbacks, video, and app-specific logs are still partly convention-driven.

Next step: add small project-specific evidence recipes where they matter, without building a giant framework.

### Autonomous Execution Means Proof Repair

Autonomous work means Codex implements, runs the proof, inspects failure, repairs the concrete cause, and repeats until the proof passes or the remaining blocker is truly external or user-owned.

Current harness: strong. The repair loop is explicit in the execution and autonomous skills.

Weak point: a final passing proof can hide wasted attempts, wrong tactics, skipped recovery, or confusion about ownership.

Next step: observe the agent when the loop matters, not only the final app result.

### Agent Behavior Is Part Of The Signal

Passing proof is not enough if Codex got there by repeatedly patching the wrong layer, ignoring repo architecture, asking too early, skipping local recovery, editing the contract after code, or using fake proof first.

Current harness: improving. `agent-observation.md` captures loop behavior when proof fails repeatedly, tactics change, `NEED_INPUT` appears, evaluator fails, proof is green-but-broken, or contract repair happens after implementation began.

Weak point: this is still lightweight observability, not a full trajectory-analysis system.

Next step: keep it lightweight, but make repeated bad agent behavior visible enough to improve skills and harness rules.

### Contract Freeze Protects The Proof

After implementation starts, Codex cannot casually change `FEATURE.md`, `PROOF.md`, or proof artifacts to make the work pass.

Current harness: important and present.

Weak point: this only works if the evaluator keeps checking whether contract changes were legitimate contract repair or proof gaming.

Next step: keep treating contract edits after coding as suspicious unless clearly justified.

### Evaluator Is The Done Judge

The evaluator is the skeptical read-only judge. It checks whether the feature contract, proof contract, evidence, proof scope, implementation behavior, and proof history support the claim that the work is done.

Current harness: strong concept. It prevents Codex from grading itself too easily.

Weak point: evaluator strength depends on real fixtures and adversarial examples.

Next step: later, build a harness regression corpus from real past false greens, evaluator misses, and bad proof patterns.

### Green-But-Broken Means Proof Failure

If commands are green but the product is still wrong, the harness treats that as a proof-system failure. Strengthen the proof before continuing to patch implementation.

Current harness: strong. This rule is already explicit.

Weak point: Codex needs discipline to stop implementation work and return to contract repair.

Next step: evaluator should continue calling this out aggressively.

### Project Improvement Is Suggestion-First

Failed proof evidence, evaluator notes, user corrections, repeated attempts, and successful features can produce suggestions for the target repo: stronger proof, better logic, readiness checks, new features, or clearer architecture.

Current harness: good. `coding-project-improvement-review` is manual and suggestion-only.

Weak point: suggestions are useful only when they stay evidence-grounded.

Next step: keep suggestions manual. Do not auto-apply improvement ideas.

### Harness Learning Is Separate From Project Learning

A project-specific lesson belongs in the target repo. A repeated cross-project lesson may belong in this harness.

Current harness: good. Learning placement now distinguishes target repo docs, feature proof templates, feature queue items, harness docs, skills, evaluator fixtures, scripts, and memory.

Weak point: deciding when a lesson is truly general is still judgment-heavy.

Next step: promote one-off lessons slowly. The harness should learn from repeated evidence, not vibes.

## What The Harness Does Now

- Shapes work before coding through `FEATURE.md`.
- Defines done before coding through `PROOF.md`.
- Pushes proof toward real product boundaries instead of fake assertions.
- Captures proof evidence into reviewable bundles.
- Runs an autonomous repair loop until proof passes or a real blocker remains.
- Freezes contracts after implementation starts unless contract repair is justified.
- Uses a skeptical evaluator as the done judge.
- Suggests target-repo improvements from evidence without applying them automatically.
- Separates target-repo learning from harness self-evolution.

## Not Well Covered Yet

### Harness Regression

Harness changes do not yet have a mature before/after benchmark corpus. A new rule may improve one project while making Codex too rigid in another.

Current harness: lightweight manifests can now record before evidence, predicted fixes, predicted regressions, held-out checks, after evidence, and verdict basis.

Next step: build a small regression set from real past harness failures, but only when the current simpler system has enough evidence to justify it.

### Agent Behavior Observability

The harness now observes some agent behavior through optional `agent-observation.md` and `agent-observation.json`, but not full decision trajectories.

Next step: keep capturing failed tactics, skipped recovery, wrong skill routing, fake proof attempts, contract edits, and unnecessary user questions when they materially affected the loop.

### Multi-Agent And Shared State

The current model is mostly one Codex, one feature, one `FEATURE_DIR`. It is intentionally simple.

Next step: if multiple agents work on the same repo, add shared-state rules for ownership, handoff, review, and conflicting contract changes.

### Cost And Efficiency

The harness proves correctness better than it measures cost. It does not yet treat excessive attempts, token waste, repeated setup, or avoidable user interruption as first-class failure signals.

Next step: capture attempt count and waste patterns before adding hard budgets.

### Tool And Model Drift

The harness has rules, but not a mature drift-detection system for changed tools, changed Codex behavior, or changed project environments.

Next step: use evaluator misses and repeated proof failures as the first drift signals before adding heavier machinery.

### Live And External Proof

Provider checks, destructive checks, paid services, credentials, production-like databases, and external account mutations still require careful approval and setup.

Next step: keep the safety boundary explicit. Live proof should be strong, but not reckless.

## Reference Direction

The Zotero Harness Engineering collection points in the same direction: spec-driven development treats specs as primary artifacts; code-as-harness work treats code, tools, memory, and verification as the agent operating substrate; observability-driven harness evolution argues that harness changes need evidence about components, experience, and decisions, not only final task success.

The local version of that idea is pragmatic: keep `FEATURE.md`, `PROOF.md`, real proof evidence, autonomous repair, evaluator judgment, and project improvement review as the center. Add harness evolution only when repeated evidence proves a rule should become durable.

## Harness Boundaries

The repo gate protects general project health. It is useful, but it is not the same thing as feature proof.

A Codex Goal keeps runtime moving during autonomous work. It is coordination state, not the source of truth.

If everything is green but the product is still broken, the harness treats that as a proof-system failure. Strengthen the proof first, then fix the implementation.

`AGENTS.md` owns the operating contract. Skills own procedure. Harness docs own the detailed map.

## More

- Operator map: [`docs/harness/operator-map.md`](docs/harness/operator-map.md).
- Target repo autonomy: [`docs/harness/repo-autonomy.md`](docs/harness/repo-autonomy.md).
- Harness references: [`docs/harness/references.md`](docs/harness/references.md).
- Non-coding and Second Brain workflows: [`docs/secondbrain.md`](docs/secondbrain.md).
