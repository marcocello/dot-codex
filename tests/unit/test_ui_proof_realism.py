from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]


def assert_complete_ui_policy(profile: str) -> None:
    assert "genuine browser/user actions" in profile
    assert "calling handlers" in profile
    assert "directly dispatching dom events" in profile
    assert "loaded, decoded, and visible" in profile
    assert "url or source attribute" in profile
    assert "real protected application api" in profile
    assert "normal authentication/authorization path" in profile
    assert "visible or durable state" in profile
    assert "presentation-only states" in profile
    assert "fake only unsafe outer providers" in profile


def test_ui_proof_routes_to_complete_realism_profile() -> None:
    proof_author = (ROOT / "skills/coding-proof-author/SKILL.md").read_text(
        encoding="utf-8"
    ).lower()
    profile = (
        ROOT / "skills/coding-proof-author/references/proof-profiles.md"
    ).read_text(encoding="utf-8").lower()

    assert "ui/rendered artifact -> ui and artifact" in proof_author
    assert_complete_ui_policy(profile)


def test_ui_policy_oracle_rejects_source_only_resource_proof() -> None:
    profile = (
        ROOT / "skills/coding-proof-author/references/proof-profiles.md"
    ).read_text(encoding="utf-8").lower()
    weakened = profile.replace("loaded, decoded, and visible", "assigned a url")

    with pytest.raises(AssertionError):
        assert_complete_ui_policy(weakened)
