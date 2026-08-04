import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8").lower()


def test_completion_kernel_requires_an_unchanged_final_candidate() -> None:
    agents = read_text("AGENTS.md")
    execute = read_text("skills/coding-feature-execute/SKILL.md")

    for text in (agents, execute):
        assert "final candidate" in text
        assert "relevant edit" in text
        assert "stale" in text
    assert "before starting the evaluator" in execute
    assert "before marking" in execute and "`done`" in execute


def test_relevant_edit_after_proof_requires_proof_then_fresh_evaluator() -> None:
    execute = read_text("skills/coding-feature-execute/SKILL.md")
    autonomous = read_text("skills/coding-autonomous-execute/SKILL.md")

    for text in (execute, autonomous):
        assert "complete official proof" in text
        assert "fresh evaluator" in text
    assert "rerun the complete official proof before starting a fresh evaluator" in execute
    assert "rerun the complete official proof, then obtain another fresh evaluator" in execute
    assert "implementation" in execute
    assert "contracts" in execute
    assert "proof runner" in execute
    assert "fixtures" in execute
    assert "runtime" in execute
    assert "configuration" in execute
    assert "call paths" in execute


def test_evaluator_pass_is_void_after_a_relevant_edit() -> None:
    evaluator = read_text("skills/coding-feature-evaluator/SKILL.md")
    queue = read_text("skills/coding-feature-queue/SKILL.md")

    for text in (evaluator, queue):
        assert "candidate it inspected" in text
        assert "relevant edit" in text
        assert "void" in text
    assert "proof and another fresh evaluator" in evaluator


def test_bookkeeping_does_not_create_a_freshness_loop() -> None:
    execute = read_text("skills/coding-feature-execute/SKILL.md")
    deep_dive = read_text("docs/harness/deep-dive.md")

    for text in (execute, deep_dive):
        assert "retained attempt" in text
        assert "queue" in text and "bookkeeping" in text
        assert "not candidate changes" in text


def test_freshness_preserves_autonomous_queue_draining() -> None:
    autonomous = read_text("skills/coding-autonomous-execute/SKILL.md")

    proof_pass = "proof and fresh evaluator `pass`"
    select_next = "select the next `ready` item"
    assert proof_pass in autonomous
    assert select_next in autonomous
    assert autonomous.index(proof_pass) < autonomous.index(select_next)
    assert "no `ready` item remains" in autonomous


def test_freshness_adds_no_durable_coordination_state() -> None:
    feature = read_text("docs/features/final-candidate-freshness/FEATURE.md")
    deep_dive = read_text("docs/harness/deep-dive.md")

    forbidden_machinery = (
        "hashes",
        "manifests",
        "receipts",
        "dependency graph",
        "commit pin",
        "branches",
        "worktrees",
        "queue fields",
        "parallel coordinator",
    )
    for term in forbidden_machinery:
        assert term in feature
    assert "rerunning executable proof replaces freshness hashes" in deep_dive

    queue = json.loads((ROOT / "docs/features/status.json").read_text(encoding="utf-8"))
    allowed_fields = {"id", "feature_dir", "priority", "status", "notes"}
    assert all(set(item) == allowed_fields for item in queue["features"])
