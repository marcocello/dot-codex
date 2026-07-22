## dot-codex

Around December 2025, I stopped writing code. I also stopped reading generated code as the primary way to decide whether the work was done.

The product still matters. The code still matters. The rendered output still matters. What changed is the control point: instead of manually inspecting every generated source file, I shape the work before generation and make the AI produce proof that its work matches the intended behavior.

This repo is my current Codex configuration. It is tuned for Codex App, Codex Goals, local skills, and a harness that refuses to call plausible output done.

## Pillars

The harness is designed for agents doing most implementation work and humans steering and correcting goals. Its seven pillars are:

- Intent and decisions: `FEATURE.md` and `PROOF.md` become decision-complete after repository inspection, focused material questions, edge-case challenge, and visible decision summaries. Codex then proceeds without asking the user to approve agent-authored contracts.
- Real-boundary proof: primary proof crosses the relevant API, UI, database, queue, provider, CLI, report, or workflow boundary and reads back durable or visible behavior. Scripts cannot make a weak scenario realistic.
- Reliable retained attempts: `scripts/proof_run_capture` records what ran, how it exited, relevant output, and contract/runner copies for every official failure, timeout, interruption, and pass.
- Autonomous repair: Codex treats proof, gate, and evaluator failures as the next work item, repairing the owning code, architecture, setup, fixture, diagnostic, or proof problem until completion or a true user/external blocker.
- Contract and proof integrity: revisions require a visible reason and must not narrow the user’s goal or weaken proof to manufacture green. Green-but-broken returns to proof design and demonstrates the missed failure when practical.
- Fresh completion judgment: a fresh read-only evaluator checks intent alignment, behavior, architecture quality, realistic proof, false-green risk, known gaps, and the gate. Behaviorally green code fails when it misses intent or weakens the owning architecture to pass.
- Learning without ceremony: retained attempts, `completion.md`, evaluator findings, and user corrections feed project/proof improvements first. Repeated cross-feature failures may change the smallest harness owner with a motivating regression and held-out check.

## References

These references live in Zotero under the `Harness Engineering` collection. They are the main external background for this dot-codex harness.

- Ryan Lopopolo, [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) - Codex harnesses as context, tools, checks, and feedback loops around the model.
- Xuying Ning et al., `Code as Agent Harness` - code as executable, inspectable, stateful harness substrate across interface, mechanisms, and multi-agent coordination.
- Jiahang Lin et al., [Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses](http://arxiv.org/abs/2604.25850) - harnesses as a first-class determinant of coding-agent performance.
- Jiawei Gu et al., `A Survey on LLM-as-a-Judge` - evaluator reliability, bias, calibration, and judging against explicit criteria.
- Wanqin Ma et al., `(Why) Is My Prompt Getting Worse? Rethinking Regression Testing for Evolving LLM APIs` - prompt/API drift, slice-level regression, nondeterminism, and held-out checks.
- Lei Wang et al., `A survey on large language model based autonomous agents` - autonomous-agent architecture around profiling, memory, planning, action, and evaluation.
- Anthropic engineers, via Anatoli Kopadze, [planner/generator/evaluator loop for full-app builds](https://x.com/AnatoliKopadze/status/2068690663919530207) - generator/evaluator separation, live app judging, and contract-driven iteration.
- dominik kundel, [A guide to /goal](https://x.com/dkundel/status/2062650378089594955) - Codex Goal as runtime state, not repo truth.
- Anatoli Kopadze, [Loops explained: Claude, GPT, Mira and what actually works](https://x.com/AnatoliKopadze/status/2068328135611822149) - autonomous loop patterns and persistent state.
- elvis, [From Prompting Agents to Loop Engineering](https://x.com/omarsar0/status/2068008743153832264) - the shift from prompting to engineered agent loops.
- Dan Farrelly, [The Agent Loop Architecture](https://x.com/djfarrelly/status/2067677007140278630) - loop primitives behind agentic systems.
- Deepak Babu Piskala, [Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants](http://arxiv.org/abs/2602.00180) - specs and contracts as primary artifacts when agents generate implementation.
- GitHub, [Spec Kit](https://github.com/github/spec-kit), and Fission AI, [OpenSpec](https://openspec.dev/) - practical SDD toolkits behind the `FEATURE.md` / `PROOF.md` split.
- Birgitta Bockeler, [Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) - pragmatic SDD tradeoffs.
- Andrej Karpathy, [Software Is Changing (Again)](https://www.youtube.com/watch?v=LCEmiRjPEtQ) and [coding workflow notes](https://x.com/karpathy/status/2015883857489522876) - human-in-the-loop coding and what remains worth reading.
- Geoffrey Huntley, [Ralph Wiggum as a "software engineer"](https://ghuntley.com/ralph/) - while-loop coding-agent pattern and its limits.
- Simon Willison, [What is agentic engineering?](https://simonwillison.net/guides/agentic-engineering-patterns/what-is-agentic-engineering/) - agentic engineering as an engineering discipline, not magic prompting.
- Peter Steinberger, [Shipping at Inference-Speed](https://steipete.me/posts/2025/shipping-at-inference-speed) - field report on high-throughput agent-assisted shipping.

The local direction is spec-driven development, code-as-harness, proof-centered execution, and observability-driven harness improvement.

## More Details

- Operating kernel: [`AGENTS.md`](AGENTS.md).
- Harness design and workflow: [`docs/harness/deep-dive.md`](docs/harness/deep-dive.md).
- Proof lifecycle and evidence bundles: [`docs/harness/proof-lifecycle.md`](docs/harness/proof-lifecycle.md).
- Proof scope and false-green risk: [`docs/harness/oracle-scope.md`](docs/harness/oracle-scope.md).
- Target repo autofix, autosuggestions, and auto-improve: [`docs/harness/repo-autonomy.md`](docs/harness/repo-autonomy.md).
- Autonomous execution and recovery: [`docs/harness/autonomous-execution.md`](docs/harness/autonomous-execution.md).
- Harness evolution: [`docs/harness/evolution/evolution-loop.md`](docs/harness/evolution/evolution-loop.md).
- Handoff format: [`docs/harness/handoff.md`](docs/harness/handoff.md).
- Non-coding and Second Brain workflows: [`docs/secondbrain.md`](docs/secondbrain.md).
