#!/usr/bin/env python3
"""Add the Highlights child note through an active Zotero connector session."""

import argparse
import json
import re
import urllib.error
import urllib.request
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", required=True, help="Session used for the RIS import")
    parser.add_argument("--target", required=True, help="Zotero tree target, such as C94 or L1")
    parser.add_argument("--note-file", required=True, help="HTML file beginning with Highlights heading")
    parser.add_argument("--tag", action="append", default=[], help="Manual parent tag; repeat as needed")
    parser.add_argument("--base-url", default="http://127.0.0.1:23119")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print metadata without writing")
    parser.add_argument("--yes", action="store_true", help="Confirm the Zotero write")
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.session):
        raise SystemExit("Invalid session ID")
    if not re.fullmatch(r"[CL]\d+", args.target):
        raise SystemExit("Target must look like C94 or L1")

    note = Path(args.note_file).read_text(encoding="utf-8").strip()
    if not note.startswith("<h1>Highlights</h1>"):
        raise SystemExit("Highlights note must begin with <h1>Highlights</h1>")

    payload = {
        "sessionID": args.session,
        "target": args.target,
        "tags": args.tag,
        "note": note,
    }
    summary = {
        "session": args.session,
        "target": args.target,
        "tags": args.tag,
        "note_characters": len(note),
    }
    if args.dry_run:
        print(json.dumps({"dry_run": True, **summary}, ensure_ascii=False))
        return 0
    if not args.yes:
        raise SystemExit("Refusing Zotero write without --yes")

    request = urllib.request.Request(
        args.base_url.rstrip("/") + "/connector/updateSession",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read().decode("utf-8", errors="replace")
            if response.status != 200:
                raise SystemExit(f"Zotero returned HTTP {response.status}: {body}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if "SESSION_NOT_FOUND" in body:
            raise SystemExit("SESSION_NOT_FOUND: stop without re-importing the source")
        raise SystemExit(f"Zotero returned HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Zotero connector unavailable: {exc.reason}") from exc

    print(json.dumps({"status": 200, **summary}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
