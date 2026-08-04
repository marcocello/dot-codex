from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = ROOT / "skills" / "coding-ui-improvement" / "SKILL.md"
OPENAI_YAML_PATH = ROOT / "skills" / "coding-ui-improvement" / "agents" / "openai.yaml"
MCP_ROUTING_PATH = (
    ROOT / "skills" / "coding-ui-improvement" / "references" / "mcp-routing.md"
)


def read_skill_parts() -> tuple[str, str]:
    skill = SKILL_PATH.read_text(encoding="utf-8")
    _, frontmatter, body = skill.split("---", 2)
    return frontmatter, body


def test_skill_is_advisory_only_for_every_ui_request() -> None:
    frontmatter, body = read_skill_parts()

    assert "written, component-specific improvement instructions" in frontmatter
    assert "never implement changes" in frontmatter
    assert "advisory-only in every invocation" in body
    assert "Do not edit product or test files, generate or apply patches" in body
    assert "install or copy components, or change dependencies or configuration" in body
    assert "Do not treat implementation-shaped wording as edit authorization" in body
    assert "requires a separate implementation task" in body
    assert "Do not invoke that implementation workflow in the current task" in body
    assert "## Implement improvements" not in body
    assert "authorization to implement" not in body


def test_written_brief_names_components_and_exact_changes() -> None:
    _, body = read_skill_parts()

    assert "Affected component" in body
    assert "existing component name and repository-relative file path" in body
    assert "Exact instruction" in body
    assert "States and adaptation" in body
    assert "Accessibility and responsive behavior" in body
    assert "Acceptance check" in body
    assert "Source and candidate" in body
    assert "source or registry, component identifier" in body
    assert "intended local target" in body


def test_feedback_and_external_components_remain_read_only() -> None:
    _, body = read_skill_parts()
    routing = MCP_ROUTING_PATH.read_text(encoding="utf-8")

    assert "Never acknowledge, resolve, or otherwise mutate an annotation" in body
    assert "Recommendations do not authorize installation or copying." in body
    assert "Never present inspiration as a tested solution." in body
    assert "Use every configured server through read-only discovery and inspection" in routing
    assert "Never call reply, acknowledge, resolve, dismiss, or other state-changing" in routing
    assert "Do not run add commands or copy registry source" in routing
    assert "Never enter an implementation phase from this skill" in routing


def test_agent_metadata_matches_the_advisory_contract() -> None:
    metadata = OPENAI_YAML_PATH.read_text(encoding="utf-8")

    assert 'short_description: "Write component-specific UI improvement briefs."' in metadata
    assert 'default_prompt: "Use $coding-ui-improvement to write' in metadata
    assert "component-specific UI improvement brief without editing the product" in metadata
    assert 'description: "Read visual feedback annotations from the running interface."' in metadata
    assert "allow_implicit_invocation: true" in metadata
