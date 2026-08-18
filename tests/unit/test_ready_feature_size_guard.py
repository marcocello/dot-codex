import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8").lower()


def test_ready_transition_rejects_oversized_feature_packages() -> None:
    owners = (
        read_text("skills/coding-product-partner/SKILL.md"),
        read_text("skills/coding-feature-queue/SKILL.md"),
    )

    partner, queue = owners
    assert "one feature package per accepted independently valuable" in partner
    assert "split god features" in partner
    assert "independently runnable proof boundary" in partner
    assert "multiple independently valuable observable outcomes" in queue
    assert "independently runnable proof boundaries" in queue
    assert "before" in queue and "`ready`" in queue
    assert "multiple files or layers" in queue


def test_size_guard_does_not_expand_queue_schema() -> None:
    queue = json.loads((ROOT / "docs/features/status.json").read_text(encoding="utf-8"))
    allowed_fields = {"id", "feature_dir", "priority", "status", "notes"}

    for item in queue["features"]:
        assert set(item) == allowed_fields
