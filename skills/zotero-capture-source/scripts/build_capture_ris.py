#!/usr/bin/env python3
"""Build one Zotero-ready RIS record from a source-capture JSON specification."""

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse


RIS_TYPES = {"video": "VIDEO", "article": "ELEC"}
NOTE_TITLES = {"video": "Raw_Transcript", "article": "Source_Outline"}


def one_line(value: str) -> str:
    return re.sub(r"\s*\n\s*", " ", value.replace("\r", "\n")).strip()


def ris_date(value: str) -> str:
    value = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return value.replace("-", "/") + "/"
    if re.fullmatch(r"\d{4}-\d{2}", value):
        return value.replace("-", "/") + "//"
    if re.fullmatch(r"\d{4}", value):
        return value
    raise ValueError("date must be YYYY, YYYY-MM, or YYYY-MM-DD")


def require_text(spec: dict, field: str) -> str:
    value = spec.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return one_line(value)


def build_ris(spec: dict) -> str:
    source_type = spec.get("source_type")
    if source_type not in RIS_TYPES:
        raise ValueError("source_type must be 'video' or 'article'")

    title = require_text(spec, "title")
    url = require_text(spec, "url")
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("url must be an absolute HTTP(S) URL")

    source_note = require_text(spec, "source_note_html")
    expected_heading = f"<h1>{NOTE_TITLES[source_type]}</h1>"
    if not source_note.startswith(expected_heading):
        raise ValueError(f"source_note_html must begin with {expected_heading}")

    authors = spec.get("authors", [])
    tags = spec.get("tags", [])
    if not isinstance(authors, list) or not all(isinstance(x, str) and x.strip() for x in authors):
        raise ValueError("authors must be a list of non-empty strings")
    if not isinstance(tags, list) or not all(isinstance(x, str) and x.strip() for x in tags):
        raise ValueError("tags must be a list of non-empty strings")

    lines = [f"TY  - {RIS_TYPES[source_type]}", f"TI  - {title}"]
    lines.extend(f"AU  - {one_line(author)}" for author in authors)
    if spec.get("date"):
        lines.append(f"DA  - {ris_date(str(spec['date']))}")
    if spec.get("publisher"):
        lines.append(f"PB  - {one_line(str(spec['publisher']))}")
    lines.append(f"UR  - {url}")
    lines.extend(f"KW  - {one_line(tag)}" for tag in tags)
    lines.extend([f"N1  - {source_note}", "ER  -", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Capture JSON shape:
{
  "source_type": "video" | "article",
  "title": "Source title",
  "url": "https://canonical.example/source",
  "authors": ["Creator One", "Creator Two"],
  "date": "YYYY-MM-DD",
  "publisher": "Channel or publication",
  "tags": ["topic tag"],
  "source_note_html": "<h1>Raw_Transcript</h1>..."
}

For an article, source_note_html must begin with Source_Outline instead.
""",
    )
    parser.add_argument("--spec", required=True, help="Capture JSON specification")
    parser.add_argument("--out", required=True, help="Destination RIS path")
    args = parser.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    output = build_ris(spec)
    destination = Path(args.out)
    destination.write_text(output, encoding="utf-8")
    print(json.dumps({"out": str(destination.resolve()), "bytes": len(output.encode("utf-8"))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
