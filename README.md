# dot-codex

In December 2025, I stopped writing code. Codex now does the implementation work.

That changed where I put my engineering effort: understanding the problem, deciding what should happen, and checking whether the result works. A convincing response or a passing test suite can still leave the user's problem unresolved. Completion needs evidence from the place where the software is actually used.

I built dot-codex to make that workflow repeatable. It gives Codex a shared set of instructions, skills, and checks for investigating rough ideas, clarifying consequential choices, implementing accepted behavior, and retaining enough evidence to explain what worked and what still needs attention.

The aim is dependable delegation. Codex should carry the work through implementation and verification while bringing decisions about scope, cost, permissions, and external effects back to me when needed. Small corrections should remain small; material features need explicit acceptance and realistic proof.

## Four pillars

**Spec-driven work.** Start with conversation and investigation. Record accepted behavior in `FEATURE.md` so implementation and verification have a stable target.

**Realistic proof.** Have a separate agent author executable acceptance checks. Exercise the user's journey on the intended runtime, verify affected existing behavior, and use a fresh final reviewer to challenge the completion claim.

**Persistent execution.** Use native Codex Goals, when explicitly authorized, to carry material implementation through proof and repair within the configured allowance. Report unfinished work when input, access, or runtime limits prevent completion.

**Evidence and reflection.** Retain decisions, attempts, corrections, and results so failures can be understood and recurring problems can inform deliberate improvements to the harness.

## How work flows

The [coding workflow](skills/coding-workflow/SKILL.md) selects Shape, Ship, Fix, Analyze, or Operate according to the request. Domain skills supply the relevant implementation technique. A rough idea needs discovery; an isolated correction needs a focused change and check.

For a material feature, the path is conversation → `FEATURE.md` → independently authored `PROOF.md` and executable proof → implementation → affected regression checks → fresh final review. Acceptance stays fixed during implementation, and repairs continue within the same feature. The [coding guide](docs/harness/coding-workflow.md) explains the decisions and completion requirements.

Codex provides the runtime, permissions, task history, and Goal controls. This repository defines how to use them. Automatic evidence capture and protected proof execution still have integration limits; the workflow must report what was verified and where evidence is missing. The [evidence guidance](skills/coding-workflow/references/evidence.md) describes those boundaries.

The same installation also supports [personal operations through Second Brain](docs/harness/secondbrain.md), with shared rules for turning notes and activity into Notion tasks, deals, and ideas.

## Install

Clone this repository as your Codex home, or point `CODEX_HOME` to the checkout:

```bash
git clone https://github.com/marcocello/dot-codex /path/to/dot-codex
export CODEX_HOME=/path/to/dot-codex
cp "$CODEX_HOME/config.template.toml" "$CODEX_HOME/config.toml"
```

Review machine-specific paths and permissions. The template enables multiple agents for separate proof authorship and final review. Start a fresh Codex task to load updated skill discovery. Use `$sync-codex-skills` to reconcile declared dependencies and `$manage-codex-skills` to change membership; system skills and runtime-managed plugins stay outside `skills.toml`.

Validate the repository:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/gate" --root "$CODEX_HOME"
```

## Documentation

`docs/harness/` describes how dot-codex operates today. `docs/features/` records dot-codex changes, feature descriptions, decisions, and verification evidence.

- [Operating rules and ownership](AGENTS.md)
- [Coding workflow and pillars](docs/harness/coding-workflow.md)
- [Safety and operations](docs/harness/safety.md)
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
