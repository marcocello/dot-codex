#!/usr/bin/env python3
"""Install this checkout as Codex Home without committing private machine state."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tomllib
import uuid

ROOT = Path(__file__).resolve().parents[1]
ENV_BEGIN = "# BEGIN dot-codex"
ENV_END = "# END dot-codex"
OPTIONAL = {
    "landingfolio": "LANDINGFOLIO_MCP_TOKEN",
    "originkit": "ORIGINKIT_API_KEY",
    "skills-registry": None,
}


class InstallError(Exception):
    """An actionable installation failure, with no secret values in its message."""


def ask(message: str) -> str:
    try:
        return input(message).strip()
    except EOFError:
        raise InstallError("No answer received; installation cancelled.") from None


def plain_file(path: Path) -> None:
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise InstallError(f"Expected a regular file, not a link or directory: {path}")


def atomic_write(path: Path, content: str, mode: int = 0o600) -> None:
    plain_file(path)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            os.chmod(temporary, mode)
            stream.write(content)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def checked(command: list[str], env: dict[str, str], label: str) -> str:
    # Provider output can contain tokens or old private configuration. Keep it local.
    recovery = f"CODEX_HOME={shlex.quote(str(ROOT))} {shlex.join(command)}"
    try:
        result = subprocess.run(command, env=env, cwd=ROOT, text=True,
                                capture_output=True, timeout=300)
    except subprocess.TimeoutExpired:
        raise InstallError(f"{label} timed out. Retry locally: {recovery}") from None
    if result.returncode:
        raise InstallError(
            f"{label} failed (exit {result.returncode}). "
            f"Diagnose locally: {recovery}\nThen rerun ./install.sh."
        )
    return result.stdout


def ignore_private(paths: list[str]) -> None:
    path = ROOT / ".gitignore"
    text = path.read_text() if path.exists() else ""
    marker = "# dot-codex installer: copied private state"
    additions = []
    for item in paths:
        escaped = "".join("\\" + c if c in "\\*?[]!# " else c for c in item)
        rule = "/" + escaped
        if rule not in text.splitlines():
            additions.append(rule)
    if additions:
        atomic_write(path, text.rstrip() + "\n\n" + marker + "\n" + "\n".join(additions) + "\n", 0o644)


def merge_plan(source: Path, destination: Path, prefix: Path = Path()) -> list[Path]:
    """Copy only absent entries; never traverse links or replace checkout content."""
    plan = []
    for child in sorted(source.iterdir()):
        if not prefix.parts and child.name in {".git", ".install-backups", ".install.lock"}:
            continue
        relative = prefix / child.name
        target = destination / child.name
        if child.is_symlink():
            continue  # Retained in the snapshot; never activate foreign links.
        if target.is_symlink():
            continue
        if not target.exists():
            plan.append(relative)
        elif child.is_dir() and target.is_dir():
            plan.extend(merge_plan(child, target, relative))
    return plan


def tree_fingerprint(root: Path) -> dict[str, tuple[str, str]]:
    result = {}
    for directory, dirs, files in os.walk(root, followlinks=False):
        parent = Path(directory)
        if parent == root:
            dirs[:] = [name for name in dirs if name != ".git"]
            files = [name for name in files if name != ".git"]
        for name in dirs + files:
            path = parent / name
            relative = str(path.relative_to(root))
            if "\n" in relative or "\r" in relative:
                raise InstallError("Rename existing state paths containing newlines before migration.")
            if path.is_symlink():
                result[relative] = ("link", os.readlink(path))
            elif path.is_file():
                digest = hashlib.sha256()
                with path.open("rb") as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(block)
                result[relative] = ("file", digest.hexdigest())
            elif path.is_dir():
                result[relative] = ("directory", "")
            else:
                raise InstallError("Existing home contains an active socket or special file. Stop Codex and retry.")
    return result


def copy_private(source: Path, target: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, target, ignore=lambda directory, names: {
            name for name in names if (Path(directory) / name).is_symlink()
        })
    else:
        shutil.copy2(source, target)
    # Parent runtime directories remain private, even if old files were permissive.
    if target.is_dir():
        os.chmod(target, 0o700)
    else:
        os.chmod(target, 0o600)


def migrate(old: Path, choice: str) -> None:
    if choice == "merge":
        backups = ROOT / ".install-backups"
        if backups.is_symlink():
            raise InstallError("Migration archive must not be a symlink.")
        backups.mkdir(mode=0o700, exist_ok=True)
        os.chmod(backups, 0o700)
        snapshot = backups / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])
        source = old.resolve()
        before = tree_fingerprint(source)
        shutil.copytree(source, snapshot, symlinks=True, ignore=lambda directory, names:
                        {".git"} & set(names) if Path(directory) == source else set())
        os.chmod(snapshot, 0o700)
        if before != tree_fingerprint(snapshot) or before != tree_fingerprint(source):
            raise InstallError("Existing state changed during copying. Original home retained; close Codex and retry.")
        plan = merge_plan(snapshot, ROOT)
        ignore_private([str(relative) + ("/" if (snapshot / relative).is_dir() else "") for relative in plan])
        for relative in plan:
            copy_private(snapshot / relative, ROOT / relative)
        if before != tree_fingerprint(source):
            raise InstallError("Existing state changed during merge; original home retained. Close Codex and retry.")
        print(f"Merged absent files. Full original state and conflicts retained privately in {snapshot}")
    if old.is_symlink():
        old.unlink()  # Never delete a symlink's target.
    elif old.exists():
        # Merge snapshots are checked before removing the old default-home entry.
        shutil.rmtree(old)


def environment_files(home: Path) -> list[Path]:
    files = [home / name for name in (".profile", ".zshenv", ".bashrc", ".bash_profile")]
    files.extend(home / name for name in (".zprofile", ".zshrc", ".zlogin", ".bash_login")
                 if (home / name).exists())
    return files


def persist_environment(home: Path) -> None:
    block = f"{ENV_BEGIN}\nexport CODEX_HOME={shlex.quote(str(ROOT))}\n{ENV_END}"
    for path in environment_files(home):
        original = path.read_text() if path.exists() else ""
        if ENV_BEGIN in original:
            start = original.index(ENV_BEGIN)
            end = original.index(ENV_END, start) + len(ENV_END)
            content = original[:start] + block + original[end:]
        else:
            content = original.rstrip() + "\n\n" + block + "\n"
        atomic_write(path, content, path.stat().st_mode & 0o777 if path.exists() else 0o600)


def install_dependencies(args: argparse.Namespace, env: dict[str, str]) -> None:
    checked([args.codex_bin, "plugin", "marketplace", "add", str(ROOT / "integrations"), "--json"],
            env, "Register dot-codex marketplace")
    manager = [sys.executable, str(ROOT / "scripts/skill_inventory.py"),
               "--manifest", str(ROOT / "skills.toml"), "--skills-root", str(ROOT / "skills"),
               "--codex-bin", args.codex_bin]
    for name in args.with_integration:
        entries = tomllib.loads((ROOT / "skills.toml").read_text())["skills"]
        if not any(entry["name"] == f"mcp-{name}" for entry in entries):
            checked(manager + ["add", f"mcp-{name}", "--kind", "plugin", "--selector",
                               f"{name}@dot-codex", "--no-sync"], env, f"Declare {name}")
    entries = tomllib.loads((ROOT / "skills.toml").read_text())["skills"]
    failures = []
    for entry in entries:
        try:
            checked(manager + ["sync", "--only", entry["name"]], env, f"Install {entry['name']}")
            print(f"Dependency ready: {entry['name']}")
        except InstallError as error:
            failures.append(str(error))
    if failures:
        raise InstallError("\n".join(failures) + "\nHome is configured; dependency installation is incomplete.")
    checked(manager + ["doctor"], env, "Verify declared skill and plugin installation")
    print("Declared skills and plugins installed and enabled.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user-home", type=Path, default=Path.home(),
                        help="User directory to configure (default: current user's home)")
    parser.add_argument("--skip-dependencies", action="store_true",
                        help="Configure the home only; explicitly leave dependencies incomplete")
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--with", dest="with_integration", action="append", default=[],
                        choices=sorted(OPTIONAL), help="Install an optional MCP plugin; repeatable")
    args = parser.parse_args()
    try:
        if sys.version_info < (3, 11) or sys.platform not in {"darwin", "linux"}:
            raise InstallError("Use Python 3.11+ on macOS or Linux; no changes made.")
        home = args.user_home.expanduser().resolve()
        if not home.is_dir() or not (ROOT / ".git").exists():
            raise InstallError("Run from a Git checkout with an existing user home.")
        if not shutil.which("git"):
            raise InstallError("Install Git before running the installer.")
        if not args.skip_dependencies:
            for tool in (args.codex_bin, "node", "npm"):
                if not shutil.which(tool):
                    raise InstallError(f"Required executable unavailable: {tool}. Install it and retry.")
            inventory = tomllib.loads((ROOT / "skills.toml").read_text())["skills"]
            configured = {name for name in OPTIONAL if any(
                entry.get("selector") == f"{name}@dot-codex" for entry in inventory
            )}
            for name in configured | set(args.with_integration):
                variable = OPTIONAL[name]
                if variable and not os.environ.get(variable):
                    raise InstallError(f"Set {variable} in the launching environment before selecting {name}.")
        for path in [ROOT / ".gitignore", ROOT / "config.toml", *environment_files(home)]:
            plain_file(path)
            if path.exists() and path.name.startswith(".") and path.name != ".gitignore":
                content = path.read_text()
                if content.count(ENV_BEGIN) != content.count(ENV_END) or content.count(ENV_BEGIN) > 1:
                    raise InstallError(f"Repair the incomplete or duplicate dot-codex block in {path} first.")
                if ENV_BEGIN in content and content.index(ENV_END) < content.index(ENV_BEGIN):
                    raise InstallError(f"Repair the reversed dot-codex block in {path} first.")
        if (ROOT / "config.toml").exists():
            tomllib.loads((ROOT / "config.toml").read_text())
        else:
            tomllib.loads((ROOT / "config.template.toml").read_text())
        old = home / ".codex"
        same = old.exists() and old.samefile(ROOT)
        choice = "empty"
        if not same and (old.exists() or old.is_symlink()):
            resolved = old.resolve()
            if resolved == home or resolved in ROOT.parents or ROOT in resolved.parents:
                raise InstallError("Old home and checkout overlap. Move the checkout outside the old home and retry.")
            if not old.is_symlink() and not old.is_dir():
                raise InstallError("Existing .codex is not a directory; resolve it before installing.")
            nonempty = old.is_symlink() or any(old.iterdir())
            if nonempty:
                print(f"Existing home: {old}\nNew Codex Home: {ROOT}")
                print("Close Codex and its terminals before continuing; live databases must not be copied.")
                print("merge: copy state; retain conflicts in a private snapshot; replace the old home with a link.")
                print("discard: permanently delete the old directory (a symlink only is unlinked).")
                choice = ask("Choose merge / discard / cancel [cancel]: ").lower()
                if choice not in {"merge", "discard"}:
                    raise InstallError("Installation cancelled; existing home unchanged.")
                if choice == "discard" and ask("Type DELETE to confirm permanent discard: ") != "DELETE":
                    raise InstallError("Discard not confirmed; existing home unchanged.")
                if choice == "merge" and not old.exists():
                    raise InstallError("Cannot merge a dangling symlink; cancel or explicitly discard the link.")
                if choice == "merge" and not (ROOT / "config.toml").exists():
                    incoming_config = old / "config.toml"
                    if incoming_config.is_file() and not incoming_config.is_symlink():
                        tomllib.loads(incoming_config.read_text())
        lock_path = ROOT / ".install.lock"
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "w") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise InstallError("Another installer is running for this checkout.") from None
            ignore_private([".install-backups/", ".install.lock", "config.toml"])
            if not same and (old.exists() or old.is_symlink()):
                migrate(old, choice)
            config = ROOT / "config.toml"
            if not config.exists():
                atomic_write(config, (ROOT / "config.template.toml").read_text())
            os.chmod(config, 0o600)
            if not same:
                old.symlink_to(ROOT, target_is_directory=True)
            persist_environment(home)
            env = dict(os.environ, HOME=str(home), CODEX_HOME=str(ROOT))
            print(f"Codex Home configured: {ROOT}")
            if args.skip_dependencies:
                print("Dependencies skipped: rerun ./install.sh to install skills and MCP plugins.")
            else:
                install_dependencies(args, env)
        print("Open a new terminal or source ~/.profile; fully quit and reopen the desktop app.")
        print("Existing terminal/app processes retain their old environment. Sign in and connect services as needed.")
        return 0
    except (InstallError, OSError, ValueError, KeyError) as error:
        if isinstance(error, InstallError):
            print(f"Install: {error}", file=sys.stderr)
        else:
            # Avoid echoing TOML content or provider secrets in generic exceptions.
            print(f"Install: {type(error).__name__}; check paths, permissions, and local TOML. Rerun after repair.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
