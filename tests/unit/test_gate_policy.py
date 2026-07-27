from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "scripts/gate"


def run_gate(root: Path, profile: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE), "--root", str(root), "--profile", profile],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def write_common_repository_files(root: Path) -> None:
    (root / ".gitignore").write_text("*.tmp\n", encoding="utf-8")
    (root / "README.md").write_text("# Fixture\n", encoding="utf-8")


def test_common_gate_accepts_repository_without_agents_md(tmp_path: Path) -> None:
    write_common_repository_files(tmp_path)

    result = run_gate(tmp_path, "other")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "PROFILE common: PASS" in result.stdout
    assert "AGENTS.md" not in result.stdout + result.stderr


def test_harness_profile_owns_global_agents_requirement(tmp_path: Path) -> None:
    write_common_repository_files(tmp_path)
    (tmp_path / "skills").mkdir()
    (tmp_path / "tests" / "unit").mkdir(parents=True)
    (tmp_path / "config.template.toml").write_text("", encoding="utf-8")

    result = run_gate(tmp_path, "harness")
    output = result.stdout + result.stderr

    assert result.returncode == 1
    assert "FAIL [harness.structure]: missing AGENTS.md" in output
    assert "FAIL [common.structure]: missing AGENTS.md" not in output


def test_sites_stays_enabled_with_explicit_routing_boundary() -> None:
    config = tomllib.loads((ROOT / "config.toml").read_text(encoding="utf-8"))
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    frontend = (ROOT / "skills" / "coding-frontend" / "SKILL.md").read_text(encoding="utf-8")

    assert config["plugins"]["sites@openai-bundled"]["enabled"] is True
    assert "Stack/domain skills own application source structure" in agents
    assert "Sites is opt-in for application construction" in agents
    assert "existed before the task began" in agents
    assert "created during the current task cannot retroactively authorize" in agents
    assert "Do not create `AGENTS.md` or `AGENTS.override.md` in target repositories" in agents
    assert "must not be treated as a gate failure" in agents
    assert "Sites remains available but does not own generic frontend construction" in frontend
    assert "existed before the task began" in frontend


def test_codex_home_has_no_nested_codex_symlink() -> None:
    nested = ROOT / ".codex"

    assert not nested.is_symlink()
    assert not nested.exists()
