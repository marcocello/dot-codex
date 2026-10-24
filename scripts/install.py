#!/usr/bin/env python3
"""Guided, repeatable Codex and harness installation on macOS and Linux."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import sys
import tarfile
import tomllib
import uuid

from install_runtime import (DEFAULT_VERSION, configure_service, find_cli, install_cli,
                             require_connection, require_login, run, version_of)
from install_state import (InstallError, Transaction, atomic_write, installation_lock,
                           environment_files, ignore_interrupts, save_json)

ROOT = Path(__file__).resolve().parents[1]
ENV_BEGIN = "# BEGIN dot-codex"
ENV_END = "# END dot-codex"
OPTIONAL = {
    "landingfolio": "LANDINGFOLIO_MCP_TOKEN",
    "originkit": "ORIGINKIT_API_KEY",
    "skills-registry": None,
}
COLOR_MODE = "auto"
# Palette adapted from https://openclaw.ai/install.sh with a blue accent.
COLORS = {
    "heading": "1;38;2;51;153;255", "prompt": "38;2;102;178;255",
    "success": "38;2;0;229;204", "skip": "38;2;255;176;32",
    "error": "38;2;230;57;70", "muted": "38;2;90;100;128",
    "info": "38;2;136;146;176",
}


def usable_terminal(stream) -> bool:
    return stream.isatty() and os.environ.get("TERM", "") not in {"", "dumb"}


def style(message: str, tone: str, *, stream=None) -> str:
    stream = stream or sys.stdout
    enabled = COLOR_MODE == "always" or (COLOR_MODE == "auto" and usable_terminal(stream))
    if not enabled or COLOR_MODE == "never" or "NO_COLOR" in os.environ:
        return message
    return f"\033[{COLORS[tone]}m{message}\033[0m"


def ui_message(message: str, tone="info", *, stream=None) -> None:
    stream = stream or sys.stdout
    mark = {"success": "✓", "skip": "!", "error": "✗"}.get(tone, "·")
    print(f"{style(mark, tone, stream=stream)} {message}", file=stream, flush=True)


def ui_section(title: str) -> None:
    print("\n" + style(title, "heading"), flush=True)


def ui_kv(key: str, value) -> None:
    print(f"{style(key + ':', 'muted')} {value}", flush=True)


def ui_banner() -> None:
    lines = [
        ("dot-codex Installer", "heading"),
        ("Your Codex setup, one step at a time.", "info"),
        ("macOS and Linux", "muted"),
    ]
    width = max(len(message) for message, _ in lines)
    framed = usable_terminal(sys.stdout) and shutil.get_terminal_size().columns >= width + 6
    print()
    if framed:
        print(style("╭" + "─" * (width + 4) + "╮", "heading"))
    for message, tone in lines:
        if framed:
            print(style("│", "heading") + "  " + style(message.ljust(width), tone)
                  + "  " + style("│", "heading"))
        else:
            print("  " + style(message, tone))
    if framed:
        print(style("╰" + "─" * (width + 4) + "╯", "heading"))
    print(flush=True)


def ask(message: str) -> str:
    try:
        return input(style(message, "prompt")).strip()
    except EOFError:
        raise InstallError("No answer received; installation cancelled.") from None


def confirm(message: str) -> bool:
    while True:
        answer = ask(message + " [y/N]: ").lower()
        if answer in {"", "n", "no"}:
            return False
        if answer in {"y", "yes"}:
            return True
        if answer in {"q", "quit", "cancel"}:
            raise InstallError("Installation cancelled; no phase started.")
        ui_message("Enter y or n. Press Enter to choose No.", "skip")


def plain_file(path: Path) -> None:
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise InstallError(f"Expected a regular file, not a link or directory: {path}")


def checked(command: list[str], env: dict[str, str], label: str) -> str:
    # Provider output can contain tokens or old private configuration. Keep it local.
    recovery = f"CODEX_HOME={shlex.quote(str(ROOT))} {shlex.join(command)}"
    try:
        result = run(command, env, label, check=False, cwd=ROOT)
    except InstallError:
        raise InstallError(f"{label} timed out or failed. Retry locally: {recovery}") from None
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
            ui_message(f"Dependency ready: {entry['name']}", "success")
        except InstallError as error:
            failures.append(str(error))
    if failures:
        raise InstallError("\n".join(failures) + "\nHome is configured; dependency installation is incomplete.")
    checked(manager + ["doctor"], env, "Verify declared skill and plugin installation")
    ui_message("Declared skills and plugins installed and enabled.", "success")


PHASES = {
    "copy": "Copy Git-owned harness files to another directory; do not activate",
    "cli": "Install or repair Codex in a stable user-local directory",
    "harness": "Activate the selected harness; merge or replace with backup",
    "dependencies": "Install declared skills and MCP plugins",
    "login": "Sign in to Codex using device authentication",
    "service": "Configure persistent Remote Control and verify its connection",
    "pair": "Display a short-lived code to pair another device",
    "doctor": "Inspect executable, active home, and configured startup service",
}
ALL_PHASES = ["cli", "harness", "dependencies", "login", "service", "pair", "doctor"]
PHASE_TITLES = {
    "copy": "Copy the harness", "cli": "Install Codex CLI",
    "harness": "Activate the harness", "dependencies": "Install skills and plugins",
    "login": "Sign in to Codex", "service": "Configure Remote Control",
    "pair": "Pair a device", "doctor": "Check installation", "restore": "Restore the previous home",
}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__, epilog=(
        "Examples: ./install.sh | ./install.sh doctor | ./install.sh --steps cli,harness "
        "--mode merge --yes | ./install.sh all | ./install.sh resume | ./install.sh restore"))
    result.add_argument("phase", nargs="?", choices=[*PHASES, "all", "resume", "restore"])
    result.add_argument("--steps", help="Comma-separated phases; 'all' selects the complete journey")
    result.add_argument("--wizard", action="store_true", help="Walk through each phase with default-No confirmations")
    result.add_argument("--color", choices=["auto", "always", "never"], default="auto",
                        help="Terminal colors; NO_COLOR always disables color")
    result.add_argument("--yes", action="store_true", help="Accept the displayed plan; never choose a migration mode implicitly")
    result.add_argument("--dry-run", action="store_true", help="Show the plan without making changes")
    result.add_argument("--destination", type=Path, help="Harness directory; copy requires a new destination")
    result.add_argument("--mode", choices=["merge", "replace", "discard", "cancel"], help="Home activation policy; replacement always retains a backup")
    result.add_argument("--user-home", type=Path, default=Path.home())
    result.add_argument("--skip-dependencies", action="store_true", help="Legacy home-only activation")
    result.add_argument("--codex-bin", default="codex", help="Existing CLI override; otherwise prefer the managed user-local CLI")
    result.add_argument("--with", dest="with_integration", action="append", default=[], choices=sorted(OPTIONAL))
    result.add_argument("--version", default=DEFAULT_VERSION, help="Explicit Codex x.y.z release for the CLI phase")
    result.add_argument("--package-file", type=Path, help="Offline standalone package; requires --sha256")
    result.add_argument("--package-url", help="Audited HTTPS standalone package URL; requires --sha256")
    result.add_argument("--sha256", help="Expected package digest for an explicit file or URL")
    result.add_argument("--service-manager", choices=["systemd", "launchd"], help="Default: the native platform manager")
    result.add_argument("--enable-linger", action="store_true", help="Allow the Linux service phase to request sudo for boot persistence")
    return result


def select_phases(args) -> list[str]:
    if args.phase and args.steps:
        raise InstallError("Choose a command or --steps, not both.")
    selection = args.steps or args.phase
    if not selection and not args.wizard:
        # Preserve the original explicitly selected home/dependency entrypoints.
        if args.skip_dependencies or args.codex_bin != "codex" or args.with_integration:
            return ["harness"] + ([] if args.skip_dependencies else ["dependencies"])
    if selection in {"q", "quit", "cancel", ""}:
        raise InstallError("Installation cancelled; no new phase started.")
    if selection in {"resume", "restore"}:
        return [selection]
    names = list(PHASES)
    if not selection:
        phases = list(ALL_PHASES) if args.dry_run else names
    elif selection == "all":
        phases = list(ALL_PHASES)
        if args.destination and not args.destination.exists():
            phases.insert(0, "copy")
    else:
        phases = []
        for value in selection.split(","):
            value = value.strip()
            if value.isdigit() and 1 <= int(value) <= len(names):
                value = names[int(value) - 1]
            if value not in PHASES:
                raise InstallError(f"Unknown phase: {value}. Run ./install.sh --help.")
            if value not in phases:
                phases.append(value)
    if args.guided and not args.dry_run:
        ui_message("Choose your steps. Press Enter to skip; q or Ctrl+C cancels.")
        ui_message("Nothing runs until you confirm the install plan.")
        chosen = []
        for number, name in enumerate(phases, 1):
            ui_section(f"[{number}/{len(phases)}] {PHASE_TITLES[name]}")
            print(style(PHASES[name], "info"), flush=True)
            if confirm("Run this step?"):
                chosen.append(name)
                ui_message(f"Selected: {name}", "success")
            else:
                ui_message(f"Skipped: {name}", "skip")
        return chosen
    return phases


def check_paths(args, phases):
    if sys.version_info < (3, 11) or sys.platform not in {"darwin", "linux"}:
        raise InstallError("Use Python 3.11+ on macOS or Linux.")
    if not args.user_home.is_dir():
        raise InstallError("--user-home must be an existing directory.")
    for path in [args.user_home, ROOT, args.destination]:
        if path and any(character in str(path) for character in "\n\r\x00"):
            raise InstallError("Paths must not contain control characters.")
    if "copy" in phases and not args.destination:
        if args.yes or args.dry_run:
            raise InstallError("copy requires --destination pointing to a new directory.")
        value = ask("New harness directory (copy only; not activated): ")
        if not value:
            raise InstallError("Copy cancelled.")
        args.destination = Path(value).expanduser().absolute()
    if not shutil.which("git"):
        raise InstallError("Install Git before preparing the harness.")


def copy_harness(source: Path, destination: Path, env: dict, *, resume=False):
    if destination.exists() or destination.is_symlink():
        marker = destination / ".dot-codex-copy.json"
        if resume and marker.is_file() and not destination.is_symlink():
            previous = json.loads(marker.read_text())
            if previous.get("source") == str(source) and all(
                (destination / name).is_file() and
                hashlib.sha256((destination / name).read_bytes()).hexdigest() == digest
                for name, digest in previous.get("files", {}).items()
            ) and previous.get("files"):
                print(f"Completed harness copy recovered: {destination}")
                return
        raise InstallError(f"Copy destination already exists; choose a new directory: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name("." + destination.name + ".copy-" + uuid.uuid4().hex)
    try:
        tracked = run(["git", "-C", source, "ls-files", "-z", "--cached"], env, "Read source files").stdout.split("\0")
        # Include this installer's bundled runtime when reviewing an uncommitted checkout;
        # never include arbitrary untracked or ignored files from the user's Codex Home.
        tracked = sorted(set(tracked) | {"install.sh", "scripts/install.py", "scripts/install_state.py",
                                        "scripts/install_runtime.py", "scripts/install_service.py"})
        # The local clone preserves Git history; overlay only Git-owned current files.
        run(["git", "clone", "--quiet", "--no-hardlinks", source, temporary], env, "Prepare harness copy")
        files = {}
        for name in filter(None, tracked):
            path = source / name
            target = temporary / name
            if path.is_symlink():
                raise InstallError(f"Review tracked source symlinks before copying: {name}")
            if path.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
                files[name] = hashlib.sha256(target.read_bytes()).hexdigest()
            elif target.is_file():
                target.unlink()
        save_json(temporary / ".dot-codex-copy.json", {"source": str(source), "files": files})
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    print(f"Harness copied; not activated: {destination}", flush=True)


def preserve_package_links(source: Path, destination: Path, transaction: Transaction, original_home: Path):
    package = source / "packages/standalone"
    if not package.is_dir() or package.is_symlink():
        return
    for parent, dirs, files in os.walk(package, followlinks=False):
        for name in dirs + files:
            path = Path(parent) / name
            if not path.is_symlink():
                continue
            raw = Path(os.readlink(path))
            referent = raw if raw.is_absolute() else path.parent / raw
            if referent.is_relative_to(original_home):
                referent = source / referent.relative_to(original_home)
            resolved = referent.resolve()
            if not resolved.is_relative_to(source.resolve()) or not resolved.exists():
                continue
            relative = path.relative_to(source)
            target = destination / relative
            if target.exists() or target.is_symlink():
                continue
            # Rebase internal absolute links to the new home; never activate foreign links.
            referent = destination / resolved.relative_to(source.resolve())
            target.parent.mkdir(parents=True, exist_ok=True)
            transaction.remember(target)
            target.symlink_to(os.path.relpath(referent, target.parent))


def activate_harness(args, state: Path, env: dict):
    home = args.user_home
    old = home / ".codex"
    if not (ROOT / ".git").exists() or not (ROOT / "config.template.toml").is_file():
        raise InstallError(f"Harness checkout unavailable at {ROOT}. Run the copy phase first.")
    same = old.exists() and old.samefile(ROOT)
    choice = args.mode
    if choice == "cancel":
        raise InstallError("Activation cancelled; existing home unchanged.")
    existing = old.exists() or old.is_symlink()
    if not same and existing:
        resolved = old.resolve()
        if resolved == home or resolved in ROOT.parents or ROOT in resolved.parents:
            raise InstallError("Old home and checkout overlap. Choose a checkout outside the old home.")
        if not old.is_symlink() and not old.is_dir():
            raise InstallError("Existing .codex is not a directory; resolve it before activation.")
        if not choice and (old.is_symlink() or any(old.iterdir())):
            ui_section("Choose how to activate")
            ui_kv("Existing home", old)
            ui_kv("New harness", ROOT)
            ui_message("Close Codex sessions before migration; live databases must not be copied.", "skip")
            ui_kv("merge", "Keep destination files and copy missing state. A full backup is retained.")
            ui_kv("replace/discard", "Use the new harness without old state. A full backup is retained.")
            if args.yes:
                raise InstallError("Choose --mode merge or --mode replace explicitly.")
            choice = ask("Choose merge / replace / discard / cancel [cancel]: ").lower()
            if choice not in {"merge", "replace", "discard"}:
                raise InstallError("Activation cancelled; existing home unchanged.")
        if choice == "discard" and not args.yes and ask("Type DELETE to confirm replacement (backup retained): ") != "DELETE":
            raise InstallError("Replacement not confirmed; existing home unchanged.")
        if choice == "merge" and not old.exists():
            raise InstallError("Cannot merge a dangling home link; choose replace or cancel.")
    choice = choice or "merge"
    args.mode = choice
    for path in [ROOT / ".gitignore", ROOT / "config.toml", *environment_files(home)]:
        plain_file(path)
        if path.exists() and path in environment_files(home):
            content = path.read_text()
            if content.count(ENV_BEGIN) != content.count(ENV_END) or content.count(ENV_BEGIN) > 1:
                raise InstallError(f"Repair the incomplete or duplicate environment block in {path}.")
            if ENV_BEGIN in content and content.index(ENV_END) < content.index(ENV_BEGIN):
                raise InstallError(f"Repair the reversed environment block in {path}.")
    config = ROOT / "config.toml"
    incoming = old / "config.toml"
    config_source = config if config.exists() else (incoming if choice == "merge" and incoming.is_file()
                                                   and not incoming.is_symlink() else ROOT / "config.template.toml")
    tomllib.loads(config_source.read_text())
    previous_cli = None
    try:
        binary = find_cli(home, args.codex_bin)
        previous_cli = (binary, version_of(binary, env))
    except InstallError:
        if args.codex_bin != "codex":
            raise
    transaction = Transaction(state)
    try:
        transaction.remember(ROOT / ".gitignore")
        ignore_private([".install-backups/", ".install.lock", "config.toml"])
        if not same:
            if existing:
                identifier = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
                archive = ROOT / ".install-backups"
                if archive.is_symlink():
                    raise InstallError("Migration archive must not be a symlink.")
                archive.mkdir(mode=0o700, exist_ok=True)
                os.chmod(archive, 0o700)
                snapshot = archive / identifier
                transaction.remember(snapshot)
                if not old.is_symlink() and old.stat().st_dev == archive.stat().st_dev:
                    backup = snapshot
                    transaction.move_home(old, backup)
                    os.chmod(backup, 0o700)
                else:
                    # Preserve a relative home symlink in its original parent. Cross-device
                    # directories also need a same-filesystem rename before activation.
                    backup = home / (".codex.backup." + identifier)
                    transaction.move_home(old, backup)
                    if backup.exists():
                        shutil.copytree(backup, snapshot, symlinks=True)
                        os.chmod(snapshot, 0o700)
                ui_message(f"Previous home retained: {backup}")
                if choice == "merge":
                    before = tree_fingerprint(backup.resolve())
                    plan = merge_plan(backup, ROOT)
                    ignore_private([str(relative) + ("/" if (backup / relative).is_dir() else "") for relative in plan])
                    for relative in plan:
                        transaction.remember(ROOT / relative)
                        copy_private(backup / relative, ROOT / relative)
                    preserve_package_links(backup, ROOT, transaction, old)
                    if before != tree_fingerprint(backup.resolve()):
                        raise InstallError("Old state changed during copying. Close Codex before retrying.")
            else:
                transaction.remember(old, role="home")
            old.symlink_to(ROOT, target_is_directory=True)
        if not config.exists():
            transaction.remember(config)
            atomic_write(config, (ROOT / "config.template.toml").read_text())
        os.chmod(config, 0o600)
        for path in environment_files(home):
            transaction.remember(path, role="shell")
        persist_environment(home)
        if previous_cli and version_of(previous_cli[0], dict(env, CODEX_HOME=str(ROOT))) != previous_cli[1]:
            raise InstallError("Home activation changed the published CLI unexpectedly.")
        receipt = state / "last-activation.json"
        if not same or not receipt.exists():
            transaction.remember(receipt)
            save_json(receipt, {"transaction": transaction.directory.name, "destination": str(ROOT)})
        transaction.commit()
    except BaseException:
        transaction.rollback()
        raise
    ui_message(f"Harness active: {ROOT}", "success")
    if not previous_cli:
        ui_message("CLI not installed yet. Run ./install.sh cli; this phase configured the harness only.", "skip")


def dependency_prerequisites(args, env):
    for tool in ("node", "npm"):
        if not shutil.which(tool, path=env.get("PATH")):
            raise InstallError(f"Required executable unavailable: {tool}. Install it, then rerun dependencies.")
    entries = tomllib.loads((ROOT / "skills.toml").read_text())["skills"]
    configured = {name for name in OPTIONAL if any(entry.get("selector") == f"{name}@dot-codex" for entry in entries)}
    for name in configured | set(args.with_integration):
        variable = OPTIONAL[name]
        if variable and not os.environ.get(variable):
            raise InstallError(f"Set {variable} before selecting {name}.")


def doctor(args, env):
    if (args.user_home / ".local/state/dot-codex/pending.json").exists():
        raise InstallError("An interrupted filesystem phase needs recovery. Run ./install.sh resume.")
    binary = find_cli(args.user_home, args.codex_bin)
    ui_kv("CLI", f"{binary} ({version_of(binary, env)})")
    home = args.user_home / ".codex"
    if not home.is_dir():
        raise InstallError(f"Codex home unavailable: {home}. Run ./install.sh harness.")
    ui_kv("Codex home", home.resolve())
    service_manifest = args.user_home / ".local/share/dot-codex/service.json"
    if service_manifest.is_file():
        configured = json.loads(service_manifest.read_text())
        if Path(configured["codex_home"]).resolve() != home.resolve():
            raise InstallError("Startup service uses another Codex Home. Rerun ./install.sh service.")
        configured_binary = Path(configured["binary"])
        version_of(configured_binary, env)
        native_binary = home / "packages/standalone/current/codex"
        if not native_binary.is_file() or native_binary.resolve() != configured_binary.resolve():
            raise InstallError("Native daemon package publication is missing or uses another CLI. Rerun ./install.sh cli, then service.")
    for path in [args.user_home / ".local/bin/codex", Path("/usr/local/bin/codex")]:
        if path.is_symlink() and not path.exists() and path.resolve().is_relative_to(args.user_home):
            raise InstallError(f"Broken executable publication: {path}. Run ./install.sh cli.")
    if (args.user_home / ".config/systemd/user/codex-remote-control.service").exists():
        for unit in ("codex-remote-control.service", "codex-remote-control-health.timer"):
            run(["systemctl", "--user", "is-active", "--quiet", unit], env, f"Read {unit}")
            run(["systemctl", "--user", "is-enabled", "--quiet", unit], env, f"Read {unit} startup")
        linger = run(["loginctl", "show-user", str(os.getuid()), "--property=Linger", "--value"], env, "Read lingering")
        if linger.stdout.strip() != "yes":
            raise InstallError("Service lacks boot persistence. Run ./install.sh service --enable-linger.")
        run([binary, "app-server", "daemon", "version"], env, "Read the live local daemon", timeout=20)
        ui_kv("Startup service", "enabled and active; lingering enabled.")
    elif (args.user_home / "Library/LaunchAgents/com.marcocello.codex-remote-control.plist").exists():
        run(["launchctl", "print", f"gui/{os.getuid()}/com.marcocello.codex-remote-control"], env, "Read LaunchAgent")
        run([binary, "app-server", "daemon", "version"], env, "Read the live local daemon", timeout=20)
        ui_kv("Startup service", "LaunchAgent loaded (starts at user login).")
    else:
        ui_kv("Startup service", "not configured. Run ./install.sh service when needed.")
    ui_message("Doctor passed.", "success")
    ui_message("Relay connectivity and an actual reboot were not tested by this read-only check.")


def restore(state: Path):
    receipt = state / "last-activation.json"
    if not receipt.is_file():
        raise InstallError("No home activation is available to restore.")
    transaction = Transaction.load(state, json.loads(receipt.read_text())["transaction"])
    transaction.check_restore()
    transaction.rollback(restore=True)
    receipt.unlink()
    print("Previous home and shell configuration restored. New harness files were retained.")


def execute_phase(name, args, state, env, source):
    if name == "copy":
        copy_harness(source, ROOT, env, resume=getattr(args, "resuming", False))
    elif name == "cli":
        args.codex_bin = str(install_cli(args, state, env))
    elif name == "harness":
        activate_harness(args, state, env)
    elif name == "doctor":
        doctor(args, env)
    elif name == "restore":
        restore(state)
    else:
        binary = find_cli(args.user_home, args.codex_bin)
        version_of(binary, env)
        if name == "dependencies":
            dependency_prerequisites(args, env)
            args.codex_bin = str(binary)
            install_dependencies(args, dict(env, CODEX_HOME=str(ROOT)))
        elif name == "login":
            status = run([binary, "login", "status"], env, "Login status", check=False)
            if status.returncode:
                run([binary, "login", "--device-auth"], env, "Device sign-in", visible=True)
            require_login(binary, env)
            ui_message("Codex login verified.", "success")
        elif name == "service":
            active = args.user_home / ".codex"
            if not active.is_dir():
                raise InstallError("Activate a harness first: ./install.sh harness.")
            configure_service(args, state, binary, active.resolve(), env)
        elif name == "pair":
            require_login(binary, env)
            require_connection(binary, env)
            run([binary, "remote-control", "pair"], env, "Device pairing", visible=True)


def retry_options(args):
    fields = ("codex_bin", "version", "package_file", "sha256", "mode", "service_manager",
              "with_integration", "enable_linger")
    values = {key: str(getattr(args, key)) if isinstance(getattr(args, key), Path) else getattr(args, key)
              for key in fields}
    values["custom_package_url"] = bool(args.package_url)
    return values


def main() -> int:
    global ROOT, COLOR_MODE
    args = parser().parse_args()
    COLOR_MODE = args.color
    explicit_flags = {value.split("=", 1)[0] for value in sys.argv[1:] if value.startswith("--")}
    args.guided = args.wizard or (not args.phase and not args.steps and not
                                 (args.skip_dependencies or args.codex_bin != "codex" or args.with_integration))
    source = ROOT
    current = None
    checkpoint = None
    state = None
    try:
        args.user_home = args.user_home.expanduser().resolve()
        if args.destination:
            args.destination = args.destination.expanduser().absolute()
        ui_banner()
        phases = select_phases(args)
        if not phases:
            ui_message("No phases selected. No changes made.", "skip")
            return 0
        check_paths(args, phases)
        if args.destination:
            ROOT = args.destination.resolve()
            if (args.phase == "all" or args.steps == "all") and not ROOT.exists() and "copy" not in phases and not args.guided:
                phases.insert(0, "copy")
        if "copy" in phases and phases.index("copy") != 0:
            raise InstallError("Put copy first so later phases use the prepared destination.")
        env = dict(os.environ, HOME=str(args.user_home), CODEX_HOME=str(args.user_home / ".codex"))
        checkpoint_path = args.user_home / ".local/state/dot-codex/install.json"
        if phases == ["resume"]:
            args.resuming = True
            if not checkpoint_path.exists():
                raise InstallError("No unfinished installation. Select phases with ./install.sh.")
            checkpoint = json.loads(checkpoint_path.read_text())
            ROOT = Path(checkpoint["destination"])
            phases = [name for name in checkpoint["plan"] if checkpoint["phases"].get(name) != "done"]
            if not phases:
                print("All recorded phases completed. Run ./install.sh doctor for a fresh check.")
                return 0
            for key, value in checkpoint.get("options", {}).items():
                if key == "custom_package_url":
                    if value and not args.package_url and "cli" in phases:
                        raise InstallError("Resume needs the original --package-url again; custom URLs are not saved.")
                    continue
                flag = "--with" if key == "with_integration" else "--" + key.replace("_", "-")
                if flag not in explicit_flags:
                    setattr(args, key, Path(value) if key == "package_file" and value else value)
        ui_section("Install plan")
        ui_kv("User home", args.user_home)
        ui_kv("Harness", ROOT)
        ui_kv("Plan", " -> ".join(phases))
        if args.dry_run:
            for name in phases:
                print(f"  {name}: {PHASES.get(name, 'Recover the previous installation')}")
            ui_message("Dry run: no changes made.", "success")
            return 0
        if args.guided and not args.yes:
            if not confirm("Run this plan?"):
                raise InstallError("Installation cancelled; no phase started.")
        if phases == ["doctor"] and not getattr(args, "resuming", False):
            doctor(args, env)
            return 0
        if "dependencies" in phases and "copy" not in phases:
            dependency_prerequisites(args, env)
            if "cli" not in phases:
                find_cli(args.user_home, args.codex_bin)
        with installation_lock(args.user_home) as state:
            if checkpoint is None:
                checkpoint = {"destination": str(ROOT), "plan": phases, "phases": {}, "options": {}}
            try:
                for number, name in enumerate(phases, 1):
                    current = name
                    checkpoint["phases"][name] = "running"
                    checkpoint["options"] = retry_options(args)
                    save_json(checkpoint_path, checkpoint)
                    ui_section(f"[{number}/{len(phases)}] {PHASE_TITLES[name]}")
                    execute_phase(name, args, state, env, source)
                    checkpoint["phases"][name] = "done"
                    checkpoint["options"] = retry_options(args)
                    save_json(checkpoint_path, checkpoint)
                    ui_message(f"Done: {name}", "success")
            except BaseException as error:
                if current:
                    checkpoint["phases"][current] = "interrupted" if isinstance(error, KeyboardInterrupt) else "failed"
                    checkpoint["options"] = retry_options(args)
                    with ignore_interrupts():
                        save_json(checkpoint_path, checkpoint)
                raise
        print()
        ui_message("Selected phases completed.", "success")
        if "harness" in phases:
            ui_message("Open a new terminal to use the activated harness.")
        if args.skip_dependencies:
            ui_message("Dependencies skipped: rerun ./install.sh dependencies to complete them.", "skip")
        return 0
    except KeyboardInterrupt:
        message = ("Cancelled safely. Completed phases retained; rerun ./install.sh resume."
                   if checkpoint is not None else "Cancelled safely. No phase started.")
        ui_message(message, "skip", stream=sys.stderr)
        return 130
    except (InstallError, OSError, ValueError, KeyError, tarfile.ReadError) as error:
        message = str(error) if isinstance(error, InstallError) else f"{type(error).__name__}; check paths, permissions, and local configuration"
        ui_message(f"Install: {message}", "error", stream=sys.stderr)
        return 1


if __name__ == "__main__":
    import signal

    def cancel(_signal, _frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, cancel)
    raise SystemExit(main())
