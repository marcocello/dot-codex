#!/usr/bin/env python3
"""Fingerprint local candidates and record review attribution, not authentication."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys


CACHE_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
DEPENDENCY_DIRS = {".venv", "node_modules", "vendor"}


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path.name}")
    return value


def repo_path(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("expected a safe repository-relative path")
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts or relative.as_posix() != value:
        raise ValueError("expected a safe repository-relative path")
    path = root / relative
    if any((root / Path(*relative.parts[:i])).is_symlink() for i in range(1, len(relative.parts) + 1)):
        raise ValueError(f"path must not use symlinks: {value}")
    return path


def excluded(relative: Path, feature_dir: str | None = None) -> bool:
    parts = relative.parts
    if any(part in CACHE_DIRS for part in parts) or relative.name == ".DS_Store" or relative.suffix in {".pyc", ".pyo"}:
        return True
    if feature_dir is not None:
        prefix = PurePosixPath(feature_dir).parts
        if parts[:len(prefix)] == prefix and parts[len(prefix):len(prefix) + 2] in {("proof", "runs"), ("tests", "runs")}:
            return True
    if parts[:2] == ("docs", "features"):
        if len(parts) == 3 and (parts[-1] == "status.json" or parts[-1].startswith(".status-")):
            return True
        if len(parts) >= 5 and parts[3:5] in {("proof", "runs"), ("tests", "runs")}:
            return True
    return False


def tree_files(root: Path, directory: Path, *, feature_dir: str | None = None, skip_dependencies: bool = False):
    """Walk without following links or reading generated evidence and cache trees."""
    for current, directories, files in os.walk(directory, followlinks=False):
        current = Path(current)
        for name in list(directories):
            path = current / name
            if excluded(path.relative_to(root), feature_dir) or (skip_dependencies and name in DEPENDENCY_DIRS):
                directories.remove(name)
            elif path.is_symlink():
                directories.remove(name)
                yield path
        for name in files:
            path = current / name
            if not excluded(path.relative_to(root), feature_dir):
                yield path


def fingerprint(path: Path) -> dict:
    mode = path.lstat().st_mode
    if stat.S_ISLNK(mode):
        checksum = hashlib.sha256(os.fsencode(os.readlink(path))).hexdigest()
    elif stat.S_ISREG(mode):
        hasher = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                hasher.update(chunk)
        checksum = hasher.hexdigest()
    else:
        raise ValueError(f"unsupported candidate file type: {path.name}")
    return {"sha256": checksum, "mode": stat.S_IFMT(mode) | stat.S_IMODE(mode)}


def candidate(root: Path, feature_dir: str, include: list[str]) -> dict:
    feature = repo_path(root, feature_dir)
    included = sorted(set(include))
    visible = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                             cwd=root, capture_output=True, check=False)
    selection = "git-visible+acceptance" if visible.returncode == 0 else "directory+acceptance"
    paths = {root / os.fsdecode(name) for name in visible.stdout.split(b"\0") if name} if visible.returncode == 0 else set(tree_files(root, root, feature_dir=feature_dir, skip_dependencies=True))
    paths.update((feature / "FEATURE.md", feature / "PROOF.md"))
    paths.update(tree_files(root, feature / "proof", feature_dir=feature_dir, skip_dependencies=visible.returncode != 0))
    for value in included:
        path = repo_path(root, value)
        if excluded(path.relative_to(root), feature_dir):
            raise ValueError(f"cannot include generated evidence or cache: {value}")
        if not path.exists():
            raise ValueError(f"included path is missing: {value}")
        paths.update(tree_files(root, path, feature_dir=feature_dir)) if path.is_dir() else paths.add(path)
    files = {}
    for path in sorted(paths):
        relative = path.relative_to(root)
        if excluded(relative, feature_dir):
            continue
        if any(parent.is_symlink() for parent in path.parents if parent != root and root in parent.parents):
            raise ValueError(f"candidate file traverses a symlink: {relative.as_posix()}")
        if not path.exists() and not path.is_symlink():
            continue  # Deletions change the manifest relative to an earlier capture.
        if path.is_dir() and not path.is_symlink():
            # Gitlinks need separate observation; don't imply subtree coverage.
            raise ValueError(f"candidate includes a nested repository: {relative.as_posix()}; capture its evidence separately")
        files[relative.as_posix()] = fingerprint(path)
    return {"version": 1, "selection": selection, "feature_dir": feature_dir, "include": included, "files": files}


def evidence_digest(run: Path) -> str:
    """Bind retained bytes, including outputs and snapshots, except the receipt itself."""
    files = {}
    for path in sorted(run.rglob("*")):
        if path.is_symlink():
            raise ValueError("retained evidence must not use symlinks")
        if path.is_file() and path != run / "review.json":
            files[path.relative_to(run).as_posix()] = fingerprint(path)
    return digest(files)


def reject_later_regression_failure(run: Path, result: dict) -> None:
    """Do not cherry-pick an older PASS after the same check reveals a failure."""
    identity = tuple(result.get(key) for key in ("command", "cwd", "target"))
    for later in sorted((path for path in run.parent.iterdir() if path.is_dir() and path.name > run.name), reverse=True):
        metadata = read_json(later / "attempt-start.json")
        if tuple(metadata.get(key) for key in ("command", "cwd", "target")) != identity:
            continue
        try:
            latest = read_json(later / "result.json")
        except (OSError, ValueError) as exc:
            raise ValueError("a newer matching regression is unfinished") from exc
        if latest.get("status") != "PASS" or latest.get("returncode") != 0:
            raise ValueError("a newer matching regression did not pass")
        return


def evidence(root: Path, relative: str, kind: str, *, passing: bool = True) -> tuple[dict, str, dict]:
    run = repo_path(root, relative)
    parts = PurePosixPath(relative).parts
    area = "proof" if kind == "proof" else "tests"
    if len(parts) != 6 or parts[:2] != ("docs", "features") or parts[3:5] != (area, "runs"):
        raise ValueError(f"expected owning {kind} run directory")
    result = read_json(run / "result.json")
    start = read_json(run / "attempt-start.json")
    manifest = read_json(run / "candidate.json")
    if result.get("kind") != kind or start.get("kind") != kind:
        raise ValueError("evidence kind does not match its use")
    feature_dir = "/".join(parts[:3])
    if manifest.get("version") != 1 or manifest.get("feature_dir") != feature_dir:
        raise ValueError("invalid candidate version or owner")
    target = result.get("target")
    if not isinstance(target, str) or not target.strip():
        raise ValueError("missing tested target")
    for record in (start, result):
        if record.get("evidence_version") != 1 or record.get("candidate_digest") != digest(manifest) or record.get("target") != target:
            raise ValueError("missing or mismatched candidate fingerprint/target")
    for name in ("stdout.txt", "stderr.txt", "FEATURE.md", "PROOF.md", "notes.md"):
        if not (run / name).is_file():
            raise ValueError(f"incomplete evidence: {name}")
    if kind == "proof" and not (run / "run.sh").is_file():
        raise ValueError("incomplete proof: run.sh")
    if passing:
        if result.get("status") != "PASS" or result.get("returncode") != 0 or result.get("runner_returncode") != 0:
            raise ValueError("evidence did not pass")
        if result.get("input_changes") or result.get("candidate_changes"):
            raise ValueError("candidate changed during execution")
        include = manifest.get("include")
        if not isinstance(include, list) or any(not isinstance(item, str) for item in include):
            raise ValueError("invalid candidate selection")
        if candidate(root, feature_dir, include) != manifest:
            raise ValueError("evidence is stale for the current candidate")
        if kind == "proof":
            attempts = sorted(path for path in run.parent.iterdir() if path.is_dir())
            if not attempts or attempts[-1] != run:
                raise ValueError("proof is not the newest official attempt")
        else:
            reject_later_regression_failure(run, result)
    return result, evidence_digest(run), manifest


def validate_supporting_inputs(proof: dict, regression: dict) -> None:
    # Feature ownership may differ; the observed candidate must still match.
    if any(regression[key] != proof[key] for key in ("selection", "include", "files")):
        raise ValueError("regression candidate inputs differ from proof inputs; recapture with the same includes and input coverage")


def validate_roles(value: dict) -> None:
    identities = [value.get(key) for key in ("implementer", "author", "reviewer")]
    if any(not isinstance(identity, str) or not identity.strip() for identity in identities):
        raise ValueError("implementer, acceptance author, and reviewer require identifiers")
    if len({identity.strip() for identity in identities}) != 3:
        raise ValueError("implementer, acceptance author, and reviewer must be distinct")
    if not isinstance(value.get("summary"), str) or not value["summary"].strip():
        raise ValueError("review requires a concise rationale")


def review(args) -> None:
    root = args.root.resolve()
    value = {key: getattr(args, key).strip() for key in ("implementer", "author", "reviewer", "summary")}
    validate_roles(value)
    passing = args.verdict == "PASS"
    proof, checksum, proof_candidate = evidence(root, args.proof_run, "proof", passing=passing)
    regressions = []
    for relative in dict.fromkeys(args.regression_run):
        result, regression_digest, regression_candidate = evidence(root, relative, "regression", passing=passing)
        if passing:
            if result["target"] != proof["target"]:
                raise ValueError("regression target differs from proof target")
            validate_supporting_inputs(proof_candidate, regression_candidate)
        regressions.append({"run": relative, "digest": regression_digest})
    value.update(version=1, reviewed_at=datetime.now(timezone.utc).isoformat(),
                 candidate_digest=proof["candidate_digest"], verdict=args.verdict, proof_run=args.proof_run, proof_digest=checksum,
                 target=proof["target"], regressions=regressions)
    value["receipt_digest"] = digest(value)
    path = repo_path(root, args.proof_run) / "review.json"
    if path.is_symlink():
        raise ValueError("review receipt must not use a symlink")
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"verification_receipt: {path}")


def validate_completion(root: Path, feature_dir: str, proof_run: str, owner: str) -> None:
    if not proof_run or not proof_run.startswith(feature_dir + "/proof/runs/"):
        raise ValueError("completion requires owning proof evidence")
    run = repo_path(root, proof_run)
    receipt_path = run / "review.json"
    if receipt_path.is_symlink():
        raise ValueError("review receipt must not use a symlink")
    receipt = read_json(receipt_path)
    checksum = receipt.pop("receipt_digest", None)
    if not checksum or checksum != digest(receipt):
        raise ValueError("review receipt changed or is incomplete")
    validate_roles(receipt)
    if receipt.get("version") != 1 or receipt.get("verdict") != "PASS" or receipt.get("implementer") != owner or receipt.get("proof_run") != proof_run:
        raise ValueError("completion requires a matching PASS review for the active implementer")
    proof, checksum, proof_candidate = evidence(root, proof_run, "proof")
    if checksum != receipt.get("proof_digest") or receipt.get("target") != proof["target"] or receipt.get("candidate_digest") != proof["candidate_digest"]:
        raise ValueError("reviewed proof evidence or target changed")
    reviewed_at = receipt.get("reviewed_at")
    if not isinstance(reviewed_at, str) or datetime.fromisoformat(reviewed_at).utcoffset() != timezone.utc.utcoffset(None):
        raise ValueError("review is missing a UTC review timestamp")
    if not isinstance(receipt.get("regressions"), list):
        raise ValueError("review is missing its selected regression list")
    for support in receipt["regressions"]:
        if not isinstance(support, dict) or set(support) != {"run", "digest"}:
            raise ValueError("invalid regression receipt")
        result, checksum, regression_candidate = evidence(root, support["run"], "regression")
        if checksum != support["digest"] or result["target"] != proof["target"]:
            raise ValueError("reviewed regression evidence or target changed")
        validate_supporting_inputs(proof_candidate, regression_candidate)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("review", help="Record an actual independent review and bind its retained evidence")
    command.add_argument("--root", type=Path, default=Path.cwd())
    for name in ("proof-run", "implementer", "author", "reviewer", "summary"):
        command.add_argument("--" + name, required=True)
    command.add_argument("--verdict", choices=("PASS", "FAIL"), required=True)
    command.add_argument("--regression-run", action="append", default=[])
    args = parser.parse_args()
    try:
        review(args)
    except (OSError, ValueError, TypeError) as error:
        print(f"verification_receipt: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
