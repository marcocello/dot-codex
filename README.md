## dot-codex

Around December 2025, I stopped writing code and stopped reading the code AI produced.

The product still matters. The code still matters. What changed is the control point: reading every generated line became less useful than shaping the work before generation and proving behavior after generation. This repo focuses on sharper feature contracts, stronger proof, runtime checks, skeptical evaluation, and a harness that refuses to call plausible output done.

This repo is my current Codex configuration. Most of it also applies to Claude Code and other agentic coding systems, but this checkout is tuned for Codex App, Codex Goals, local skills, and the way I build software.

It mixes roughly twenty years of software work with what is now called harness engineering. Vibe coding was the trial phase. Feature-driven coding made the work describable. Ralph-style loops made agents persistent. Goals made long runs controllable. Proof and evaluators decide whether the output is worth trusting.

When AI writes most of the code, the old pipeline is incomplete. Issues, PRs, human-style review, and CI were designed for a world where humans produced most of the output. This repo is my attempt to adapt that pipeline to bounded agentic workflows.


## Core Idea

The repo forces Codex to work like this:

```text
describe the change
  -> write what should happen
  -> PROOF.md + anti-gaming review + executable proof tests
  -> implement one feature
  -> run the feature proof
  -> run the repo safety checks
  -> read-only done evaluator
  -> fix only concrete failures
  -> mark it passing, failing, or blocked
```

`FEATURE.md` says what the feature is supposed to do. It is the product/behavior contract.

`PROOF.md` says how we prove the feature works. It must include the command to run, the expected evidence, the test data or environment needed, and the cases that would catch a fake or half-working implementation.

The proof command executes evidence. The primary proof is the real feature test. For a UI feature, that usually means opening the app and driving it like a user. For an API, it means calling the real route. For an external provider, it means using realistic payloads and checking the state that comes back. For an internal change, it means proving the invariant, migration, equivalence, or performance claim.

The gate protects repo health. It checks tests, lint, type checks, build, or whatever the project defines. A passing gate does not prove the feature works.

The evaluator judges whether the evidence and implementation are enough. It is a read-only judge that looks at the feature, the proof, the code changes, and the command results, then returns `PASS`, `FAIL`, or `BLOCKED`.

The Goal only keeps runtime moving. It is not the source of truth. The source of truth is still `FEATURE.md`, `PROOF.md`, the proof result, the gate result, and the evaluator result.

If everything is green but the product is still broken, treat that as a proof-system failure. Strengthen the proof first, then fix the implementation.

## Greenfield

1. Describe the app.
2. Use `coding-app-to-features`.
3. Review the generated `docs/APP.md`, `docs/ARCHITECTURE.md`, feature specs, proof packages, and `docs/features/status.json`.
4. Use `coding-autonomous-execute` when you want Codex to keep working through the queue.
5. Codex works one feature at a time until everything is passing or the remaining items are blocked with concrete reasons.

## Brownfield

1. Describe the feature or change.
2. Use `coding-feature-spec` to create or refine one `docs/features/<feature-id>/FEATURE.md`.
3. Let `coding-proof-author` create or repair `PROOF.md` plus executable proof artifacts.
4. Use `coding-feature-execute` for one ready feature, or `coding-autonomous-execute` for queue execution.
5. Completion requires primary proof, gate, and evaluator `PASS`.

## Bug Fixes

1. Bugfixes first look for one clear matching `docs/features/*/FEATURE.md`.
2. If exactly one feature matches, use that feature's `PROOF.md` and strengthen it with a focused failing regression when the existing proof misses the bug.
3. If no feature clearly matches, do not create `FEATURE.md` by default. Add the smallest local regression proof near the affected code.
4. Fix the root cause, rerun the narrow proof, then rerun the relevant broader checks.
5. Use `coding-feature-evaluator` before calling the fix done.

## Fundamental References

These references live in Zotero under the `Harness Engineering` collection. They are the main external background for this dot-codex harness.

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
