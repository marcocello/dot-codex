#!/usr/bin/env python3
"""Bounded Notion operations through one explicitly configured knowledge profile."""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys
import uuid
from urllib import error, request
from urllib.parse import urlparse

from clickup_http import APIError, NoRedirect, read_token
from knowledge_profile import ProfileError, SetupRequired, read_config, resolve, setup_error

KINDS = ("tasks", "deals", "ideas")


def identity(value: object) -> str:
    if not isinstance(value, str):
        raise APIError("Missing Notion UUID")
    try:
        return str(uuid.UUID(value))
    except ValueError:
        raise APIError("Invalid Notion UUID") from None


class Transport:
    def __init__(self, source: dict):
        self.authorization = "Bearer " + read_token(source)
        self.opener = request.build_opener(NoRedirect())

    def call(self, method: str, path: str, body: dict | None = None) -> dict:
        payload = None if body is None else json.dumps(body, allow_nan=False).encode()
        req = request.Request("https://api.notion.com/v1" + path, data=payload, method=method,
                              headers={"Authorization": self.authorization,
                                       "Content-Type": "application/json",
                                       "Notion-Version": "2026-03-11"})
        try:
            with self.opener.open(req, timeout=30) as response:
                status = response.getcode()
                if status is None or not 200 <= status < 300:
                    raise APIError("Notion HTTP request not verified")
                raw = response.read(32 * 1024 * 1024 + 1)
                if len(raw) > 32 * 1024 * 1024:
                    raise APIError("Notion response exceeds bounded read limit")
                data = json.loads(raw)
                if not isinstance(data, dict):
                    raise APIError("Malformed Notion response")
                return data
        except error.HTTPError as exc:
            raise APIError(f"Notion HTTP {exc.code}; request rejected; no automatic retry") from None
        except (error.URLError, TimeoutError, OSError):
            raise APIError("Notion connection failed; outcome unverified; no automatic retry") from None
        except (ValueError, UnicodeError):
            raise APIError("Malformed Notion JSON; outcome unverified") from None


def authenticated(http: Transport) -> dict:
    user = http.call("GET", "/users/me")
    bot = user.get("bot")
    if user.get("type") != "bot" or not isinstance(bot, dict):
        raise APIError("Integration bot identity required; personal user tokens are unsupported")
    return {"account": identity(user.get("id")), "workspace_id": identity(bot.get("workspace_id"))}


def schema(http: Transport, source: str) -> dict:
    data = http.call("GET", "/data_sources/" + source)
    props = data.get("properties")
    if data.get("object") != "data_source" or identity(data.get("id")) != source:
        raise APIError("Notion data-source identity mismatch")
    if (not isinstance(props, dict) or not props
            or any(not isinstance(p, dict) or not isinstance(p.get("type"), str) for p in props.values())):
        raise APIError("Malformed Notion property schema")
    return props


def scoped(page: dict, source: str, expected: str | None = None) -> dict:
    page_id = identity(page.get("id"))
    parent = page.get("parent")
    if (page.get("object") != "page" or not isinstance(parent, dict)
            or parent.get("type") != "data_source_id"
            or identity(parent.get("data_source_id")) != source
            or (expected is not None and page_id != expected)):
        raise APIError("Notion page identity or data-source scope mismatch")
    return page


def list_pages(http: Transport, source: str) -> dict:
    pages, cursors, seen = [], set(), set()
    body = {"page_size": 100}
    for _ in range(100):
        data = http.call("POST", "/data_sources/" + source + "/query", body)
        status = data.get("request_status")
        if (data.get("truncated") or (status is not None
                and (not isinstance(status, dict) or status.get("type") != "complete"))):
            raise APIError("Incomplete Notion query; cannot establish completeness")
        results = data.get("results")
        if (data.get("object") != "list" or not isinstance(results, list)
                or any(not isinstance(p, dict) for p in results)
                or type(data.get("has_more")) is not bool):
            raise APIError("Malformed Notion query pagination")
        for page in results:
            scoped(page, source)
            key = identity(page["id"])
            if key in seen:
                raise APIError("Repeated page in Notion query; completeness unverified")
            seen.add(key)
            pages.append(page)
        if len(pages) >= 10000:
            raise APIError("Notion query limit reached; completeness unverified")
        if not data["has_more"]:
            if data.get("next_cursor") is not None:
                raise APIError("Inconsistent Notion query cursor")
            return {"pages": pages, "complete": True}
        cursor = data.get("next_cursor")
        if not isinstance(cursor, str) or not cursor or cursor in cursors:
            raise APIError("Missing or repeated Notion query cursor")
        cursors.add(cursor)
        body = {"page_size": 100, "start_cursor": cursor}
    raise APIError("Notion pagination limit reached; completeness unverified")


def typed_properties(values: dict, props: dict, creating: bool) -> dict:
    if not isinstance(values, dict) or not values:
        raise APIError("Payload must be a nonempty property-name object")
    title_keys = [key for key, prop in props.items() if prop["type"] == "title"]
    if creating and (len(title_keys) != 1 or title_keys[0] not in values):
        raise APIError("Create requires the existing title property")
    output = {}
    for name, value in values.items():
        if name not in props:
            raise APIError("Unknown property; schema changes are unsupported")
        prop = props[name]
        kind = prop["type"]
        if kind in {"title", "rich_text"}:
            if not isinstance(value, str) or len(value) > 2000:
                raise APIError("Text properties require strings of at most 2000 characters")
            encoded = [] if value == "" else [{"type": "text", "text": {"content": value}}]
        elif kind in {"select", "status"}:
            options = prop.get(kind, {}).get("options")
            if (not isinstance(options, list) or any(not isinstance(o, dict) or not isinstance(o.get("name"), str) for o in options)
                    or (value is not None and (not isinstance(value, str) or value not in [o["name"] for o in options]))):
                raise APIError("Select/status requires an existing option name or null")
            encoded = None if value is None else {"name": value}
        elif kind == "checkbox":
            if type(value) is not bool:
                raise APIError("Checkbox requires a boolean")
            encoded = value
        elif kind == "number":
            if value is not None and (type(value) not in {int, float} or not math.isfinite(value)):
                raise APIError("Number requires a finite number or null")
            encoded = value
        elif kind == "url":
            if value is not None and (not isinstance(value, str) or urlparse(value).scheme not in {"http", "https"} or not urlparse(value).netloc):
                raise APIError("URL requires HTTP(S) or null")
            encoded = value
        else:
            raise APIError("Unsupported property type; no mutation performed")
        output[name] = {kind: encoded}
    return output


def verify_values(page: dict, requested: dict, props: dict) -> None:
    actual = page.get("properties")
    if not isinstance(actual, dict):
        raise APIError("Read-back properties missing")
    for name, value in requested.items():
        prop = actual.get(name)
        kind = props[name]["type"]
        if not isinstance(prop, dict) or prop.get("type", kind) != kind or kind not in prop:
            raise APIError("Requested property missing from read-back")
        returned = prop[kind]
        if kind in {"title", "rich_text"}:
            if not isinstance(returned, list):
                raise APIError("Malformed read-back text")
            chunks = []
            for item in returned:
                if not isinstance(item, dict) or item.get("type", "text") != "text":
                    raise APIError("Unsupported read-back text")
                text_obj = item.get("text")
                text = text_obj.get("content") if isinstance(text_obj, dict) else None
                if not isinstance(text, str):
                    raise APIError("Malformed read-back text")
                chunks.append(text)
            returned = "".join(chunks)
        elif kind in {"select", "status"} and returned is not None:
            if not isinstance(returned, dict) or not isinstance(returned.get("name"), str):
                raise APIError("Malformed read-back option")
            returned = returned.get("name")
        if (returned != value or (kind == "checkbox" and type(returned) is not bool)
                or (kind == "number" and returned is not None and type(returned) not in {int, float})):
            raise APIError("Read-back values do not match requested values")


def write_page(http: Transport, source: str, props: dict, args) -> dict:
    try:
        values = json.loads(args.data_file.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        raise APIError("Cannot read valid JSON payload file") from None
    typed = typed_properties(values, props, args.command == "create")
    page_id = None
    if args.command == "update":
        page_id = identity(args.page_id)
        scoped(http.call("GET", "/pages/" + page_id), source, page_id)
    try:
        if page_id is None:
            response = http.call("POST", "/pages", {"parent": {"type": "data_source_id", "data_source_id": source}, "properties": typed})
            page_id = identity(response.get("id"))
        else:
            response = http.call("PATCH", "/pages/" + page_id, {"properties": typed})
        scoped(response, source, page_id)
        page = scoped(http.call("GET", "/pages/" + page_id), source, page_id)
        verify_values(page, values, props)
        return {"page": page, "verified": True}
    except APIError as exc:
        suffix = f"; page ID {page_id}" if page_id else "; page ID unknown"
        raise APIError(str(exc) + suffix + "; write unverified; do not retry automatically") from None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    home = Path(os.environ.get("CODEX_HOME") or str(Path.home() / ".codex"))
    parser.add_argument("--config", type=Path, default=home / "knowledge.toml")
    parser.add_argument("--profile")
    parser.add_argument("--transport", choices=("api",), help="Use API for this invocation without changing preference")
    commands = parser.add_subparsers(dest="command", required=True)
    discover = commands.add_parser("discover")
    credentials = discover.add_mutually_exclusive_group(required=True)
    credentials.add_argument("--token-env")
    credentials.add_argument("--token-file")
    commands.add_parser("check")
    for command in ("fields", "list", "get", "create", "update"):
        sub = commands.add_parser(command)
        sub.add_argument("kind", metavar="DESTINATION", help="Explicit data-source UUID or configured legacy alias")
        if command in {"get", "update"}:
            sub.add_argument("page_id")
        if command in {"create", "update"}:
            sub.add_argument("--data-file", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "discover":
            result = authenticated(Transport(vars(args)))
        else:
            profile = resolve(read_config(args.config), args.profile, args.transport)
            if profile["provider"] != "notion" or profile.get("transport", "mcp") != "api":
                raise APIError("Selected profile is not a Notion API profile; no transport fallback")
            sources = {kind: identity(profile[kind]) for kind in KINDS if kind in profile}
            if args.command != "check":
                if args.kind in KINDS and args.kind not in profile:
                    raise APIError("Destination alias is not configured; supply an explicit data-source UUID")
                source = identity(profile[args.kind] if args.kind in KINDS else args.kind)
            http = Transport(profile)
            auth = authenticated(http)
            if any(auth[key] != identity(profile[key]) for key in ("account", "workspace_id")):
                raise APIError("Authenticated Notion account or workspace mismatch")
            if args.command == "check":
                result = {"verified": True, "sources": {kind: schema(http, source) for kind, source in sources.items()}}
            else:
                props = schema(http, source)
                if args.command == "fields":
                    result = {"properties": props}
                elif args.command == "list":
                    result = list_pages(http, source)
                elif args.command == "get":
                    page_id = identity(args.page_id)
                    result = {"page": scoped(http.call("GET", "/pages/" + page_id), source, page_id), "verified": True}
                else:
                    result = write_page(http, source, props, args)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except SetupRequired as exc:
        return setup_error(str(exc))
    except (APIError, ProfileError) as exc:
        print(f"notion_api: {exc}", file=sys.stderr)
        return 2
    except (OSError, ValueError, TypeError, AttributeError, OverflowError):
        print("notion_api: invalid local data or malformed response; outcome unverified; no automatic retry", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
