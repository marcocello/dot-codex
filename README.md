# dot-codex

In December 2025, I stopped writing code. Codex now does the implementation work.

That changed where I put my engineering effort: understanding the problem, deciding what should happen, and checking whether the result works. A convincing response or a passing test suite can still leave the user's problem unresolved. Completion needs evidence from the place where the software is actually used.

I built dot-codex to make that workflow repeatable. It gives Codex a shared set of instructions, skills, and checks for investigating rough ideas, clarifying consequential choices, implementing accepted behavior, and retaining enough evidence to explain what worked and what still needs attention.

The aim is dependable delegation. Codex should carry the work through implementation and verification while bringing decisions about scope, cost, permissions, and external effects back to me when needed. Small corrections should remain small; material features need explicit acceptance and realistic proof.

## Harness north star

Understand the request, implement the agreed behavior, prove it works, and retain evidence to improve future work. Codex supplies the runtime; the harness organizes how its capabilities are used.

This README preserves the harness’s north star: how it should behave and why. [`AGENTS.md`](AGENTS.md) owns operational routing and global boundaries; the four lifecycle skills own detailed procedures. Domain skills supply implementation technique. Use this design to judge future harness changes and actual coding runs.

### Pillars

- **Spec-driven:** accepted behavior gives implementation and verification a shared target.
- **Proof-driven:** realistic executable checks establish whether the intended behavior works.
- **Proactive execution:** investigate, resolve routine choices, implement authorized work, and verify. The user’s standing request starts a native Goal at Shape entry and carries it through Ship within configured limits; missing Goal tooling does not block ordinary execution.
- **Evidence and reflection:** retained decisions and results support diagnosis and deliberate improvement. Capture automation depends on the available runtime integration.

### Workflows

The depth of work follows the intended outcome, inferred from the request and current context. Quick notes and reports of strange behavior do not require formal tickets or named skills. Inspect relevant supplied artifacts or PRs, distinguish changed behavior from a defect, and explain the route briefly. A rough idea needs investigation and useful product questions; a clear correction needs a focused change and check. Proactivity means proposing a concrete interpretation, investigating ordinary cases the user has not named, and recommending choices that make the intended outcome work. Curiosity should uncover consequential gaps before implementation, such as absent configuration behind an automatic default. Those discoveries belong in acceptance and verification, not only in conversation. Preserve explicit review-only or planning-only scope.

| What the user needs | Procedure |
| --- | --- |
| New or changed behavior | [Shape](skills/coding-shape/SKILL.md), then [Ship](skills/coding-ship/SKILL.md) |
| Implementation of a ready feature | [Ship](skills/coding-ship/SKILL.md) |
| Repair of known behavior or small maintenance | [Fix](skills/coding-fix/SKILL.md) |
| Explanation, assessment, or architecture review | [Direct specialist analysis](AGENTS.md#understand-and-route) |
| Investigation of a running-system problem | [Operate](skills/coding-operate/SKILL.md) |

For example, adding CSV export changes capability and needs Shape and Ship. Restoring an export that stopped working is Fix. Changing a button label can remain a standalone Fix. A defect that invalidates a delivered feature reopens its verification obligations; the [Fix scope criteria](skills/coding-fix/SKILL.md#classify-and-explain-the-scope) define that distinction.

A concrete running-system symptom routes to Operate before general assessment, even when the request says “analyze” or “understand” and asks for diagnosis only. “Understand why this production job failed” is Operate; “assess the production architecture” without an observed failure uses the relevant specialist directly. Runtime evidence establishes the owning component before a confirmed code defect moves to Fix.

The harness announces each exact skill name and its purpose before use, including specialist skills and lifecycle switches, and states substantive phase changes in commentary. The handoff states the final lane/phase and outcome. The [communication rules](AGENTS.md#work-with-the-user) owns this behavior; labels do not grant permission or imply successful verification.

### From intent to completion

1. **Understand and agree.** Conversation and repository investigation establish the user's journey, boundaries, consequential decisions, and existing behavior to preserve. `FEATURE.md` records the accepted outcome. [Shape](skills/coding-shape/SKILL.md) governs discovery, authorization, and when the specification is ready.

2. **Define independent proof.** A separate author turns the accepted scenarios into `PROOF.md`, executable acceptance tests, and `proof/run.sh`. Tests follow the features they verify, with acceptance and implementer-authored regressions kept separate. The [proof procedure](docs/harness/coding/proof.md) owns test placement, authorship, realistic boundaries, and recorded attempts.

3. **Implement and repair.** The implementer works against fixed acceptance, using domain skills and the matching Goal carried from Shape when available. A ready feature can also proceed directly without a Goal; internal tools or skill transitions do not introduce approval gates. [Ship](skills/coding-ship/SKILL.md) governs continuation, affected regression checks, stopping, and resuming. Proof defects follow the [fixed-acceptance procedure](docs/harness/coding/proof.md#fixed-acceptance), which distinguishes code repair, independent setup repair, and decisions about required behavior.

4. **Verify where the result is consumed.** Proof exercises the intended runtime and reads back the relevant behavior. Supporting regressions check affected existing behavior. A fresh reviewer, separate from the implementer and proof author, challenges the completion claim. [Ship verification and completion](skills/coding-ship/SKILL.md#complete) defines the evidence required to finish.

Analysis ends at its requested explanation or assessment. Runtime investigation begins with the observed symptom and follows the evidence to an authorized remedy; a local repair still needs verification on the affected runtime. The [Direct specialist analysis](AGENTS.md#understand-and-route), [Operate](skills/coding-operate/SKILL.md), and [global boundaries](AGENTS.md#global-boundaries) provide the corresponding procedures and boundaries.

### Feature records and ownership

`docs/features/` holds feature descriptions, accepted decisions, and verification evidence. Its `status.json` records ownership and completion references. The [status procedure](docs/harness/coding/status.md) owns the schema, migration, transitions, concurrent work, and handoff rules.

When required historical proof no longer runs, the [restoration procedure](docs/harness/coding/proof.md#restore-unrunnable-proof) recovers executable checks in the current feature structure through an independent author while preserving accepted behavior and old evidence.

A feature record preserves the history of a change. Current operating instructions live in `AGENTS.md` and the workflow skills; earlier specifications remain evidence of what was accepted at the time.

### Saving work and learning

Retain enough evidence to explain the request, decisions, implementation attempts, verification, and remaining gaps. [Evidence and reflection](docs/harness/coding/evidence.md) defines what to record, how to protect private dialogue, and how to report missing capture.

Official proof and every supporting regression run used to justify feature completion go through `proof_run_capture.py`, with separate result kinds and evidence directories. Investigation commands and conversation context follow the [per-feature evidence procedure](docs/harness/coding/evidence.md#evidence-for-one-feature).

Complete automatic lifecycle capture is not configured by this repository. Use supported capture where available and identify partial or unavailable evidence. Current proof capture also has limited write protection; its [documented boundary](docs/harness/coding/proof.md#fixed-acceptance) explains what it can establish.

The [improvement-review skill](skills/coding-review-workflow/SKILL.md) examines actual runs and proposes corrections supported by recurring failures or a demonstrated harness defect. Retaining evidence supports that review; changes to global instructions remain deliberate decisions.

The same installation supports [knowledge capture and review](docs/harness/secondbrain.md) through reusable ClickUp, Notion or Markdown connections, following the user's existing organization. $knowledge-tool-connect handles setup, saved credentials, defaults, capability checks and plugin/MCP or API access in one skill. When MCP is limited, it offers an explicitly chosen API switch for supported operations, reusing credentials without silently changing the preferred transport. Destinations are optional and none disables storage.

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
- [Runtime diagnosis and recovery](skills/coding-operate/SKILL.md)
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
