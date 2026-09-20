#!/usr/bin/env python3
"""Use ClickUp directly through one explicitly configured knowledge profile."""
from __future__ import annotations

import argparse
import clickup_docs
from decimal import Decimal, InvalidOperation
import json
import math
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlencode, urlparse

from clickup_http import APIError, HTTPStatusError, Transport, identity, object_list, segment
from knowledge_profile import ProfileError, SetupRequired, read_config, resolve, setup_error

KINDS = ("tasks", "deals", "ideas")


def numeric_id(value: str) -> str:
    if not re.fullmatch(r"[0-9]+", value):
        raise APIError("Workspace identity must be a numeric ClickUp ID")
    return value


def user_identity(http: Transport) -> dict:
    user = http.call("GET", "/user").get("user")
    if not isinstance(user, dict):
        raise APIError("Malformed authenticated user response")
    identity(user)
    return user


def workspaces(http: Transport) -> list[dict]:
    teams = object_list(http.call("GET", "/team"), "teams")
    for team in teams:
        identity(team)
    return teams


def spaces(http: Transport, workspace: str, *, archived: bool = False) -> list[dict]:
    result = object_list(http.call("GET", f"/team/{segment(workspace)}/space?archived={str(archived).lower()}"), "spaces")
    for item in result:
        identity(item)
    return result


def discover(args) -> dict:
    source = {key: getattr(args, key) for key in ("token_env", "token_file", "auth_type")}
    http = Transport(source)
    user = user_identity(http)
    teams = workspaces(http)
    result = {"account": identity(user), "user": {k: user.get(k) for k in ("id", "username", "email")},
              "workspaces": [{"id": identity(t), "name": t.get("name")} for t in teams]}
    if args.workspace_id:
        workspace = numeric_id(args.workspace_id)
        if workspace not in {identity(t) for t in teams}:
            raise APIError("Selected workspace is not authorized for this credential")
        result["workspace_id"] = workspace
        result["spaces"] = []
        for space in spaces(http, workspace):
            sid = identity(space)
            lists = object_list(http.call("GET", f"/space/{sid}/list?archived=false"), "lists")
            folders = object_list(http.call("GET", f"/space/{sid}/folder?archived=false"), "folders")
            for folder in folders:
                lists.extend(object_list(http.call("GET", f"/folder/{identity(folder)}/list?archived=false"), "lists"))
            result["spaces"].append({"id": sid, "name": space.get("name"),
                                     "lists": [{"id": identity(x), "name": x.get("name")} for x in lists]})
    return result


class Client:
    def __init__(self, profile: dict, target: str | None = None, *, docs: bool = False):
        if profile["provider"] != "clickup" or profile.get("transport", "mcp") != "api":
            raise APIError("Selected profile is not ClickUp API; explicitly configure its transport first")
        self.profile = dict(profile)
        if docs:
            destinations = {}
        elif target is None:
            destinations = {key: profile[key] for key in KINDS if key in profile}
        else:
            if target in KINDS and target not in profile:
                raise APIError("Destination alias is not configured; supply an explicit list ID")
            value = profile.get(target) if target in KINDS else target
            if not re.fullmatch(r"[0-9]+", value):
                raise APIError("Destination must be a numeric ClickUp list ID")
            destinations = {target: value}
            self.profile[target] = value
        self.http = Transport(profile)
        user = user_identity(self.http)
        if identity(user) != profile["account"]:
            raise APIError("Authenticated account mismatch; no workspace content accessed")
        workspace = profile["workspace_id"]
        if workspace not in {identity(t) for t in workspaces(self.http)}:
            raise APIError("Configured workspace is not authorized for this account")
        self.lists = {}
        if not destinations:
            return
        allowed = {identity(s) for archived in (False, True) for s in spaces(self.http, workspace, archived=archived)}
        for kind, lid in destinations.items():
            meta = self.http.call("GET", f"/list/{segment(lid)}")
            if identity(meta) != lid or str(meta.get("space", {}).get("id")) not in allowed:
                raise APIError("Configured list does not belong to the selected workspace")
            self.lists[kind] = meta

    def context(self) -> dict:
        return {"profile": self.profile["profile"], "account": self.profile["account"],
                "workspace_id": self.profile["workspace_id"]}

    def fields(self, kind: str) -> list[dict]:
        return object_list(self.http.call("GET", f'/list/{self.profile[kind]}/field'), "fields")

    def get(self, kind: str, task_id: str) -> dict:
        task = self.http.call("GET", f"/task/{segment(task_id)}?include_markdown_description=true")
        if (identity(task) != task_id or str(task.get("team_id")) != self.profile["workspace_id"]
                or str(task.get("list", {}).get("id")) != self.profile[kind]):
            raise APIError("Task identity/workspace/home list does not match the selected destination")
        return task

    def list_tasks(self, kind: str) -> dict:
        by_id = {}
        for archived in (False, True):
            seen = set()
            for page in range(1000):
                query = urlencode({"archived": str(archived).lower(), "page": page,
                                   "include_closed": "true", "subtasks": "true", "include_timl": "true",
                                   "include_markdown_description": "true"})
                data = self.http.call("GET", f'/list/{self.profile[kind]}/task?{query}')
                tasks = object_list(data, "tasks")
                ids = tuple(identity(t) for t in tasks)
                if ids in seen:
                    raise APIError("Repeated task page; complete coverage cannot be established")
                seen.add(ids)
                for task in tasks:
                    if str(task.get("team_id")) != self.profile["workspace_id"]:
                        raise APIError("Task page contains a foreign or unknown workspace")
                    by_id[identity(task)] = task
                last = data.get("last_page")
                if last is not None and not isinstance(last, bool):
                    raise APIError("Malformed pagination marker")
                if last is True or (last is None and not tasks):
                    break
            else:
                raise APIError("Task pagination limit reached; results are incomplete")
        return {**self.context(), "complete": True, "tasks": list(by_id.values()),
                "coverage": "accessible tasks in configured list; includes closed, archived, subtasks and multi-list tasks"}

    def mutate(self, kind: str, body: dict, task_id: str | None = None) -> dict:
        validate_payload(body, self.lists[kind], create=task_id is None)
        if task_id is not None:
            self.get(kind, task_id)
        known = task_id
        try:
            if task_id is None:
                created = self.http.call("POST", f'/list/{self.profile[kind]}/task',
                                         {**body, "check_required_custom_fields": True})
                known = identity(created)
            else:
                self.http.call("PUT", f"/task/{segment(task_id)}", body)
            task = self.get(kind, known)
            for key, expected in body.items():
                actual = task.get(key)
                if key == "status" and isinstance(actual, dict):
                    actual = actual.get("status")
                if key == "priority" and isinstance(actual, dict):
                    actual = actual.get("id")
                if key == "markdown_content":
                    actual = task.get("markdown_description", task.get("markdown_content"))
                if not equivalent(actual, expected):
                    raise APIError(f"Read-back did not verify requested field {key}")
            return {**self.context(), "verified": True, "task": task}
        except (APIError, KeyError, TypeError, AttributeError, ValueError) as exc:
            label = f" task {known}" if known else " new task (identity unknown)"
            detail = str(exc) if isinstance(exc, APIError) else "Malformed write response"
            raise APIError(f"Write unverified for{label}: {detail}. Inspect existing state before retrying; not retried") from None

    def delete(self, kind: str, task_id: str) -> dict:
        # Preflight absence is not a successful deletion. Verify the home list
        # as well as workspace: removal from an additional list is another action.
        self.get(kind, task_id)
        path = f"/task/{segment(task_id)}"
        try:
            self.http.call("DELETE", path, allow_empty=True)
            try:
                self.http.call("GET", path)
            except HTTPStatusError as exc:
                if exc.status != 404:
                    raise
                return {**self.context(), "task_id": task_id, "deleted": True,
                        "verified": True,
                        "verification": "DELETE succeeded; subsequent GET returned HTTP 404"}
            raise APIError("Task remains readable after DELETE")
        except APIError as exc:
            raise APIError(f"Deletion unverified for task {task_id}: {exc}. Inspect before retrying; not retried") from None

    def set_field(self, kind: str, task_id: str, field_id: str, value) -> dict:
        segment(field_id)
        task = self.get(kind, task_id)
        field = next((f for f in self.fields(kind) if f.get("id") == field_id), None)
        if field is None:
            raise APIError("Custom field is not defined on the selected list")
        applicable = object_list(task, "custom_fields")
        if field_id not in {f.get("id") for f in applicable}:
            raise APIError("Custom field applicability to this task cannot be established")
        validate_field(field, value)
        try:
            self.http.call("POST", f"/task/{segment(task_id)}/field/{segment(field_id)}", {"value": value})
            result = self.get(kind, task_id)
            returned = next((f for f in object_list(result, "custom_fields") if f.get("id") == field_id), {})
            actual = returned.get("value")
            if field["type"] == "drop_down" and actual != value:
                option = next(o for o in field["type_config"]["options"] if o["id"] == value)
                if option.get("orderindex") is not None and equivalent(actual, numeric_option(option["orderindex"])):
                    actual = value
            if not equivalent(actual, value):
                raise APIError("Custom-field read-back differs from requested value")
            return {**self.context(), "verified": True, "task": result}
        except (APIError, KeyError, TypeError, AttributeError, ValueError) as exc:
            detail = str(exc) if isinstance(exc, APIError) else "Malformed write response"
            raise APIError(f"Write unverified for task {task_id}: {detail}. Inspect before retrying; not retried") from None


def numeric_option(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        raise APIError("Malformed dropdown option order") from None


def equivalent(actual, expected) -> bool:
    if type(expected) in (int, float):
        try:
            return not isinstance(actual, bool) and Decimal(str(actual)) == Decimal(str(expected))
        except InvalidOperation:
            return False
    return type(actual) is type(expected) and actual == expected


def validate_payload(body, meta: dict, *, create: bool) -> None:
    allowed = {"name", "description", "markdown_content", "status", "priority", "due_date", "due_date_time"}
    if not isinstance(body, dict) or not body or set(body) - allowed:
        raise APIError("Payload must be a nonempty object of supported task fields; use set-field for custom fields")
    if create and (not isinstance(body.get("name"), str) or not body["name"].strip()):
        raise APIError("Create requires a nonempty name")
    if "description" in body and "markdown_content" in body:
        raise APIError("Choose description or markdown_content, not both")
    for key in {"name", "description", "markdown_content", "status"} & set(body):
        if not isinstance(body[key], str) or (key in {"name", "status"} and not body[key].strip()):
            raise APIError(f"{key} must be a valid string")
    if "priority" in body and body["priority"] is not None:
        if type(body["priority"]) is not int or body["priority"] not in {1, 2, 3, 4}:
            raise APIError("priority must be 1–4 or null")
    if "due_date" in body and body["due_date"] is not None:
        if type(body["due_date"]) is not int or body["due_date"] < 0:
            raise APIError("due_date must be epoch milliseconds or null")
    if "due_date_time" in body and type(body["due_date_time"]) is not bool:
        raise APIError("due_date_time must be boolean")
    if "status" in body:
        statuses = object_list(meta, "statuses")
        if body["status"] not in {s.get("status") for s in statuses}:
            raise APIError("Status does not match the selected list schema")


def validate_field(field: dict, value) -> None:
    kind = field.get("type")
    if kind in {"short_text", "text", "url", "email", "phone"}:
        if not isinstance(value, str):
            raise APIError("Custom field requires a string")
        if kind == "url" and (urlparse(value).scheme not in {"http", "https"} or not urlparse(value).netloc):
            raise APIError("Custom URL field requires an HTTP(S) URL")
        if kind == "email" and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise APIError("Custom email field requires an email address")
        if kind == "phone" and not re.fullmatch(r"\+[0-9 ()-]+", value):
            raise APIError("Custom phone field requires a number with country code")
    elif kind in {"number", "currency"}:
        if type(value) not in {int, float} or not math.isfinite(value):
            raise APIError("Custom numeric field requires a finite number")
    elif kind == "checkbox":
        if type(value) is not bool:
            raise APIError("Custom checkbox requires a boolean")
    elif kind == "drop_down":
        options = object_list(field.get("type_config", {}), "options")
        if not isinstance(value, str) or value not in {o.get("id") for o in options}:
            raise APIError("Custom dropdown requires an existing option ID")
    else:
        raise APIError("Unsupported custom-field type; no mutation performed")


def reject_constant(value: str):
    raise ValueError("Non-finite JSON number")


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)
    except (OSError, UnicodeError, ValueError):
        raise APIError("Cannot read a valid JSON input file") from None


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    home = Path(os.environ.get("CODEX_HOME") or str(Path.home() / ".codex")).expanduser()
    result.add_argument("--config", type=Path, default=home / "knowledge.toml")
    result.add_argument("--profile")
    result.add_argument("--transport", choices=("api",), help="Use API for this invocation without changing preference")
    commands = result.add_subparsers(dest="command", required=True)
    discovery = commands.add_parser("discover", help="Discover identity/workspaces for an explicitly supplied credential reference")
    credentials = discovery.add_mutually_exclusive_group(required=True)
    credentials.add_argument("--token-env")
    credentials.add_argument("--token-file")
    discovery.add_argument("--auth-type", choices=("personal", "oauth"), default="personal")
    discovery.add_argument("--workspace-id")
    commands.add_parser("check")
    for name in ("fields", "list", "get", "create", "update", "set-field", "delete"):
        command = commands.add_parser(name)
        command.add_argument("kind", metavar="DESTINATION", help="Explicit list ID or configured legacy alias")
        if name in {"get", "update", "set-field", "delete"}:
            command.add_argument("task_id")
        if name in {"create", "update"}:
            command.add_argument("--data-file", type=Path, required=True)
        if name == "set-field":
            command.add_argument("--field-id", required=True)
            command.add_argument("--value-file", type=Path, required=True)
    clickup_docs.add_commands(commands)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "discover":
            output = discover(args)
        else:
            profile = resolve(read_config(args.config), args.profile, args.transport)
            is_docs = args.command.startswith(('doc-', 'docs-', 'page-', 'pages-'))
            client = Client(profile, getattr(args, "kind", None), docs=is_docs)
            if is_docs:
                output = clickup_docs.execute(client, args, read_json)
            elif args.command == "check":
                output = {**client.context(), "verified": True, "lists": {k: profile[k] for k in KINDS if k in profile}}
            elif args.command == "fields":
                output = {**client.context(), "list": client.lists[args.kind], "fields": client.fields(args.kind)}
            elif args.command == "list":
                output = client.list_tasks(args.kind)
            elif args.command == "get":
                output = {**client.context(), "verified": True, "task": client.get(args.kind, args.task_id)}
            elif args.command == "delete":
                output = client.delete(args.kind, args.task_id)
            elif args.command in {"create", "update"}:
                output = client.mutate(args.kind, read_json(args.data_file), getattr(args, "task_id", None))
            else:
                output = client.set_field(args.kind, args.task_id, args.field_id, read_json(args.value_file))
        print(json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except SetupRequired as exc:
        return setup_error(str(exc))
    except (APIError, ProfileError) as exc:
        print(f"clickup_api: {exc}", file=sys.stderr)
        return 2
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, AttributeError):
        print("clickup_api: invalid local input or malformed provider response; no verified outcome", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
