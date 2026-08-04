from pathlib import Path
import re

import pytest


ROOT = Path(__file__).resolve().parents[2]
TEST_SELECTOR = re.compile(r"tests/[^\s\\]+\.py(?:::[^\s\\]+)?")


def assert_isolated_selection(selector: str, owned_module: str) -> None:
    module, separator, test_name = selector.partition("::")
    if module != owned_module:
        assert separator == "::" and test_name


def test_proof_author_forbids_complete_cross_feature_proof_reuse() -> None:
    proof_author = (ROOT / "skills/coding-proof-author/SKILL.md").read_text(
        encoding="utf-8"
    ).lower()

    assert "must not import or execute another feature's complete proof" in proof_author
    assert "prerequisite behavior as setup" in proof_author
    assert "smallest necessary integration canary" in proof_author


def test_current_feature_runners_do_not_invoke_complete_feature_proofs() -> None:
    for runner in (ROOT / "docs/features").glob("*/proof/run.sh"):
        assert "proof/run.sh" not in runner.read_text(encoding="utf-8").lower(), runner


def test_selection_oracle_rejects_complete_external_module() -> None:
    with pytest.raises(AssertionError):
        assert_isolated_selection(
            "tests/unit/test_gate_policy.py",
            "tests/unit/test_feature_proof_isolation.py",
        )


def test_selection_oracle_accepts_owned_module_and_explicit_external_canary() -> None:
    assert_isolated_selection(
        "tests/unit/test_feature_proof_isolation.py",
        "tests/unit/test_feature_proof_isolation.py",
    )
    assert_isolated_selection(
        "tests/unit/test_gate_policy.py::test_harness_gate_ignores_external_skills_and_runs_tests_after_lint_failure",
        "tests/unit/test_feature_proof_isolation.py",
    )


def test_current_shared_gate_consumers_select_explicit_canaries() -> None:
    for feature_id in ("lean-completion-lifecycle", "frontend-sites-routing"):
        runner = ROOT / "docs/features" / feature_id / "proof/run.sh"
        selectors = TEST_SELECTOR.findall(runner.read_text(encoding="utf-8"))
        gate_selectors = [item for item in selectors if "test_gate_policy.py" in item]

        assert gate_selectors, runner
        assert all("::" in item for item in gate_selectors), (runner, gate_selectors)
