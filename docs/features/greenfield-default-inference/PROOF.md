# Greenfield Default Inference Proof

## Done
- The composed global, app-discovery, feature-spec, and proof-author instruction surfaces consistently require safe default inference before user questions.
- The greenfield profile preserves explicit constraints, material ambiguity questions, stack-skill scaffold ownership, and create/build continuation into implementation.
- Question-first default prompts no longer override the conditional ask policy in the skill bodies.

## Command

```bash
"${CODEX_HOME:-$HOME/.codex}/scripts/proof_run_capture" --feature-dir docs/features/greenfield-default-inference --timeout-seconds 60 --note "verify greenfield default inference policy"
```

## Scenario: Minimal greenfield create request
- Producer/activation: pytest reads the actual `AGENTS.md`, `coding-app-to-features`, `coding-feature-spec`, and proof-author instruction artifacts loaded by Codex.
- Consumer: the composed global and skill instruction surface.
- Read-back: assertions require a zero-question decision-pass option, the safe greenfield profile, conditional questions, and same-run create/build continuation.
- Fake: none.
- Catches: retaining mandatory question rounds, prohibiting every architecture default, or stopping a create/build request after planning.

## Scenario: Prompt metadata agrees with skill policy
- Producer/activation: pytest reads the actual app, feature, and proof `agents/openai.yaml` files.
- Consumer: the skill invocation prompts.
- Read-back: assertions require infer-first conditional wording and reject unconditional `Ask material questions` variants.
- Fake: none.
- Catches: correcting skill bodies while leaving stronger question-first invocation prompts active.

## Scenario: Material ambiguity and ownership remain protected
- Producer/activation: pytest reads the global kernel and app/feature skill contracts.
- Consumer: the same policy sources used for greenfield routing.
- Read-back: assertions require explicit constraints to override defaults, no-safe-default material choices to remain questions, and stack skills to retain concrete scaffold ownership.
- Fake: none.
- Catches: replacing question-first behavior with unsafe silent guessing or moving folder/starter ownership into app discovery.

## Scope
Proves:
- The active instruction artifacts expose one consistent infer-first greenfield decision policy.
- The original question-first prompt metadata is absent from all three involved skills.
- The policy distinguishes safe defaults from material unresolved choices and distinguishes create/build from planning-only requests.

Does not prove:
- Deterministic instruction compliance by every future model or product version.
- Behavior in an already-running task that loaded older instructions.
- Live OpenAI provider behavior or deployment behavior.

False-green risks:
- Static policy assertions can pass while a future model ignores the instructions; the claimed deterministic boundary is policy availability and consistency, while live model adherence remains a declared gap.
- Checking only one skill could miss a stronger conflicting prompt elsewhere; the regression reads the global kernel, all three skill bodies or prompts involved in the original interaction, and the scaffold ownership rule.

Evidence method:
- deterministic

Known gaps:
- Live model adherence is probabilistic and would require a fresh paid/external inference run.

## Environment
- Repository-local Python virtual environment and pytest.
- No network, credentials, provider calls, or external mutations.
- Runner stdout: resolved Python executable/version and the instruction files under test.
