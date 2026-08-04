from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def normalized(text: str) -> str:
    return " ".join(text.split())


def test_global_kernel_treats_decisions_as_optional_question_passes() -> None:
    agents = read_text("AGENTS.md")

    assert "use two decision passes before substantial implementation" in agents
    assert "Each pass may contain zero user questions" in agents
    assert "no safe default" in agents
    assert "feature questions/challenge/decision summary" not in agents


def test_app_discovery_exposes_safe_greenfield_defaults() -> None:
    app_skill = read_text("skills/coding-app-to-features/SKILL.md")

    expected = (
        "smallest local-first, single-user application shape",
        "generic web application, use a React frontend",
        "backend API boundary",
        "OpenAI adapter behind a provider boundary",
        "credentials server-side",
        "deterministic fake only at the outer provider boundary",
        "Explicit user or repository constraints override inferred defaults",
        "no safe default",
        "same parent run",
        "Planning or specification-only requests stop after preparation",
        "Stack/domain skills own concrete implementation structure",
    )

    for phrase in expected:
        assert phrase in app_skill

    assert "Do not impose a default stack, folder tree, architecture" not in app_skill
    assert "No default stack, count, tree, or foundation-first sequence" not in app_skill


def test_feature_spec_infers_before_asking_about_architecture() -> None:
    feature_skill = read_text("skills/coding-feature-spec/SKILL.md")

    assert "Infer and disclose safe defaults before asking the user" in feature_skill
    assert "Do not ask architecture questions unless architecture changes" in feature_skill
    assert "no authoritative repository decision or safe default resolves it" in feature_skill
    assert "Ask focused grouped questions only for the remaining unresolved choices" in feature_skill


def test_proof_author_uses_safe_defaults_before_questions() -> None:
    proof_skill = read_text("skills/coding-proof-author/SKILL.md")

    assert "Infer deterministic safe proof defaults before asking" in proof_skill
    assert "Ask proof-specific questions only when" in proof_skill
    assert "has no safe default" in proof_skill
    assert "repository, request, or safe defaults resolve those choices" in proof_skill


def test_skill_prompts_do_not_force_question_first_behavior() -> None:
    app_prompt = normalized(read_text("skills/coding-app-to-features/agents/openai.yaml"))
    feature_prompt = normalized(read_text("skills/coding-feature-spec/agents/openai.yaml"))
    proof_prompt = normalized(read_text("skills/coding-proof-author/agents/openai.yaml"))

    assert "Infer safe defaults first" in app_prompt
    assert "Infer and disclose safe defaults before asking" in feature_prompt
    assert "Use deterministic safe proof defaults before asking" in proof_prompt

    combined = "\n".join((app_prompt, feature_prompt, proof_prompt))
    assert "Ask material questions" not in combined
    assert "Ask focused material feature questions" not in combined
    assert "Ask material proof questions" not in combined


def test_contract_authoring_requires_separate_implementation_request() -> None:
    agents = read_text("AGENTS.md")
    app_skill = read_text("skills/coding-app-to-features/SKILL.md")
    feature_skill = read_text("skills/coding-feature-spec/SKILL.md")
    proof_skill = read_text("skills/coding-proof-author/SKILL.md")
    execute_skill = read_text("skills/coding-feature-execute/SKILL.md")

    assert "requested deliverable" in agents
    assert "do not authorize implementation" in agents
    assert "separate explicit request" in agents

    for skill in (app_skill, feature_skill, proof_skill):
        assert "requested deliverable" in skill
        assert "do not authorize implementation" in skill
        assert "must not invoke `coding-feature-execute`" in skill
        assert "separate explicit request" in skill

    assert "Contract readiness alone is not implementation authorization" in execute_skill


def test_contract_authoring_prompts_stop_before_execution() -> None:
    prompts = (
        read_text("skills/coding-app-to-features/agents/openai.yaml"),
        read_text("skills/coding-feature-spec/agents/openai.yaml"),
        read_text("skills/coding-proof-author/agents/openai.yaml"),
    )

    for prompt in prompts:
        prompt_text = normalized(prompt)
        assert "requested deliverable" in prompt_text
        assert "separate explicit implementation request" in prompt_text

    feature_prompt = normalized(prompts[1])
    proof_prompt = normalized(prompts[2])
    assert "Stop after the contract package" in feature_prompt
    assert "do not invoke coding-feature-execute" in feature_prompt
    assert "Stop after proof authoring" in proof_prompt
    assert "do not invoke coding-feature-execute" in proof_prompt
