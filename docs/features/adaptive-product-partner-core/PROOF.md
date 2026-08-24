# Adaptive Product Partner Core Proof

## Done

- Active global routing, inventory, public design, agent metadata, and delivery fallbacks use one product-partner entry.
- The retired split app/feature shaping skills are absent from the active skill surface.
- The partner contract adapts to input cardinality and maturity, explores unknown, user, and technical implications, supports purposeful multi-turn questions without a fixed round cap, presents a concise practical working brief, controls adjacent scope, conditionally creates artifacts, contains no global React or OpenAI default, and names the separate delivery transitions.
- The complete repository gate remains green after affected active tests migrate away from the retired shaping skills.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/adaptive-product-partner-core --timeout-seconds 60 --note "verify one adaptive product partner and semantic eval corpus"
```

## Scenario: One active shaping authority serves all product input

- Producer/activation: pytest parses `skills.toml`, resolves the owned skill path, parses agent YAML, and reads `AGENTS.md`, `README.md`, `docs/harness/deep-dive.md`, the product-partner skill, and active delivery fallback references.
- Consumer: Codex receiving a rough idea, one feature, several possible outcomes, an app-level decision, or an implementation-authorized request.
- Read-back: assertions require the new partner across every active routing surface and reject the retired skill names and directories.
- Fake: none.
- Catches: adding a facade while leaving competing shaping skills or stale active routes in place.

## Scenario: Architecture selection and artifacts remain adaptive

- Producer/activation: pytest parses the product-partner structure and technology references.
- Consumer: greenfield and existing-repository product shaping.
- Read-back: assertions require the partner's understand, decide, scope, record, and continuation boundaries; the three discovery lenses; iterative resynthesis; no fixed question-round cap; and rejection of global React/OpenAI defaults.
- Fake: none.
- Catches: replacing question ceremony with a prescribed global stack or mandatory artifact bundle.

## Scenario: Discovery can deepen across multiple purposeful turns

- Producer/activation: pytest parses the active `Understand` and `Decide` contracts and mutation-canary versions with those sections hollowed.
- Consumer: Codex shaping an idea whose first answers reveal additional user implications, technical constraints, or unknowns.
- Read-back: assertions require focused grouped questions, resynthesis after each round, continuation while consequential unknowns remain, and termination based on decision readiness rather than a one- or two-round limit.
- Fake: none.
- Catches: treating questions only as a one-shot approval gate, skipping user or implementation implications, or allowing endless repetitive interrogation.

## Scenario: Deep analysis produces a practical response

- Producer/activation: pytest parses the active response contract and a mutation-canary version with that section hollowed.
- Consumer: a user who needs the partner's current understanding, recommendation, unresolved decisions, and questions without an analysis essay.
- Read-back: assertions require a concise one-screen synthesis, one recommended direction, highest-value missing or undecided items, short focused questions, expansion only when requested or risk warrants it, omission of empty sections and raw reasoning, and a direct fast path for clear requests.
- Fake: none.
- Catches: dumping internal analysis, repeating the request, hiding the recommendation, forcing a verbose template, or asking questions when nothing material is missing.

## Scenario: Delivery handoffs remain decomposed

- Producer/activation: pytest parses the partner continuation boundary and active delivery skill references.
- Consumer: planning-only, isolated repair, one-feature implementation, and authorized multi-feature continuation requests.
- Read-back: assertions require distinct routes to proof authoring, feature execution, repair, autonomous execution, and optional queue coordination.
- Fake: none.
- Catches: collapsing delivery into the partner, treating planning as implementation authorization, or sending every request through autonomous execution.

## Scenario: Active compatibility remains green

- Producer/activation: the official feature runner executes the repository gate after retired shaping skills and affected phrase-contract tests migrate.
- Consumer: existing proof capture, reviewer, freshness, runtime truth, repair, queue, and unrelated harness mechanics.
- Read-back: the gate exits successfully without unknown active skill references.
- Fake: none.
- Catches: an isolated partner test passing while the active harness remains internally inconsistent.

## Scope

Proves:
- The checkout exposes one discoverable adaptive shaping authority, open architecture selection, conditional artifact policy, explicit delivery handoffs, and compatible active consumers.

Does not prove:
- Delivery lifecycle consolidation, assurance transitions, or reviewer behavior.
- Comparative model behavior, which belongs to a separate behavioral-evaluation feature.

False-green risks:
- Static instruction and gate checks can validate active authority and boundaries but cannot guarantee future model judgment.

Evidence method:
- deterministic active-surface and corpus validation

Known gaps:
- Semantic replay is deferred to `product-partner-behavioral-evals`.

## Environment

- Repository-local Python and pytest; no network, credentials, deployment, or external mutation.
- Runner stdout identifies the repository Python runtime.
