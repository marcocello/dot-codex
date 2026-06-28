## dot-codex

Around December 2025, I stopped writing code and stopped reading the code AI produced.

The product still matters. The code still matters. What changed is the control point: reading every generated line became less useful than shaping the work before generation and proving behavior after generation.

This repo is my current Codex configuration. It is tuned for Codex App, Codex Goals, local skills, and a harness that refuses to call plausible output done.

## Core Idea

This repo treats AI coding as a harness problem. The useful control surface is not a longer prompt; it is a small set of durable artifacts around the model.

`FEATURE.md` says what the feature is supposed to do. It is the product and behavior contract.

`PROOF.md` says how the feature earns trust. It keeps proof central by naming evidence, runtime checks, and the ways a fake or half-working implementation should be caught.

The repo gate protects general project health. It is useful, but it is not the same thing as feature proof.

The evaluator is the skeptical read-only judge. It exists because a green command is not always enough; the evidence has to match the behavior being claimed.

A Codex Goal keeps runtime moving during autonomous work. It is coordination state, not the source of truth.

If everything is green but the product is still broken, the harness treats that as a proof-system failure. Strengthen the proof first, then fix the implementation.

`AGENTS.md` owns the operating contract. Skills own procedure. Harness docs own the detailed map.

## More

- Operator map: [`docs/harness/operator-map.md`](docs/harness/operator-map.md).
- Harness references: [`docs/harness/references.md`](docs/harness/references.md).
- Non-coding and Second Brain workflows: [`docs/secondbrain.md`](docs/secondbrain.md).
