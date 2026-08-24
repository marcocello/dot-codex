#!/usr/bin/env python3
"""Capture completed, human-visible Codex dialogue into project-owned JSON."""

from __future__ import annotations

import argparse
import json
import os
import re
import select
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
APP_SERVER_TIMEOUT_SECONDS = 20
TASK_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,199}")
SECRET_PATTERNS = (
    (
        "github_token",
        re.compile(r"(?<![A-Za-z0-9])gh[pousr]_[A-Za-z0-9]{36,255}"),
    ),
    (
        "openai_api_key",
        re.compile(r"(?<![A-Za-z0-9])sk-(?:proj-)?[A-Za-z0-9_-]{20,255}"),
    ),
    (
        "aws_access_key",
        re.compile(r"(?<![A-Z0-9])(?:AKIA|ASIA)[A-Z0-9]{16}(?![A-Z0-9])"),
    ),
    (
        "private_key",
        re.compile(
            r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----.*?"
            r"-----END (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
            re.DOTALL,
        ),
    ),
)


@dataclass(frozen=True)
class ParsedSession:
    task_id: str
    project_root: Path
    record: dict[str, Any]
    event_count: int


@dataclass(frozen=True)
class SourceIssue:
    path: Path
    message: str
    task_id: str | None = None
    project_root: Path | None = None


def normalize_path(path: Path | str) -> Path:
    return Path(path).expanduser().resolve(strict=False)


def redact_text(text: str, counts: Counter[str]) -> str:
    redacted = text
    for secret_type, pattern in SECRET_PATTERNS:
        redacted, replacements = pattern.subn(f"[REDACTED:{secret_type}]", redacted)
        if replacements:
            counts[secret_type] += replacements
    return redacted


def attachment_metadata(
    payload: dict[str, Any], counts: Counter[str]
) -> list[dict[str, str]]:
    attachments: list[dict[str, str]] = []
    for key in ("images", "local_images"):
        values = payload.get(key)
        if not isinstance(values, list):
            continue
        for value in values:
            item: dict[str, str] = {"kind": "image"}
            if isinstance(value, str):
                item["name"] = redact_text(Path(value).name, counts)
            elif isinstance(value, dict):
                for source_key, target_key in (
                    ("name", "name"),
                    ("filename", "name"),
                    ("mime_type", "mime_type"),
                    ("type", "source_type"),
                ):
                    source_value = value.get(source_key)
                    if isinstance(source_value, str) and target_key not in item:
                        item[target_key] = redact_text(source_value, counts)
            attachments.append(item)
    return attachments


def dialogue_message(payload: dict[str, Any], counts: Counter[str]) -> dict[str, Any] | None:
    event_type = payload.get("type")
    text = payload.get("message")
    if event_type not in {"user_message", "agent_message"} or not isinstance(text, str):
        return None
    message: dict[str, Any] = {
        "role": "user" if event_type == "user_message" else "assistant",
        "text": redact_text(text, counts),
    }
    if event_type == "agent_message":
        phase = payload.get("phase")
        if isinstance(phase, str):
            message["phase"] = phase
    else:
        attachments = attachment_metadata(payload, counts)
        if attachments:
            message["attachments"] = attachments
    return message


def load_jsonl(path: Path) -> tuple[list[dict[str, Any]], SourceIssue | None]:
    values: list[dict[str, Any]] = []
    task_id: str | None = None
    project_root: Path | None = None
    try:
        with path.open("r", encoding="utf-8") as source:
            for line_number, line in enumerate(source, start=1):
                try:
                    value = json.loads(line)
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    return values, SourceIssue(
                        path,
                        f"unsupported JSONL at line {line_number}: {exc}",
                        task_id,
                        project_root,
                    )
                if not isinstance(value, dict):
                    return values, SourceIssue(
                        path,
                        f"unsupported non-object event at line {line_number}",
                        task_id,
                        project_root,
                    )
                values.append(value)
                if value.get("type") == "session_meta" and isinstance(value.get("payload"), dict):
                    meta = value["payload"]
                    identity = meta.get("id") or meta.get("session_id")
                    cwd = meta.get("cwd")
                    if isinstance(identity, str):
                        task_id = identity
                    if isinstance(cwd, str):
                        project_root = normalize_path(cwd)
    except (OSError, UnicodeDecodeError) as exc:
        return values, SourceIssue(path, f"cannot read source: {exc}", task_id, project_root)
    return values, None


def session_metadata(values: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, str | None]:
    for value in values:
        if value.get("type") != "session_meta" or not isinstance(value.get("payload"), dict):
            continue
        payload = value["payload"]
        task_id = payload.get("id") or payload.get("session_id")
        cwd = payload.get("cwd")
        if not isinstance(task_id, str) or not TASK_ID_PATTERN.fullmatch(task_id):
            return None, "session metadata has an unsafe or missing task identity"
        if not isinstance(cwd, str):
            return None, "session metadata has no workspace path"
        return payload, None
    return None, "session metadata is missing"


def parse_turns(values: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str], Counter[str]]:
    turns: list[dict[str, Any]] = []
    incomplete_ids: list[str] = []
    active: dict[str, Any] | None = None
    redactions: Counter[str] = Counter()
    sequence = 0
    for value in values:
        payload = value.get("payload")
        if value.get("type") != "event_msg" or not isinstance(payload, dict):
            continue
        event_type = payload.get("type")
        if event_type == "task_started":
            if active is not None:
                incomplete_ids.append(active["id"])
            sequence += 1
            turn_id = payload.get("turn_id")
            active = {
                "id": turn_id if isinstance(turn_id, str) else f"turn-{sequence}",
                "status": "complete",
                "messages": [],
            }
            continue
        if active is None:
            continue
        message = dialogue_message(payload, redactions)
        if message is not None:
            active["messages"].append(message)
        if event_type == "task_complete":
            turns.append(active)
            active = None
    if active is not None:
        incomplete_ids.append(active["id"])
    return turns, incomplete_ids, redactions


def build_record(values: list[dict[str, Any]], source_path: Path) -> tuple[ParsedSession | None, SourceIssue | None]:
    metadata, error = session_metadata(values)
    if metadata is None:
        return None, SourceIssue(source_path, error or "invalid metadata")
    task_id = str(metadata.get("id") or metadata["session_id"])
    project_root = normalize_path(str(metadata["cwd"]))
    turns, incomplete_ids, redactions = parse_turns(values)
    started_at = next(
        (value.get("timestamp") for value in values if value.get("type") == "session_meta"),
        None,
    )
    task: dict[str, Any] = {"id": task_id, "workspace": "."}
    if isinstance(metadata.get("originator"), str):
        task["originator"] = metadata["originator"]
    if isinstance(started_at, str):
        task["started_at"] = started_at
    capture: dict[str, Any] = {
        "state": "partial" if incomplete_ids else "complete",
        "completed_through_turn_id": turns[-1]["id"] if turns else None,
        "incomplete_turn_ids": incomplete_ids,
        "redactions": [
            {"type": secret_type, "count": redactions[secret_type]}
            for secret_type in sorted(redactions)
            if redactions[secret_type]
        ],
    }
    record = {
        "schema_version": SCHEMA_VERSION,
        "task": task,
        "capture": capture,
        "turns": turns,
    }
    return ParsedSession(task_id, project_root, record, len(values)), None


def parse_source(path: Path) -> tuple[ParsedSession | None, SourceIssue | None]:
    values, issue = load_jsonl(path)
    if issue is not None:
        return None, issue
    return build_record(values, path)


def render_json(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def atomic_write(path: Path, content: bytes) -> bool:
    if path.is_file() and path.read_bytes() == content:
        return False
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("wb") as destination:
            destination.write(content)
            destination.flush()
            os.fsync(destination.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    return True


def load_existing_index(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"existing interaction index is unreadable: {exc}") from exc
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION:
        raise RuntimeError("existing interaction index has an unsupported schema")
    records = value.get("records")
    if not isinstance(records, list):
        raise RuntimeError("existing interaction index has no records list")
    existing: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("task_id"), str):
            raise RuntimeError("existing interaction index contains an invalid record")
        existing[record["task_id"]] = record
    return existing


class CaptureLock:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.fd: int | None = None

    def __enter__(self) -> "CaptureLock":
        try:
            self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise RuntimeError("another capture is in progress (interaction store is locked)") from exc
        os.write(self.fd, f"pid={os.getpid()}\n".encode())
        return self

    def __exit__(self, _type: object, _value: object, _traceback: object) -> None:
        if self.fd is not None:
            os.close(self.fd)
        self.path.unlink(missing_ok=True)


class AppServerClient:
    def __init__(self, codex_bin: str) -> None:
        self.codex_bin = codex_bin
        self.process: subprocess.Popen[str] | None = None
        self.request_id = 0

    def __enter__(self) -> "AppServerClient":
        try:
            self.process = subprocess.Popen(
                [self.codex_bin, "app-server", "--stdio"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
        except OSError as exc:
            raise RuntimeError(f"cannot start Codex app server: {exc}") from exc
        self.request(
            "initialize",
            {"clientInfo": {"name": "capture-interactions", "version": "1"}},
        )
        self.notify("initialized")
        return self

    def __exit__(self, _type: object, _value: object, _traceback: object) -> None:
        if self.process is None:
            return
        if self.process.stdin is not None:
            self.process.stdin.close()
        try:
            self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=2)

    def send(self, payload: dict[str, Any]) -> None:
        if self.process is None or self.process.stdin is None:
            raise RuntimeError("Codex app server is not running")
        try:
            self.process.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise RuntimeError(f"cannot write to Codex app server: {exc}") from exc

    def notify(self, method: str) -> None:
        self.send({"method": method})

    def request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self.request_id += 1
        request_id = self.request_id
        self.send({"id": request_id, "method": method, "params": params})
        return self.read_response(request_id)

    def read_response(self, request_id: int) -> dict[str, Any]:
        if self.process is None or self.process.stdout is None:
            raise RuntimeError("Codex app server is not running")
        deadline = time.monotonic() + APP_SERVER_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            ready, _, _ = select.select(
                [self.process.stdout], [], [], max(0.0, deadline - time.monotonic())
            )
            if not ready:
                break
            line = self.process.stdout.readline()
            if not line:
                break
            try:
                message = json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Codex app server returned invalid JSON: {exc}") from exc
            if message.get("id") != request_id:
                continue
            if isinstance(message.get("error"), dict):
                error = message["error"].get("message") or message["error"]
                raise RuntimeError(f"Codex app server request failed: {error}")
            result = message.get("result")
            if not isinstance(result, dict):
                raise RuntimeError("Codex app server response has no result object")
            return result
        detail = self.process_error()
        raise RuntimeError(f"Codex app server response timed out{detail}")

    def process_error(self) -> str:
        if self.process is None or self.process.poll() is None:
            return ""
        if self.process.stderr is None:
            return f" after exit {self.process.returncode}"
        stderr = self.process.stderr.read().strip()
        suffix = f": {stderr}" if stderr else ""
        return f" after exit {self.process.returncode}{suffix}"


def list_app_threads(codex_bin: str) -> list[dict[str, Any]]:
    threads: list[dict[str, Any]] = []
    cursor: str | None = None
    with AppServerClient(codex_bin) as client:
        while True:
            params: dict[str, Any] = {
                "archived": False,
                "limit": 100,
                "sourceKinds": ["vscode"],
            }
            if cursor is not None:
                params["cursor"] = cursor
            result = client.request("thread/list", params)
            page = result.get("data")
            if not isinstance(page, list) or not all(
                isinstance(thread, dict) for thread in page
            ):
                raise RuntimeError("Codex app server returned an invalid thread page")
            threads.extend(page)
            next_cursor = result.get("nextCursor")
            if next_cursor is None:
                return threads
            if not isinstance(next_cursor, str) or next_cursor == cursor:
                raise RuntimeError("Codex app server returned an invalid pagination cursor")
            cursor = next_cursor


def repository_worktrees(project_root: Path) -> set[Path]:
    result = subprocess.run(
        ["git", "-C", str(project_root), "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return {project_root}
    worktrees = {
        normalize_path(line.removeprefix("worktree "))
        for line in result.stdout.splitlines()
        if line.startswith("worktree ")
    }
    worktrees.add(project_root)
    return worktrees


def load_workspace_hints(path: Path, worktree_count: int) -> dict[str, Path]:
    if not path.is_file():
        if worktree_count <= 1:
            return {}
        raise RuntimeError(f"Codex app workspace state is unavailable: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Codex app workspace state is unreadable: {exc}") from exc
    raw_hints = value.get("thread-workspace-root-hints") if isinstance(value, dict) else None
    if raw_hints is None:
        return {}
    if not isinstance(raw_hints, dict):
        raise RuntimeError("Codex app workspace hints have an invalid shape")
    return {
        task_id: normalize_path(root)
        for task_id, root in raw_hints.items()
        if isinstance(task_id, str) and isinstance(root, str)
    }


def belongs_to_project(
    thread: dict[str, Any],
    project_root: Path,
    worktrees: set[Path],
    workspace_hints: dict[str, Path],
) -> bool:
    task_id = thread.get("id")
    cwd = thread.get("cwd")
    if not isinstance(task_id, str) or not isinstance(cwd, str):
        return False
    thread_root = normalize_path(cwd)
    if thread_root == project_root:
        return True
    return (
        thread_root in worktrees
        and workspace_hints.get(task_id) == project_root
    )


def matching_app_threads(
    project_root: Path,
    threads: list[dict[str, Any]],
    workspace_state: Path,
) -> tuple[dict[str, ParsedSession], list[SourceIssue], set[str]]:
    worktrees = repository_worktrees(project_root)
    hints = load_workspace_hints(workspace_state, len(worktrees))
    project_threads = [
        thread
        for thread in threads
        if belongs_to_project(thread, project_root, worktrees, hints)
    ]
    selected: dict[str, ParsedSession] = {}
    issues: list[SourceIssue] = []
    visible_ids: set[str] = set()
    for thread in project_threads:
        task_id = thread.get("id")
        source = thread.get("path")
        if not isinstance(task_id, str) or not TASK_ID_PATTERN.fullmatch(task_id):
            issues.append(SourceIssue(Path("<app-server>"), "unsafe task identity"))
            continue
        visible_ids.add(task_id)
        if not isinstance(source, str):
            issues.append(
                SourceIssue(
                    Path("<app-server>"),
                    "visible task has no readable session path",
                    task_id,
                    project_root,
                )
            )
            continue
        path = normalize_path(source)
        candidate, issue = parse_source(path)
        if candidate is not None and candidate.task_id == task_id:
            selected[task_id] = candidate
        elif candidate is not None:
            issues.append(
                SourceIssue(
                    path,
                    "app task identity does not match session metadata",
                    task_id,
                    project_root,
                )
            )
        elif issue is not None:
            issues.append(
                SourceIssue(path, issue.message, task_id, project_root)
            )
        else:
            issues.append(
                SourceIssue(
                    path,
                    "visible task could not be parsed",
                    task_id,
                    project_root,
                )
            )
    return selected, issues, visible_ids


def record_index_entry(task_id: str, candidate: ParsedSession) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "path": f"threads/{task_id}.json",
        "state": candidate.record["capture"]["state"],
    }


def write_capture(
    project_root: Path,
    selected: dict[str, ParsedSession],
    issues: list[SourceIssue],
) -> Counter[str]:
    interactions = project_root / "docs/interactions"
    threads = interactions / "threads"
    interactions.mkdir(parents=True, exist_ok=True)
    threads.mkdir(exist_ok=True)
    counts: Counter[str] = Counter()
    with CaptureLock(interactions / ".capture.lock"):
        index_path = interactions / "index.json"
        existing_records = load_existing_index(index_path)
        index_records = dict(existing_records)
        for task_id in sorted(selected):
            candidate = selected[task_id]
            record_path = threads / f"{task_id}.json"
            existed = record_path.is_file()
            changed = atomic_write(record_path, render_json(candidate.record))
            if not existed:
                counts["captured"] += 1
            elif changed:
                counts["updated"] += 1
            else:
                counts["unchanged"] += 1
            if candidate.record["capture"]["state"] == "partial":
                counts["incomplete"] += 1
            index_records[task_id] = record_index_entry(task_id, candidate)
        index = {
            "schema_version": SCHEMA_VERSION,
            "records": [index_records[task_id] for task_id in sorted(index_records)],
        }
        atomic_write(index_path, render_json(index))
    counts["unavailable"] = len(issues)
    return counts


def parser() -> argparse.ArgumentParser:
    argument_parser = argparse.ArgumentParser(
        description="Manually capture completed Codex dialogue into project-owned JSON."
    )
    argument_parser.add_argument(
        "mode", nargs="?", choices=("current", "project"), default="project"
    )
    argument_parser.add_argument("--project-root", type=Path, default=Path.cwd())
    argument_parser.add_argument(
        "--codex-bin",
        default=os.environ.get("CODEX_BIN", "codex"),
        help="Codex executable used for the read-only app-server thread list.",
    )
    argument_parser.add_argument(
        "--workspace-state",
        type=Path,
        default=Path.home() / ".codex/.codex-global-state.json",
        help="Codex app state containing worktree-to-project workspace hints.",
    )
    argument_parser.add_argument("--task-id")
    return argument_parser


def select_mode(
    arguments: argparse.Namespace,
    candidates: dict[str, ParsedSession],
    issues: list[SourceIssue],
) -> tuple[dict[str, ParsedSession], list[SourceIssue]]:
    if arguments.mode == "project":
        return candidates, issues
    if not isinstance(arguments.task_id, str):
        raise RuntimeError("current capture requires --task-id; refusing to guess the active task")
    if not TASK_ID_PATTERN.fullmatch(arguments.task_id):
        raise RuntimeError("current capture received an unsafe task identity")
    current = candidates.get(arguments.task_id)
    current_issues = [issue for issue in issues if issue.task_id == arguments.task_id]
    if current is None:
        if current_issues:
            return {}, current_issues
        raise RuntimeError(
            f"task {arguments.task_id} is not an app-visible chat for the selected project"
        )
    return {arguments.task_id: current}, current_issues


def print_summary(mode: str, counts: Counter[str]) -> None:
    fields = (
        "captured",
        "updated",
        "unchanged",
        "removed",
        "incomplete",
        "unavailable",
    )
    summary = " ".join(f"{field}={counts[field]}" for field in fields)
    print(f"mode={mode} {summary}")


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    project_root = normalize_path(arguments.project_root)
    if not project_root.is_dir():
        print(f"capture failed: project root is not a directory: {project_root}", file=sys.stderr)
        return 2
    try:
        app_threads = list_app_threads(str(arguments.codex_bin))
        candidates, issues, _visible_ids = matching_app_threads(
            project_root,
            app_threads,
            normalize_path(arguments.workspace_state),
        )
        selected, selected_issues = select_mode(arguments, candidates, issues)
        counts = write_capture(
            project_root,
            selected,
            selected_issues,
        )
    except RuntimeError as exc:
        print(f"capture failed: {exc}", file=sys.stderr)
        return 2
    print_summary(arguments.mode, counts)
    for issue in selected_issues:
        identity = issue.task_id or issue.path.name
        print(f"unavailable task={identity}: {issue.message}", file=sys.stderr)
    return 1 if selected_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
