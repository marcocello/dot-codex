## dot-codex

Around December 2025, I stopped writing code. I also stopped reading generated code as the primary way to decide whether the work was done.

The product still matters. The code still matters. The rendered output still matters. What changed is the control point: instead of manually inspecting every generated source file, I shape the work before generation and make the AI produce proof that its work matches the intended behavior.

This repo is my current Codex configuration. It is tuned for Codex App, Codex Goals, local skills, and a harness that refuses to call plausible output done.

## Pillars

The harness is designed for agents doing most implementation work and humans steering, judging, and correcting the system. These are the public pillar names in the README; the presentation groups them into the compact seven-pillar model.

- Feature spec: `FEATURE.md` is the agent-native behavior source of truth before implementation, including expected outcome, constraints, architecture boundaries, and user-visible result. Why it matters: the agent works from a stable contract instead of guessing from a prompt.
- Proof contract: `PROOF.md` defines the command, scenario, proof scope, anti-gaming pressure, and evidence needed to prove done. Why it matters: done becomes testable before code exists.
- Real-boundary proof: primary proof must cross the relevant API, UI, DB, queue, provider, CLI, report, or workflow boundary. Why it matters: the harness proves behavior where the product can actually fail.
- Captured evidence: feature proof runs must leave `FEATURE_DIR/proof/runs/<timestamp>/` evidence through `scripts/proof_run_capture`, with enough structure for another agent or human to inspect the run. Why it matters: later review can audit what happened without trusting the assistant's summary.
- Autonomous repair: Codex keeps repairing code, setup, fixtures, diagnostics, or proof ownership until proof, gate, and evaluator pass or a true blocker remains. Why it matters: failures become the next input, not a reason to stop early.
- Contract freeze: after implementation starts, Codex must not change `FEATURE.md`, `PROOF.md`, or proof artifacts to make the result green. Why it matters: the agent cannot move the goalposts after seeing the answer.
- Proof scope: every non-trivial proof states what it proves, what it does not prove, false-green risks, and evidence strength. Why it matters: humans can see the remaining risk instead of reading a vague pass/fail.
- Done evaluator: `coding-feature-evaluator` is the skeptical read-only judge before completion, and the final handoff must be precise, clear, actionable, and grounded in proof, gate, evaluator, blockers, and changed surface. Why it matters: completion is judged separately from the agent that produced the work.
- Green-but-broken: a green command with broken behavior means the proof is insufficient and must be repaired first. Why it matters: the harness optimizes for real behavior, not green output.
- App improvement review: `coding-app-improvement-review` suggests app, proof, readiness, and harness improvements from proof history and human-agent interaction, including corrections, repeated questions, scope misses, and unclear handoffs. Why it matters: useful lessons are captured without automatically broadening scope.
- Harness evolution: harness changes need repeated evidence, before/after expectations, held-out checks, and a rollbackable manifest, with accepted learning routed to the smallest durable owner. Why it matters: the harness improves deliberately instead of accumulating random prompt tweaks.

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
- Harness workflow: [`docs/harness/operator-map.md`](docs/harness/operator-map.md).
- Proof lifecycle and evidence bundles: [`docs/harness/proof-lifecycle.md`](docs/harness/proof-lifecycle.md).
- Proof scope and false-green risk: [`docs/harness/oracle-scope.md`](docs/harness/oracle-scope.md).
- Target repo autofix, autosuggestions, and auto-improve: [`docs/harness/repo-autonomy.md`](docs/harness/repo-autonomy.md).
- Autonomous execution and recovery: [`docs/harness/autonomous-execution.md`](docs/harness/autonomous-execution.md).
- Harness evolution: [`docs/harness/evolution/evolution-loop.md`](docs/harness/evolution/evolution-loop.md).
- Handoff format: [`docs/harness/handoff.md`](docs/harness/handoff.md).
- Non-coding and Second Brain workflows: [`docs/secondbrain.md`](docs/secondbrain.md).
