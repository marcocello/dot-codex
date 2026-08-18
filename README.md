# dot-codex

In December 2025, I stopped writing code. Codex now does the implementation work.

That only works because I also changed how work begins and how completion is judged. Codex investigates rough product input, helps clarify the outcome and architecture, asks the material questions early, and then turns accepted decisions into lean contracts. Source inspection is no longer the primary completion control point: realistic executable proof and a fresh final review are.

This repository is the control layer behind that workflow. It turns Codex from a fast code generator into a product and engineering partner that can take anything from a loose app idea to a detailed feature through evidence-backed completion.

## Pillars

- **Understand before producing.** Investigate the user, purpose, benefit, current repository, and material uncertainty before creating artifacts.
- **Questions deepen understanding without becoming ceremony.** Ask focused grouped questions when answers can clarify or expand the problem, user implications, product, architecture, safety, cost, or proof. Continue across multiple rounds when answers expose consequential new unknowns; resynthesize and stop when the outcome is decision-ready.
- **Enrich without speculative scope.** Classify adjacent capabilities and preserve only useful future seams; do not automatically build or specify plausible follow-ups.
- **Record lean authority.** Create `APP.md`, `ARCHITECTURE.md`, feature packages, and queues only when accepted durable decisions justify them.
- **Prefer simple modular architecture.** Separate real responsibilities and ownership without adding abstractions or orchestration for hypothetical flexibility.
- **Prove the real lifecycle.** Cross the real boundary and exercise relevant existing state, visible read-back, affected consumers, failures, and runtime environment—not only fresh happy-path data.
- **Own truthful completion.** One parent drives one feature through proof, repair, and fresh evaluation. When an existing runtime is the accepted target, source proof remains intermediate until that runtime works.

The standard is simple: understand the outcome, record only accepted decisions, prove the real behavior, and leave no plausible shortcuts.

## From idea to implementation

The starting point can be a rough app idea, a detailed feature, one correction, or a bundle of potential capabilities. Input polish does not determine the workflow:

```text
product input
  -> investigate and clarify material choices
  -> classify adjacent outcomes
  -> write only earned authority and proof
  -> for sensitive work, run a fresh preflight
  -> implement and capture realistic evidence
  -> fresh final review and repair when needed
  -> truthful source/active-runtime handoff
```

Product input of any maturity or cardinality routes through `coding-product-partner`. The partner adapts its depth, may produce one or several accepted feature packages, and hands them to separate proof, implementation, review, and repair skills. Implementation remains serial: one accountable parent completes one feature before selecting the next.

Contract authoring and implementation are separate authorities. A request to shape, specify, or prepare proof stops after decision-ready artifacts; answering discovery questions does not silently authorize product implementation.

## Install

Clone the repository as your Codex home, or point `CODEX_HOME` at another checkout:

```bash
git clone https://github.com/marcocello/dot-codex /path/to/dot-codex
export CODEX_HOME=/path/to/dot-codex
cp "$CODEX_HOME/config.template.toml" "$CODEX_HOME/config.toml"
```

Review `config.toml` and replace the example paths, permission roots, notification command, and MCP settings for your machine. Then ask Codex to manage the installation through the included skills:

- “Use `$sync-codex-skills` to bootstrap this installation.”
- “Use `$sync-codex-skills` to reconcile all declared skills and plugins.”
- “Use `$manage-codex-skills` to add, update, diagnose, list, or remove an inventory entry.”

System skills and `openai-primary-runtime` plugins remain runtime-managed and stay outside `skills.toml`. The [skill management guide](docs/skill-management.md) explains ownership, reconciliation, plugin handling, and update policy.

When editing this repository, run its read-only gate:

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/gate" --root "$CODEX_HOME"
```

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

</details>

## Go deeper

- [Harness design and workflow](docs/harness/deep-dive.md)
- [Proof lifecycle and retained attempts](docs/harness/proof-lifecycle.md)
- [Proof scope and false-green risk](docs/harness/oracle-scope.md)
- [Repository discovery and harness learning](docs/harness/repo-autonomy.md)
- [Autonomous execution and recovery](docs/harness/autonomous-execution.md)
- [Harness evolution](docs/harness/evolution/evolution-loop.md)
- [Handoff format](docs/harness/handoff.md)
- [Non-coding and Second Brain workflows](docs/secondbrain.md)
- [Skill inventory and maintenance](docs/skill-management.md)

Code generation is becoming abundant. Reliable acceptance remains scarce. dot-codex concentrates engineering effort on the scarce part: deciding behavior, producing evidence, and preserving enough context to repair failures without starting over.
