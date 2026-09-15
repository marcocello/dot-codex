#!/usr/bin/env python3
import argparse
import csv
import json
import os
import tempfile
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


COMMON_FIELDS = [
    "analysis_date", "provider", "provider_rank", "job_title", "company",
    "location", "work_mode", "employment_type", "job_url", "listing_date",
]
TRAILING_FIELDS = ["overall_points", "fit", "reason", "missing_constraints"]
GENERIC_SCORE_LIMITS = {
    "role_scope_points": 30,
    "experience_evidence_points": 25,
    "objective_alignment_points": 20,
    "practical_conditions_points": 25,
}
LEGACY_SCORE_LIMITS = {
    "implementation_product_points": 30,
    "authority_people_points": 25,
    "ai_relevance_points": 20,
    "company_conditions_points": 25,
}
SUPPORTED_SCORECARDS = (GENERIC_SCORE_LIMITS, LEGACY_SCORE_LIMITS)
TRACKING_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "referrer"}


def fields_for(score_limits):
    return [*COMMON_FIELDS, *score_limits, *TRAILING_FIELDS]


def scorecard_for(fieldnames):
    for score_limits in SUPPORTED_SCORECARDS:
        if fieldnames == fields_for(score_limits):
            return score_limits
    supported = " or ".join(",".join(fields_for(item)) for item in SUPPORTED_SCORECARDS)
    raise ValueError(f"unsupported CSV header; expected: {supported}")


def canonical_url(raw_url):
    parts = urlsplit(raw_url.strip())
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        raise ValueError(f"job_url must be an absolute HTTP(S) URL: {raw_url!r}")
    host = parts.hostname.lower()
    port = parts.port
    if port and not ((parts.scheme.lower() == "http" and port == 80) or
                     (parts.scheme.lower() == "https" and port == 443)):
        host = f"{host}:{port}"
    path = parts.path.rstrip("/") or "/"
    query = [
        (key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in TRACKING_KEYS
    ]
    return urlunsplit((parts.scheme.lower(), host, path, urlencode(query), ""))


def read_rows(path, required):
    if not path.exists():
        if required:
            raise FileNotFoundError(f"incoming CSV does not exist: {path}")
        return None, [], None
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        score_limits = scorecard_for(fieldnames)
        rows = list(reader)
    for line_number, row in enumerate(rows, start=2):
        validate_row(row, path, line_number, score_limits)
    return fieldnames, rows, score_limits


def validate_row(row, path, line_number, score_limits):
    label = f"{path}:{line_number}"
    for field in (
        "analysis_date", "provider", "provider_rank", "job_title", "company",
        "job_url", "overall_points", "fit", "reason",
    ):
        if not row[field].strip():
            raise ValueError(f"{label}: {field} is required")
    try:
        parsed_date = date.fromisoformat(row["analysis_date"])
    except ValueError as error:
        raise ValueError(f"{label}: analysis_date must be YYYY-MM-DD") from error
    if str(parsed_date) != row["analysis_date"]:
        raise ValueError(f"{label}: analysis_date must be YYYY-MM-DD")
    canonical_url(row["job_url"])
    scores = {
        field: parse_score(row[field], field, maximum, label)
        for field, maximum in score_limits.items()
    }
    overall = parse_score(row["overall_points"], "overall_points", 100, label)
    if overall != sum(scores.values()):
        raise ValueError(f"{label}: overall_points must equal the four components")


def parse_score(raw_value, field, maximum, label):
    try:
        value = int(raw_value)
    except ValueError as error:
        raise ValueError(f"{label}: {field} must be an integer") from error
    if not 0 <= value <= maximum:
        raise ValueError(f"{label}: {field} must be between 0 and {maximum}")
    return value


def write_rows(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temp_path, path)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def merge_findings(existing_path, incoming_path, output_path):
    existing_fields, existing, _ = read_rows(Path(existing_path), required=False)
    incoming_fields, incoming, _ = read_rows(Path(incoming_path), required=True)
    if existing_fields and existing_fields != incoming_fields:
        raise ValueError("incoming CSV header must match the existing findings header")
    fieldnames = existing_fields or incoming_fields
    seen = {canonical_url(row["job_url"]) for row in existing}
    added = []
    duplicates = 0
    for row in incoming:
        identity = canonical_url(row["job_url"])
        if identity in seen:
            duplicates += 1
            continue
        seen.add(identity)
        added.append(row)
    write_rows(Path(output_path), fieldnames, [*existing, *added])
    return {"existing": len(existing), "added": len(added), "duplicates": duplicates}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Append URL-unique job findings to a validated CSV history."
    )
    parser.add_argument("--existing", required=True, type=Path)
    parser.add_argument("--incoming", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main():
    args = parse_args()
    output = args.output or args.existing
    result = merge_findings(args.existing, args.incoming, output)
    print(json.dumps({**result, "output": str(output)}, sort_keys=True))


if __name__ == "__main__":
    main()
