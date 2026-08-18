from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from pathlib import Path
import subprocess

import yaml


ROOT = Path(__file__).resolve().parents[2]
EVAL_ROOT = ROOT / "evals" / "product-partner"
EXPECTED_CASES = {
    "rough-idea",
    "detailed-build",
    "adjacent-scope",
    "low-risk-fix",
    "future-seam",
    "runtime-proof",
}
DIMENSIONS = {
    "problem_synthesis",
    "question_economy",
    "initiative",
    "scope_control",
    "architecture_proportionality",
    "proof_fidelity",
    "completion_truth",
}
VERDICTS = {"meets", "mixed", "misses", "not_applicable"}


def load(name: str) -> dict:
    return yaml.safe_load((EVAL_ROOT / name).read_text(encoding="utf-8"))


def meaningful(value: object, minimum: int = 20) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value.strip().casefold()
    return len(normalized) >= minimum and "placeholder" not in normalized


def validate(corpus: dict, samples: dict, judgments: dict) -> list[str]:
    errors: list[str] = []
    case_items = corpus.get("cases", [])
    sample_items = samples.get("samples", [])
    review_items = judgments.get("cases", [])
    cases = {item.get("id"): item for item in case_items}
    outputs = {item.get("case_id"): item for item in sample_items}
    reviews = {item.get("case_id"): item for item in review_items}
    if len(case_items) != len(EXPECTED_CASES) or len(case_items) != len(cases):
        errors.append("case cardinality")
    if len(sample_items) != len(EXPECTED_CASES) or len(sample_items) != len(outputs):
        errors.append("sample cardinality")
    if len(review_items) != len(EXPECTED_CASES) or len(review_items) != len(reviews):
        errors.append("judgment cardinality")
    if set(cases) != EXPECTED_CASES:
        errors.append("case coverage")
    if set(outputs) != set(cases):
        errors.append("sample coverage")
    if set(reviews) != set(cases):
        errors.append("judgment coverage")
    if not meaningful(samples.get("sampling_context"), 40):
        errors.append("sampling context")
    if not meaningful(judgments.get("reviewer_context"), 40):
        errors.append("reviewer context")

    for case_id, case in cases.items():
        if not meaningful(case.get("prompt"), 40):
            errors.append(f"{case_id}: prompt")
        if not all(meaningful(item) for item in case.get("expected_outcomes", [])):
            errors.append(f"{case_id}: expected outcomes")
        if not all(meaningful(item) for item in case.get("disallowed_outcomes", [])):
            errors.append(f"{case_id}: disallowed outcomes")
        if not case.get("expected_outcomes") or not case.get("disallowed_outcomes"):
            errors.append(f"{case_id}: semantic pressure")

        sample = outputs.get(case_id, {})
        if not meaningful(sample.get("output"), 120):
            errors.append(f"{case_id}: sampled output")
        if not meaningful(sample.get("context"), 20):
            errors.append(f"{case_id}: sample context")

        dimensions = reviews.get(case_id, {}).get("dimensions", {})
        if set(dimensions) != DIMENSIONS:
            errors.append(f"{case_id}: dimensions")
        for dimension, result in dimensions.items():
            if result.get("verdict") not in VERDICTS:
                errors.append(f"{case_id}: {dimension} verdict")
            if not meaningful(result.get("evidence"), 25):
                errors.append(f"{case_id}: {dimension} evidence")

    try:
        sampled_at = datetime.fromisoformat(samples["sampled_at"])
        reviewed_at = datetime.fromisoformat(judgments["reviewed_at"])
        if sampled_at.tzinfo is None or reviewed_at.tzinfo is None:
            errors.append("timestamp timezone")
        elif reviewed_at < sampled_at:
            errors.append("judgment predates samples")
        else:
            now = datetime.now(sampled_at.tzinfo)
            if sampled_at > now or reviewed_at.astimezone(sampled_at.tzinfo) > now:
                errors.append("future evidence")
    except (KeyError, TypeError, ValueError):
        errors.append("timestamps")
    if "aggregate_score" in judgments:
        errors.append("aggregate score")
    return errors


def test_retained_behavioral_evaluation_is_complete() -> None:
    assert validate(load("cases.yaml"), load("samples.yaml"), load("judgments.yaml")) == []


def test_evaluation_artifacts_are_not_ignored() -> None:
    for name in ("cases.yaml", "samples.yaml", "judgments.yaml"):
        result = subprocess.run(
            ["git", "check-ignore", "--quiet", str(EVAL_ROOT / name)],
            cwd=ROOT,
            check=False,
        )
        assert result.returncode == 1, name


def test_semantic_cases_do_not_prescribe_response_phrases_or_templates() -> None:
    corpus = load("cases.yaml")
    serialized = yaml.safe_dump(corpus).casefold()
    for forbidden in ("must say", "must include", "exact phrase", "required heading"):
        assert forbidden not in serialized
    assert "response_template" not in corpus


def test_integrity_oracle_rejects_hollow_evidence() -> None:
    corpus = load("cases.yaml")
    samples = load("samples.yaml")
    judgments = load("judgments.yaml")

    missing_case = deepcopy(corpus)
    missing_case["cases"].pop()
    assert validate(missing_case, samples, judgments)

    missing_sample = deepcopy(samples)
    missing_sample["samples"].pop()
    assert validate(corpus, missing_sample, judgments)

    duplicate_case = deepcopy(corpus)
    duplicate_case["cases"].append(deepcopy(duplicate_case["cases"][0]))
    assert "case cardinality" in validate(duplicate_case, samples, judgments)

    duplicate_sample = deepcopy(samples)
    duplicate_sample["samples"].append(deepcopy(duplicate_sample["samples"][0]))
    assert "sample cardinality" in validate(corpus, duplicate_sample, judgments)

    duplicate_judgment = deepcopy(judgments)
    duplicate_judgment["cases"].append(deepcopy(duplicate_judgment["cases"][0]))
    assert "judgment cardinality" in validate(corpus, samples, duplicate_judgment)

    missing_dimension = deepcopy(judgments)
    missing_dimension["cases"][0]["dimensions"].pop("scope_control")
    assert validate(corpus, samples, missing_dimension)

    hollow_rationale = deepcopy(judgments)
    hollow_rationale["cases"][0]["dimensions"]["initiative"]["evidence"] = "placeholder"
    assert validate(corpus, samples, hollow_rationale)

    hollow_sampling_context = deepcopy(samples)
    hollow_sampling_context["sampling_context"] = "placeholder"
    assert "sampling context" in validate(corpus, hollow_sampling_context, judgments)

    hollow_reviewer_context = deepcopy(judgments)
    hollow_reviewer_context["reviewer_context"] = "placeholder"
    assert "reviewer context" in validate(corpus, samples, hollow_reviewer_context)

    future_judgment = deepcopy(judgments)
    future_judgment["reviewed_at"] = "2999-01-01T00:00:00+00:00"
    assert "future evidence" in validate(corpus, samples, future_judgment)
