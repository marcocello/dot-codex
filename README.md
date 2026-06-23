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

## Harness Shape

The skills split responsibility instead of repeating one large workflow everywhere.

`coding-feature-spec` turns intent into a feature contract.

`coding-proof-author` is central: it turns the contract into executable proof and
anti-gaming pressure.

`coding-feature-execute`, `coding-repair`, and `coding-autonomous-execute` change code
inside those contracts.

`AGENTS.md` owns the operating contract. Skill files own local procedure. README stays
conceptual.

## Fundamental References

These references live in Zotero under the `Harness Engineering` collection. They are the
main external background for this dot-codex harness.

- Ryan Lopopolo, [Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/) — OpenAI framing for Codex harnesses as context, tools, checks, and feedback loops around the model.
- Jiahang Lin et al., [Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses](http://arxiv.org/abs/2604.25850) — research framing for harnesses as a first-class determinant of coding-agent performance.
- Anthropic engineers, via Anatoli Kopadze, [Planner/generator/evaluator loop for full-app builds](https://x.com/AnatoliKopadze/status/2068690663919530207) — practical generator/evaluator separation, live app judging, and contract-driven iteration.
- dominik kundel, [A guide to /goal](https://x.com/dkundel/status/2062650378089594955) — Codex Goal as runtime state and durable objective control, not a replacement for repo truth.
- Anatoli Kopadze, [Loops explained: Claude, GPT, Mira and what actually works](https://x.com/AnatoliKopadze/status/2068328135611822149) — comparison of autonomous loop patterns and where persistent state matters.
- elvis, [From Prompting Agents to Loop Engineering](https://x.com/omarsar0/status/2068008743153832264) — shift from one-shot prompting to engineered agent loops.
- Dan Farrelly, [The Agent Loop Architecture](https://x.com/djfarrelly/status/2067677007140278630) — concise framing of the loop primitives behind agentic systems.
- Deepak Babu Piskala, [Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants](http://arxiv.org/abs/2602.00180) — why specs and contracts become primary artifacts when agents generate implementation.
- GitHub, [Spec Kit](https://github.com/github/spec-kit) and Fission AI, [OpenSpec](https://openspec.dev/) — practical SDD toolkits that informed the `FEATURE.md` / `PROOF.md` split.
- Birgitta Bockeler, [Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) — pragmatic analysis of SDD tools and tradeoffs.
- Andrej Karpathy, [Software Is Changing (Again)](https://www.youtube.com/watch?v=LCEmiRjPEtQ) and [coding workflow notes](https://x.com/karpathy/status/2015883857489522876) — human-in-the-loop coding, agent workflows, and what remains worth reading.
- Geoffrey Huntley, [Ralph Wiggum as a "software engineer"](https://ghuntley.com/ralph/) — while-loop coding-agent pattern and its limits.
- Simon Willison, [What is agentic engineering?](https://simonwillison.net/guides/agentic-engineering-patterns/what-is-agentic-engineering/) — clear language for agentic engineering as an engineering discipline, not magic prompting.
- Peter Steinberger, [Shipping at Inference-Speed](https://steipete.me/posts/2025/shipping-at-inference-speed) — field report on high-throughput agent-assisted shipping.
