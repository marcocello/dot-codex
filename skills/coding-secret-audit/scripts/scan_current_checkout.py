#!/usr/bin/env python3
"""Scan checkout files for secrets and structured personal information."""

from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Any

DEFAULT_URL = "http://127.0.0.1:8000"
DEFAULT_MAX_BYTES = 1_000_000
DEFAULT_BATCH_SIZE = 20
SECRET_KEYS = {"match", "secret", "value", "token", "password", "apikey", "api_key"}
VISIBILITY_ENV_NAMES = (
    "AUDIT_REPOSITORY_VISIBILITY",
    "GITHUB_REPOSITORY_VISIBILITY",
    "CI_PROJECT_VISIBILITY",
)
VISIBILITY_VALUES = {"public", "private", "internal", "unknown"}
RESERVED_EMAIL_DOMAINS = {
    "example.com",
    "example.net",
    "example.org",
    "localhost",
}
EMAIL_PATTERN = re.compile(
    r"(?i)(?<![A-Z0-9._%+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,63}"
    r"(?![A-Z0-9._%+-])"
)
POSIX_HOME_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_.-])/(?:Users|home)/[A-Za-z0-9._-]+"
    r"(?:/[^\s\"'`<>]*)?"
)
WINDOWS_HOME_PATTERN = re.compile(
    r"(?i)(?<![A-Z0-9_])[A-Z]:\\Users\\[A-Z0-9._-]+"
    r"(?:\\[^\s\"'`<>]*)?"
)
SUBSCRIPTION_FIELD_PATTERN = re.compile(
    r"(?i)\b(?:azure[_\s.-]*)?subscription[_\s.-]*id\b"
)
UUID_PATTERN = re.compile(
    r"(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12}\b"
)


def git_output(root: Path, args: list[str]) -> bytes:
    return subprocess.check_output(["git", *args], cwd=root)


def checkout_paths(root: Path) -> list[str]:
    output = git_output(root, ["ls-files", "--cached", "--others", "--exclude-standard", "-z"])
    return [item.decode("utf-8", errors="surrogateescape") for item in output.split(b"\0") if item]


def read_checkout_document(
    root: Path, relative_path: str, max_bytes: int
) -> tuple[dict[str, str] | None, dict[str, str] | None]:
    path = root / relative_path
    if not path.is_file():
        return None, {"path": relative_path, "reason": "not a file"}

    size = path.stat().st_size
    if size > max_bytes:
        return None, {"path": relative_path, "reason": f"larger than {max_bytes} bytes"}

    data = path.read_bytes()
    if b"\0" in data:
        return None, {"path": relative_path, "reason": "binary content"}

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None, {"path": relative_path, "reason": "non-utf8 content"}

    return {"document": text, "filename": relative_path}, None


def collect_checkout_documents(
    root: Path, max_bytes: int = DEFAULT_MAX_BYTES
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    root = root.resolve()
    documents: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []

    for relative_path in checkout_paths(root):
        document, skip = read_checkout_document(root, relative_path, max_bytes)
        if document is not None:
            documents.append(document)
        if skip is not None:
            skipped.append(skip)

    return documents, skipped


def normalize_visibility(raw_value: str) -> str | None:
    value = raw_value.strip().lower()
    return value if value in VISIBILITY_VALUES else None


def repository_visibility(root: Path) -> tuple[str, str]:
    for name in VISIBILITY_ENV_NAMES:
        raw_value = os.environ.get(name)
        if raw_value is None:
            continue
        value = normalize_visibility(raw_value)
        if value is None:
            return "unknown", f"invalid environment:{name}"
        return value, f"environment:{name}"

    gh = shutil.which("gh")
    if gh is None:
        return "unknown", "provider lookup unavailable"
    try:
        result = subprocess.run(
            [gh, "repo", "view", "--json", "visibility", "--jq", ".visibility"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown", "provider lookup failed"
    value = normalize_visibility(result.stdout) if result.returncode == 0 else None
    if value is None:
        return "unknown", "provider lookup failed"
    return value, "gh"


def reserved_email(value: str) -> bool:
    domain = value.rsplit("@", maxsplit=1)[-1].lower()
    return (
        domain in RESERVED_EMAIL_DOMAINS
        or domain.endswith(".invalid")
        or domain.endswith(".test")
    )


def personal_information_findings(
    documents: list[dict[str, str]],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str, str]] = set()

    def add(filename: str, line_number: int, detector: str, value: str) -> None:
        key = (filename, line_number, detector, value)
        if key in seen:
            return
        seen.add(key)
        findings.append(
            {
                "file": filename,
                "line": line_number,
                "detector": detector,
                "value": value,
            }
        )

    for document in documents:
        filename = document["filename"]
        for line_number, line in enumerate(document["document"].splitlines(), start=1):
            for match in EMAIL_PATTERN.finditer(line):
                value = match.group(0)
                if not reserved_email(value):
                    add(filename, line_number, "personal_email", value)
            for pattern in (POSIX_HOME_PATTERN, WINDOWS_HOME_PATTERN):
                for match in pattern.finditer(line):
                    add(filename, line_number, "local_home_path", match.group(0))
            if SUBSCRIPTION_FIELD_PATTERN.search(line):
                for match in UUID_PATTERN.finditer(line):
                    add(
                        filename,
                        line_number,
                        "cloud_subscription_id",
                        match.group(0),
                    )
    return findings


def chunked(items: list[dict[str, str]], size: int) -> list[list[dict[str, str]]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def call_ggmcp_scan(
    url: str,
    token: str | None,
    documents: list[dict[str, str]],
    timeout: float,
) -> list[dict[str, Any]]:
    endpoint = url.rstrip("/")
    if not endpoint.endswith("/mcp"):
        endpoint += "/mcp"
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "scan_secrets",
                "arguments": {"params": {"documents": documents}},
            },
        }
    ).encode("utf-8")
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    parsed = urllib.parse.urlsplit(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise RuntimeError("GitGuardian ggmcp URL must use http or https")
    connection_type = (
        http.client.HTTPSConnection
        if parsed.scheme == "https"
        else http.client.HTTPConnection
    )
    connection = connection_type(parsed.hostname, parsed.port, timeout=timeout)
    target = urllib.parse.urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
    try:
        connection.request("POST", target, body=payload, headers=headers)
        response = connection.getresponse()
        body = response.read().decode("utf-8")
        if not 200 <= response.status < 300:
            raise RuntimeError(
                f"GitGuardian ggmcp scan failed: HTTP {response.status}"
            )
    except (OSError, http.client.HTTPException) as exc:
        raise RuntimeError(f"GitGuardian ggmcp scan failed: {exc}") from exc
    finally:
        connection.close()

    response = json.loads(body)
    return validate_scan_response(response, expected_count=len(documents))


def extract_scan_results(response: Any) -> list[dict[str, Any]]:
    if isinstance(response, list):
        return [item for item in response if isinstance(item, dict)]
    if not isinstance(response, dict):
        return []
    if isinstance(response.get("scan_results"), list):
        return response["scan_results"]
    if isinstance(response.get("result"), dict):
        return extract_scan_results(response["result"])
    if isinstance(response.get("structuredContent"), dict):
        return extract_scan_results(response["structuredContent"])
    if isinstance(response.get("content"), list):
        for item in response["content"]:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                try:
                    return extract_scan_results(json.loads(item["text"]))
                except json.JSONDecodeError:
                    continue
    return []


def response_has_tool_error(response: Any) -> bool:
    if not isinstance(response, dict):
        return False
    if response.get("isError") is True:
        return True
    if "error" in response and response["error"] is not None:
        return True
    return any(
        response_has_tool_error(response.get(key))
        for key in ("result", "structuredContent")
        if key in response
    )


def validate_scan_response(response: Any, expected_count: int) -> list[dict[str, Any]]:
    if response_has_tool_error(response):
        raise RuntimeError("GitGuardian ggmcp returned a tool error")
    scan_results = extract_scan_results(response)
    if len(scan_results) != expected_count:
        raise RuntimeError(
            "GitGuardian ggmcp returned an incomplete scan response: "
            f"expected {expected_count} results, received {len(scan_results)}"
        )
    for result in scan_results:
        if not isinstance(result, dict):
            raise RuntimeError("GitGuardian ggmcp returned an unrecognized scan result")
        policy_breaks = result.get("policy_breaks")
        if not isinstance(policy_breaks, list) or any(
            not isinstance(policy_break, dict) for policy_break in policy_breaks
        ):
            raise RuntimeError("GitGuardian ggmcp returned an unrecognized scan result")
        if "policy_break_count" in result:
            policy_break_count = result["policy_break_count"]
            if (
                isinstance(policy_break_count, bool)
                or not isinstance(policy_break_count, int)
                or policy_break_count < 0
                or policy_break_count != len(policy_breaks)
            ):
                raise RuntimeError("GitGuardian ggmcp returned an unrecognized scan result")
    return scan_results


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, child in value.items():
            if key.lower() in SECRET_KEYS:
                redacted[key] = "[redacted]"
            else:
                redacted[key] = redact(child)
        return redacted
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def normalize_severity(raw_value: Any) -> str:
    if raw_value is None:
        return "unknown"
    value = str(raw_value).strip().lower()
    return value or "unknown"


def finding_line(match: dict[str, Any]) -> str:
    start = match.get("line_start") or match.get("line")
    end = match.get("line_end") or start
    if start is None:
        return "unknown"
    if end == start or end is None:
        return str(start)
    return f"{start}-{end}"


def format_scan_report(
    documents: list[dict[str, str]],
    scan_results: list[dict[str, Any]],
    skipped: list[dict[str, str]],
    personal_findings: list[dict[str, Any]],
    visibility: str,
    visibility_source: str,
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    for index, result in enumerate(scan_results):
        if index < len(documents):
            filename = documents[index].get("filename", f"document-{index}")
        else:
            filename = f"document-{index}"
        for policy_break in result.get("policy_breaks", []):
            if not isinstance(policy_break, dict):
                continue
            severity = normalize_severity(policy_break.get("severity"))
            critical = severity in {"critical", "high", "unknown"}
            raw_matches = policy_break.get("matches")
            matches: list[Any] = (
                raw_matches if isinstance(raw_matches, list) and raw_matches else [{}]
            )
            for match in matches:
                match_data = match if isinstance(match, dict) else {}
                findings.append(
                    {
                        "file": filename,
                        "detector": policy_break.get("type", "unknown"),
                        "policy": policy_break.get("policy", "unknown"),
                        "line": finding_line(match_data),
                        "severity": severity,
                        "critical": critical,
                        "details": redact(
                            {
                                key: value
                                for key, value in policy_break.items()
                                if key not in {"matches"}
                            }
                        ),
                    }
                )

    critical_count = sum(1 for finding in findings if finding["critical"])
    if not personal_findings:
        personal_disposition = "clear"
    elif visibility == "public":
        personal_disposition = "block"
    else:
        personal_disposition = "warn"
    return {
        "repository_visibility": visibility,
        "repository_visibility_source": visibility_source,
        "personal_information_disposition": personal_disposition,
        "summary": {
            "files_scanned": len(documents),
            "files_skipped": len(skipped),
            "findings": len(findings),
            "critical_findings": critical_count,
            "personal_information_findings": len(personal_findings),
            "personal_information_blocking": personal_disposition == "block",
        },
        "findings": findings,
        "personal_information_findings": personal_findings,
        "skipped": skipped,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Git repository root")
    parser.add_argument("--url", default=os.environ.get("GGMCP_URL", DEFAULT_URL))
    parser.add_argument(
        "--token",
        default=os.environ.get("GITGUARDIAN_PERSONAL_ACCESS_TOKEN")
        or os.environ.get("GGMCP_TOKEN"),
    )
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--dry-run", action="store_true", help="List counts without calling ggmcp")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    documents, skipped = collect_checkout_documents(args.root, max_bytes=args.max_bytes)
    personal_findings = personal_information_findings(documents)
    visibility, visibility_source = repository_visibility(args.root)
    if args.dry_run:
        report = format_scan_report(
            documents,
            [],
            skipped,
            personal_findings,
            visibility,
            visibility_source,
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1 if report["summary"]["personal_information_blocking"] else 0

    scan_results: list[dict[str, Any]] = []
    for batch in chunked(documents, args.batch_size):
        scan_results.extend(call_ggmcp_scan(args.url, args.token, batch, args.timeout))

    report = format_scan_report(
        documents,
        scan_results,
        skipped,
        personal_findings,
        visibility,
        visibility_source,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    if report["personal_information_disposition"] == "block":
        print(
            "PERSONAL INFORMATION: BLOCKED (confirmed public repository)",
            file=sys.stderr,
        )
    elif report["personal_information_disposition"] == "warn":
        print(
            f"PERSONAL INFORMATION: WARNING ({visibility} visibility; non-blocking)",
            file=sys.stderr,
        )
    return 1 if (
        report["summary"]["findings"]
        or report["summary"]["personal_information_blocking"]
    ) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
