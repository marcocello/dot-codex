#!/usr/bin/env python3
"""Dedicated acceptance for the installed coding harness alignment."""

from __future__ import annotations

import copy
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
import tempfile
import shutil
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
    "coding-prepare-environment", "coding-architecture-deep-dive",
    "coding-antipattern-review", "coding-commit", "coding-secret-audit",
    "coding-ui-toolkit", "coding-review-workflow",
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
                 ("feature_status.py", "proof_run_capture.py", "skill_inventory.py", "gate.py"))
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
    require(REQUIRED_CAPABILITIES == {name for name in names if name.startswith("coding-")},
            "declared coding capabilities differ from the accepted current inventory")
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


def fixture(folder: Path, body: str, feature_id: str = "example") -> Path:
    feature = folder / "docs/features" / feature_id
    (feature / "proof").mkdir(parents=True)
    initialized = command(["git", "init", "-q", str(folder)])
    require(initialized.returncode == 0, initialized.stderr)
    (feature / "FEATURE.md").write_text("# Fixture\nPreserve one visible marker.\n")
    (feature / "PROOF.md").write_text("# Fixture proof\nRunner observes marker.\n")
    runner = feature / "proof/run.sh"
    runner.write_text("#!/bin/sh\nset -eu\n" + body + "\n")
    runner.chmod(0o755)
    status = folder / "docs/features/status.json"
    payload = json.loads(status.read_text()) if status.exists() else {"version": 2, "features": []}
    payload["features"].append({
        "id": feature_id, "feature_dir": f"docs/features/{feature_id}",
        "priority": len(payload["features"]) + 1,
        "status": "ready", "owner": None, "proof_run": None, "notes": "retain unrelated metadata",
    })
    status.write_text(json.dumps(payload))
    return feature


def transition(folder: Path, owner: str, before: str, after: str, *extra: str,
               feature_id: str = "example") -> subprocess.CompletedProcess:
    return command([str(ROOT / "scripts/feature_status.py"), "--root", str(folder),
                    "--id", feature_id, "--owner", owner, "--from", before, "--to", after, *extra])


def capture(folder: Path) -> tuple[subprocess.CompletedProcess, Path, dict]:
    result = command([str(ROOT / "scripts/proof_run_capture.py"), "--feature-dir", "docs/features/example",
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
        before = status.read_bytes()
        require(transition(folder, "owner-a", "active", "done", "--proof-run", pointer).returncode != 0,
                "new failed attempt allowed completion using old PASS")
        require(status.read_bytes() == before, "rejected old PASS changed state")

        mutation = Path(temporary) / "mutation"
        fixture(mutation, "printf '# altered acceptance\\n' > docs/features/example/PROOF.md")
        result, _, retained = capture(mutation)
        require(result.returncode == 126 and retained["status"] == "FAIL",
                "capture accepted mutation of guarded PROOF.md input")
        require("PROOF.md" in retained.get("input_changes", []), "guarded mutation was not identified")


def ownership_concurrency() -> None:
    with tempfile.TemporaryDirectory(prefix="harness-concurrent-") as temporary:
        folder = Path(temporary)
        ids = ["example", "second", "third", "fourth"]
        for feature_id in ids:
            fixture(folder, "true", feature_id)
        status = folder / "docs/features/status.json"
        barrier = threading.Barrier(len(ids))

        def claim(feature_id: str) -> subprocess.CompletedProcess:
            barrier.wait(timeout=10)
            return transition(folder, f"task-{feature_id}", "ready", "active", feature_id=feature_id)

        with ThreadPoolExecutor(max_workers=len(ids)) as executor:
            results = list(executor.map(claim, ids))
        require(all(result.returncode == 0 for result in results),
                f"independent concurrent claims failed: {[result.stderr for result in results]}")
        entries = {entry["id"]: entry for entry in json.loads(status.read_text())["features"]}
        require(set(entries) == set(ids), "concurrent update lost a feature")
        for feature_id in ids:
            require(entries[feature_id]["status"] == "active"
                    and entries[feature_id]["owner"] == f"task-{feature_id}",
                    f"concurrent update lost ownership: {feature_id}")
            require(entries[feature_id]["notes"] == "retain unrelated metadata",
                    "concurrent update altered metadata")
        before = status.read_bytes()
        require(transition(folder, "task-example", "ready", "active").returncode != 0,
                "stale expected state was accepted")
        require(status.read_bytes() == before, "rejected stale update changed durable state")
        fixture(folder, "true", "duplicate")
        before = status.read_bytes()
        require(transition(folder, "task-example", "ready", "active", feature_id="duplicate").returncode != 0,
                "one task claimed two active features")
        require(status.read_bytes() == before, "rejected duplicate ownership changed durable state")


def unfinished_attempt() -> None:
    with tempfile.TemporaryDirectory(prefix="harness-unfinished-") as temporary:
        folder = Path(temporary)
        fixture(folder, "if test -f hold; then touch runner-started; sleep 30; fi")
        require(transition(folder, "owner-a", "ready", "active").returncode == 0, "claim rejected")
        passed, old_run, retained = capture(folder)
        require(passed.returncode == 0 and retained["status"] == "PASS", "initial proof failed")
        (folder / "hold").touch()
        process = subprocess.Popen([
            str(ROOT / "scripts/proof_run_capture.py"), "--feature-dir", "docs/features/example",
            "--timeout-seconds", "15", "--note", "unfinished official attempt fixture",
        ], cwd=folder, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 10
            while not (folder / "runner-started").exists() and process.poll() is None and time.monotonic() < deadline:
                time.sleep(0.02)
            require((folder / "runner-started").exists(), "new official attempt did not reach its runner")
            newest = sorted((folder / "docs/features/example/proof/runs").iterdir())[-1]
            require(newest != old_run and (newest / "attempt-start.json").is_file()
                    and not (newest / "result.json").exists(), "did not observe genuinely unfinished attempt")
            status = folder / "docs/features/status.json"
            before = status.read_bytes()
            result = transition(folder, "owner-a", "active", "done", "--proof-run", old_run.relative_to(folder).as_posix())
            require(result.returncode != 0, "unfinished newer attempt allowed older PASS completion")
            require(status.read_bytes() == before, "rejected unfinished-attempt completion changed state")
        finally:
            if process.poll() is None:
                process.terminate()
            process.communicate(timeout=10)
        newest = sorted((folder / "docs/features/example/proof/runs").iterdir())[-1]
        retained = json.loads((newest / "result.json").read_text())
        require(retained["status"] != "PASS", "interrupted attempt was mislabeled PASS")


def regression_separation() -> None:
    with tempfile.TemporaryDirectory(prefix="harness-regression-") as temporary:
        folder = Path(temporary)
        fixture(folder, "printf 'official proof observed\\n'")
        require(transition(folder, "owner-a", "ready", "active").returncode == 0, "claim rejected")
        passed, proof_run, retained = capture(folder)
        require(passed.returncode == 0 and retained["status"] == "PASS", "official proof failed")
        regression = command([
            str(ROOT / "scripts/proof_run_capture.py"), "--feature-dir", "docs/features/example",
            "--kind", "regression", "--timeout-seconds", "3", "--note", "separate regression fixture",
            "--", sys.executable, "-c", "print('regression observed')",
        ], cwd=folder)
        require(regression.returncode == 0, regression.stderr)
        regression_run = sorted((folder / "docs/features/example/tests/runs").iterdir())[-1]
        retained = json.loads((regression_run / "result.json").read_text())
        require(retained["status"] == "PASS" and retained["kind"] == "regression",
                "capture did not retain regression identity")
        require("regression observed" in (regression_run / "stdout.txt").read_text(), "regression output missing")
        status = folder / "docs/features/status.json"
        before = status.read_bytes()
        rejected = transition(folder, "owner-a", "active", "done", "--proof-run", regression_run.relative_to(folder).as_posix())
        require(rejected.returncode != 0, "regression path accepted as official proof")
        require(status.read_bytes() == before, "rejected regression completion changed state")
        completed = transition(folder, "owner-a", "active", "done", "--proof-run", proof_run.relative_to(folder).as_posix())
        require(completed.returncode == 0, "new regression incorrectly invalidated official proof: " + completed.stderr)
        require(transition(folder, "owner-a", "done", "active").returncode == 0, "reopen rejected")
        # Copy actual captured output to a proof-shaped path: the validator must inspect its kind,
        # not trust location or PASS alone. This is malformed caller evidence, not a fake capture.
        misplaced = folder / "docs/features/example/proof/runs/zz-regression-evidence"
        shutil.copytree(regression_run, misplaced)
        before = status.read_bytes()
        rejected = transition(folder, "owner-a", "active", "done", "--proof-run", misplaced.relative_to(folder).as_posix())
        require(rejected.returncode != 0 and "not official proof" in rejected.stderr,
                "completion validator accepted regression-labeled evidence at a proof-shaped path")
        require(status.read_bytes() == before, "rejected regression-kind completion changed state")


def validate_assessment(report_path: Path, candidate: dict) -> None:
    report = json.loads(report_path.read_text())
    require(report.get("schema") == 1, "unrecognized assessment schema")
    require(report.get("candidate") == candidate, "assessment is stale or belongs to another candidate")
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


def assessed_behavior() -> None:
    location = os.environ.get("HARNESS_ALIGNMENT_ASSESSMENT")
    require(location, "missing HARNESS_ALIGNMENT_ASSESSMENT: independent behavioral evidence is required")
    report_path = Path(location).resolve()
    validate_assessment(report_path, snapshot())
    print(f"assessed_behavior: retained evidence {report_path}")



def assessment_rejection() -> None:
    # Synthetic records test report validation only. They are never semantic evidence and
    # cannot satisfy assessed_behavior, which requires a separately supplied real assessment.
    with tempfile.TemporaryDirectory(prefix="harness-assessment-validator-") as temporary:
        folder = Path(temporary)
        transcript = folder / "validator-fixture.txt"
        transcript.write_text("Synthetic validator fixture; no agent exercise took place.\n")
        candidate = snapshot()
        report = {
            "schema": 1, "candidate": candidate,
            "exercise_agent": {"id": "fixture-actor", "history_ref": "synthetic-validation-only"},
            "assessor": {"id": "fixture-assessor", "history_ref": "synthetic-validation-only"},
            "transcript": {"path": transcript.name, "sha256": digest(transcript)},
            "cases": [{"id": case["id"], "verdict": "PASS", "evidence": "Synthetic structure fixture",
                       "limitations": "Not behavioral evidence"}
                      for case in json.loads((PROOF / "cases.json").read_text())],
            "limitations": "Synthetic validator exercise only",
        }
        report_path = folder / "report.json"
        report_path.write_text(json.dumps(report))
        validate_assessment(report_path, candidate)
        mutations = {
            "missing case": lambda value: value["cases"].pop(),
            "failed assessment": lambda value: value["cases"][0].update(verdict="FINDINGS"),
            "duplicate case": lambda value: value["cases"].__setitem__(0, value["cases"][1]),
            "same identity": lambda value: value["assessor"].update(id=value["exercise_agent"]["id"]),
            "missing history": lambda value: value["assessor"].pop("history_ref"),
            "altered transcript": lambda value: value["transcript"].update(sha256="0" * 64),
            "missing transcript": lambda value: value["transcript"].update(path="absent.txt"),
            "stale candidate": lambda value: value["candidate"].update(digest="0" * 64),
            "missing reasoning": lambda value: value["cases"][0].update(evidence=""),
            "missing limitations": lambda value: value.pop("limitations"),
        }
        for label, mutate in mutations.items():
            invalid = copy.deepcopy(report)
            mutate(invalid)
            report_path.write_text(json.dumps(invalid))
            try:
                validate_assessment(report_path, candidate)
            except AssertionError:
                continue
            raise AssertionError(f"assessment validator accepted {label}")


def main() -> int:
    if sys.argv[1:] == ["snapshot"]:
        print(json.dumps(snapshot(), indent=2, sort_keys=True))
        return 0
    require(sys.argv[1:] == ["run"], "usage: acceptance.py run|snapshot")
    print(f"coding-harness-alignment target={ROOT} python={sys.version.split()[0]}")
    failures = []
    checks = (discovery, references, supporting_journey, ownership_concurrency,
              unfinished_attempt, regression_separation, assessment_rejection, assessed_behavior)
    for check in checks:
        try:
            check()
        except (AssertionError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
            failures.append(check.__name__)
            print(f"FAIL {check.__name__}: {error}")
        else:
            print(f"PASS {check.__name__}")
    print(f"alignment proof: {len(checks) - len(failures)} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
