#!/usr/bin/env python3
"""Create or update VS Code tasks for a backend/frontend dev loop."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

GENERATED_LABELS = {"frontend", "backend:app", "backend:ngrok", "backend", "fullstack"}
DEFAULT_BACKEND_CWD = "${workspaceFolder}/backend/app"
PROJECT_VENV_PYTHON = "${workspaceFolder}/.venv/bin/python"


def shell_task(label: str, command: str, cwd: str, is_background: bool) -> dict[str, Any]:
    task: dict[str, Any] = {
        "label": label,
        "type": "shell",
        "command": command,
        "options": {"cwd": cwd},
    }
    if is_background:
        task["isBackground"] = True
    task["presentation"] = {"reveal": "always", "panel": "dedicated"}
    return task


def aggregate_task(label: str, depends_on: list[str]) -> dict[str, Any]:
    return {"label": label, "dependsOn": depends_on, "dependsOrder": "parallel"}


def generated_tasks(args: argparse.Namespace) -> list[dict[str, Any]]:
    backend_app_command = resolve_backend_app_command(args)
    return [
        shell_task("frontend", args.frontend_command, args.frontend_cwd, True),
        shell_task("backend:app", backend_app_command, args.backend_cwd, True),
        shell_task("backend:ngrok", args.backend_ngrok_command, args.backend_cwd, True),
        aggregate_task("backend", ["backend:app", "backend:ngrok"]),
        aggregate_task("fullstack", ["frontend", "backend"]),
    ]


def resolve_backend_app_command(args: argparse.Namespace) -> str:
    if args.backend_app_command:
        return args.backend_app_command
    backend_path = vscode_cwd_to_path(args.project_root.resolve(), args.backend_cwd)
    if has_fastapi_app(backend_path):
        return f"{PROJECT_VENV_PYTHON} -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"
    return f"{PROJECT_VENV_PYTHON} main.py"


def vscode_cwd_to_path(project_root: Path, cwd: str) -> Path:
    if cwd.startswith("${workspaceFolder}"):
        suffix = cwd.removeprefix("${workspaceFolder}").lstrip("/")
        return project_root / suffix
    return Path(cwd)


def has_fastapi_app(backend_path: Path) -> bool:
    main_path = backend_path / "main.py"
    if not main_path.exists():
        return False
    try:
        main_source = main_path.read_text(encoding="utf-8")
    except OSError:
        return False
    if "FastAPI(" not in main_source or "app" not in main_source:
        return False
    dependency_text = read_backend_dependency_text(backend_path)
    if not dependency_text:
        return True
    return "fastapi" in dependency_text or "uvicorn" in dependency_text


def read_backend_dependency_text(backend_path: Path) -> str:
    dependency_paths = [
        backend_path / "requirements.txt",
        backend_path.parent / "requirements.txt",
        backend_path / "pyproject.toml",
        backend_path.parent / "pyproject.toml",
    ]
    dependency_text = []
    for dependency_path in dependency_paths:
        if not dependency_path.exists():
            continue
        try:
            dependency_text.append(dependency_path.read_text(encoding="utf-8").lower())
        except OSError:
            continue
    return "\n".join(dependency_text)


def load_existing_tasks(tasks_path: Path) -> dict[str, Any]:
    if not tasks_path.exists():
        return {"version": "2.0.0", "tasks": []}

    with tasks_path.open(encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"{tasks_path} must contain a JSON object")
    tasks = data.get("tasks", [])
    if not isinstance(tasks, list):
        raise ValueError(f"{tasks_path} must contain a tasks array")
    return data


def task_labels(tasks: list[Any]) -> list[str]:
    labels = []
    for task in tasks:
        if isinstance(task, dict) and isinstance(task.get("label"), str):
            labels.append(task["label"])
    return labels


def summarize_existing_tasks(tasks_path: Path, existing: dict[str, Any]) -> list[str]:
    tasks = existing.get("tasks", [])
    labels = task_labels(tasks if isinstance(tasks, list) else [])
    generated_present = sorted(label for label in labels if label in GENERATED_LABELS)
    unrelated = sorted(label for label in labels if label not in GENERATED_LABELS)
    missing_generated = sorted(GENERATED_LABELS - set(generated_present))
    duplicate_labels = sorted({label for label in labels if labels.count(label) > 1})

    if tasks_path.exists():
        lines = ["Review existing .vscode/tasks.json"]
    else:
        lines = ["Review existing .vscode/tasks.json: none found"]

    if unrelated:
        lines.append(f"preserve unrelated labels: {', '.join(unrelated)}")
    if generated_present:
        lines.append(f"replace generated labels: {', '.join(generated_present)}")
    if missing_generated:
        lines.append(f"improvement: add missing generated labels: {', '.join(missing_generated)}")
    if duplicate_labels:
        lines.append(f"improvement: review duplicate labels: {', '.join(duplicate_labels)}")
    return lines


def merge_tasks(existing: dict[str, Any], generated: list[dict[str, Any]]) -> dict[str, Any]:
    preserved = [
        task
        for task in existing.get("tasks", [])
        if not isinstance(task, dict) or task.get("label") not in GENERATED_LABELS
    ]
    return {"version": existing.get("version", "2.0.0"), "tasks": [*preserved, *generated]}


def write_tasks(project_root: Path, tasks: dict[str, Any]) -> Path:
    tasks_dir = project_root / ".vscode"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    tasks_path = tasks_dir / "tasks.json"
    tasks_path.write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")
    return tasks_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".", type=Path)
    parser.add_argument("--frontend-command", default="npm run dev")
    parser.add_argument("--frontend-cwd", default="${workspaceFolder}/frontend/app")
    parser.add_argument("--backend-cwd", default=DEFAULT_BACKEND_CWD)
    parser.add_argument("--backend-app-command")
    parser.add_argument(
        "--backend-ngrok-command",
        default="ngrok http 8000",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    tasks_path = project_root / ".vscode" / "tasks.json"
    existing = load_existing_tasks(tasks_path)
    for line in summarize_existing_tasks(tasks_path, existing):
        print(line)
    merged = merge_tasks(existing, generated_tasks(args))
    output_path = write_tasks(project_root, merged)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
