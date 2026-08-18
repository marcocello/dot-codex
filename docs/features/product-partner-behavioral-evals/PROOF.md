# Product Partner Behavioral Evaluations Proof

## Done

- Six representative product-partner cases use semantic expected and disallowed outcomes without response templates or required phrases.
- Each case has one retained sampled output and evidence-backed judgment across all seven accepted dimensions.
- Deterministic checks prove corpus, sample, and judgment integrity while leaving semantic quality to a fresh read-only reviewer.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/product-partner-behavioral-evals --timeout-seconds 60 --note "verify retained semantic product-partner evaluations"
```

## Scenario: Representative outputs remain inspectable

- Producer/activation: pytest loads the active YAML corpus, samples, and judgments from the checkout.
- Consumer: a maintainer assessing whether `coding-product-partner` behaves as a proactive but scope-controlled partner.
- Read-back: assertions join all six case identifiers across prompt, sample, and judgment artifacts and reject missing or placeholder content.
- Fake: the retained outputs are explicitly labelled samples from this Codex task; no external model endpoint is simulated.
- Catches: a structural corpus that claims evaluation without actual outputs, lost provenance, or silently omitted difficult cases.

## Scenario: Judgments remain dimensional and evidence-backed

- Producer/activation: pytest validates every case against the seven accepted dimensions.
- Consumer: the fresh final reviewer reads each output and checks the recorded judgment against semantic expected and disallowed outcomes.
- Read-back: every dimension has an allowed verdict and non-placeholder evidence; `not_applicable` requires an explanation and no aggregate score exists.
- Fake: none. Deterministic tests validate integrity, not prose quality.
- Catches: one headline score hiding weak behavior, hollow rationales, phrase-match scoring, or a claimed universal model-quality result.

## Scenario: Integrity regressions are detectable

- Producer/activation: mutation canaries remove a case, sample, dimension, and rationale from parsed in-memory copies.
- Consumer: the same integrity validator used by the active test.
- Read-back: each mutation produces an explicit validation error.
- Fake: in-memory mutations are diagnostic canaries, not substitutes for the retained sample boundary.
- Catches: a validator that only checks whether files exist.

## Scope

Proves:
- The active checkout retains a coherent six-case semantic evaluation set with complete dimensional evidence.

Does not prove:
- Universal product-partner quality, deterministic future responses, or superiority over another model or harness.
- Product feature correctness; each delivered feature still requires its own executable proof.

False-green risks:
- Structurally valid judgments could be semantically generous. A fresh read-only final reviewer must inspect outputs before policy and challenge unsupported verdicts.

Evidence method:
- deterministic YAML integrity validation, mutation canaries, complete repository gate, and fresh semantic final review

Known gaps:
- The initial set is small and sampled in one task context; expand it only after observed misses justify a distinct pressure.

## Environment

- Active repository checkout, repository-local Python, PyYAML, and pytest.
- No credentials, external model endpoint, deployment, paid resource, or external mutation.
