#!/usr/bin/env python3
"""Coverage and round receipts, using the existing capture evidence format."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path, PurePosixPath
import re

from verification_receipt import (
    add_attribution_arguments, review_attribution, candidate, digest, evidence, fingerprint, read_json, repo_path, validate_roles,
)


IDENTIFIER = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def coverage(root: Path, feature_dir: str) -> dict:
    """Validate structure, not natural-language completeness or oracle adequacy."""
    value = read_json(repo_path(root, feature_dir + "/COVERAGE.json"))
    criteria = value.get("criteria")
    if set(value) != {"version", "criteria"} or value["version"] != 1 or not isinstance(criteria, dict) or not criteria:
        raise ValueError("coverage requires version 1 and nonempty criteria")
    for criterion, packages in criteria.items():
        if not criterion.strip() or not isinstance(packages, list) or not packages:
            raise ValueError("each acceptance criterion requires check packages")
        for name in packages:
            package = repo_path(root, name)
            parts = PurePosixPath(name).parts
            if len(parts) != 3 or parts[:2] not in {("docs", "features"), ("docs", "verification")} or parts[2] == "rounds" or not IDENTIFIER.fullmatch(parts[2]):
                raise ValueError("coverage check must name a feature or shared verification package")
            for filename in ("PROOF.md", "proof/run.sh"):
                path = repo_path(root, name + "/" + filename)
                if not path.is_file() or not path.read_bytes().strip():
                    raise ValueError(f"missing or empty check input: {name}/{filename}")
            if not os.access(package / "proof/run.sh", os.X_OK):
                raise ValueError(f"check runner is not executable: {name}")
    return value


def feature_bindings(root: Path, identifiers: list[str]) -> dict:
    entries = read_json(root / "docs/features/status.json").get("features", [])
    bindings = {}
    for identifier in sorted(set(identifiers)):
        if not IDENTIFIER.fullmatch(identifier):
            raise ValueError("invalid feature identifier")
        matches = [entry for entry in entries if entry.get("id") == identifier]
        if len(matches) != 1:
            raise ValueError(f"feature must exist exactly once in inventory: {identifier}")
        feature_dir = matches[0]["feature_dir"]
        path = repo_path(root, feature_dir + "/FEATURE.md")
        if not path.is_file() or not path.read_bytes().strip():
            raise ValueError(f"feature contract is missing: {identifier}")
        bindings[identifier] = {"feature_dir": feature_dir, "feature": fingerprint(path), "coverage": coverage(root, feature_dir)}
    if not bindings:
        raise ValueError("round requires features")
    return bindings


def required_packages(bindings: dict) -> set[str]:
    return {package for binding in bindings.values() for packages in binding["coverage"]["criteria"].values() for package in packages}


def checked_runs(root: Path, proofs: list[str], regressions: list[str], *, passing: bool) -> tuple[list[dict], str]:
    records = []
    targets = set()
    packages = set()
    for kind, runs in (("proof", proofs), ("regression", regressions)):
        for relative in dict.fromkeys(runs):
            result, checksum, manifest = evidence(root, relative, kind, passing=passing)
            package = manifest["feature_dir"]
            if kind == "proof":
                if package in packages:
                    raise ValueError("select only one current proof per check package")
                packages.add(package)
            targets.add(result["target"])
            records.append({"run": relative, "kind": kind, "package": package, "digest": checksum})
    if passing and (not proofs or len(targets) != 1):
        raise ValueError("round requires passing proof on one consistent target")
    return records, next(iter(targets)) if len(targets) == 1 else "mixed-diagnostic-targets"


def round_path(root: Path, relative: str) -> Path:
    path = repo_path(root, relative)
    parts = PurePosixPath(relative).parts
    if len(parts) != 5 or parts[:3] != ("docs", "verification", "rounds") or parts[4] != "review.json" or not IDENTIFIER.fullmatch(parts[3]):
        raise ValueError("expected docs/verification/rounds/<id>/review.json")
    return path


def read_round(root: Path, relative: str) -> dict:
    value = read_json(round_path(root, relative))
    checksum = value.pop("receipt_digest", None)
    if not checksum or checksum != digest(value):
        raise ValueError("round receipt changed or is incomplete")
    validate_roles(value)
    if value.get("version") not in (1, 2) or value.get("kind") != "round" or value.get("verdict") != "PASS":
        raise ValueError("completion requires a PASS round review")
    if not isinstance(value.get("features"), dict) or not value["features"] or not isinstance(value.get("evidence"), list):
        raise ValueError("round requires coverage and evidence")
    if not isinstance(value.get("reviewed_at"), str) or datetime.fromisoformat(value["reviewed_at"]).utcoffset() != timezone.utc.utcoffset(None):
        raise ValueError("round requires a UTC review timestamp")
    return value


def validate_round(root: Path, relative: str, *, feature_id: str | None = None, owner: str | None = None, current: bool = True) -> dict:
    value = read_round(root, relative)
    if feature_id is not None and feature_id not in value["features"]:
        raise ValueError("round does not cover this feature")
    if owner is not None and value["implementer"] != owner:
        raise ValueError("round implementer does not match completion owner")
    # Inventory reads retain the historical receipt, without asserting freshness.
    if not current:
        return value
    selected = [feature_id] if feature_id is not None else list(value["features"])
    bindings = feature_bindings(root, selected)
    if bindings != {key: value["features"][key] for key in selected}:
        raise ValueError("round coverage or feature contract changed")
    if value["version"] == 1 and candidate(root, "docs/verification/rounds", []) != value.get("candidate"):
        raise ValueError("round candidate is stale")
    proofs, regressions = [], []
    for item in value["evidence"]:
        if not isinstance(item, dict) or set(item) != {"run", "kind", "package", "digest"} or item["kind"] not in {"proof", "regression"}:
            raise ValueError("invalid round evidence")
        if feature_id is None or item["kind"] == "regression" or item["package"] in required_packages(bindings):
            (proofs if item["kind"] == "proof" else regressions).append(item["run"])
    records, target = checked_runs(root, proofs, regressions, passing=True)
    selected_runs = set(proofs + regressions)
    if records != [item for item in value["evidence"] if item["run"] in selected_runs] or target != value.get("target"):
        raise ValueError("round evidence or target changed")
    if not required_packages(bindings).issubset({item["package"] for item in records if item["kind"] == "proof"}):
        raise ValueError("round has uncovered acceptance criteria")
    return value


def record_round(args) -> None:
    root = args.root.resolve()
    relative = f"docs/verification/rounds/{args.round}/review.json"
    path = round_path(root, relative)
    value = review_attribution(args)
    validate_roles(value)
    bindings = feature_bindings(root, args.feature)
    passing = args.verdict == "PASS"
    records, target = checked_runs(root, args.proof_run, args.regression_run, passing=passing)
    if passing and not required_packages(bindings).issubset({item["package"] for item in records if item["kind"] == "proof"}):
        raise ValueError("round has uncovered acceptance criteria; provide all mapped checks")
    value.update(version=2, kind="round", verdict=args.verdict, reviewed_at=datetime.now(timezone.utc).isoformat(),
                 features=bindings, evidence=records, target=target)
    value["receipt_digest"] = digest(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    # A new review gets a new round ID; do not rewrite retained history.
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(f"verification_receipt: {path}")


def add_commands(commands) -> None:
    command = commands.add_parser("round", help="Record an actual attributed review across mapped features")
    command.add_argument("--root", type=Path, default=Path.cwd())
    for name in ("round", "implementer", "summary"):
        command.add_argument("--" + name, required=True)
    command.add_argument("--feature", action="append", required=True)
    command.add_argument("--proof-run", action="append", default=[])
    command.add_argument("--regression-run", action="append", default=[])
    add_attribution_arguments(command)
    command.add_argument("--verdict", choices=("PASS", "FAIL"), required=True)
    command = commands.add_parser("check-round", help="Read-only validation of current round evidence and candidate")
    command.add_argument("--root", type=Path, default=Path.cwd())
    command.add_argument("--round-review", required=True)


def dispatch(args) -> None:
    if args.command == "round":
        record_round(args)
    else:
        validate_round(args.root.resolve(), args.round_review)
        print("verification_receipt: round is current for its recorded coverage and target")
