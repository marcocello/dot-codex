#!/usr/bin/env python3
"""Read and write the configured Second Brain through the Notion API."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib import error, request

API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2026-03-11"
TOKEN_FILE = Path.home() / ".config" / "codex" / "notion_secondbrain_token"

DATA_SOURCES = {
    "tasks": "<tasks-data-source-id>",
    "deals": "<deals-data-source-id>",
    "ideas": "<ideas-data-source-id>",
}

TABLE_NAMES = {
    "tasks": "SB - Tasks",
    "deals": "SB - Deals",
    "ideas": "SB - Ideas",
}

TITLE_PROPERTIES = {
    "tasks": "Task",
    "deals": "Deal",
    "ideas": "Idea",
}


def require_token() -> str:
    token = file_token()
    if not token:
        raise SystemExit(f"Write the Notion token to {TOKEN_FILE}.")
    return token


def file_token() -> str | None:
    try:
        return TOKEN_FILE.read_text(encoding="utf-8").strip() or None
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise SystemExit(f"Cannot read Notion token file {TOKEN_FILE}: {exc}") from exc


def api_request(method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = None if body is None else json.dumps(body).encode("utf-8")
    req = request.Request(
        f"{API_BASE}{path}",
        data=payload,
        method=method,
        headers={
            "Authorization": f"Bearer {require_token()}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        },
    )
    try:
        with request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        raise SystemExit(f"Notion API error {exc.code}: {detail}") from exc
    except error.URLError as exc:
        raise SystemExit(f"Notion API connection error: {exc.reason}") from exc


def rich_text(value: str | None) -> dict[str, Any]:
    if not value:
        return {"rich_text": []}
    return {"rich_text": [{"type": "text", "text": {"content": value}}]}


def title(value: str) -> dict[str, Any]:
    return {"title": [{"type": "text", "text": {"content": value}}]}


def select(value: str | None) -> dict[str, Any]:
    return {"select": {"name": value}} if value else {"select": None}


def date_prop(value: str | None) -> dict[str, Any]:
    return {"date": {"start": value}} if value else {"date": None}


def url_prop(value: str | None) -> dict[str, Any]:
    return {"url": value or None}


def compact_value(prop: dict[str, Any]) -> Any:
    kind = prop.get("type")
    value = prop.get(kind or "")
    if kind == "title" or kind == "rich_text":
        return "".join(part.get("plain_text", "") for part in value)
    if kind == "select":
        return None if not value else value.get("name")
    if kind == "multi_select":
        return [item.get("name") for item in value]
    if kind == "date":
        return None if not value else value.get("start")
    if kind in {"url", "email", "phone_number", "number", "checkbox"}:
        return value
    if kind == "status":
        return None if not value else value.get("name")
    return value


def compact_page(page: dict[str, Any]) -> dict[str, Any]:
    props = page.get("properties", {})
    values = {name: compact_value(prop) for name, prop in props.items()}
    return {
        "id": page.get("id"),
        "url": page.get("url"),
        "created_time": page.get("created_time"),
        "last_edited_time": page.get("last_edited_time"),
        "properties": values,
    }


def base_properties(args: argparse.Namespace, table: str) -> dict[str, Any]:
    props: dict[str, Any] = {TITLE_PROPERTIES[table]: title(args.title)}
    if table != "deals" and getattr(args, "status", None):
        props["Status"] = select(args.status)
    if table == "deals" and getattr(args, "stage", None):
        props["Stage"] = select(args.stage)
    if table == "ideas" and getattr(args, "source", None):
        props["Source"] = select(args.source)
    if getattr(args, "evidence", None):
        props["Evidence"] = rich_text(args.evidence)
    if getattr(args, "confidence", None):
        props["Confidence"] = select(args.confidence)
    if table in {"tasks", "deals", "ideas"} and getattr(args, "next_step", None):
        props["Next Step"] = rich_text(args.next_step)
    if getattr(args, "source_link", None):
        props["Source Link"] = url_prop(args.source_link)
    return props


def create_page(table: str, properties: dict[str, Any]) -> dict[str, Any]:
    body = {
        "parent": {"type": "data_source_id", "data_source_id": DATA_SOURCES[table]},
        "properties": properties,
    }
    return api_request("POST", "/pages", body)


def build_filter(args: argparse.Namespace) -> dict[str, Any] | None:
    if not args.filter_property:
        return None
    return {
        "property": args.filter_property,
        "select": {"equals": args.filter_value},
    }


def list_rows(args: argparse.Namespace) -> dict[str, Any]:
    body: dict[str, Any] = {"page_size": args.limit}
    row_filter = build_filter(args)
    if row_filter:
        body["filter"] = row_filter
    data = api_request("POST", f"/data_sources/{DATA_SOURCES[args.table]}/query", body)
    if args.raw:
        return data
    return {
        "table": TABLE_NAMES[args.table],
        "count": len(data.get("results", [])),
        "rows": [compact_page(page) for page in data.get("results", [])],
    }


def create_task(args: argparse.Namespace) -> dict[str, Any]:
    props = base_properties(args, "tasks")
    if args.priority:
        props["Priority"] = select(args.priority)
    if args.due:
        props["Due Date"] = date_prop(args.due)
    page = create_page("tasks", props)
    return page if args.raw else compact_page(page)


def create_simple_row(args: argparse.Namespace) -> dict[str, Any]:
    props = base_properties(args, args.table)
    if getattr(args, "next_step_date", None):
        props["Next Step Date"] = date_prop(args.next_step_date)
    page = create_page(args.table, props)
    return page if args.raw else compact_page(page)


def update_page(args: argparse.Namespace) -> dict[str, Any]:
    props: dict[str, Any] = {}
    if args.status:
        props["Status"] = select(args.status)
    if args.next_step:
        props["Next Step"] = rich_text(args.next_step)
    if args.evidence:
        props["Evidence"] = rich_text(args.evidence)
    data = api_request("PATCH", f"/pages/{args.page_id}", {"properties": props})
    return data if args.raw else compact_page(data)


def print_json(data: dict[str, Any]) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def valid_date(value: str) -> str:
    try:
        datetime.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use an ISO date like 2026-06-28.") from exc
    return value


def add_common_create_args(
    parser: argparse.ArgumentParser,
    include_status: bool = True,
    include_source: bool = True,
    include_next_step: bool = True,
) -> None:
    parser.add_argument("--title", required=True)
    if include_status:
        parser.add_argument("--status")
    if include_source:
        parser.add_argument("--source")
    parser.add_argument("--evidence")
    parser.add_argument("--confidence")
    if include_next_step:
        parser.add_argument("--next-step")
    parser.add_argument("--source-link")
    parser.add_argument("--raw", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list", help="List rows from a Second Brain table.")
    list_parser.add_argument("table", choices=sorted(DATA_SOURCES))
    list_parser.add_argument("--limit", type=int, default=25)
    list_parser.add_argument("--filter-property")
    list_parser.add_argument("--filter-value")
    list_parser.add_argument("--raw", action="store_true")
    list_parser.set_defaults(func=list_rows)

    task_parser = sub.add_parser("create-task", help="Create an SB - Tasks row.")
    add_common_create_args(task_parser, include_source=False)
    task_parser.add_argument("--priority")
    task_parser.add_argument("--due", type=valid_date)
    task_parser.set_defaults(status="Active", func=create_task)

    deal_parser = sub.add_parser("create-deal", help="Create an SB - Deals row.")
    add_common_create_args(deal_parser, include_status=False, include_source=False)
    deal_parser.add_argument("--stage")
    deal_parser.add_argument("--next-step-date", type=valid_date)
    deal_parser.set_defaults(table="deals", func=create_simple_row)

    idea_parser = sub.add_parser("create-idea", help="Create an SB - Ideas row.")
    add_common_create_args(idea_parser)
    idea_parser.set_defaults(table="ideas", func=create_simple_row)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    print_json(args.func(args))


if __name__ == "__main__":
    main()
