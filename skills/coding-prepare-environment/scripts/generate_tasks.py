#!/usr/bin/env python3
"""Create or update VS Code tasks for a backend/frontend dev loop."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

DEFAULT_BACKEND_CWD = "${workspaceFolder}/app/backend"
PROJECT_VENV_PYTHON = "${workspaceFolder}/.venv/bin/python"


def shell_task(label: str, command: str, cwd: str, is_background: bool) -> dict[str, Any]:
    task: dict[str, Any] = {
        "label": label,
        "type": "shell",
        "command": command,
        "options": {"cwd": cwd},
        "problemMatcher": [],
    }
    if is_background:
        task["isBackground"] = True
        task["runOptions"] = {"instanceLimit": 1}
    task["presentation"] = {"reveal": "always", "panel": "dedicated"}
    return task


def aggregate_task(label: str, depends_on: list[str]) -> dict[str, Any]:
    return {"label": label, "dependsOn": depends_on, "dependsOrder": "parallel", "problemMatcher": []}


def track_ready(task: dict[str, Any], pattern: str | None) -> None:
    if pattern:
        task["problemMatcher"] = {
            "owner": "local-run",
            # Track startup output without treating arbitrary server logs as diagnostics.
            "pattern": {"regexp": r"^(?!)()(\d+)()$", "file": 1, "line": 2, "message": 3},
            "background": {"activeOnStart": True, "beginsPattern": "^(?!)", "endsPattern": pattern},
        }


def package_command(path: Path) -> str:
    manifest = path / "package.json"
    package = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else {}
    manager = str(package.get("packageManager", "")).split("@", 1)[0]
    if not manager:
        locks = {"package-lock.json": "npm", "pnpm-lock.yaml": "pnpm", "yarn.lock": "yarn",
                 "bun.lock": "bun", "bun.lockb": "bun"}
        detected = {manager for lock, manager in locks.items() if (path / lock).is_file()}
        if len(detected) > 1:
            raise ValueError(f"conflicting package-manager lockfiles in {path}; select an explicit command")
        manager = next(iter(detected), "npm")
    if manager not in {"npm", "pnpm", "yarn", "bun"}:
        raise ValueError(f"unsupported package manager {manager!r}; select an explicit command")
    scripts = package.get("scripts", {})
    script = "dev" if "dev" in scripts else "start" if "start" in scripts else None
    if not script:
        raise ValueError(f"no dev or start script in {manifest}; select an explicit command")
    return f"{manager} run {script}"


def selected_components(args: argparse.Namespace) -> tuple[bool, bool]:
    if args.components != "auto":
        return args.components in {"backend", "fullstack"}, args.components in {"frontend", "fullstack"}
    root = args.project_root.resolve()
    backend = vscode_cwd_to_path(root, args.backend_cwd).is_dir() or bool(args.backend_app_command)
    frontend = vscode_cwd_to_path(root, args.frontend_cwd).is_dir() or bool(args.frontend_command)
    if not backend and not frontend:
        raise ValueError("no components found; select component paths or use --components with explicit commands")
    return backend, frontend


def generated_tasks(args: argparse.Namespace) -> list[dict[str, Any]]:
    backend, frontend = selected_components(args)
    tasks = []
    if frontend:
        path = vscode_cwd_to_path(args.project_root.resolve(), args.frontend_cwd)
        command = args.frontend_command or package_command(path)
        task = shell_task("frontend", command, args.frontend_cwd, True)
        pattern = args.frontend_ready_pattern
        if not pattern and not args.frontend_command and any(path.glob("vite.config.*")):
            pattern = r"Local:.*https?://"
        track_ready(task, pattern)
        if args.frontend_depends_on:
            task["dependsOn"] = args.frontend_depends_on
            task["dependsOrder"] = "sequence"
        tasks.append(task)
    if backend:
        task = backend_app_task(args)
        if args.backend_depends_on:
            task["dependsOn"] = args.backend_depends_on
            task["dependsOrder"] = "sequence"
        tasks.append(task)
        dependencies = ["backend:app"]
        if args.backend_ngrok_command:
            tasks.append(shell_task("backend:ngrok", args.backend_ngrok_command, "${workspaceFolder}", True))
            dependencies.append("backend:ngrok")
        if args.backend_down_command:
            tasks.append(shell_task("backend:down", args.backend_down_command, args.backend_cwd, False))
        tasks.append(aggregate_task("backend", dependencies))
    components = []
    if frontend:
        components.append("frontend")
    if backend:
        components.append("backend")
    tasks.append(aggregate_task("fullstack", components))
    return tasks


def backend_app_task(args: argparse.Namespace) -> dict[str, Any]:
    if args.backend_app_command:
        task = shell_task("backend:app", args.backend_app_command, args.backend_cwd, True)
        track_ready(task, args.backend_ready_pattern)
        return task
    backend_path = vscode_cwd_to_path(args.project_root.resolve(), args.backend_cwd)
    if (backend_path / "package.json").is_file():
        task = shell_task("backend:app", package_command(backend_path), args.backend_cwd, True)
        track_ready(task, args.backend_ready_pattern)
        return task
    task = shell_task("backend:app", PROJECT_VENV_PYTHON, args.backend_cwd, True)
    # Keep the resolved executable as one argument, including spaces or shell characters.
    task["type"] = "process"
    task["args"] = ["main.py"]
    module = fastapi_module(backend_path)
    if module:
        task["args"] = ["-m", "uvicorn", module, "--reload", "--host", "127.0.0.1", "--port", "8000"]
    track_ready(task, args.backend_ready_pattern or (r"Application startup complete\." if module else None))
    return task


def vscode_cwd_to_path(project_root: Path, cwd: str) -> Path:
    if cwd.startswith("${workspaceFolder}"):
        suffix = cwd.removeprefix("${workspaceFolder}").lstrip("/")
        return project_root / suffix
    return Path(cwd)


def fastapi_module(backend_path: Path) -> str | None:
    main_path = backend_path / "main.py"
    module = "main:app"
    if not main_path.exists():
        main_path = backend_path / "app/main.py"
        module = "app.main:app"
    if not main_path.exists():
        return None
    try:
        main_source = main_path.read_text(encoding="utf-8")
    except OSError:
        return None
    if "FastAPI(" not in main_source or "app" not in main_source:
        return None
    dependency_text = read_backend_dependency_text(backend_path)
    if not dependency_text:
        return module
    return module if "fastapi" in dependency_text or "uvicorn" in dependency_text else None


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


def parse_jsonc(source: str) -> Any:
    # Match complete strings first so URLs, escapes and comment-like string values survive.
    string = r'"(?:\\.|[^"\\])*"'
    without_comments = re.sub(
        string + r"|//[^\r\n]*|/\*[\s\S]*?\*/",
        lambda match: match[0] if match[0].startswith('"') else re.sub(r"[^\r\n]", " ", match[0]),
        source,
    )
    without_trailing_commas = re.sub(
        string + r"|(?<=[^\s\[{,:])\s*,(?=\s*[\]}])",
        lambda match: match[0] if match[0].startswith('"') else match[0].replace(",", " "),
        without_comments,
    )
    return json.loads(without_trailing_commas)


def load_existing_tasks(tasks_path: Path) -> dict[str, Any]:
    if not tasks_path.exists():
        return {"version": "2.0.0", "tasks": []}

    data = parse_jsonc(tasks_path.read_text(encoding="utf-8"))

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


def summarize_existing_tasks(tasks_path: Path, existing: dict[str, Any], generated: list[dict[str, Any]], replace: bool) -> list[str]:
    tasks = existing.get("tasks", [])
    labels = task_labels(tasks if isinstance(tasks, list) else [])
    selected = set(task_labels(generated))
    generated_present = sorted(label for label in labels if label in selected)
    unrelated = sorted(label for label in labels if label not in selected)
    missing_generated = sorted(selected - set(generated_present))
    duplicate_labels = sorted({label for label in labels if labels.count(label) > 1})

    if tasks_path.exists():
        lines = ["Review existing .vscode/tasks.json"]
    else:
        lines = ["Review existing .vscode/tasks.json: none found"]

    if unrelated:
        lines.append(f"preserve unrelated labels: {', '.join(unrelated)}")
    if generated_present:
        action = "replace" if replace else "preserve"
        lines.append(f"{action} existing selected labels: {', '.join(generated_present)}")
    if missing_generated:
        lines.append(f"improvement: add missing generated labels: {', '.join(missing_generated)}")
    if duplicate_labels:
        lines.append(f"improvement: review duplicate labels: {', '.join(duplicate_labels)}")
    return lines


def merge_tasks(existing: dict[str, Any], generated: list[dict[str, Any]], replace: bool = False) -> dict[str, Any]:
    selected = set(task_labels(generated))
    preserved = [
        task
        for task in existing.get("tasks", [])
        if not replace or not isinstance(task, dict) or task.get("label") not in selected
    ]
    present = set(task_labels(preserved))
    additions = [task for task in generated if task["label"] not in present]
    return {**existing, "version": existing.get("version", "2.0.0"), "tasks": [*preserved, *additions]}


def write_tasks(project_root: Path, tasks: dict[str, Any]) -> Path:
    tasks_dir = project_root / ".vscode"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    tasks_path = tasks_dir / "tasks.json"
    tasks_path.write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")
    return tasks_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".", type=Path)
    parser.add_argument("--components", choices=["auto", "backend", "frontend", "fullstack"], default="auto")
    parser.add_argument("--replace", action="store_true", help="Replace selected standard labels after reviewing their commands and dependencies")
    parser.add_argument("--frontend-command")
    parser.add_argument("--frontend-cwd", default="${workspaceFolder}/app/frontend")
    parser.add_argument("--backend-cwd", default=DEFAULT_BACKEND_CWD)
    parser.add_argument("--backend-app-command")
    parser.add_argument("--backend-down-command")
    parser.add_argument("--backend-ready-pattern")
    parser.add_argument("--frontend-ready-pattern")
    parser.add_argument("--backend-depends-on", action="append", default=[])
    parser.add_argument("--frontend-depends-on", action="append", default=[])
    parser.add_argument(
        "--backend-ngrok-command",
        help="Include an explicitly selected tunnel command; omitted for local-only startup",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    tasks_path = project_root / ".vscode" / "tasks.json"
    existing = load_existing_tasks(tasks_path)
    generated = generated_tasks(args)
    for line in summarize_existing_tasks(tasks_path, existing, generated, args.replace):
        print(line)
    merged = merge_tasks(existing, generated, args.replace)
    output_path = write_tasks(project_root, merged)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
