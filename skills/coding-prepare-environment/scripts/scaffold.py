#!/usr/bin/env python3
"""Copy the bundled starter into an absent or empty directory."""

import argparse
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument(
        "--github-actions",
        action="store_true",
        help="Include the optional GitHub Actions workflow",
    )
    args = parser.parse_args()
    target = args.destination.expanduser().absolute()
    source = Path(__file__).resolve().parents[1] / "assets" / "react-fastapi"
    if target.is_symlink():
        parser.error("destination must not be a symlink")
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        parser.error(
            "destination must be absent or empty; existing files are never merged"
        )
    if source == target.resolve() or source in target.resolve().parents:
        parser.error("destination must be outside the bundled template")
    ignored = shutil.ignore_patterns(
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        "dist",
        "build",
        "backups",
        "logs",
        "test-results",
        "playwright-report",
        "*.pyc",
        "*.tsbuildinfo",
    )

    def source_only(directory: str, names: list[str]) -> set[str]:
        omitted = ignored(directory, names) | {
            name for name in names if name.startswith(".env") and name != ".env.example"
        }
        if Path(directory) == source:
            omitted.update({"Makefile", "PRODUCT.md"})
            if not args.github_actions:
                omitted.add(".github")
        return omitted

    shutil.copytree(source, target, dirs_exist_ok=True, ignore=source_only)
    print(f"Created {target}")
    print("Next: run python3 deployments/setup.py; use Compose files in deployments/.")


if __name__ == "__main__":
    main()
