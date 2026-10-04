# dot-codex

In December 2025, I stopped writing code. Codex now does the implementation work.

That changed where I put my engineering effort: understanding the problem, deciding what should happen, and checking whether the result works. A convincing response or a passing test suite can still leave the user's problem unresolved. Completion needs evidence from the place where the software is actually used.

I built dot-codex to make that workflow repeatable. It gives Codex a shared set of instructions, skills, and checks for investigating rough ideas, clarifying consequential choices, implementing accepted behavior, and retaining enough evidence to explain what worked and what still needs attention.

The aim is dependable delegation. Codex should carry the work through implementation and verification while bringing decisions about scope, cost, permissions, and external effects back to me when needed. Small corrections should remain small; material features need explicit acceptance and realistic proof.

The agent is also a sparring partner in both new and existing projects: investigate the surrounding context, challenge weak assumptions, and discuss product direction and the user's work before settling a feature. Even a small request can raise a question about where the product is going; an established direction need not be reopened. Ask those high-level questions early, then own the routine details. Future ambition informs narrow composable slices without authorizing a larger build. Clear authorized work proceeds with justified choices and explicit assumptions; only work depending on a consequential decision the agent cannot responsibly make needs the user's answer.

## Harness north star

Understand the request, implement the agreed behavior, prove it works, and retain evidence to improve future work. Codex supplies the runtime; the harness organizes how its capabilities are used.

This README preserves the harness’s north star: how it should behave and why. [`AGENTS.md`](AGENTS.md) owns operational routing and global boundaries; the coding roles own detailed responsibilities. Domain skills supply implementation technique. Use this design to judge future harness changes and actual coding runs.

### Pillars

- **Spec-driven:** accepted behavior gives implementation and verification a shared target.
- **Proof-driven:** realistic executable checks establish whether the intended behavior works.
- **Proactive execution:** investigate, resolve routine choices, implement authorized work, and verify. Product discovery and specification/proof design remain conversational work without starting a native Goal. The user’s standing request starts a scoped Goal when authorized implementation begins and carries it through verification within configured limits; missing Goal tooling does not block ordinary execution.
- **Evidence and reflection:** retained decisions and results support diagnosis and deliberate improvement. Capture automation depends on the available runtime integration.

### Workflows

The depth of work follows the intended outcome, inferred from the request and current context. Quick notes and reports of strange behavior do not require formal tickets or named skills. Inspect relevant supplied artifacts or PRs, distinguish changed behavior from a defect, and explain the route briefly. A rough idea needs investigation and useful product questions; a clear correction needs a focused change and check. Proactivity means proposing a concrete interpretation, investigating ordinary cases the user has not named, and recommending choices that make the intended outcome work. Curiosity should uncover consequential gaps before implementation, such as absent configuration behind an automatic default. Those discoveries belong in acceptance and verification, not only in conversation. Preserve explicit review-only or planning-only scope.

| What the user needs | Procedure |
| --- | --- |
| New or changed product behavior needing investigation and direction | [Product Partner](skills/coding-product-partner/SKILL.md) |
| Understood behavior needing specifications or acceptance proof | [Design Specs and Proof](skills/coding-design-specs-proof/SKILL.md) |
| Implementation of a scoped feature set, including drafts | [Implement](skills/coding-implement/SKILL.md) |
| Repair of known behavior or small maintenance | [Repair](skills/coding-repair/SKILL.md) |
| Explanation, assessment, or architecture review | [Direct specialist analysis](AGENTS.md#understand-and-route) |
| Investigation of a running-system problem | [Runtime Ops](skills/coding-runtime-ops/SKILL.md) |

For example, adding CSV export changes capability: Product Partner examines the intended use, asks about consequential gaps, and recommends a narrow outcome; Design Specs and Proof prepares acceptance, and Implement delivers authorized work. A clear export request can proceed using established conventions, while permission to expose additional data needs resolution if not already established. Restoring an export that stopped working is Repair. Changing a button label can remain a standalone Repair. A defect that invalidates a delivered feature reopens its verification obligations; the [Repair scope criteria](skills/coding-repair/SKILL.md#classify-and-explain-the-scope) define that distinction.

A concrete running-system symptom routes to Runtime Ops before general assessment, even when the request says “analyze” or “understand” and asks for diagnosis only. “Understand why this production job failed” is Runtime Ops; “assess the production architecture” without an observed failure uses the relevant specialist directly. Runtime evidence establishes the owning component before a confirmed code defect moves to Repair.

The harness announces each exact skill name and its purpose before use, including specialist skills and lifecycle switches, and states substantive phase changes in commentary. The handoff states the final lane/phase and outcome. The [communication rules](AGENTS.md#work-with-the-user) owns this behavior; labels do not grant permission or imply successful verification.

### From intent to completion

The responsibilities below can overlap as evidence develops. They do not require every request to traverse a fixed sequence or create the same documents.

1. **Understand and agree.** Read enough context to orient the discussion, then explore the user's journey, product ambition, and consequential tradeoffs before dependent specifications or implementation. Agree the direction with the user; derive routine design and engineering choices yourself. Prefer atomic features: one specific demonstrable outcome with its necessary end-to-end path and proof. A short journey outline connects the slices; later details can remain provisional while a clear slice is delivered. [Product Partner](skills/coding-product-partner/SKILL.md#discovery-and-autonomy) owns this conversation without a Goal. [Design Specs and Proof](skills/coding-design-specs-proof/SKILL.md) and Implement carry that understanding forward, distinguishing user decisions from assumptions without adding confirmation rounds. APP/ARCHITECTURE capture useful cross-feature context when needed, rather than acting as universal prerequisites.

2. **Define independent proof.** Design Specs and Proof prepares the next useful slice with a separate author who turns accepted scenarios into `PROOF.md`, executable acceptance tests, and `proof/run.sh`. Tests follow the features they verify, with acceptance and implementer-authored regressions kept separate. The [proof procedure](docs/harness/coding/proof.md) owns test placement, authorship, realistic boundaries, and recorded attempts.

3. **Implement and repair.** Once the intended outcome is understood and the next slice is ready and authorized, the implementer starts or resumes its scoped native Goal and works against fixed acceptance using domain skills. Internal tools or skill transitions do not introduce approval gates; unavailable Goal tools do not prevent ordinary work. [Implement](skills/coding-implement/SKILL.md) governs continuation, affected regression checks, stopping, and resuming. Proof defects follow the [fixed-acceptance procedure](docs/harness/coding/proof.md#fixed-acceptance), which distinguishes code repair, independent setup repair, and decisions about required behavior.

4. **Verify where the result is consumed.** Proof exercises the intended runtime and reads back the relevant behavior. Supporting regressions check affected existing behavior. A fresh reviewer, separate from the implementer and proof author, challenges the completion claim. [Implement verification and completion](skills/coding-implement/SKILL.md#complete) defines the evidence required to finish.

Analysis ends at its requested explanation or assessment. Runtime investigation begins with the observed symptom and follows the evidence to an authorized remedy; a local repair still needs verification on the affected runtime. The [Direct specialist analysis](AGENTS.md#understand-and-route), [Runtime Ops](skills/coding-runtime-ops/SKILL.md), and [global boundaries](AGENTS.md#global-boundaries) provide the corresponding procedures and boundaries.

### Feature records and ownership

`docs/features/` holds feature descriptions, accepted decisions, and verification evidence. Its `status.json` records ownership and completion references. The [status procedure](docs/harness/coding/status.md) owns the schema, migration, transitions, concurrent work, and handoff rules.

When required historical proof no longer runs, the [restoration procedure](docs/harness/coding/proof.md#restore-unrunnable-proof) recovers executable checks in the current feature structure through an independent author while preserving accepted behavior and old evidence.

A feature record preserves the history of a change. Current operating instructions live in `AGENTS.md` and the workflow skills; earlier specifications remain evidence of what was accepted at the time.

### Saving work and learning

Retain enough evidence to explain the request, decisions, implementation attempts, verification, and remaining gaps. [Evidence and reflection](docs/harness/coding/evidence.md) defines what to record, how to protect private dialogue, and how to report missing capture.

Official proof and every supporting regression run used to justify feature completion go through `proof_run_capture.py`, with separate result kinds and evidence directories. Investigation commands and conversation context follow the [per-feature evidence procedure](docs/harness/coding/evidence.md#evidence-for-one-feature).

Complete automatic lifecycle capture is not configured by this repository. Use supported capture where available and identify partial or unavailable evidence. New completion checks bind proof and an independent review receipt to the captured candidate; retained historical acceptance does not establish current regression coverage. Fingerprints provide bounded change detection, not write isolation or external runtime attestation; [capture scope and limits](docs/harness/coding/evidence.md#current-candidate-and-review) explain the boundary.

The [improvement-review skill](skills/coding-review-workflow/SKILL.md) examines actual runs and proposes corrections supported by recurring failures or a demonstrated harness defect. [Harness evaluation](docs/harness/coding/harness-evaluation.md) compares actual behavior using raw task context and unseen checks; wording checks and retained model judgments do not establish improved agent performance. Retaining evidence supports that review; changes to global instructions remain deliberate decisions.

The same installation supports [knowledge capture and review](docs/harness/secondbrain.md) through reusable ClickUp, Notion or Markdown connections, following the user's existing organization. $knowledge-tool-connect handles setup, saved credentials, defaults, capability checks and plugin/MCP or API access in one skill. When MCP is limited, it offers an explicitly chosen API switch for supported operations, reusing credentials without silently changing the preferred transport. Destinations are optional and none disables storage.

For ongoing personal context and follow-through, [the second-brain cycle](docs/harness/secondbrain-cycle.md) adds `$secondbrain-update` and `$secondbrain-review`. Both use one explicit private workspace containing source history, current facts, a living agenda, action receipts and readable user direction. A standard-library SQLite helper preserves checkpoints, rejects stale updates and prevents duplicate local action claims. Existing connectors provide source access and execution; skills interpret and decide. Installation alone does not connect accounts, enable autonomous sends or start a recurring run. `secondbrain.yaml` selects the workspace, sources, initial lookback and separate native update/review intervals. Copy `secondbrain.template.yaml` for private setup. WhatsApp intake uses wacli. The cycle documentation covers configuration, manual activation and native schedule reconciliation.

## Install

Clone this repository as your Codex home, or point `CODEX_HOME` to the checkout:

```bash
git clone https://github.com/marcocello/dot-codex /path/to/dot-codex
export CODEX_HOME=/path/to/dot-codex
cp "$CODEX_HOME/config.template.toml" "$CODEX_HOME/config.toml"
```

Review machine-specific paths and permissions. The template enables multiple agents for separate proof authorship and final review. Start a fresh Codex task to load updated skill discovery. Use `$harness-manage-skills sync` to reconcile declared dependencies and `$harness-manage-skills` to change membership; system skills and runtime-managed plugins stay outside `skills.toml`.

Validate the repository:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/gate.py" --root "$CODEX_HOME"
```

## Documentation

`docs/harness/` describes how dot-codex operates today. `docs/features/` records dot-codex changes, feature descriptions, decisions, and verification evidence.

- [Operating rules and ownership](AGENTS.md)
- [Skill routing and global boundaries](AGENTS.md#understand-and-route)
- [Runtime diagnosis and recovery](skills/coding-runtime-ops/SKILL.md)
- [Skill inventory](docs/harness/skill-management.md)
- [Non-coding workflows](docs/harness/secondbrain.md)

## Design references

The external background for this work lives in Zotero under the `Harness Engineering` collection.

<details>
<summary>Research and field reports</summary>

- Ryan Lopopolo, [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) on context, tools, checks, and feedback loops around the model.
- Xuying Ning et al., `Code as Agent Harness` on executable, inspectable, stateful harness substrate.
- Jiahang Lin et al., [Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses](http://arxiv.org/abs/2604.25850) on harnesses as a determinant of coding-agent performance.
- Jiawei Gu et al., `A Survey on LLM-as-a-Judge` on evaluator reliability, bias, and the need to preserve executable evidence alongside semantic judgment.
- Wanqin Ma et al., `(Why) Is My Prompt Getting Worse? Rethinking Regression Testing for Evolving LLM APIs` on prompt drift, nondeterminism, and held-out checks.
- Lei Wang et al., `A survey on large language model based autonomous agents` on profiling, memory, planning, action, and evaluation.
- Anthropic engineers, via Anatoli Kopadze, on the [planner, generator, and evaluator loop for full-app builds](https://x.com/AnatoliKopadze/status/2068690663919530207).
- dominik kundel, [A guide to /goal](https://x.com/dkundel/status/2062650378089594955) on Codex Goal as runtime state.
- Anatoli Kopadze, [Loops explained: Claude, GPT, Mira and what actually works](https://x.com/AnatoliKopadze/status/2068328135611822149) on autonomous loop patterns and persistent state.
- elvis, [From Prompting Agents to Loop Engineering](https://x.com/omarsar0/status/2068008743153834264) on engineered agent loops.
- Dan Farrelly, [The Agent Loop Architecture](https://x.com/djfarrelly/status/2067677007140278630) on the primitives behind agentic systems.
- Deepak Babu Piskala, [Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants](http://arxiv.org/abs/2602.00180) on contracts as primary artifacts.
- GitHub, [Spec Kit](https://github.com/github/spec-kit), and Fission AI, [OpenSpec](https://openspec.dev/) as practical spec-driven development toolkits.
- Birgitta Bockeler, [Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) on the tradeoffs of spec-driven development.
- Andrej Karpathy, [Software Is Changing (Again)](https://www.youtube.com/watch?v=LCEmiRjPEtQ) and [coding workflow notes](https://x.com/karpathy/status/2015883857489522876) on human-in-the-loop coding.
- Geoffrey Huntley, [Ralph Wiggum as a “software engineer”](https://ghuntley.com/ralph/) on while-loop coding agents and their limits.
- Simon Willison, [What is agentic engineering?](https://simonwillison.net/guides/agentic-engineering-patterns/what-is-agentic-engineering/) on agentic engineering as an engineering discipline.
- Peter Steinberger, [Shipping at Inference-Speed](https://steipete.me/posts/2025/shipping-at-inference-speed) on high-throughput agent-assisted shipping.
- [Pi](https://pi.dev/) as an extensible coding agent with project instructions and a programmable SDK.
- [Exo](https://github.com/exoharness/exo) on inspectable execution history, durable canonical state, and an agent-modifiable harness.

</details>
