from __future__ import annotations

from pathlib import Path
import re
import tomllib

import yaml


ROOT = Path(__file__).resolve().parents[2]
PARTNER = "coding-product-partner"
RETIRED = {"coding-app-to-features", "coding-feature-spec"}
SECTION_CONCEPTS = {
    "Understand": (
        {"repository", "request"},
        {"problem", "users", "benefit"},
        {"evidence", "assumptions", "constraints", "unknowns"},
        {"user", "journey", "expectations", "friction", "trust"},
        {"technical", "architecture", "implementation", "risks"},
        {"ownership", "data", "integrations", "operations"},
        {"recommend"},
    ),
    "Decide": (
        {"grouped", "question"},
        {"multiple", "rounds", "new", "unknown"},
        {"resynthesize", "changed", "decision-ready"},
        {"alternatives", "consequences", "recommend"},
        {"reversible", "infer"},
        {"behavior", "ownership", "scope", "safety"},
    ),
    "Respond Practically": (
        {"concise", "practical", "synthesis"},
        {"one screen", "one recommended direction"},
        {"highest-value", "short", "questions"},
        {"expand", "asks", "risk"},
        {"understand", "recommend"},
        {"missing", "undecided", "questions"},
        {"omit", "empty", "raw reasoning"},
        {"clear", "assumptions", "proceed"},
    ),
    "Bound Scope": (
        {"current", "prerequisite", "follow-up", "alternative", "unrelated"},
        {"accepted", "scope"},
        {"architecture", "smallest", "boundary", "seam"},
        {"independently", "proof"},
    ),
    "Record": (
        {"docs/app.md", "docs/architecture.md"},
        {"feature.md", "proof.md", "proof/run.sh"},
        {"coding-proof-author", "coding-feature-queue"},
        {"only", "durable"},
    ),
    "Continue": (
        {"planning", "stop"},
        {"coding-repair"},
        {"coding-proof-author", "coding-feature-execute"},
        {"coding-autonomous-execute", "coding-feature-queue"},
        {"authorization", "implementation"},
    ),
}
def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def inventory() -> dict[str, dict[str, str]]:
    return {
        item["name"]: item
        for item in tomllib.loads(read("skills.toml"))["skills"]
    }


def headings(document: str) -> set[str]:
    return {
        line.removeprefix("## ").strip()
        for line in document.splitlines()
        if line.startswith("## ")
    }


def sections(document: str) -> dict[str, str]:
    result: dict[str, str] = {}
    current: str | None = None
    lines: list[str] = []
    for line in document.splitlines():
        if line.startswith("## "):
            if current is not None:
                result[current] = "\n".join(lines).casefold()
            current = line.removeprefix("## ").strip()
            lines = []
        elif current is not None:
            lines.append(line)
    if current is not None:
        result[current] = "\n".join(lines).casefold()
    return result


def policy_gaps(document: str) -> list[str]:
    bodies = sections(document)
    gaps: list[str] = []
    for section_name, concept_groups in SECTION_CONCEPTS.items():
        body = bodies.get(section_name, "")
        for concepts in concept_groups:
            if not all(concept in body for concept in concepts):
                gaps.append(f"{section_name}: {sorted(concepts)}")
    return gaps


def test_active_routing_has_one_product_partner() -> None:
    entries = inventory()
    surfaces = [
        read("AGENTS.md"),
        read("README.md"),
        read("docs/harness/deep-dive.md"),
        read("skills/coding-feature-execute/SKILL.md"),
        read("skills/coding-repair/SKILL.md"),
        read("skills/coding-product-partner/agents/openai.yaml"),
    ]

    assert entries[PARTNER] == {
        "name": PARTNER,
        "kind": "owned",
        "path": PARTNER,
    }
    assert entries.keys().isdisjoint(RETIRED)
    for retired in RETIRED:
        assert not (ROOT / "skills" / retired).exists()
    for surface in surfaces:
        assert PARTNER in surface
        assert all(retired not in surface for retired in RETIRED)


def test_product_partner_structure_and_metadata_are_valid() -> None:
    document = read("skills/coding-product-partner/SKILL.md")
    agent = yaml.safe_load(read("skills/coding-product-partner/agents/openai.yaml"))
    match = re.match(r"^---\n(.*?)\n---", document, re.DOTALL)

    assert match is not None
    metadata = yaml.safe_load(match.group(1))
    assert metadata["name"] == PARTNER
    assert {
        "Understand",
        "Decide",
        "Respond Practically",
        "Bound Scope",
        "Record",
        "Continue",
    } <= headings(document)
    assert policy_gaps(document) == []
    assert not re.search(r"\bReact\b|\bOpenAI\b", document)
    assert f"${PARTNER}" in agent["interface"]["default_prompt"]
    assert agent["policy"]["allow_implicit_invocation"] is True


def test_policy_oracle_rejects_hollow_core_sections() -> None:
    document = read("skills/coding-product-partner/SKILL.md")

    for section_name in SECTION_CONCEPTS:
        pattern = rf"(## {re.escape(section_name)}\n).*?(?=\n## |\Z)"
        hollow = re.sub(pattern, r"\1\nplaceholder\n", document, flags=re.DOTALL)
        assert any(gap.startswith(f"{section_name}:") for gap in policy_gaps(hollow))


def test_partner_preserves_distinct_delivery_transitions() -> None:
    document = read("skills/coding-product-partner/SKILL.md")

    for delivery_skill in (
        "coding-proof-author",
        "coding-feature-execute",
        "coding-repair",
        "coding-autonomous-execute",
        "coding-feature-queue",
    ):
        assert delivery_skill in document


def test_discovery_has_no_fixed_question_round_cap() -> None:
    surfaces = [
        read("skills/coding-product-partner/SKILL.md"),
        read("skills/coding-product-partner/agents/openai.yaml"),
        read("docs/harness/deep-dive.md"),
        read("README.md"),
    ]
    document = "\n".join(surfaces).casefold()

    assert "one focused grouped round" not in document
    assert "one recommended grouped round" not in document
    assert "second round only" not in document
    assert re.search(r"multiple[^\n]+round", document)
    assert "decision-ready" in sections(surfaces[0])["Decide"]
