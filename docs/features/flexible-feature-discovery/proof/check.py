#!/usr/bin/env python3
"""Validate an honest retained behavioral review, not agent language compliance."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_file(record):
    path = BASE / record["path"]
    require(path.is_file(), f"missing retained evidence: {path}")
    require(digest(path) == record["sha256"], f"evidence changed: {path}")
    return path


def main():
    authoring = json.loads((BASE / "authoring.json").read_text())
    for name, expected in authoring["acceptance_input_hashes"].items():
        require(digest(BASE / name) == expected, f"acceptance input changed: {name}")
    manifest_path = BASE / "trials.json"
    require(manifest_path.is_file(), "fresh trials and independent adjudication have not been retained")
    manifest = json.loads(manifest_path.read_text())
    require(manifest.get("schema_version") == 1, "unsupported trial manifest")
    require(manifest.get("observation_kind") == "fresh-agent-execution", "static responses are not live task trials")
    require(bool(manifest.get("limitations")), "trial limitations must be disclosed")
    trials = manifest["trials"]
    for trial in trials:
        require(trial.get("worker_id") and trial.get("model") and trial.get("effort"), "missing worker conditions")
        require(trial.get("fixture_sha256") and trial.get("instruction_snapshot"), "missing trial input identity")
        require(trial["fixture_sha256"] == authoring["fixture_hashes"][trial["case"]], "trial does not identify the frozen fixture")
        require(trial.get("native_trace"), "native visible-event trace required; summaries alone are insufficient")
        checked_file(trial["native_trace"])
        for artifact in trial.get("artifacts", []):
            checked_file(artifact)
    candidates = {t["case"]: t for t in trials if t["variant"] == "candidate" and t.get("final_for_case")}
    require(set(candidates) == {"studio", "export", "repair", "portal"}, "candidate scenario coverage incomplete")
    baselines = [t for t in trials if t["variant"] == "baseline" and t["case"] == "studio"]
    require(bool(baselines), "motivating baseline comparison missing")
    compared = baselines[-1]
    for field in ("model", "effort", "fixture_sha256"):
        require(compared[field] == candidates["studio"][field], f"comparison differs on {field}")
    review = manifest["independent_review"]
    require(review["reviewer_id"] not in {manifest["implementer_id"], manifest["proof_author_id"]}, "reviewer is not independent")
    checked_file(review["evidence"])
    require(review.get("verdict") == "PASS", "final independent review did not pass")
    require(set(review.get("passed_cases", [])) == set(candidates), "review did not accept every required candidate case")
    snapshot = manifest["candidate_instruction_hashes"]
    root = BASE.parents[3]
    for name, expected in snapshot.items():
        require(digest(root / name) == expected, f"candidate changed since review: {name}")
    require(snapshot, "candidate instruction identity is empty")
    print("PASS: retained fresh task samples and independent review match the recorded candidate.")
    print("LIMIT: one sample per case is not a reliability estimate; semantic judgment is retained review evidence.")


if __name__ == "__main__":
    main()
