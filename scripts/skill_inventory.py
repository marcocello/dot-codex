#!/usr/bin/env python3
"""Reconcile Codex skills and plugins from a source-based TOML inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
from typing import Any
from urllib.request import Request, urlopen
import uuid

import tomllib


METADATA_FILE = ".codex-skill-source.json"
IGNORE_START = "# BEGIN skill_inventory.py managed skills"
IGNORE_END = "# END skill_inventory.py managed skills"
KIND_KEYS = {
    "owned": ("name", "kind", "path"),
    "git": ("name", "kind", "repository", "source_path", "path"),
    "url": ("name", "kind", "url", "sha256", "path"),
    "bundle": ("name", "kind", "url", "path"),
    "plugin": ("name", "kind", "selector", "enabled"),
}
RAW_KINDS = {"git", "url", "bundle"}


class InventoryError(Exception):
    """A user-actionable inventory or provider error."""


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()


def safe_relative(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "." not in path.parts


def entry_errors(entry: object) -> list[str]:
    if not isinstance(entry, dict):
        return ["each [[skills]] entry must be a table"]
    name = entry.get("name")
    kind = entry.get("kind")
    errors: list[str] = []
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        errors.append("skill name must use lowercase letters, digits, and hyphens")
    if kind == "system":
        return errors + [
            f"{name or '<unnamed>'}: system skills are runtime-managed and not allowed in skills.toml"
        ]
    if kind not in KIND_KEYS:
        return errors + [f"{name or '<unnamed>'}: unsupported kind {kind!r}"]
    for key in KIND_KEYS[kind]:
        if key not in entry:
            errors.append(f"{name or '<unnamed>'}: missing {key}")
    for forbidden in ("revision", "version"):
        if forbidden in entry:
            errors.append(f"{name or '<unnamed>'}: {forbidden} is not allowed in skills.toml")
    if (kind == "owned" or kind in RAW_KINDS) and not safe_relative(
        entry.get("path")
    ):
        errors.append(f"{name or '<unnamed>'}: path must be a safe relative path")
    if kind == "git":
        if not safe_relative(entry.get("source_path")):
            errors.append(f"{name or '<unnamed>'}: source_path must be a safe relative path")
        if not isinstance(entry.get("repository"), str) or not entry.get("repository"):
            errors.append(f"{name or '<unnamed>'}: repository must be non-empty")
    if kind in {"url", "bundle"}:
        if not str(entry.get("url", "")).startswith(("https://", "http://")):
            errors.append(f"{name or '<unnamed>'}: url must use HTTP or HTTPS")
    if kind == "url" and not re.fullmatch(
        r"[0-9a-f]{64}", str(entry.get("sha256", ""))
    ):
        errors.append(f"{name or '<unnamed>'}: sha256 must be a 64-character digest")
    if kind == "plugin":
        selector = str(entry.get("selector", ""))
        if not re.fullmatch(r"[^@\s]+@[^@\s]+", selector):
            errors.append(f"{name or '<unnamed>'}: selector must be plugin@marketplace")
        elif selector.endswith("@openai-primary-runtime"):
            errors.append(
                f"{name or '<unnamed>'}: openai-primary-runtime plugins are runtime-managed and not allowed in skills.toml"
            )
        if not isinstance(entry.get("enabled"), bool):
            errors.append(f"{name or '<unnamed>'}: enabled must be true or false")
    return errors


def validate_manifest(data: object) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        raise InventoryError("manifest root must be a TOML table")
    if data.get("schema") != 1:
        raise InventoryError("manifest schema must equal 1")
    entries = data.get("skills", [])
    if not isinstance(entries, list):
        raise InventoryError("manifest skills must be an array of tables")
    errors = [error for entry in entries for error in entry_errors(entry)]
    names = [entry.get("name") for entry in entries if isinstance(entry, dict)]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    errors.extend(f"duplicate skill name: {name}" for name in duplicates)
    if errors:
        raise InventoryError("\n".join(errors))
    return entries


def load_manifest(path: Path) -> list[dict[str, Any]]:
    try:
        data = tomllib.loads(path.read_text())
    except FileNotFoundError as error:
        raise InventoryError(f"manifest not found: {path}") from error
    except tomllib.TOMLDecodeError as error:
        raise InventoryError(f"invalid TOML in {path}: {error}") from error
    return validate_manifest(data)


def toml_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    raise InventoryError(f"cannot serialize manifest value {value!r}")


def write_manifest(path: Path, entries: list[dict[str, Any]]) -> None:
    lines = ["schema = 1", ""]
    for entry in entries:
        lines.append("[[skills]]")
        for key in KIND_KEYS[entry["kind"]]:
            lines.append(f"{key} = {toml_value(entry[key])}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text("\n".join(lines))
    os.replace(temporary, path)


def run_provider(command: list[str], *, label: str) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(command, text=True, capture_output=True)
    except FileNotFoundError as error:
        raise InventoryError(f"{label} executable not found: {command[0]}") from error
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise InventoryError(f"{label} failed: {detail}")
    return result


def plugin_state(codex_bin: str) -> dict[str, dict[str, Any]]:
    result = run_provider(
        [codex_bin, "plugin", "list", "--json"], label="codex plugin list"
    )
    try:
        payload = json.loads(result.stdout)
        installed = payload["installed"]
        return {item["pluginId"]: item for item in installed if item.get("installed")}
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise InventoryError("codex plugin list returned invalid JSON") from error


def expected_metadata(
    entry: dict[str, Any],
    resolved_revision: str | None = None,
    resolved_version: str | None = None,
) -> dict[str, Any]:
    keys = KIND_KEYS[entry["kind"]]
    metadata = {key: entry[key] for key in keys if key != "path"}
    if entry["kind"] == "git" and resolved_revision is not None:
        metadata["resolved_revision"] = resolved_revision
    if entry["kind"] == "bundle" and resolved_version is not None:
        metadata["resolved_version"] = resolved_version
    return metadata


def read_metadata(destination: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads((destination / METADATA_FILE).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def managed_identity_matches(metadata: dict[str, Any] | None, entry: dict[str, Any]) -> bool:
    return bool(
        metadata
        and metadata.get("name") == entry["name"]
        and metadata.get("kind") == entry["kind"]
    )


def metadata_matches(
    destination: Path,
    entry: dict[str, Any],
    resolved_revision: str | None = None,
    resolved_version: str | None = None,
) -> bool:
    metadata = read_metadata(destination)
    if metadata is None:
        return False
    expected = expected_metadata(entry)
    if any(metadata.get(key) != value for key, value in expected.items()):
        return False
    if entry["kind"] == "git":
        installed_revision = metadata.get("resolved_revision")
        if not re.fullmatch(r"[0-9a-f]{40}", str(installed_revision or "")):
            return False
        return resolved_revision is None or installed_revision == resolved_revision
    if entry["kind"] == "bundle":
        installed_version = metadata.get("resolved_version")
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", str(installed_version or "")):
            return False
        return resolved_version is None or installed_version == resolved_version
    return metadata == expected


def resolve_git_head(entry: dict[str, Any]) -> str:
    result = run_provider(
        ["git", "ls-remote", entry["repository"], "HEAD"],
        label=f"resolve {entry['name']} HEAD",
    )
    revision = result.stdout.split(maxsplit=1)[0] if result.stdout.strip() else ""
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise InventoryError(f"{entry['name']}: provider returned an invalid HEAD revision")
    return revision


def contained_destination(entry: dict[str, Any], skills_root: Path) -> Path:
    root = skills_root.resolve(strict=False)
    current = root
    for part in PurePosixPath(entry["path"]).parts:
        current /= part
        if current.is_symlink():
            raise InventoryError(
                f"{entry['name']}: symlinked destination path is not allowed: {current}"
            )
    try:
        current.resolve(strict=False).relative_to(root)
    except ValueError as error:
        raise InventoryError(
            f"{entry['name']}: destination escapes the selected skill root"
        ) from error
    return current


def checked_git_source(entry: dict[str, Any], checkout: Path) -> Path:
    root = checkout.resolve()
    current = root
    for part in PurePosixPath(entry["source_path"]).parts:
        current /= part
        if current.is_symlink():
            raise InventoryError(
                f"{entry['name']}: symlinked Git source is not allowed: {current}"
            )
    try:
        current.resolve(strict=True).relative_to(root)
    except (FileNotFoundError, ValueError) as error:
        raise InventoryError(f"{entry['name']}: Git source escapes its checkout") from error
    symlink = next((item for item in current.rglob("*") if item.is_symlink()), None)
    if symlink:
        raise InventoryError(
            f"{entry['name']}: symlinked Git source payload is not allowed: {symlink}"
        )
    return current


def build_git_skill(entry: dict[str, Any], staging: Path, revision: str) -> None:
    checkout = staging.parent / "checkout"
    run_provider(
        ["git", "clone", "--quiet", "--no-checkout", entry["repository"], str(checkout)],
        label=f"clone {entry['name']}",
    )
    run_provider(
        [
            "git",
            "-C",
            str(checkout),
            "checkout",
            "--quiet",
            revision,
            "--",
            entry["source_path"],
        ],
        label=f"checkout {entry['name']}",
    )
    source = checked_git_source(entry, checkout)
    if not (source / "SKILL.md").is_file():
        raise InventoryError(f"{entry['name']}: source_path does not contain SKILL.md")
    shutil.copytree(source, staging)


def build_url_skill(entry: dict[str, Any], staging: Path) -> None:
    context = verified_ssl_context()
    request = Request(entry["url"], headers={"User-Agent": "dot-codex-skill-inventory/1"})
    try:
        with urlopen(request, timeout=30, context=context) as response:  # noqa: S310
            content = response.read()
    except OSError as error:
        raise InventoryError(f"download {entry['name']} failed: {error}") from error
    digest = hashlib.sha256(content).hexdigest()
    if digest != entry["sha256"]:
        raise InventoryError(
            f"{entry['name']}: SHA-256 mismatch; expected {entry['sha256']}, got {digest}"
        )
    staging.mkdir()
    (staging / "SKILL.md").write_bytes(content)


def fetch_bundle(entry: dict[str, Any]) -> tuple[str, list[tuple[PurePosixPath, str]]]:
    context = verified_ssl_context()
    request = Request(entry["url"], headers={"User-Agent": "dot-codex-skill-inventory/1"})
    try:
        with urlopen(request, timeout=30, context=context) as response:  # noqa: S310
            payload = json.loads(response.read())
    except (OSError, json.JSONDecodeError) as error:
        raise InventoryError(f"download {entry['name']} bundle failed: {error}") from error
    if not isinstance(payload, dict):
        raise InventoryError(f"{entry['name']}: bundle response must be a JSON object")
    version = payload.get("version")
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", str(version or "")):
        raise InventoryError(f"{entry['name']}: bundle version is invalid")
    raw_files = payload.get("files")
    if not isinstance(raw_files, list) or not raw_files or len(raw_files) > 256:
        raise InventoryError(f"{entry['name']}: bundle files must contain 1-256 entries")
    files: list[tuple[PurePosixPath, str]] = []
    seen: set[str] = set()
    for raw_file in raw_files:
        if not isinstance(raw_file, dict):
            raise InventoryError(f"{entry['name']}: bundle file entry must be an object")
        path = raw_file.get("path")
        content = raw_file.get("content")
        if not safe_relative(path) or path == METADATA_FILE or not isinstance(content, str):
            raise InventoryError(f"{entry['name']}: bundle contains an invalid file entry")
        if path in seen:
            raise InventoryError(f"{entry['name']}: bundle contains duplicate path {path}")
        seen.add(path)
        files.append((PurePosixPath(path), content))
    if "SKILL.md" not in seen:
        raise InventoryError(f"{entry['name']}: bundle does not contain SKILL.md")
    return str(version), files


def build_bundle_skill(
    entry: dict[str, Any], staging: Path, files: list[tuple[PurePosixPath, str]]
) -> None:
    staging.mkdir()
    for relative_path, content in files:
        destination = staging.joinpath(*relative_path.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content)


def verified_ssl_context() -> ssl.SSLContext:
    candidates = [
        os.environ.get("SSL_CERT_FILE"),
        ssl.get_default_verify_paths().cafile,
        "/etc/ssl/cert.pem",
        "/opt/homebrew/etc/openssl@3/cert.pem",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return ssl.create_default_context(cafile=candidate)
    return ssl.create_default_context()


def replace_destination(staging: Path, destination: Path) -> None:
    backup = destination.parent / f".{destination.name}.backup-{uuid.uuid4().hex}"
    if not destination.exists():
        staging.rename(destination)
        return
    destination.rename(backup)
    try:
        staging.rename(destination)
    except Exception:
        backup.rename(destination)
        raise
    shutil.rmtree(backup)


def install_raw_skill(entry: dict[str, Any], skills_root: Path) -> bool:
    destination = contained_destination(entry, skills_root)
    resolved_revision = resolve_git_head(entry) if entry["kind"] == "git" else None
    resolved_version = None
    bundle_files = None
    if entry["kind"] == "bundle":
        resolved_version, bundle_files = fetch_bundle(entry)
    if destination.exists() and metadata_matches(
        destination, entry, resolved_revision, resolved_version
    ):
        if not (destination / "SKILL.md").is_file():
            raise InventoryError(f"{entry['name']}: managed destination lacks SKILL.md")
        return False
    metadata = read_metadata(destination) if destination.exists() else None
    if destination.exists() and not managed_identity_matches(metadata, entry):
        raise InventoryError(f"{entry['name']}: refusing to overwrite unmanaged destination")
    skills_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".skill-install-", dir=skills_root) as temp:
        temporary = Path(temp)
        staging = temporary / "staging"
        if entry["kind"] == "git":
            assert resolved_revision is not None
            build_git_skill(entry, staging, resolved_revision)
        elif entry["kind"] == "bundle":
            assert bundle_files is not None
            build_bundle_skill(entry, staging, bundle_files)
        else:
            build_url_skill(entry, staging)
        (staging / METADATA_FILE).write_text(
            json.dumps(
                expected_metadata(entry, resolved_revision, resolved_version),
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        replace_destination(staging, destination)
    return True


def local_skill_error(entry: dict[str, Any], skills_root: Path) -> str | None:
    if entry["kind"] in RAW_KINDS:
        destination = contained_destination(entry, skills_root)
    else:
        destination = skills_root / entry["path"]
    if not (destination / "SKILL.md").is_file():
        return f"{entry['name']}: missing {destination / 'SKILL.md'}"
    if entry["kind"] in RAW_KINDS and not metadata_matches(destination, entry):
        return f"{entry['name']}: installer metadata does not match the manifest source"
    if entry["kind"] in RAW_KINDS:
        symlink = next((item for item in destination.rglob("*") if item.is_symlink()), None)
        if symlink:
            return f"{entry['name']}: managed skill contains a symlink: {symlink}"
    return None


def plugin_error(entry: dict[str, Any], state: dict[str, dict[str, Any]]) -> str | None:
    installed = state.get(entry["selector"])
    if not installed:
        return f"{entry['name']}: plugin {entry['selector']} is not installed"
    if installed.get("enabled") is not entry["enabled"]:
        return (
            f"{entry['name']}: plugin enabled={installed.get('enabled')!r}, "
            f"expected {entry['enabled']!r}"
        )
    return None


def find_git_paths(manifest: Path, skills_root: Path) -> tuple[Path, str] | None:
    root_result = subprocess.run(
        ["git", "-C", str(manifest.parent), "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
    )
    if root_result.returncode != 0:
        return None
    repo_root = Path(root_result.stdout.strip()).resolve()
    try:
        relative_skills = skills_root.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return None
    return repo_root / ".gitignore", relative_skills


def update_generated_ignores(
    manifest: Path, skills_root: Path, entries: list[dict[str, Any]]
) -> None:
    paths = find_git_paths(manifest, skills_root)
    if not paths:
        return
    ignore_file, relative_skills = paths
    current = ignore_file.read_text() if ignore_file.exists() else ""
    before, marker, remainder = current.partition(IGNORE_START)
    if marker:
        _, end, after = remainder.partition(IGNORE_END)
        if not end:
            raise InventoryError(f"unterminated managed block in {ignore_file}")
        current = before.rstrip() + ("\n" + after.lstrip() if after.strip() else "")
    managed = sorted(entry["path"] for entry in entries if entry["kind"] in RAW_KINDS)
    block = [IGNORE_START]
    block.extend(f"{relative_skills}/{path}/" for path in managed)
    block.append(IGNORE_END)
    content = current.rstrip() + "\n\n" + "\n".join(block) + "\n"
    ignore_file.write_text(content.lstrip("\n"))


def selected_entries(
    entries: list[dict[str, Any]], only: str | None
) -> list[dict[str, Any]]:
    if only is None:
        return entries
    matches = [entry for entry in entries if entry["name"] == only]
    if not matches:
        raise InventoryError(f"unknown skill: {only}")
    return matches


def sync_entries(args: argparse.Namespace, entries: list[dict[str, Any]]) -> None:
    targets = selected_entries(entries, args.only)
    plugins = [entry for entry in targets if entry["kind"] == "plugin"]
    state = plugin_state(args.codex_bin) if plugins else {}
    changed = False
    errors: list[str] = []
    for entry in targets:
        kind = entry["kind"]
        if kind == "owned":
            error = local_skill_error(entry, args.skills_root)
            if error:
                errors.append(error)
        elif kind in RAW_KINDS:
            if install_raw_skill(entry, args.skills_root):
                source_label = {"url": "URL", "git": "git", "bundle": "bundle"}[kind]
                print(f"installed {source_label} skill {entry['name']}")
                changed = True
        elif entry["selector"] not in state:
            run_provider(
                [args.codex_bin, "plugin", "add", entry["selector"], "--json"],
                label=f"install plugin {entry['selector']}",
            )
            print(f"installed plugin {entry['selector']}")
            changed = True
    if plugins:
        state = plugin_state(args.codex_bin)
        errors.extend(error for entry in plugins if (error := plugin_error(entry, state)))
    update_generated_ignores(args.manifest, args.skills_root, entries)
    if errors:
        raise InventoryError("\n".join(errors))
    if not changed:
        print("already synchronized")


def command_list(args: argparse.Namespace) -> None:
    entries = load_manifest(args.manifest)
    for entry in entries:
        kind = entry["kind"]
        if kind == "owned":
            detail = entry["path"]
        elif kind == "git":
            detail = entry["repository"]
        elif kind == "url":
            detail = entry["sha256"]
        elif kind == "bundle":
            detail = entry["url"]
        else:
            detail = f"{entry['selector']} enabled={str(entry['enabled']).lower()}"
        print(f"{entry['name']}\t{kind}\t{detail}")


def command_doctor(args: argparse.Namespace) -> None:
    entries = load_manifest(args.manifest)
    plugins = [entry for entry in entries if entry["kind"] == "plugin"]
    state = plugin_state(args.codex_bin) if plugins else {}
    errors: list[str] = []
    for entry in entries:
        if entry["kind"] == "plugin":
            error = plugin_error(entry, state)
        else:
            error = local_skill_error(entry, args.skills_root)
        if error:
            errors.append(error)
    if errors:
        raise InventoryError("\n".join(errors))
    print(f"doctor: healthy ({len(entries)} dependencies)")


def entry_from_add_args(args: argparse.Namespace) -> dict[str, Any]:
    entry: dict[str, Any] = {"name": args.name, "kind": args.kind}
    if args.kind == "owned":
        entry["path"] = args.path or args.name
    elif args.kind == "git":
        entry.update(
            repository=args.repository,
            source_path=args.source_path,
            path=args.path or args.name,
        )
    elif args.kind == "url":
        entry.update(url=args.url, sha256=args.sha256, path=args.path or args.name)
    elif args.kind == "bundle":
        entry.update(url=args.url, path=args.path or args.name)
    else:
        entry.update(
            selector=args.selector,
            enabled=args.enabled == "true",
        )
    errors = entry_errors(entry)
    if errors:
        raise InventoryError("\n".join(errors))
    return entry


def command_add(args: argparse.Namespace) -> None:
    entries = load_manifest(args.manifest)
    if any(entry["name"] == args.name for entry in entries):
        raise InventoryError(f"skill already declared: {args.name}")
    entry = entry_from_add_args(args)
    entries.append(entry)
    write_manifest(args.manifest, entries)
    print(f"added {args.name} to {args.manifest}")
    if not args.no_sync:
        args.only = args.name
        sync_entries(args, entries)


def updated_entry(entry: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    result = dict(entry)
    supplied: set[str] = set()
    for key in ("sha256", "url"):
        value = getattr(args, key)
        if value is not None:
            result[key] = value
            supplied.add(key)
    if args.enabled is not None:
        result["enabled"] = args.enabled == "true"
        supplied.add("enabled")
    if not supplied and entry["kind"] not in {"git", "bundle", "plugin"}:
        raise InventoryError("update requires a URL or SHA-256 for this dependency")
    allowed = {
        "owned": set(),
        "git": set(),
        "url": {"url", "sha256"},
        "bundle": {"url"},
        "plugin": {"enabled"},
    }[entry["kind"]]
    invalid = sorted(supplied - allowed)
    if invalid:
        raise InventoryError(
            f"{entry['name']}: cannot update {', '.join(invalid)} for kind {entry['kind']}"
        )
    errors = entry_errors(result)
    if errors:
        raise InventoryError("\n".join(errors))
    return result


def command_update(args: argparse.Namespace) -> None:
    entries = load_manifest(args.manifest)
    index = next((i for i, entry in enumerate(entries) if entry["name"] == args.name), None)
    if index is None:
        raise InventoryError(f"unknown skill: {args.name}")
    entries[index] = updated_entry(entries[index], args)
    write_manifest(args.manifest, entries)
    print(f"updated {args.name} in {args.manifest}")
    if not args.no_sync:
        if entries[index]["kind"] == "plugin":
            uninstall_entry(args, entries[index])
        args.only = args.name
        sync_entries(args, entries)


def uninstall_entry(args: argparse.Namespace, entry: dict[str, Any]) -> None:
    if entry["kind"] in RAW_KINDS:
        destination = contained_destination(entry, args.skills_root)
        if destination.exists():
            if not managed_identity_matches(read_metadata(destination), entry):
                raise InventoryError(f"{entry['name']}: refusing to remove unmanaged destination")
            shutil.rmtree(destination)
            print(f"removed managed skill {entry['name']}")
    elif entry["kind"] == "plugin":
        state = plugin_state(args.codex_bin)
        if entry["selector"] in state:
            run_provider(
                [args.codex_bin, "plugin", "remove", entry["selector"], "--json"],
                label=f"remove plugin {entry['selector']}",
            )
            print(f"removed plugin {entry['selector']}")


def command_remove(args: argparse.Namespace) -> None:
    entries = load_manifest(args.manifest)
    entry = next((item for item in entries if item["name"] == args.name), None)
    if entry is None:
        raise InventoryError(f"unknown skill: {args.name}")
    if not args.keep_installed:
        uninstall_entry(args, entry)
    retained = [item for item in entries if item["name"] != args.name]
    write_manifest(args.manifest, retained)
    update_generated_ignores(args.manifest, args.skills_root, retained)
    print(f"removed {args.name} from {args.manifest}")


def build_parser() -> argparse.ArgumentParser:
    home = default_codex_home()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=home / "skills.toml")
    parser.add_argument("--skills-root", type=Path, default=home / "skills")
    parser.add_argument("--codex-bin", default="codex")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="print desired skill dependencies").set_defaults(
        handler=command_list
    )
    commands.add_parser("doctor", help="report manifest and installation drift").set_defaults(
        handler=command_doctor
    )
    sync = commands.add_parser("sync", help="reconcile declared dependencies without pruning")
    sync.add_argument("--only", help="reconcile one named dependency")
    sync.set_defaults(handler=lambda args: sync_entries(args, load_manifest(args.manifest)))
    add = commands.add_parser("add", help="declare and reconcile one dependency")
    add.add_argument("name")
    add.add_argument("--kind", required=True, choices=sorted(KIND_KEYS))
    add.add_argument("--path")
    add.add_argument("--repository")
    add.add_argument("--source-path")
    add.add_argument("--url")
    add.add_argument("--sha256")
    add.add_argument("--selector")
    add.add_argument("--enabled", choices=("true", "false"), default="true")
    add.add_argument("--no-sync", action="store_true", help="write desired state only")
    add.set_defaults(handler=command_add)
    update = commands.add_parser("update", help="refresh one dependency from its provider")
    update.add_argument("name")
    update.add_argument("--url")
    update.add_argument("--sha256")
    update.add_argument("--enabled", choices=("true", "false"))
    update.add_argument("--no-sync", action="store_true", help="write desired state only")
    update.set_defaults(handler=command_update)
    remove = commands.add_parser("remove", help="uninstall and remove desired state")
    remove.add_argument("name")
    remove.add_argument("--keep-installed", action="store_true")
    remove.set_defaults(handler=command_remove)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.handler(args)
    except InventoryError as error:
        for line in str(error).splitlines():
            print(f"error: {line}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
