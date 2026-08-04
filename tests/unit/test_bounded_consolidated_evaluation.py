import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8").lower()


def test_evaluator_completes_review_and_consolidates_material_findings() -> None:
    evaluator = read_text("skills/coding-feature-evaluator/SKILL.md")
    evaluator_prompt = read_text("skills/coding-feature-evaluator/agents/openai.yaml")

    for text in (evaluator, evaluator_prompt):
        assert "all material findings" in text
        assert "do not stop at the first" in text
    assert "complete the bounded review" in evaluator
    assert "preferences" in evaluator


def test_same_evaluator_performs_ordered_evidence_then_implementation_passes() -> None:
    evaluator = read_text("skills/coding-feature-evaluator/SKILL.md")
    execute = read_text("skills/coding-feature-execute/SKILL.md")
    evaluator_prompt = read_text("skills/coding-feature-evaluator/agents/openai.yaml")
    deep_dive = read_text("docs/harness/deep-dive.md")

    evidence_heading = "pass 1 — evidence"
    implementation_heading = "pass 2 — implementation"
    assert evaluator.index(evidence_heading) < evaluator.index(implementation_heading)
    assert "before opening implementation files" in evaluator
    assert "actual retained output" in evaluator
    assert "do not use parent implementation summaries as evidence" in evaluator
    assert "challenge the evidence-pass claim map" in evaluator

    for text in (execute, evaluator_prompt, deep_dive):
        assert "evidence-first" in text
        assert "implementation-second" in text


def test_two_pass_review_does_not_add_an_agent_or_durable_intermediate_stage() -> None:
    feature = read_text("docs/features/bounded-consolidated-evaluation/FEATURE.md")
    evaluator = read_text("skills/coding-feature-evaluator/SKILL.md")
    execute = read_text("skills/coding-feature-execute/SKILL.md")

    for text in (feature, evaluator, execute):
        assert "same evaluator" in text
        assert "no intermediate report" in text
    assert "one final verdict" in evaluator


def test_same_checkout_evaluation_uses_transient_active_feature_surface() -> None:
    execute = read_text("skills/coding-feature-execute/SKILL.md")
    autonomous = read_text("skills/coding-autonomous-execute/SKILL.md")
    evaluator = read_text("skills/coding-feature-evaluator/SKILL.md")

    for text in (execute, autonomous, evaluator):
        assert "transient active-feature surface" in text
    assert "files changed for this feature" in execute
    assert "directly relevant call paths" in execute
    assert "reset" in autonomous and "next" in autonomous
    assert "accumulated dirty diff" in evaluator
    assert "follow a call path outside that surface" in evaluator
    for forbidden_state in (
        "queue fields",
        "intermediate reports",
        "receipts",
        "hashes",
        "commits",
        "branches",
        "worktrees",
        "another agent",
        "another completion stage",
    ):
        assert forbidden_state in execute

    queue = json.loads((ROOT / "docs/features/status.json").read_text(encoding="utf-8"))
    allowed_fields = {"id", "feature_dir", "priority", "status", "notes"}
    assert all(set(item) == allowed_fields for item in queue["features"])


def test_findings_keep_proof_backed_repair_and_fresh_evaluation() -> None:
    execute = read_text("skills/coding-feature-execute/SKILL.md")
    evaluator = read_text("skills/coding-feature-evaluator/SKILL.md")

    for text in (execute, evaluator):
        assert "strengthen proof" in text
        assert "repair" in text
        assert "fresh evaluat" in text
    assert "repeat until a fresh evaluator returns `pass`" in execute


def test_autonomous_execution_still_drains_all_ready_features() -> None:
    autonomous = read_text("skills/coding-autonomous-execute/SKILL.md")
    lifecycle = read_text("docs/harness/autonomous-execution.md")

    for text in (autonomous, lifecycle):
        assert "select the next" in text
        assert "no `ready` item remains" in text or "no ready item remains" in text
    assert "one feature and one `feature_dir`" in autonomous
    assert autonomous.index("proof and fresh evaluator `pass`") < autonomous.index(
        "select the next `ready` item"
    )


def test_durable_rationale_matches_bounded_comprehensive_review() -> None:
    deep_dive = read_text("docs/harness/deep-dive.md")

    assert "bounded evaluation" in deep_dive
    assert "evidence-first" in deep_dive
    assert "implementation-second" in deep_dive
    assert "transient changed-file surface" in deep_dive
    assert "all material findings" in deep_dive
    assert "one parent completes one feature before selecting the next" in deep_dive
