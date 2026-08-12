from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8").lower()


def test_preflight_is_fresh_separate_bounded_and_runs_before_red() -> None:
    execute = read_text("skills/coding-feature-execute/SKILL.md")
    preflight = read_text("skills/coding-feature-preflight/SKILL.md")
    prompt = read_text("skills/coding-feature-preflight/agents/openai.yaml")

    assert execute.index("coding-feature-preflight") < execute.index(
        "establish red evidence"
    )
    for text in (execute, preflight, prompt):
        assert "fresh" in text
        assert "separate" in text
        assert "read-only" in text
        assert "at most three" in text or "no more than three" in text
    assert "one bounded" in preflight
    assert "repeat until" not in preflight
    assert "allow_implicit_invocation: false" in prompt


def test_preflight_challenges_general_contract_failure_surfaces() -> None:
    feature_spec = read_text("skills/coding-feature-spec/SKILL.md")
    proof_author = read_text("skills/coding-proof-author/SKILL.md")
    preflight = read_text("skills/coding-feature-preflight/SKILL.md")

    assert "strongest materially different interpretation" in feature_spec
    assert "authority" in proof_author
    assert "materially affected consumers" in proof_author
    for phrase in (
        "intent",
        "authority",
        "state transition",
        "affected consumers",
        "central false-green",
        "feature cohesion",
    ):
        assert phrase in preflight


def test_preflight_cannot_replace_implementation_proof_or_final_evaluation() -> None:
    feature = read_text("docs/features/lean-completion-lifecycle/FEATURE.md")
    preflight = read_text("skills/coding-feature-preflight/SKILL.md")
    execute = read_text("skills/coding-feature-execute/SKILL.md")
    evaluator = read_text("skills/coding-feature-evaluator/SKILL.md")

    for text in (feature, preflight):
        assert "does not" in text and "execute proof" in text
        assert "completion authority" in text
        assert "durable receipt" in text
    assert "candidate implementation" in preflight
    assert "lightweight" in preflight
    assert "after the current proof passes" in execute
    assert "completion requires its fresh `pass`" in evaluator


def test_preflight_need_input_blocks_the_real_implementation_path() -> None:
    execute = read_text("skills/coding-feature-execute/SKILL.md")
    preflight = read_text("skills/coding-feature-preflight/SKILL.md")

    for text in (execute, preflight):
        assert "need_input" in text
        assert "do not begin red evidence or implementation" in text or (
            "blocks red evidence and implementation" in text
        )
    assert "queue item `blocked`" in execute


def test_preflight_is_owned_without_expanding_queue_state() -> None:
    inventory = read_text("skills.toml")
    queue = read_text("skills/coding-feature-queue/SKILL.md")
    deep_dive = read_text("docs/harness/deep-dive.md")

    assert 'name = "coding-feature-preflight"' in inventory
    assert "coding-feature-preflight" in deep_dive
    for forbidden in ("preflight_pass", "preflight_status", "preflight_findings"):
        assert forbidden not in queue
