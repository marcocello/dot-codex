from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = ROOT / "skills" / "coding-commit" / "SKILL.md"
OPENAI_YAML_PATH = ROOT / "skills" / "coding-commit" / "agents" / "openai.yaml"


def read_skill_parts() -> tuple[str, str]:
    skill = SKILL_PATH.read_text(encoding="utf-8")
    _, frontmatter, body = skill.split("---", 2)
    return frontmatter, body


def test_commit_scope_is_repository_driven_not_task_driven() -> None:
    frontmatter, body = read_skill_parts()

    assert "regardless of which task or chat produced the changes" in frontmatter
    assert "Task provenance is not a commit-scope boundary." in body
    assert "Explicit scope:" in body
    assert "include only the named paths or concern" in body
    assert "Unscoped commit request:" in body
    assert "include the complete repository change set" in body
    assert "Do not exclude, refuse, or request confirmation for a change solely because" in body
    assert "it predates or is unrelated to the current task" in body


def test_cross_task_scope_retains_commit_safeguards() -> None:
    _, body = read_skill_parts()

    assert "Stage selected files for each commit group; do not use `git add .`." in body
    assert "Preserve an explicit existing staged selection." in body
    assert "If the user only asks for a commit message, do not stage files and do not commit." in body
    assert "Never push. Do not run `git push`." in body
    assert "Create multiple commits when the selected repository scope contains" in body


def test_skill_remains_available_for_implicit_project_invocation() -> None:
    metadata = OPENAI_YAML_PATH.read_text(encoding="utf-8")

    assert 'default_prompt: "Use $coding-commit' in metadata
    assert "including changes from other tasks" in metadata
    assert "allow_implicit_invocation: true" in metadata
