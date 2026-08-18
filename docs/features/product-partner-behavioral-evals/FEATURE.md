# Product Partner Behavioral Evaluations

## Goal

Evaluate sampled product-partner outputs against representative semantic outcomes instead of exact prompt wording.

## Behavior

- Maintain representative rough-idea, detailed-build, adjacent-scope, low-risk-fix, future-seam, and runtime-proof cases.
- Score sampled outputs for problem synthesis, question economy, initiative, scope control, architecture proportionality, proof fidelity, and completion truth.
- Expected and disallowed outcomes are semantic criteria, not required phrases or fixed response templates.
- A harness revision does not claim improved partner behavior from corpus structure alone; it must retain sampled outputs and a fresh evidence-backed judgment.
- Store one small human-readable case corpus, one sampled-output set, and one judgment set. Each sample and judgment identifies its case and capture context.
- Judge each dimension as `meets`, `mixed`, `misses`, or `not_applicable`, with concise evidence. Do not calculate an aggregate score that hides a weak dimension.
- A judgment may honestly report mixed or missed behavior; evidence integrity, not a forced green behavioral verdict, is the feature outcome.

## Decisions

- The initial corpus contains exactly the six representative situations above. Add a case only when observed behavior exposes a materially different pressure.
- Product-partner prose remains unconstrained. The corpus describes outcomes to notice and failure modes to reject; it does not prescribe headings, phrases, question counts, or response schemas.
- Deterministic checks validate case coverage, referential integrity, evidence completeness, timestamps, and the absence of placeholder evidence. A fresh semantic reviewer assesses whether the judgments are supported by the sampled outputs.
- The active checkout is the consumption target; no deployed runtime or external model API is required.

## Acceptance

- All six situations have non-placeholder prompts, semantic expected/disallowed outcomes, and retained sampled outputs.
- Every sample receives evidence-backed judgments for all seven dimensions, allowing an explained `not_applicable` result.
- The proof fails when a case, sample, dimension, rationale, or capture relationship is removed or hollowed.
- A fresh final review reads outputs before implementation policy and confirms that judgments are supported without relying on exact phrases.

## Constraints

- Do not add a model-calling service, score database, or mandatory response format.
- Keep deterministic gate checks limited to corpus and evidence integrity; behavioral verdicts remain probabilistic and explicit.
- Do not make a behavioral pass a repository-gate requirement; future model variability must remain inspectable rather than silently blocking unrelated changes.

## Non-Goals

- Replacing feature-specific executable proof.
- Claiming universal model quality from a small scenario set.
- Benchmarking models or comparing vendors.
- Automatically invoking a paid or external model endpoint.
