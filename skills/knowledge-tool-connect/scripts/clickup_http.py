"""Private credential loading and bounded ClickUp HTTP transport."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import stat
from urllib import error, request

API_BASE = "https://api.clickup.com/api/v2"


class APIError(Exception):
    """Safe user-facing error; never includes response bodies or credentials."""


class HTTPStatusError(APIError):
    """A provider HTTP failure with a structured status for outcome checks."""

    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


def segment(value: object) -> str:
    text = str(value)
    if not re.fullmatch(r"[A-Za-z0-9_-]+", text):
        raise APIError("Invalid resource identifier")
    return text


def read_token(source: dict) -> str:
    if sum(key in source and source[key] is not None for key in ("token", "token_env", "token_file")) != 1:
        raise APIError("Choose exactly one inline token, environment variable or private token file")
    if "token" in source:
        token = source["token"]
    elif source.get("token_env"):
        token = os.environ.get(source["token_env"], "")
        if not token:
            raise APIError("Configured token environment variable is missing or empty; set it privately")
    else:
        path = Path(source["token_file"])
        if not path.is_absolute():
            raise APIError("Token file must be an absolute path")
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            with os.fdopen(fd, "r", encoding="utf-8") as stream:
                info = os.fstat(stream.fileno())
                if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                        or info.st_mode & 0o077):
                    raise APIError("Token file must be a regular owner-only file (chmod 600), not a symlink")
                token = stream.read(16385).strip()
        except (OSError, UnicodeError):
            raise APIError("Cannot read the configured private token file; check path and permissions") from None
    if not isinstance(token, str) or not token or token == "[redacted]" or len(token) > 16384 or any(ord(c) < 33 or ord(c) > 126 for c in token):
        raise APIError("Credential is empty or contains invalid header characters")
    return token


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Transport:
    def __init__(self, source: dict):
        token = read_token(source)
        auth_type = source.get("auth_type", "personal")
        if auth_type not in {"personal", "oauth"}:
            raise APIError("Unsupported authentication type")
        self.authorization = ("Bearer " if auth_type == "oauth" else "") + token
        self.opener = request.build_opener(NoRedirect())

    def call(self, method: str, path: str, body: dict | None = None, *,
             version: str = 'v2', response_type: type = dict, allow_empty: bool = False):
        if version not in ('v2', 'v3') or not path.startswith('/') or path.startswith('//'):
            raise APIError('Unsupported API version or path')
        base = API_BASE if version == 'v2' else 'https://api.clickup.com/api/v3'
        payload = None if body is None else json.dumps(body, allow_nan=False).encode("utf-8")
        req = request.Request(base + path, data=payload, method=method,
                              headers={"Authorization": self.authorization,
                                       "Content-Type": "application/json"})
        try:
            with self.opener.open(req, timeout=30) as response:
                status = response.getcode()
                if status is not None and not 200 <= status < 300:
                    raise HTTPStatusError(status, f"ClickUp HTTP {status}; request not verified")
                raw = response.read(32 * 1024 * 1024 + 1)
                if len(raw) > 32 * 1024 * 1024:
                    raise APIError("ClickUp response exceeds the bounded read limit")
                if allow_empty and not raw.strip():
                    return {}
                data = json.loads(raw)
                if not isinstance(data, response_type):
                    raise APIError("Malformed ClickUp response: unexpected JSON shape")
                return data
        except error.HTTPError as exc:
            detail = {401: "authentication failed", 403: "access denied",
                      429: "rate limit reached; wait before retrying"}.get(exc.code, "request rejected")
            raise HTTPStatusError(exc.code, f"ClickUp HTTP {exc.code}: {detail}; no automatic retry") from None
        except (error.URLError, TimeoutError, OSError):
            raise APIError("ClickUp connection failed or timed out; outcome unverified; no automatic retry") from None
        except (ValueError, UnicodeError):
            raise APIError("Malformed ClickUp JSON response; outcome unverified") from None


def object_list(data: dict, key: str) -> list[dict]:
    values = data.get(key)
    if not isinstance(values, list) or any(not isinstance(x, dict) for x in values):
        raise APIError(f"Malformed ClickUp response: expected {key} array")
    return values


def identity(data: dict) -> str:
    value = data.get("id")
    if isinstance(value, bool) or not isinstance(value, (str, int)) or not str(value):
        raise APIError("Malformed ClickUp resource identity")
    return segment(value)
