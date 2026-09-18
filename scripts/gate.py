#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath


PROFILES = ("python", "react", "wordpress", "harness", "other")
LOCAL_DIRS = {".venv", "node_modules", "vendor", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SKILL_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_REF = re.compile(r"(?<![A-Za-z0-9_-])((?:coding|prospecting)-[a-z0-9-]+)")
SECRET_PATTERNS = tuple(
    re.compile(value)
    for value in (
        r"\bctx7sk-[A-Za-z0-9._-]+\b",
        r"\bsk-[A-Za-z0-9][A-Za-z0-9_-]{20,}\b",
        r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b",
        r"\bAKIA[0-9A-Z]{16}\b",
    )
)
FEATURE_STATUS_FIELDS = {"id", "feature_dir", "priority", "status", "owner", "proof_run", "notes"}
FEATURE_STATUSES = {"draft", "ready", "active", "blocked", "done"}


class Gate:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.require_feature_status = False
        self.failures: list[tuple[str, str, str, str]] = []

    def fail(self, code: str, message: str, fix: str, details: str = "") -> None:
        self.failures.append((code, message, fix, details.strip()))

    def run(self, command: list[str], code: str, label: str, fix: str, env: dict[str, str] | None = None) -> bool:
        result = subprocess.run(command, cwd=self.root, env=env, capture_output=True, text=True, check=False)
        output = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
        if result.returncode:
            self.fail(code, f"{label} failed with exit {result.returncode}", fix, "\n".join(output.splitlines()[-20:]))
            return False
        if output:
            print(output)
        print(f"{label}: PASS")
        return True

    def profile(self, name: str, check) -> None:
        before = len(self.failures)
        check(self)
        if len(self.failures) == before:
            print(f"PROFILE {name}: PASS")


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run read-only repository checks and report actionable failures.",
        epilog="Exit status: 0 when checks pass, 1 for check failures, or 2 for an invalid repository root.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to inspect; defaults to the current directory.",
    )
    parser.add_argument(
        "--profile",
        action="append",
        choices=PROFILES,
        default=[],
        help="Check profile to run; repeat for multiple profiles. Auto-detected when omitted.",
    )
    parser.add_argument('--require-feature-status', action='store_true', help='Require status even before a feature directory exists; always enabled for the harness profile.')
    return parser.parse_args()


def git(gate: Gate, *args: str) -> subprocess.CompletedProcess[str] | None:
    probe = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=gate.root, capture_output=True, text=True, check=False)
    if probe.returncode:
        return None
    return subprocess.run(["git", *args], cwd=gate.root, capture_output=True, text=True, check=False)


def common(gate: Gate) -> None:
    for name in (".gitignore",):
        if not (gate.root / name).is_file():
            gate.fail("common.structure", f"missing {name}", f"Create {name} at the repository root.")
    if not any(path.is_file() for path in gate.root.glob("README*")):
        print("SUGGESTION [common.structure]: No README found. Consider creating README.md at the repository root to describe the project and how to use it.")
    feature_status_lint(gate)
    tracked = git(gate, "ls-files", "-z")
    if tracked is None or tracked.returncode:
        return
    forbidden: list[str] = []
    for value in filter(None, tracked.stdout.split("\0")):
        path = PurePosixPath(value)
        secret = path.name == ".env" or (
            path.name.startswith(".env.") and not path.name.endswith((".example", ".sample", ".template"))
        )
        if secret or any(part in LOCAL_DIRS for part in path.parts):
            forbidden.append(value)
    if forbidden:
        gate.fail(
            "common.tracked",
            f"tracked local or secret-bearing artifacts: {', '.join(sorted(forbidden))}",
            "Untrack these paths and keep them ignored; do not delete required local data.",
        )


def safe_repo_path(value: object) -> PurePosixPath | None:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return None
    if path.as_posix() != value:
        return None
    return path


def read_feature_status(gate: Gate, status_path: Path) -> dict[str, object] | None:
    try:
        payload = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        gate.fail("common.feature-status", f"cannot parse docs/features/status.json: {exc}", "Repair the status JSON.")
        return None
    if not isinstance(payload, dict):
        gate.fail("common.feature-status", "status.json root must be an object", "Use the versioned feature-status schema.")
        return None
    if set(payload) != {"version", "features"}:
        gate.fail("common.feature-status", "status.json must contain only version and features", "Use the versioned feature-status schema.")
    if type(payload.get("version")) is not int or payload.get("version") != 2:
        gate.fail("common.feature-status", "status.json version must be 2", "Use schema version 2; legacy schemas are not accepted.")
    if not isinstance(payload.get("features"), list):
        gate.fail("common.feature-status", "status.json features must be a list", "Use a JSON list for feature entries.")
        return None
    return payload


def feature_status_lint(gate: Gate, payload: dict | None = None, *, check_inventory: bool = True, target_id: str | None = None) -> None:
    features_root = gate.root / "docs/features"
    if not features_root.is_dir() and not gate.require_feature_status:
        return
    status_path = features_root / "status.json"
    if not status_path.is_file():
        gate.fail(
            "common.feature-status",
            "missing docs/features/status.json",
            "Create a version 2 status file with an empty features list before adopting feature packages.",
        )
        return
    if payload is None:
        payload = read_feature_status(gate, status_path)
    if payload is None:
        return

    seen_ids: set[str] = set()
    seen_dirs: set[str] = set()
    seen_priorities: set[int] = set()
    active_owners: set[str] = set()
    for index, entry in enumerate(payload["features"]):
        label = f"status.json feature {index}"
        if not isinstance(entry, dict):
            gate.fail("common.feature-status", f"{label} must be an object", "Use one schema-complete object per feature.")
            continue
        if set(entry) != FEATURE_STATUS_FIELDS:
            gate.fail("common.feature-status", f"{label} has invalid fields", "Use exactly id, feature_dir, priority, status, owner, proof_run, and notes.")
            continue

        feature_id = entry["id"]
        feature_path = safe_repo_path(entry["feature_dir"])
        priority = entry["priority"]
        state = entry["status"]
        notes = entry["notes"]
        proof_path = safe_repo_path(entry["proof_run"]) if entry["proof_run"] is not None else None
        if not isinstance(feature_id, str) or not SKILL_NAME.fullmatch(feature_id):
            gate.fail("common.feature-status", f"{label} has invalid id", "Use a unique lowercase hyphen-case id.")
        elif feature_id in seen_ids:
            gate.fail("common.feature-status", f"duplicate feature id {feature_id}", "Keep one entry per feature id.")
        else:
            seen_ids.add(feature_id)
        if feature_path is None or feature_path.parts[:2] != ("docs", "features") or len(feature_path.parts) != 3:
            gate.fail("common.feature-status", f"{label} has invalid feature_dir", "Use docs/features/<id> as a safe repository-relative path.")
            continue
        feature_dir = feature_path.as_posix()
        if feature_dir in seen_dirs:
            gate.fail("common.feature-status", f"duplicate feature_dir {feature_dir}", "Keep one entry per feature directory.")
        seen_dirs.add(feature_dir)
        if not isinstance(priority, int) or isinstance(priority, bool):
            gate.fail("common.feature-status", f"{label} has invalid priority", "Use a unique integer priority.")
        elif priority in seen_priorities:
            gate.fail("common.feature-status", f"duplicate feature priority {priority}", "Use unique integer priorities.")
        else:
            seen_priorities.add(priority)
        if not isinstance(state, str) or state not in FEATURE_STATUSES:
            gate.fail("common.feature-status", f"{label} has invalid status", "Use draft, ready, active, blocked, or done.")
        owner = entry["owner"]
        if state == "active":
            if not isinstance(owner, str) or not owner.strip():
                gate.fail("common.feature-status", f"{label} active feature requires owner", "Record the owning task id.")
            elif owner in active_owners:
                gate.fail("common.feature-status", f"duplicate active owner {owner}", "One task owns at most one active feature.")
            else:
                active_owners.add(owner)
        elif owner is not None:
            gate.fail("common.feature-status", f"{label} inactive owner must be null", "Release ownership outside active state.")
        # Identity and ownership are shared; another task's local evidence is not.
        if target_id is not None and feature_id != target_id:
            continue
        if not isinstance(notes, str):
            gate.fail("common.feature-status", f"{label} notes must be a string", "Keep concise lifecycle context in notes.")

        directory = gate.root / feature_path
        required = (directory / "FEATURE.md", directory / "PROOF.md", directory / "proof/run.sh")
        for required_path in required:
            if not required_path.is_file():
                gate.fail("common.feature-status", f"{required_path.relative_to(gate.root)} is missing", "Restore the complete feature package.")
        runner = directory / "proof/run.sh"
        if runner.is_file() and not os.access(runner, os.X_OK):
            gate.fail("common.feature-status", f"{runner.relative_to(gate.root)} is not executable", "Make the feature proof runner executable.")

        if state == "done" and entry["proof_run"] is None:
            gate.fail("common.feature-status", f"{label} done requires passing proof_run", "Retain passing evidence or reopen the unsupported completion claim.")
        if state != "done" and entry["proof_run"] is not None:
            gate.fail("common.feature-status", f"{label} non-done proof_run must be null", "Clear the completion pointer when reopening work; retain run files.")
        if entry["proof_run"] is not None and proof_path is None:
            gate.fail("common.feature-status", f"{label} has invalid proof_run", "Use null or a safe repository-relative retained run path.")
        elif proof_path is not None:
            expected_prefix = feature_path / "proof/runs"
            if proof_path.parts[: len(expected_prefix.parts)] != expected_prefix.parts or len(proof_path.parts) != len(expected_prefix.parts) + 1:
                gate.fail("common.feature-status", f"{label} proof_run is outside its feature", "Point to a retained run inside the owning feature's proof/runs directory.")
            elif any((gate.root / Path(*proof_path.parts[:i])).is_symlink() for i in range(1, len(proof_path.parts) + 1)) or (gate.root / proof_path / "result.json").is_symlink():
                gate.fail("common.feature-status", f"{label} proof_run uses a symlink", "Use retained evidence physically inside its owning feature.")
            else:
                attempts_root = directory / "proof/runs"
                resolved_attempts = sorted(
                    attempt
                    for attempt in attempts_root.iterdir()
                    if attempt.is_dir()
                ) if attempts_root.is_dir() else []
                latest_attempt = resolved_attempts[-1] if resolved_attempts else None
                pointed_attempt = gate.root / proof_path
                if latest_attempt is None or pointed_attempt != latest_attempt:
                    gate.fail(
                        "common.feature-status",
                        f"{label} proof_run is not the latest official attempt",
                        "Resolve the newest attempt; an unfinished newer run invalidates an older PASS.",
                    )
                result_path = gate.root / proof_path / "result.json"
                try:
                    result = json.loads(result_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    gate.fail("common.feature-status", f"cannot read {result_path.relative_to(gate.root)}: {exc}", "Keep a valid retained result.json.")
                else:
                    if not isinstance(result, dict) or result.get("status") != "PASS":
                        gate.fail("common.feature-status", f"{result_path.relative_to(gate.root)} is not PASS", "Point proof_run to passing retained evidence.")
                    elif result.get("kind", "proof") != "proof":
                        gate.fail("common.feature-status", f"{result_path.relative_to(gate.root)} is not official proof", "Use a passing proof run; regression evidence cannot establish feature acceptance.")

    if not check_inventory:
        return
    actual_dirs = {
        path.parent.relative_to(gate.root).as_posix()
        for path in features_root.glob("*/FEATURE.md")
    }
    if actual_dirs != seen_dirs:
        missing = sorted(actual_dirs - seen_dirs)
        extra = sorted(seen_dirs - actual_dirs)
        gate.fail(
            "common.feature-status",
            "status.json and feature directories differ",
            "Add one status entry for every durable feature package and remove stale entries.",
            f"unlisted={missing} missing_packages={extra}",
        )


def diff_hygiene(gate: Gate) -> None:
    if git(gate, "status", "--porcelain") is None:
        print("GIT diff: SKIPPED (not a Git repository)")
        return
    before = len(gate.failures)
    for label, args in (("unstaged", ("diff", "--check")), ("staged", ("diff", "--cached", "--check"))):
        result = git(gate, *args)
        if result is not None and result.returncode:
            gate.fail(
                "git.diff",
                f"{label} diff has whitespace errors",
                "Remove the reported whitespace errors and rerun scripts/gate.py.",
                result.stdout + result.stderr,
            )
    if len(gate.failures) == before:
        print("GIT diff: PASS")


def python_manifests(root: Path) -> list[Path]:
    names = (
        "pyproject.toml",
        "requirements.txt",
        "requirements-dev.txt",
        "backend/pyproject.toml",
        "backend/requirements.txt",
        "backend/app/requirements.txt",
    )
    return [root / name for name in names if (root / name).is_file()]


def python_profile(gate: Gate) -> None:
    if not python_manifests(gate.root):
        gate.fail("python.structure", "no Python project manifest found", "Add the repository-owned pyproject.toml or requirements file.")
    roots = [gate.root / name for name in ("src", "app", "backend", "scripts")]
    if not any(path.is_dir() and next(path.rglob("*.py"), None) for path in roots):
        gate.fail("python.structure", "no Python source found", "Add source under src/, app/, backend/, or scripts/.")
    python = gate.root / ".venv/bin/python"
    if not python.is_file() or not os.access(python, os.X_OK):
        gate.fail(
            "python.environment",
            ".venv/bin/python is missing or not executable",
            "Run python3 -m venv .venv, then install the repository-declared dependencies.",
        )
    else:
        gate.run([str(python), "--version"], "python.environment", "PYTHON runtime", "Repair the repo-local .venv.")


def node_manifests(root: Path) -> list[Path]:
    candidates = (root / "package.json", root / "frontend/package.json", root / "frontend/app/package.json")
    return [path for path in candidates if path.is_file()]


def react_profile(gate: Gate) -> None:
    manifests = node_manifests(gate.root)
    if not manifests:
        gate.fail("react.structure", "package.json is missing", "Add the project-owned package.json.")
        return
    root_manifest = gate.root / "package.json"
    if root_manifest in manifests:
        try:
            if json.loads(root_manifest.read_text(encoding="utf-8")).get("workspaces"):
                manifests = [root_manifest]
        except (OSError, json.JSONDecodeError, AttributeError):
            pass
    locks = {"package-lock.json": "npm", "pnpm-lock.yaml": "pnpm", "yarn.lock": "yarn", "bun.lock": "bun", "bun.lockb": "bun"}
    for manifest in manifests:
        present = [name for name in locks if (manifest.parent / name).is_file()]
        if len(present) != 1:
            gate.fail("react.lockfile", f"{manifest.parent} has {len(present)} supported lockfiles", "Keep exactly one package-manager lockfile.")
            continue
        try:
            package = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            gate.fail("react.manifest", f"cannot parse {manifest}: {exc}", "Repair package.json JSON syntax.")
            continue
        declared = str(package.get("packageManager", "")).split("@", 1)[0]
        if declared and declared != locks[present[0]]:
            gate.fail("react.lockfile", f"packageManager {declared} conflicts with {present[0]}", "Use the matching lockfile.")
        if not (manifest.parent / "node_modules").is_dir():
            gate.fail("react.environment", f"node_modules is missing beside {manifest}", f"Run the repository {locks[present[0]]} install command.")
    node = shutil.which("node")
    if node:
        gate.run([node, "--version"], "react.environment", "NODE runtime", "Repair the selected Node runtime.")
    else:
        gate.fail("react.environment", "node is unavailable on PATH", "Enable the repository-required Node runtime.")


def wordpress_profile(gate: Gate) -> None:
    if not (gate.root / "wp-config.php").exists() and not (gate.root / "wp-content").exists():
        gate.fail("wordpress.structure", "no WordPress project markers found", "Use this profile only for WordPress repositories.")
    if (gate.root / "composer.json").is_file():
        if not (gate.root / "composer.lock").is_file():
            gate.fail("wordpress.lockfile", "composer.lock is missing", "Generate and commit the Composer lockfile.")
        if not (gate.root / "vendor").is_dir():
            gate.fail("wordpress.environment", "vendor is missing", "Run the repository Composer install command.")
    php = shutil.which("php")
    if php:
        gate.run([php, "--version"], "wordpress.environment", "PHP runtime", "Repair the selected PHP runtime.")
    else:
        gate.fail("wordpress.environment", "php is unavailable on PATH", "Enable the repository-required PHP runtime.")


def skill_data(gate: Gate, path: Path, yaml):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if match is None:
        gate.fail("harness.skill", f"{path.relative_to(gate.root)} has invalid frontmatter", "Add valid YAML frontmatter.")
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        gate.fail("harness.skill", f"{path.relative_to(gate.root)} YAML is invalid: {exc}", "Repair the skill frontmatter.")
        return None
    if not isinstance(data, dict):
        gate.fail("harness.skill", f"{path.relative_to(gate.root)} frontmatter is not a mapping", "Use a YAML mapping.")
        return None
    return data


def repository_skill_files(gate: Gate) -> list[Path]:
    listed = git(
        gate,
        "ls-files",
        "-z",
        "--cached",
        "--others",
        "--exclude-standard",
        "--",
        "skills",
    )
    if listed is not None and listed.returncode == 0:
        return sorted(
            gate.root / value
            for value in filter(None, listed.stdout.split("\0"))
            if PurePosixPath(value).name == "SKILL.md"
            and (gate.root / value).is_file()
        )
    return sorted((gate.root / "skills").rglob("SKILL.md"))


def harness_lint(gate: Gate) -> None:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        gate.fail("harness.environment", "PyYAML is unavailable", "Install PyYAML for the Python running scripts/gate.py.")
        return
    skills = repository_skill_files(gate)
    names: set[str] = set()
    operational = [gate.root / "AGENTS.md", gate.root / "README.md", gate.root / "config.template.toml"]
    for path in skills:
        data = skill_data(gate, path, yaml)
        if data is None:
            continue
        local = not path.relative_to(gate.root / "skills").parts[0].startswith(".")
        unexpected = set(data) - SKILL_KEYS
        name, description = data.get("name"), data.get("description")
        if unexpected:
            gate.fail("harness.skill", f"{path.relative_to(gate.root)} has unexpected keys: {sorted(unexpected)}", "Keep supported frontmatter fields only.")
        if not isinstance(name, str) or not SKILL_NAME.fullmatch(name) or len(name) > 64 or name != path.parent.name:
            gate.fail("harness.skill", f"{path.relative_to(gate.root)} has invalid name {name!r}", "Use the hyphen-case directory name.")
            continue
        names.add(name)
        if not isinstance(description, str) or not description.strip() or (local and len(description.split()) > 32):
            gate.fail("harness.skill", f"{path.relative_to(gate.root)} has an invalid description", "Use 1-32 descriptive words.")
        agent = path.parent / "agents/openai.yaml"
        if agent.is_file():
            operational.append(agent)
            try:
                prompt = yaml.safe_load(agent.read_text(encoding="utf-8")).get("interface", {}).get("default_prompt", "")
            except (OSError, yaml.YAMLError, AttributeError) as exc:
                gate.fail("harness.agent", f"{agent.relative_to(gate.root)} is invalid: {exc}", "Repair agents/openai.yaml.")
            else:
                if local and f"${name}" not in str(prompt):
                    gate.fail("harness.agent", f"{agent.relative_to(gate.root)} does not reference ${name}", "Reference the owning skill.")
        operational.append(path)
    for path in operational:
        if path.is_file():
            for reference in SKILL_REF.findall(path.read_text(encoding="utf-8")):
                if reference not in names and reference not in {"coding-agent", "coding-agents", "coding-oriented"}:
                    gate.fail("harness.reference", f"{path.relative_to(gate.root)} references unknown skill {reference}", "Repair the stale reference.")
    template = gate.root / "config.template.toml"
    if template.is_file() and any(pattern.search(template.read_text(encoding="utf-8")) for pattern in SECRET_PATTERNS):
        gate.fail("harness.secret", "config.template.toml contains a possible secret", "Use a non-secret placeholder.")


def harness_profile(gate: Gate) -> None:
    for name in ("skills",):
        if not (gate.root / name).is_dir():
            gate.fail("harness.structure", f"missing {name}", f"Restore {name}.")
    if not (gate.root / "AGENTS.md").is_file():
        gate.fail(
            "harness.structure",
            "missing AGENTS.md",
            "Restore the global operating kernel source in the dot-codex harness.",
        )
    if not (gate.root / "config.template.toml").is_file():
        gate.fail("harness.structure", "missing config.template.toml", "Restore the checked template.")
    before = len(gate.failures)
    harness_lint(gate)
    if len(gate.failures) == before:
        print("HARNESS lint: PASS")
    print("HARNESS verification: structural checks only; run feature proof and affected regressions separately.")


def discover(root: Path) -> list[str]:
    profiles: list[str] = []
    profiles += ["python"] if python_manifests(root) else []
    profiles += ["react"] if node_manifests(root) else []
    profiles += ["wordpress"] if (root / "wp-config.php").exists() or (root / "wp-content").exists() else []
    profiles += ["harness"] if all((root / name).exists() for name in ("skills", "config.template.toml")) else []
    return profiles or ["other"]


def main() -> int:
    args = arguments()
    gate = Gate(args.root)
    if not gate.root.is_dir():
        print(f"GATE: FAIL: repository root does not exist: {gate.root}", file=sys.stderr)
        return 2
    profiles = list(dict.fromkeys(args.profile or discover(gate.root)))
    gate.require_feature_status = args.require_feature_status or 'harness' in profiles
    print(f"== gate: repo={gate.root} profiles={','.join(profiles)} ==")
    gate.profile("common", common)
    checks = {"python": python_profile, "react": react_profile, "wordpress": wordpress_profile, "harness": harness_profile, "other": lambda gate: None}
    for profile in profiles:
        gate.profile(profile, checks[profile])
    diff_hygiene(gate)
    if not gate.failures:
        print("GATE: PASS")
        return 0
    for code, message, fix, details in gate.failures:
        print(f"FAIL [{code}]: {message}", file=sys.stderr)
        if details:
            print(details, file=sys.stderr)
        print(f"Fix: {fix}", file=sys.stderr)
    print(f"GATE: FAIL ({len(gate.failures)} issue(s))", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
