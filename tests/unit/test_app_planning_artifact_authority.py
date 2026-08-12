from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_app_planning_keeps_one_authoritative_repository_record() -> None:
    app_skill = (
        ROOT / "skills/coding-app-to-features/SKILL.md"
    ).read_text(encoding="utf-8")

    assert "Do not create a parallel app plan" in app_skill
    assert "`outputs/`" in app_skill
    assert "The handoff is a chat response, not another repository artifact" in app_skill
    assert "Fold durable planning decisions into their owning document" in app_skill
