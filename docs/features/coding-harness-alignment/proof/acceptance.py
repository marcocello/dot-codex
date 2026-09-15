#!/usr/bin/env python3
"""Dedicated acceptance for the installed coding harness alignment."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
from urllib.parse import unquote, urlsplit


PROOF = Path(__file__).resolve().parent
ROOT = PROOF.parents[3]
RETIRED = {
    "acceptance-author", "auto-improve", "coding-autonomous-execute",
    "coding-feature-execute", "coding-feature-queue", "coding-feature-review",
    "coding-operational-issue-diagnostics", "coding-product-partner",
    "coding-proof-author", "coding-repair", "feature-execute", "fix-issue",
    "frontend", "python-backend", "prepare-environment", "research",
    "laravel-feature-builder", "php-legacy-maintainer", "architecture-deep-dive",
    "commit_message", "maintainability-review", "compare-architectures",
}
REQUIRED_CAPABILITIES = {
    "coding-workflow", "coding-frontend", "coding-python-backend",
    "coding-laravel-feature-builder", "coding-php-legacy-maintainer",
    "coding-wordpress", "coding-architecture-deep-dive", "coding-antipattern-review",
    "coding-app-improvement-review", "coding-ui-improvement", "coding-commit",
    "coding-prepare-environment", "coding-research", "coding-secret-audit",
}


def require(condition: object, reason: str) -> None:
    if not condition:
        raise AssertionError(reason)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def active_documents() -> list[Path]:
    paths = [ROOT / "AGENTS.md", ROOT / "README.md"]
    paths.extend((ROOT / "docs/harness").glob("*.md"))
    for folder in (ROOT / "skills").glob("coding-*"):
        paths.extend(p for p in folder.rglob("*") if p.is_file()
                     and p.suffix in {".md", ".yaml", ".yml"})
    return sorted(set(paths))


def snapshot() -> dict:
    paths = active_documents() + [ROOT / "skills.toml", ROOT / "config.template.toml", ROOT / ".gitignore"]
    if (ROOT / "config.toml").exists():
        paths.append(ROOT / "config.toml")
    paths.extend(ROOT / "scripts" / name for name in
                 ("feature_status", "proof_run_capture", "skill_inventory.py"))
    paths.extend(p for p in PROOF.iterdir() if p.is_file())
    paths.extend((PROOF.parent / "FEATURE.md", PROOF.parent / "PROOF.md"))
    files = {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(set(paths))}
    value = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    return {"files": files, "digest": value}


def command(args: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=20)


def discovery() -> None:
    entries = tomllib.loads((ROOT / "skills.toml").read_text())["skills"]
    names = [entry["name"] for entry in entries]
    require(len(names) == len(set(names)), "duplicate inventory names")
    require(REQUIRED_CAPABILITIES <= set(names), "useful coding capability removed")
    require(not RETIRED.intersection(names), "retired skill remains registered")
    listed = command([sys.executable, str(ROOT / "scripts/skill_inventory.py"),
                      "--manifest", str(ROOT / "skills.toml"), "list"])
    require(listed.returncode == 0, listed.stderr)
    require({line.split("\t")[0] for line in listed.stdout.splitlines()} == set(names),
            "actual inventory CLI does not expose the declared inventory")
    coding = [entry for entry in entries if entry["name"].startswith("coding-")]
    with tempfile.TemporaryDirectory(prefix="harness-discovery-") as temporary:
        manifest = Path(temporary) / "skills.toml"
        lines = ["schema = 1"]
        for entry in coding:
            require(entry["kind"] == "owned", "coding lifecycle/domain guidance must be authored here")
            lines.append("\n[[skills]]")
            lines.extend(f"{key} = {json.dumps(entry[key])}" for key in ("name", "kind", "path"))
            skill = ROOT / "skills" / entry["path"] / "SKILL.md"
            require(skill.is_file(), f"missing installed skill: {entry['name']}")
            frontmatter = skill.read_text().split("---", 2)
            require(len(frontmatter) == 3 and not frontmatter[0].strip(), f"invalid frontmatter: {skill}")
            identity = re.search(r"^name:\s*[\"']?([^\"'\n]+?)[\"']?\s*$", frontmatter[1], re.M)
            require(identity and identity.group(1) == entry["name"], f"wrong skill identity: {skill}")
        manifest.write_text("\n".join(lines) + "\n")
        checked = command([sys.executable, str(ROOT / "scripts/skill_inventory.py"),
                           "--manifest", str(manifest), "--skills-root", str(ROOT / "skills"), "doctor"])
        require(checked.returncode == 0, checked.stderr)
    for name in RETIRED:
        path = ROOT / "skills" / name
        require(not path.exists() and not path.is_symlink(), f"retired skill entrypoint exists: {name}")
    for path in [PROOF.parent / "FEATURE.md", PROOF.parent / "PROOF.md"] + [
        item for item in PROOF.iterdir() if item.is_file()
    ]:
        ignored = command(["git", "check-ignore", "--", str(path)])
        require(ignored.returncode == 1, f"fixed proof input is not deliverable: {path.relative_to(ROOT)}")
    for path in (ROOT / "config.template.toml", ROOT / "config.toml"):
        if path.name == "config.toml" and not path.exists():
            continue
        config = tomllib.loads(path.read_text())
        require(config.get("features", {}).get("multi_agent") is True,
                f"separate-agent capability is disabled in {path.name}")


def references() -> None:
    for relative in ("docs/harness/core.md", "docs/harness/proof.md"):
        require(not (ROOT / relative).exists(), f"duplicate lifecycle guidance remains: {relative}")
    for path in active_documents():
        content = path.read_text()
        for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", content):
            parsed = urlsplit(target.strip("<>"))
            if parsed.scheme or not parsed.path:
                continue
            linked = (path.parent / unquote(parsed.path)).resolve()
            require(linked.is_relative_to(ROOT), f"active reference escapes checkout: {path}: {target}")
            require(linked.exists(), f"broken active reference: {path.relative_to(ROOT)} -> {target}")
        for name in RETIRED:
            # Check explicit skill invocations and filesystem references, not ordinary words.
            retired_call = re.search(r"(?:\$|skills/)" + re.escape(name) + r"(?![a-zA-Z0-9_-])", content)
            require(not retired_call, f"retired invocation in {path.relative_to(ROOT)}: {name}")
        for relative in ("docs/harness/core.md", "docs/harness/proof.md"):
            require(relative not in content, f"retired document reference in {path.relative_to(ROOT)}")


def fixture(folder: Path, body: str) -> Path:
    feature = folder / "docs/features/example"
    (feature / "proof").mkdir(parents=True)
    command(["git", "init", "-q", str(folder)])
    (feature / "FEATURE.md").write_text("# Fixture\nPreserve one visible marker.\n")
    (feature / "PROOF.md").write_text("# Fixture proof\nRunner observes marker.\n")
    runner = feature / "proof/run.sh"
    runner.write_text("#!/bin/sh\nset -eu\n" + body + "\n")
    runner.chmod(0o755)
    (folder / "docs/features/status.json").write_text(json.dumps({"version": 2, "features": [{
        "id": "example", "feature_dir": "docs/features/example", "priority": 1,
        "status": "ready", "owner": None, "proof_run": None, "notes": "retain unrelated metadata",
    }]}))
    return feature


def transition(folder: Path, owner: str, before: str, after: str, *extra: str) -> subprocess.CompletedProcess:
    return command([str(ROOT / "scripts/feature_status"), "--root", str(folder),
                    "--id", "example", "--owner", owner, "--from", before, "--to", after, *extra])


def capture(folder: Path) -> tuple[subprocess.CompletedProcess, Path, dict]:
    result = command([str(ROOT / "scripts/proof_run_capture"), "--feature-dir", "docs/features/example",
                      "--timeout-seconds", "3", "--note", "alignment acceptance fixture"], cwd=folder)
    runs = sorted((folder / "docs/features/example/proof/runs").iterdir())
    require(bool(runs), "capture produced no retained attempt")
    run = runs[-1]
    return result, run, json.loads((run / "result.json").read_text())


def supporting_journey() -> None:
    with tempfile.TemporaryDirectory(prefix="harness-commands-") as temporary:
        folder = Path(temporary) / "owned"
        feature = fixture(folder, "test -f visible-marker\nprintf 'marker observed\\n'")
        (folder / "visible-marker").write_text("visible")
        status = folder / "docs/features/status.json"
        require(transition(folder, "owner-a", "ready", "active").returncode == 0, "claim rejected")
        before = status.read_bytes()
        require(transition(folder, "owner-b", "active", "ready").returncode != 0, "ownership takeover accepted")
        require(status.read_bytes() == before, "rejected takeover changed state")
        require(transition(folder, "owner-a", "active", "done").returncode != 0, "completion without evidence accepted")
        require(status.read_bytes() == before, "rejected completion changed state")
        result, run, retained = capture(folder)
        require(result.returncode == 0 and retained["status"] == "PASS", "real passing runner not retained")
        require("marker observed" in (run / "stdout.txt").read_text(), "consumer output not retained")
        pointer = run.relative_to(folder).as_posix()
        completed = transition(folder, "owner-a", "active", "done", "--proof-run", pointer)
        require(completed.returncode == 0, completed.stderr)
        entry = json.loads(status.read_text())["features"][0]
        require(entry["status"] == "done" and entry["proof_run"] == pointer and entry["owner"] is None,
                "completion result differs from accepted transition")
        require(entry["notes"] == "retain unrelated metadata", "status update destroyed unrelated metadata")
        require(transition(folder, "owner-a", "done", "active").returncode == 0, "reopen rejected")
        (folder / "visible-marker").unlink()
        result, failed_run, retained = capture(folder)
        require(result.returncode != 0 and retained["status"] == "FAIL" and failed_run != run,
                "real failing attempt not independently retained")
        require(transition(folder, "owner-a", "active", "done", "--proof-run", pointer).returncode != 0,
                "new failed attempt allowed completion using old PASS")

        mutation = Path(temporary) / "mutation"
        fixture(mutation, "printf '# altered acceptance\\n' > docs/features/example/PROOF.md")
        result, _, retained = capture(mutation)
        require(result.returncode == 126 and retained["status"] == "FAIL",
                "capture accepted mutation of guarded PROOF.md input")
        require("PROOF.md" in retained.get("input_changes", []), "guarded mutation was not identified")


def assessed_behavior() -> None:
    location = os.environ.get("HARNESS_ALIGNMENT_ASSESSMENT")
    require(location, "missing HARNESS_ALIGNMENT_ASSESSMENT: independent behavioral evidence is required")
    report_path = Path(location).resolve()
    report = json.loads(report_path.read_text())
    require(report.get("schema") == 1, "unrecognized assessment schema")
    require(report.get("candidate") == snapshot(), "assessment is stale or belongs to another candidate")
    actor = report.get("exercise_agent", {})
    assessor = report.get("assessor", {})
    require(all(isinstance(role.get(key), str) and role[key].strip()
                for role in (actor, assessor) for key in ("id", "history_ref")), "missing actual role/history identifiers")
    require(actor["id"] != assessor["id"], "exercise agent cannot assess its own responses")
    transcript_info = report.get("transcript", {})
    transcript = (report_path.parent / transcript_info.get("path", "")).resolve()
    require(transcript.is_file(), "missing retained exercise transcript")
    require(digest(transcript) == transcript_info.get("sha256"), "retained transcript changed")
    require(transcript.stat().st_size > 0, "empty exercise transcript")
    expected = {case["id"] for case in json.loads((PROOF / "cases.json").read_text())}
    cases = report.get("cases", [])
    require(len(cases) == len(expected) and {case.get("id") for case in cases} == expected,
            "assessment omitted or duplicated an accepted case")
    for case in cases:
        require(case.get("verdict") == "PASS", f"behavioral finding remains: {case.get('id')}")
        require(isinstance(case.get("evidence"), str) and case["evidence"].strip(), "case lacks reasoned assessment")
        require(isinstance(case.get("limitations"), str) and case["limitations"].strip(), "case omits limitations")
    require(isinstance(report.get("limitations"), str) and report["limitations"].strip(), "assessment omits overall limits")
    print(f"assessed_behavior: retained evidence {report_path}")


def main() -> int:
    if sys.argv[1:] == ["snapshot"]:
        print(json.dumps(snapshot(), indent=2, sort_keys=True))
        return 0
    require(sys.argv[1:] == ["run"], "usage: acceptance.py run|snapshot")
    print(f"coding-harness-alignment target={ROOT} python={sys.version.split()[0]}")
    failures = []
    for check in (discovery, references, supporting_journey, assessed_behavior):
        try:
            check()
        except (AssertionError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
            failures.append(check.__name__)
            print(f"FAIL {check.__name__}: {error}")
        else:
            print(f"PASS {check.__name__}")
    print(f"alignment proof: {4 - len(failures)} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
