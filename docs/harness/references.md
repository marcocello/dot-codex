# Harness References

These references live in Zotero under the `Harness Engineering` collection. They are the main external background for this dot-codex harness.

- Ryan Lopopolo, [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) - OpenAI framing for Codex harnesses as context, tools, checks, and feedback loops around the model.
- Xuying Ning et al., `Code as Agent Harness` - survey framing for code as executable, inspectable, stateful harness substrate across interface, mechanisms, and multi-agent coordination.
- Jiahang Lin et al., [Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses](http://arxiv.org/abs/2604.25850) - research framing for harnesses as a first-class determinant of coding-agent performance.
- Jiawei Gu et al., `A Survey on LLM-as-a-Judge` - evaluator reliability, bias, calibration, and the need to judge against explicit criteria rather than model confidence.
- Wanqin Ma et al., `(Why) Is My Prompt Getting Worse? Rethinking Regression Testing for Evolving LLM APIs` - prompt/API drift, slice-level regression, nondeterminism, and why harness rules need held-out checks.
- Lei Wang et al., `A survey on large language model based autonomous agents` - autonomous-agent architecture patterns around profiling, memory, planning, action, and evaluation.
- Anthropic engineers, via Anatoli Kopadze, [Planner/generator/evaluator loop for full-app builds](https://x.com/AnatoliKopadze/status/2068690663919530207) - practical generator/evaluator separation, live app judging, and contract-driven iteration.
- dominik kundel, [A guide to /goal](https://x.com/dkundel/status/2062650378089594955) - Codex Goal as runtime state and durable objective control, not a replacement for repo truth.
- Anatoli Kopadze, [Loops explained: Claude, GPT, Mira and what actually works](https://x.com/AnatoliKopadze/status/2068328135611822149) - comparison of autonomous loop patterns and where persistent state matters.
- elvis, [From Prompting Agents to Loop Engineering](https://x.com/omarsar0/status/2068008743153832264) - shift from one-shot prompting to engineered agent loops.
- Dan Farrelly, [The Agent Loop Architecture](https://x.com/djfarrelly/status/2067677007140278630) - concise framing of the loop primitives behind agentic systems.
- Deepak Babu Piskala, [Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants](http://arxiv.org/abs/2602.00180) - why specs and contracts become primary artifacts when agents generate implementation.
- GitHub, [Spec Kit](https://github.com/github/spec-kit) and Fission AI, [OpenSpec](https://openspec.dev/) - practical SDD toolkits that informed the `FEATURE.md` / `PROOF.md` split.
- Birgitta Bockeler, [Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) - pragmatic analysis of SDD tools and tradeoffs.
- Andrej Karpathy, [Software Is Changing (Again)](https://www.youtube.com/watch?v=LCEmiRjPEtQ) and [coding workflow notes](https://x.com/karpathy/status/2015883857489522876) - human-in-the-loop coding, agent workflows, and what remains worth reading.
- Geoffrey Huntley, [Ralph Wiggum as a "software engineer"](https://ghuntley.com/ralph/) - while-loop coding-agent pattern and its limits.
- Simon Willison, [What is agentic engineering?](https://simonwillison.net/guides/agentic-engineering-patterns/what-is-agentic-engineering/) - clear language for agentic engineering as an engineering discipline, not magic prompting.
- Peter Steinberger, [Shipping at Inference-Speed](https://steipete.me/posts/2025/shipping-at-inference-speed) - field report on high-throughput agent-assisted shipping.
