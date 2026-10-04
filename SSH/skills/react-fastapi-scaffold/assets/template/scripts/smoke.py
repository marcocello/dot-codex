#!/usr/bin/env python3
"""Check a disposable running starter through its public HTTP endpoint."""
import argparse
import json
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", nargs="?", default="http://127.0.0.1:8080")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    def request(path: str, data: dict | None = None) -> tuple[int, bytes]:
        req = Request(base + path, data=json.dumps(data).encode() if data is not None else None,
                      headers={"Content-Type": "application/json"})
        try:
            with urlopen(req, timeout=15) as response:
                return response.status, response.read()
        except HTTPError as error:
            return error.code, error.read()

    status, body = request("/")
    assert status == 200 and b'id="root"' in body, "frontend is unavailable"
    for path in ("/api/health", "/api/ready"):
        assert request(path)[0] == 200, f"{path} is unavailable"
    text = f"Smoke check {uuid.uuid4()}"
    status, body = request("/api/notes", {"text": text})
    assert status == 201, f"create failed: {status}"
    saved = json.loads(body)
    assert saved["text"] == text
    status, body = request("/api/notes")
    assert status == 200 and saved in json.loads(body), "saved note was not read back"
    for invalid in ("   ", "x" * 501):
        assert request("/api/notes", {"text": invalid})[0] == 422, "invalid note accepted"
    assert request("/api/does-not-exist")[0] == 404, "API fallback incorrectly served the SPA"
    print("PASS: frontend, readiness, save/read-back, validation, and API routing")


if __name__ == "__main__":
    main()
