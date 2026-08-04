import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8").lower()


def test_ready_transition_rejects_oversized_feature_packages() -> None:
    owners = (
        read_text("skills/coding-app-to-features/SKILL.md"),
        read_text("skills/coding-feature-spec/SKILL.md"),
        read_text("skills/coding-feature-queue/SKILL.md"),
    )

    for owner in owners:
        assert "multiple independently valuable observable outcomes" in owner
        assert "independently runnable proof boundaries" in owner
        assert "before" in owner and "`ready`" in owner
    assert "multiple files or layers" in owners[0]
    assert "multiple files or layers" in owners[2]


def test_size_guard_does_not_expand_queue_schema() -> None:
    queue = json.loads((ROOT / "docs/features/status.json").read_text(encoding="utf-8"))
    allowed_fields = {"id", "feature_dir", "priority", "status", "notes"}

    for item in queue["features"]:
        assert set(item) == allowed_fields

