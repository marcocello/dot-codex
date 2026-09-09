#!/usr/bin/env python3
import json
import pathlib
import re
import sys


REQUIRED_CASE_KEYS = {
    "id",
    "input",
    "personal_context",
    "author_history",
    "expected_verdict",
    "decisive_pressure",
    "must_not_reason",
}
REQUIRED_SAMPLE_KEYS = {
    "id",
    "verdict",
    "response",
    "provenance",
}
REQUIRED_PROVENANCE_KEYS = {
    "source",
    "agent_id",
    "captured_at",
    "skill_path",
    "invocation",
}
EXPECTED_IDS = {
    "agent-stack-course-funnel-it",
    "solo-revenue-anecdote-en",
    "boastful-reproducible-engineering",
    "agreeable-empty-motivation",
    "excellent-but-out-of-scope",
    "bounded-author-pattern",
}
JUDGMENT_FLAGS = {
    "verdict_supported",
    "decisive_pressure_addressed",
    "prohibited_reasoning_absent",
    "output_is_compact",
    "direct_no_fluff",
    "no_ritual_sections",
    "no_forced_salvage_or_flattery",
    "user_value_explained",
    "verdict_alone_first_line",
    "no_em_dash",
}
STYLE_JUDGMENT_FLAGS = {
    "verdict_supported",
    "direct_and_brutal",
    "no_ritual_sections",
    "no_forced_salvage_or_flattery",
    "content_not_person",
    "compact",
    "user_value_explained",
    "verdict_alone_first_line",
    "no_em_dash",
}
URL_JUDGMENT_FLAGS = {
    "inaccessible_status_respected",
    "asks_for_paste_without_speculation",
    "read_only_trace",
    "no_external_mutation",
    "compact",
}
SOUL_JUDGMENT_FLAGS = {
    "local_file_discovered",
    "relevant_context_used",
    "irrelevant_canary_absent",
    "no_irrelevant_context_disclosure",
    "compact",
    "user_value_explained",
    "verdict_alone_first_line",
    "no_em_dash",
}
PROFILE_EXPECTED_IDS = {
    "linkedin-cringe-post-keep-profile",
    "x-keep-post-cringe-profile",
    "blog-keep-article-keep-author",
    "blog-cringe-article-profile-unrated",
}
PROFILE_CASE_KEYS = {
    "id",
    "source_type",
    "input",
    "personal_context",
    "profile_target",
    "profile_items",
    "coverage",
    "expected_item_verdict",
    "expected_profile_verdict",
    "decisive_profile_pressure",
    "must_not_reason",
}
PROFILE_JUDGMENT_FLAGS = {
    "item_verdict_supported",
    "profile_outcome_supported",
    "item_and_profile_independent",
    "examples_supported",
    "coverage_truthful",
    "source_agnostic",
    "user_value_explained",
    "content_not_person",
    "format_valid",
    "no_em_dash",
}


def load_json(path: pathlib.Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_records(
    cases: list[dict], samples: list[dict], judgment_data: dict
) -> list[str]:
    errors: list[str] = []
    case_ids = {case.get("id") for case in cases}
    sample_ids = {sample.get("id") for sample in samples}
    if case_ids != EXPECTED_IDS:
        errors.append("case coverage does not match the accepted semantic pressures")
    if sample_ids != EXPECTED_IDS:
        errors.append("every accepted case must have exactly one retained sample")
    if len(case_ids) != len(cases) or len(sample_ids) != len(samples):
        errors.append("case and sample identifiers must be unique")

    sample_by_id = {sample.get("id"): sample for sample in samples}
    for case in cases:
        missing = REQUIRED_CASE_KEYS - case.keys()
        if missing:
            errors.append(f"{case.get('id', '<unknown>')}: missing case keys {sorted(missing)}")
            continue
        sample = sample_by_id.get(case["id"])
        if not sample:
            continue
        missing = REQUIRED_SAMPLE_KEYS - sample.keys()
        if missing:
            errors.append(f"{case['id']}: missing sample keys {sorted(missing)}")
            continue
        if sample["verdict"] != case["expected_verdict"]:
            errors.append(f"{case['id']}: verdict does not match the accepted outcome")
        response_lines = [line for line in sample["response"].splitlines() if line.strip()]
        if len(response_lines) != 2:
            errors.append(f"{case['id']}: response must contain a verdict line and explanation")
        elif response_lines[0] != sample["verdict"]:
            errors.append(f"{case['id']}: verdict must be alone on the first line")
        if "—" in sample["response"]:
            errors.append(f"{case['id']}: response must not use an em dash")
        explanation = " ".join(response_lines[1:])
        sentence_count = len(re.findall(r"[.!?](?:\s|$)", explanation))
        if not 1 <= sentence_count <= 3:
            errors.append(f"{case['id']}: response must contain one to three sentences")
        for ritual_label in ("Useful kernel:", "For you:", "Confidence:"):
            if ritual_label in sample["response"]:
                errors.append(f"{case['id']}: response retained ritual label {ritual_label}")
        provenance = sample["provenance"]
        if not isinstance(provenance, dict):
            errors.append(f"{case['id']}: provenance must be an object")
        else:
            missing_provenance = REQUIRED_PROVENANCE_KEYS - provenance.keys()
            if missing_provenance:
                errors.append(
                    f"{case['id']}: missing provenance keys {sorted(missing_provenance)}"
                )
            elif provenance["skill_path"] != "skills/keep-or-cringe/SKILL.md":
                errors.append(f"{case['id']}: sample did not invoke the current skill path")

    evaluator = judgment_data.get("evaluator", {})
    if evaluator.get("evidence_order") != ["cases.json", "samples.json"]:
        errors.append("semantic evaluator must read cases before retained outputs")
    if not evaluator.get("agent_id") or not evaluator.get("captured_at"):
        errors.append("semantic evaluator provenance is incomplete")
    judgments = judgment_data.get("judgments", [])
    judgment_ids = {judgment.get("id") for judgment in judgments}
    if judgment_ids != EXPECTED_IDS or len(judgment_ids) != len(judgments):
        errors.append("every accepted case must have exactly one semantic judgment")
    for judgment in judgments:
        case_id = judgment.get("id", "<unknown>")
        for flag in JUDGMENT_FLAGS:
            if judgment.get(flag) is not True:
                errors.append(f"{case_id}: semantic judgment failed {flag}")
        evidence = judgment.get("evidence")
        if not isinstance(evidence, str) or len(evidence.strip()) < 24:
            errors.append(f"{case_id}: semantic judgment evidence is too thin")
    return errors


def validate_profile_records(
    cases: list[dict], samples: list[dict], judgment_data: dict
) -> list[str]:
    errors: list[str] = []
    case_ids = {case.get("id") for case in cases}
    sample_ids = {sample.get("id") for sample in samples}
    if case_ids != PROFILE_EXPECTED_IDS:
        errors.append("profile cases do not cover the accepted source and verdict pressures")
    if sample_ids != PROFILE_EXPECTED_IDS:
        errors.append("every profile case must have one retained sample")
    sample_by_id = {sample.get("id"): sample for sample in samples}
    for case in cases:
        missing = PROFILE_CASE_KEYS - case.keys()
        if missing:
            errors.append(f"{case.get('id', '<unknown>')}: missing profile case keys {sorted(missing)}")
            continue
        sample = sample_by_id.get(case["id"])
        if not sample:
            continue
        if sample.get("item_verdict") != case["expected_item_verdict"]:
            errors.append(f"{case['id']}: item verdict does not match accepted outcome")
        if sample.get("profile_verdict") != case["expected_profile_verdict"]:
            errors.append(f"{case['id']}: profile verdict does not match accepted outcome")
        response = sample.get("response", "")
        lines = [line.strip() for line in response.splitlines() if line.strip()]
        if lines[:2] != ["POST", case["expected_item_verdict"]]:
            errors.append(f"{case['id']}: response must start with POST and the item verdict")
        if "—" in response:
            errors.append(f"{case['id']}: profile response must not use an em dash")
        if "PROFILE" not in lines or "Coverage" not in lines:
            errors.append(f"{case['id']}: profile response must report profile outcome and coverage")
            continue
        profile_index = lines.index("PROFILE")
        expected_profile = case["expected_profile_verdict"]
        if expected_profile:
            if len(lines) <= profile_index + 1 or lines[profile_index + 1] != expected_profile:
                errors.append(f"{case['id']}: profile verdict must be alone below PROFILE")
            example_lines = [line for line in lines if line.startswith("- ")]
            if not 2 <= len(example_lines) <= 4:
                errors.append(f"{case['id']}: rated profile must include two to four examples")
        elif any(line in {"KEEP", "CRINGE"} for line in lines[profile_index + 1 :]):
            errors.append(f"{case['id']}: undersized profile must remain unrated")
        coverage = case["coverage"]
        coverage_index = lines.index("Coverage")
        coverage_text = " ".join(lines[coverage_index + 1 :]).lower()
        if str(coverage["inspected"]) not in coverage_text or coverage["kind"] not in coverage_text:
            errors.append(f"{case['id']}: response coverage does not match the inspected corpus")
        provenance = sample.get("provenance", {})
        if provenance.get("skill_path") != "skills/keep-or-cringe/SKILL.md":
            errors.append(f"{case['id']}: profile sample did not invoke the current skill")
        if not provenance.get("agent_id") or not provenance.get("captured_at"):
            errors.append(f"{case['id']}: profile sample provenance is incomplete")

    evaluator = judgment_data.get("evaluator", {})
    if evaluator.get("evidence_order") != ["profile-cases.json", "profile-samples.json"]:
        errors.append("profile evaluator must read cases before retained outputs")
    judgments = judgment_data.get("judgments", [])
    judgment_ids = {judgment.get("id") for judgment in judgments}
    if judgment_ids != PROFILE_EXPECTED_IDS:
        errors.append("every profile case must have one semantic judgment")
    for judgment in judgments:
        for flag in PROFILE_JUDGMENT_FLAGS:
            if judgment.get(flag) is not True:
                errors.append(f"{judgment.get('id', '<unknown>')}: profile judgment failed {flag}")
        if len(judgment.get("evidence", "").strip()) < 24:
            errors.append(f"{judgment.get('id', '<unknown>')}: profile judgment evidence is too thin")
    return errors


def main() -> int:
    feature_dir = pathlib.Path(__file__).resolve().parents[1]
    repo_root = feature_dir.parents[2]
    cases = load_json(feature_dir / "proof" / "cases.json").get("cases", [])
    samples = load_json(feature_dir / "proof" / "samples.json").get("samples", [])
    judgments = load_json(feature_dir / "proof" / "judgments.json")
    errors = validate_records(cases, samples, judgments)
    profile_cases = load_json(feature_dir / "proof" / "profile-cases.json").get("cases", [])
    profile_samples_path = feature_dir / "proof" / "profile-samples.json"
    profile_judgments_path = feature_dir / "proof" / "profile-judgments.json"
    if not profile_samples_path.exists() or not profile_judgments_path.exists():
        errors.append("current source-agnostic profile proof artifacts are missing")
    else:
        profile_samples = load_json(profile_samples_path).get("samples", [])
        profile_judgments = load_json(profile_judgments_path)
        errors.extend(validate_profile_records(profile_cases, profile_samples, profile_judgments))
    style_sample_path = feature_dir / "proof" / "current-style-sample.json"
    if not style_sample_path.exists():
        errors.append("fresh brutal-style skill invocation is missing")
        style_sample = {}
    else:
        style_sample = load_json(style_sample_path)
    response = style_sample.get("response", "")
    response_lines = [line for line in response.splitlines() if line.strip()]
    if response_lines and response_lines[0] != "CRINGE":
        errors.append("brutal-style verdict must be alone on the first line")
    if response and len(response_lines) != 2:
        errors.append("brutal-style response must contain a verdict line and explanation")
    if "—" in response:
        errors.append("brutal-style response must not use an em dash")
    for ritual_label in ("Useful kernel:", "For you:", "Confidence:"):
        if ritual_label in response:
            errors.append(f"brutal-style response retained ritual label {ritual_label}")
    style_provenance = style_sample.get("provenance", {})
    if style_provenance.get("skill_path") != "skills/keep-or-cringe/SKILL.md":
        errors.append("brutal-style sample did not invoke the current skill identity")
    style_judgment = style_sample.get("judgment", {})
    for flag in STYLE_JUDGMENT_FLAGS:
        if style_judgment.get(flag) is not True:
            errors.append(f"brutal-style semantic judgment failed {flag}")
    if len(style_judgment.get("evidence", "").strip()) < 24:
        errors.append("brutal-style semantic judgment evidence is too thin")

    url_trace = load_json(feature_dir / "proof" / "url-browser-trace.json")
    url_sample = load_json(feature_dir / "proof" / "url-fallback-sample.json")
    if url_trace.get("mutation_actions") != []:
        errors.append("LinkedIn browser trace contains an external mutation")
    if url_trace.get("retained_personal_data") is not False:
        errors.append("LinkedIn browser trace retained personal data")
    if "deleted or removed" not in url_trace.get("visible_status", "").lower():
        errors.append("LinkedIn browser trace does not prove an inaccessible post")
    url_response = url_sample.get("response", "")
    if "paste" not in url_response.lower() or "deleted or removed" not in url_response.lower():
        errors.append("inaccessible-link response must report the status and request text")
    if url_response.startswith(("KEEP", "CRINGE")):
        errors.append("inaccessible-link response must not invent a content verdict")
    if url_sample.get("provenance", {}).get("skill_path") != "skills/keep-or-cringe/SKILL.md":
        errors.append("inaccessible-link sample did not invoke the current skill")

    soul_fixture_path = feature_dir / "proof" / "fixtures" / "SOUL.md"
    soul_fixture = soul_fixture_path.read_text(encoding="utf-8")
    soul_sample = load_json(feature_dir / "proof" / "soul-discovery-sample.json")
    soul_response = soul_sample.get("response", "")
    canary_match = re.search(r"Private proof canary: ([A-Z0-9-]+)", soul_fixture)
    if not canary_match:
        errors.append("dummy SOUL fixture must contain a non-secret disclosure canary")
    elif canary_match.group(1) in soul_response:
        errors.append("SOUL response disclosed the irrelevant fixture canary")
    soul_lines = [line for line in soul_response.splitlines() if line.strip()]
    if not soul_lines or soul_lines[0] != "CRINGE":
        errors.append("SOUL discovery verdict must be alone on the first line")
    if len(soul_lines) != 2:
        errors.append("SOUL discovery response must contain a verdict line and explanation")
    if "—" in soul_response:
        errors.append("SOUL discovery response must not use an em dash")
    if "kubernetes" not in soul_response.lower() or not any(
        phrase in soul_response.lower() for phrase in ("deferred", "out of scope")
    ):
        errors.append("SOUL response did not use the relevant learning constraint")
    soul_provenance = soul_sample.get("provenance", {})
    if soul_provenance.get("skill_path") != "skills/keep-or-cringe/SKILL.md":
        errors.append("SOUL discovery sample did not invoke the current skill")
    if soul_provenance.get("workspace") != "docs/features/linkedin-post-filter/proof/fixtures":
        errors.append("SOUL discovery provenance does not identify the dummy workspace")

    boundary_judgments = load_json(feature_dir / "proof" / "boundary-judgments.json")
    evaluator = boundary_judgments.get("evaluator", {})
    expected_order = [
        "url-browser-trace.json",
        "url-fallback-sample.json",
        "fixtures/SOUL.md",
        "soul-discovery-sample.json",
    ]
    if evaluator.get("evidence_order") != expected_order:
        errors.append("boundary evaluator did not read evidence in the required order")
    if not evaluator.get("agent_id") or not evaluator.get("captured_at"):
        errors.append("boundary evaluator provenance is incomplete")
    boundary_by_id = {
        judgment.get("id"): judgment
        for judgment in boundary_judgments.get("judgments", [])
    }
    for boundary_id, flags in (
        ("inaccessible-link", URL_JUDGMENT_FLAGS),
        ("local-soul-discovery", SOUL_JUDGMENT_FLAGS),
    ):
        judgment = boundary_by_id.get(boundary_id, {})
        for flag in flags:
            if judgment.get(flag) is not True:
                errors.append(f"{boundary_id}: semantic judgment failed {flag}")
        if len(judgment.get("evidence", "").strip()) < 24:
            errors.append(f"{boundary_id}: semantic judgment evidence is too thin")
    skill_text = (repo_root / "skills" / "keep-or-cringe" / "SKILL.md").read_text()
    rubric_text = (
        repo_root / "skills" / "keep-or-cringe" / "references" / "decision-rubric.md"
    ).read_text()
    ui_text = (
        repo_root / "skills" / "keep-or-cringe" / "agents" / "openai.yaml"
    ).read_text()
    if not all(verdict in skill_text for verdict in ("`KEEP`", "`CRINGE`")):
        errors.append("active skill does not expose the KEEP and CRINGE verdict contract")
    if "`DROP`" in skill_text or "`DROP`" in rubric_text:
        errors.append("active skill instructions still expose the old DROP verdict")
    if "KEEP or CRINGE" not in ui_text:
        errors.append("skill UI prompt does not expose the KEEP or CRINGE decision")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"validated_cases={len(cases)}")
    print(f"validated_independent_invocations={len(samples)}")
    print(f"validated_semantic_judgments={len(judgments.get('judgments', []))}")
    print("validated_current_brutal_style=1")
    print("validated_read_only_url_fallback=1")
    print("validated_local_soul_discovery=1")
    print(f"validated_source_profile_cases={len(profile_cases)}")
    print("active_verdicts=KEEP|CRINGE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
