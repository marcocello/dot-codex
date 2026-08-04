import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_completion_owner_requires_proof_then_fresh_evaluator_pass() -> None:
    agents = read_text("AGENTS.md")
    execute = read_text("skills/coding-feature-execute/SKILL.md")
    evaluator = read_text("skills/coding-feature-evaluator/SKILL.md")

    assert "passing realistic proof and a fresh" in agents
    assert "fresh read-only `coding-feature-evaluator` `pass`" in agents.lower()
    assert execute.index("Capture proof") < execute.index("Run fresh evaluator")
    assert execute.index("Run fresh evaluator") < execute.index("Finalize queue")
    assert "repeat until a fresh evaluator returns `pass`" in execute.lower()
    assert "completion requires its fresh `PASS`" in evaluator


def test_active_completion_policy_has_no_fast_check_or_batch() -> None:
    paths = (
        "AGENTS.md",
        "docs/harness/autonomous-execution.md",
        "docs/harness/deep-dive.md",
        "skills/coding-autonomous-execute/SKILL.md",
        "skills/coding-feature-evaluator/SKILL.md",
        "skills/coding-feature-execute/SKILL.md",
        "skills/coding-feature-queue/SKILL.md",
    )
    forbidden = (
        "repository-native fast check",
        "repository fast check",
        "fast-check",
        "two-feature",
        "next batch",
        "compatible ready",
        "accountable coordinator",
        "stable-checkout barrier",
    )

    for path in paths:
        lowered = read_text(path).lower()
        for phrase in forbidden:
            assert phrase not in lowered, (path, phrase)


def test_queue_has_four_states_and_proof_evaluator_completion() -> None:
    queue_skill = read_text("skills/coding-feature-queue/SKILL.md")
    queue = json.loads(read_text("docs/features/status.json"))
    allowed_fields = {"id", "feature_dir", "priority", "status", "notes"}
    allowed_statuses = {"draft", "ready", "blocked", "done"}

    for status in allowed_statuses:
        assert f"`{status}`" in queue_skill
    assert "realistic feature proof" in queue_skill
    assert "fresh evaluator `PASS`" in queue_skill
    assert "lowest-priority-number `ready` item" in queue_skill
    assert "revalidate_on" not in queue_skill
    assert "invalidate_feature_status" not in queue_skill

    for item in queue["features"]:
        assert set(item) == allowed_fields
        assert item["status"] in allowed_statuses


def test_autonomous_execution_selects_one_feature_serially() -> None:
    autonomous = read_text("skills/coding-autonomous-execute/SKILL.md")

    assert "lowest-priority-number `ready` item" in autonomous
    assert "one feature and one `FEATURE_DIR`" in autonomous
    assert "coding-feature-execute" in autonomous
    assert "select the next `ready` item" in autonomous
    assert "no `ready` item remains" in autonomous


def test_evaluator_runs_for_every_non_lightweight_feature_and_repeats_after_findings() -> None:
    agents = read_text("AGENTS.md")
    execute = read_text("skills/coding-feature-execute/SKILL.md")
    evaluator = read_text("skills/coding-feature-evaluator/SKILL.md")
    evaluator_prompt = read_text("skills/coding-feature-evaluator/agents/openai.yaml")

    assert "Every tracked and autonomous feature" in agents
    assert "Lightweight work does not invoke the evaluator" in agents
    assert "after the current proof passes" in execute.lower()
    assert "another fresh evaluator" in execute
    assert "FINDINGS" in evaluator
    assert "strengthen proof" in evaluator
    assert "fresh evaluation" in evaluator
    assert "allow_implicit_invocation: false" in evaluator_prompt
    assert "final" in evaluator_prompt.lower()
    assert "pass" in evaluator_prompt.lower()


def test_proof_capture_keeps_evaluator_driven_corrections() -> None:
    execute = read_text("skills/coding-feature-execute/SKILL.md")
    lifecycle = read_text("docs/harness/proof-lifecycle.md")

    assert "meaningful red" in lifecycle
    assert "final passing" in lifecycle
    assert "materially distinct" in lifecycle
    assert "next proof attempt note" in execute
    assert "demonstrate the missed failure" in execute


def test_app_preparation_authors_every_decided_lean_feature_and_proof() -> None:
    app_to_features = read_text("skills/coding-app-to-features/SKILL.md")
    app_prompt = read_text("skills/coding-app-to-features/agents/openai.yaml")

    combined = "\n".join((app_to_features, app_prompt)).lower()
    assert "complete non-speculative feature set" in combined
    assert "every decided feature" in combined
    assert "one coherent observable outcome" in combined
    assert "god feature" in combined
    assert "coding-feature-spec" in combined
    assert "coding-proof-author" in combined
    assert "executable `proof/run.sh`" in combined


def test_graphify_is_not_global_harness_policy() -> None:
    paths = (
        "AGENTS.md",
        "README.md",
        "docs/harness/autonomous-execution.md",
        "docs/harness/deep-dive.md",
        "skills/coding-autonomous-execute/SKILL.md",
        "skills/coding-feature-execute/SKILL.md",
        "skills/coding-feature-queue/SKILL.md",
    )

    for path in paths:
        assert "graphify" not in read_text(path).lower(), path


def test_obsolete_overlap_invalidator_is_removed() -> None:
    assert not (ROOT / "scripts/invalidate_feature_status").exists()
