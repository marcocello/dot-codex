from __future__ import annotations

from pathlib import Path
import re
import tomllib

import yaml


ROOT = Path(__file__).resolve().parents[2]
REVIEW = "coding-feature-review"
RETIRED = {"coding-feature-preflight", "coding-feature-evaluator"}
REQUIRED_DELIVERY = {
    "coding-proof-author",
    "coding-feature-execute",
    REVIEW,
    "coding-repair",
    "coding-autonomous-execute",
    "coding-feature-queue",
}
ACTIVE_LIFECYCLE_SURFACES = (
    "AGENTS.md",
    "README.md",
    "docs/harness/deep-dive.md",
    "docs/harness/autonomous-execution.md",
    "docs/harness/handoff.md",
    "skills/coding-product-partner/SKILL.md",
    "skills/coding-proof-author/SKILL.md",
    "skills/coding-feature-execute/SKILL.md",
    "skills/coding-feature-review/SKILL.md",
    "skills/coding-repair/SKILL.md",
    "skills/coding-feature-queue/SKILL.md",
    "skills/coding-autonomous-execute/SKILL.md",
    "skills/coding-app-improvement-review/SKILL.md",
    "skills/create-cli-toolkit-kit/SKILL.md",
    "skills/create-cli-toolkit-kit/references/proof-checklist.md",
)
OBSOLETE_LIFECYCLE_PATTERNS = (
    r"\blightweight work\b",
    r"\btracked feature(?:s| work)?\b",
    r"tracked/autonomous",
    r"\bwhen tracked\b",
    r"fresh evaluator",
    r"evaluator verdict",
    r"coding-feature-preflight",
    r"coding-feature-evaluator",
)
SECTION_CONCEPTS = {
    "Assurance": (
        {"focused", "standard", "sensitive"},
        {"data", "migration", "authorization", "security"},
        {"destructive", "paid", "external"},
        {"ownership", "proof"},
        {"floor", "escalate", "downgrade"},
        {"resume", "repair", "inherit"},
    ),
    "Preflight Mode": (
        {"mode", "fresh", "separate"},
        {"before", "red", "implementation"},
        {"intent", "authority", "consumers", "false-green"},
        {"clear", "findings", "need_input"},
        {"candidate", "execute proof", "completion authority"},
    ),
    "Final Mode": (
        {"mode", "fresh", "separate"},
        {"proof", "passes", "evidence", "implementation"},
        {"result.json", "runtime"},
        {"active-feature surface", "activation", "authority", "consumers"},
        {"target", "pass"},
        {"pass", "findings", "need_input"},
    ),
    "Shared Boundaries": (
        {"read-only", "relevance-bounded"},
        {"scope", "speculative"},
        {"fresh", "edit"},
    ),
}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


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


def concept_gaps(document: str, names: set[str]) -> list[str]:
    bodies = sections(document)
    gaps: list[str] = []
    for section_name in names:
        for concepts in SECTION_CONCEPTS[section_name]:
            if not all(concept in bodies.get(section_name, "") for concept in concepts):
                gaps.append(f"{section_name}: {sorted(concepts)}")
    return gaps


def test_inventory_and_metadata_expose_split_delivery() -> None:
    entries = {
        item["name"]: item
        for item in tomllib.loads(read("skills.toml"))["skills"]
    }
    agent = yaml.safe_load(read("skills/coding-feature-review/agents/openai.yaml"))

    assert REQUIRED_DELIVERY <= entries.keys()
    assert entries.keys().isdisjoint(RETIRED)
    assert entries[REVIEW] == {"name": REVIEW, "kind": "owned", "path": REVIEW}
    assert f"${REVIEW}" in agent["interface"]["default_prompt"]
    assert agent["policy"]["allow_implicit_invocation"] is False
    for name in RETIRED:
        assert not (ROOT / "skills" / name).exists()


def test_assurance_and_review_modes_have_complete_policy() -> None:
    execute = read("skills/coding-feature-execute/SKILL.md")
    review = read("skills/coding-feature-review/SKILL.md")

    assert concept_gaps(execute, {"Assurance"}) == []
    assert concept_gaps(
        review, {"Preflight Mode", "Final Mode", "Shared Boundaries"}
    ) == []


def test_policy_oracle_rejects_hollow_assurance_and_review_sections() -> None:
    documents = {
        "Assurance": read("skills/coding-feature-execute/SKILL.md"),
        "Preflight Mode": read("skills/coding-feature-review/SKILL.md"),
        "Final Mode": read("skills/coding-feature-review/SKILL.md"),
        "Shared Boundaries": read("skills/coding-feature-review/SKILL.md"),
    }

    for section_name, document in documents.items():
        pattern = rf"(## {re.escape(section_name)}\n).*?(?=\n## |\Z)"
        hollow = re.sub(pattern, r"\1\nplaceholder\n", document, flags=re.DOTALL)
        assert concept_gaps(hollow, {section_name})


def test_active_consumers_use_one_reviewer_and_preserve_completion_truth() -> None:
    surfaces = [
        read("AGENTS.md"),
        read("docs/harness/deep-dive.md"),
        read("skills/coding-feature-execute/SKILL.md"),
        read("skills/coding-autonomous-execute/SKILL.md"),
        read("skills/coding-feature-queue/SKILL.md"),
    ]

    for surface in surfaces:
        assert REVIEW in surface
        assert all(retired not in surface for retired in RETIRED)
    combined = "\n".join(surfaces).casefold()
    for concept in (
        "final candidate",
        "relevant edit",
        "strengthen proof",
        "rerun",
        "named consumption target",
        "source proof",
        "intermediate",
    ):
        assert concept in combined
    autonomous = surfaces[3].casefold()
    assert "continuation mode" in autonomous
    assert "assurance tier" in autonomous


def test_active_lifecycle_surface_rejects_obsolete_contracts() -> None:
    for path in ACTIVE_LIFECYCLE_SURFACES:
        surface = read(path).casefold()
        for pattern in OBSOLETE_LIFECYCLE_PATTERNS:
            assert re.search(pattern, surface) is None, f"{path}: {pattern}"


def test_public_flows_make_preflight_conditional_and_final_review_explicit() -> None:
    for path in ("README.md", "docs/harness/deep-dive.md"):
        surface = read(path).casefold()
        assert re.search(r"sensitive work[^\n]*preflight", surface), path
        assert "fresh final review" in surface, path


def test_review_modes_are_dispatched_at_distinct_lifecycle_boundaries() -> None:
    execute = read("skills/coding-feature-execute/SKILL.md").casefold()
    review = read("skills/coding-feature-review/SKILL.md").casefold()

    assert execute.index("mode: preflight") < execute.index("establish red evidence")
    assert execute.index("capture proof") < execute.index("mode: final")
    assert "clear|findings|need_input" in review
    assert "pass|findings|need_input" in review
    assert review.index("evidence-first") < review.index("implementation-second")


def test_migrated_completion_guarantees_cover_all_owners() -> None:
    owners = {
        "proof": read("skills/coding-proof-author/SKILL.md").casefold(),
        "execute": read("skills/coding-feature-execute/SKILL.md").casefold(),
        "review": read("skills/coding-feature-review/SKILL.md").casefold(),
        "repair": read("skills/coding-repair/SKILL.md").casefold(),
        "queue": read("skills/coding-feature-queue/SKILL.md").casefold(),
        "autonomous": read("skills/coding-autonomous-execute/SKILL.md").casefold(),
        "autonomous_doc": read("docs/harness/autonomous-execution.md").casefold(),
        "handoff": read("docs/harness/handoff.md").casefold(),
    }

    assert "public or production boundary" in owners["proof"]
    assert "proof_run_capture" in owners["execute"]
    assert "evidence-first" in owners["review"]
    assert "inherit" in owners["repair"] and "assurance" in owners["repair"]
    assert "fresh" in owners["queue"] and "review" in owners["queue"]
    assert "continuation mode" in owners["autonomous"]
    assert "named consumption target" in owners["autonomous_doc"]
    assert "source proven; activation required" in owners["handoff"]


def test_contract_authoring_synchronizes_an_existing_feature_queue() -> None:
    partner = read("skills/coding-product-partner/SKILL.md").casefold()
    proof = read("skills/coding-proof-author/SKILL.md").casefold()
    queue = read("skills/coding-feature-queue/SKILL.md").casefold()

    for owner in (partner, proof, queue):
        assert "status.json" in owner
        assert "same task" in owner

    assert "ensure its queue entry exists" in partner
    assert "materially amend" in partner
    assert "`draft` before" in partner
    assert "ensure the queue entry exists" in proof
    assert "mark it `ready`" in proof
    assert "new highest numeric priority plus one" in queue
    assert "must synchronize" in queue
    assert "return it to `draft` before" in queue


def test_delivery_prompts_do_not_route_to_retired_reviewers() -> None:
    prompts = [
        read("skills/coding-feature-execute/agents/openai.yaml"),
        read("skills/coding-feature-review/agents/openai.yaml"),
        read("skills/coding-repair/agents/openai.yaml"),
        read("skills/coding-feature-queue/agents/openai.yaml"),
        read("skills/coding-autonomous-execute/agents/openai.yaml"),
    ]

    for prompt in prompts:
        assert all(retired not in prompt for retired in RETIRED)
