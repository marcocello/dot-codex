#!/usr/bin/env python3
"""Persist and resolve harness-local knowledge connections (Python 3.11+)."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import sys
import stat
import tempfile
import tomllib
import uuid


sys.path.insert(0, str(Path(__file__).resolve().parent))
from clickup_http import APIError, read_token


class ProfileError(Exception):
    """Configuration cannot safely identify a destination."""


class SetupRequired(ProfileError):
    """The invoking agent must run knowledge-tool-connect and ask the user."""


def setup_error(message: str) -> int:
    print(json.dumps({"code": "SETUP_REQUIRED", "skill": "knowledge-tool-connect", "message": message}), file=sys.stderr)
    return 3


API_FIELDS = {"transport", "token", "token_env", "token_file", "auth_type"}
REMOTE_FIELDS = {"connection", "account", "workspace_id"}
DESTINATION_FIELDS = {"destination", "tasks", "deals", "ideas"}
PROVIDERS = {"clickup", "notion", "markdown", "none"}
NAME = re.compile(r"[a-z0-9][a-z0-9_-]*\Z")


def require_text(value: object, field: str) -> str:
    if (not isinstance(value, str) or not value.strip() or value != value.strip()
            or any(ord(char) < 32 or ord(char) == 127 for char in value)
            or "<" in value or ">" in value or value in {"...", "…"}):
        raise ProfileError(f"{field}: supply a concrete, nonempty value, not a placeholder")
    return value


def validate_profile(name: str, profile: object) -> None:
    if not NAME.fullmatch(name):
        raise ProfileError("Profile names must use lowercase letters, digits, hyphens or underscores")
    if not isinstance(profile, dict):
        raise ProfileError(f"{name}: expected a profile table")
    provider = profile.get("provider")
    if not isinstance(provider, str) or provider not in PROVIDERS:
        raise ProfileError(f"{name}: unsupported provider")
    required = REMOTE_FIELDS if provider in {"notion", "clickup"} else (
        {"root"} if provider == "markdown" else set()
    )
    optional = API_FIELDS | DESTINATION_FIELDS if provider in {"clickup", "notion"} else set()
    if not required <= set(profile) or set(profile) - (required | optional | {"provider"}):
        raise ProfileError(f"{name}: invalid profile fields")
    for key in (required | (optional & set(profile))) - {"token"}:
        require_text(profile[key], f"{name}.{key}")
    if provider in {"clickup", "notion"}:
        transport = profile.get("transport", "mcp")
        if transport not in {"mcp", "api"}:
            raise ProfileError("Remote transport must be mcp or api")
        if transport == "api" or set(profile) & {"token", "token_env", "token_file", "auth_type"}:
            if len(set(profile) & {"token", "token_env", "token_file"}) != 1:
                raise ProfileError("API profiles require exactly one token, token_env or token_file")
            if "token" in profile:
                read_token({"token": profile["token"]})
            default_auth = "personal" if provider == "clickup" else "internal"
            if profile.get("auth_type", default_auth) not in {default_auth, "oauth"}:
                raise ProfileError(f"auth_type must be {default_auth} or oauth")
            if "token_env" in profile and not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", profile["token_env"]):
                raise ProfileError("token_env must be an environment variable name, not a token")
            if "token_file" in profile and not Path(profile["token_file"]).is_absolute():
                raise ProfileError("token_file must be an absolute private file path")
            for key in {"account", "workspace_id", "tasks", "deals", "ideas"} & set(profile):
                if provider == "clickup":
                    if not re.fullmatch(r"[0-9]+", profile[key]):
                        raise ProfileError(f"API {key} must be a numeric ClickUp ID")
                else:
                    try:
                        uuid.UUID(profile[key])
                    except ValueError:
                        raise ProfileError(f"API {key} must be a Notion UUID") from None
    if provider == "markdown":
        root = Path(profile["root"])
        if not root.is_absolute() or root == Path(root.anchor) or ".." in root.parts:
            raise ProfileError(f"{name}.root: use an absolute directory below the filesystem root")
        if root.exists() and not root.is_dir():
            raise ProfileError(f"{name}.root: expected a directory")


def validate_config(config: object) -> dict:
    if not isinstance(config, dict) or set(config) - {"version", "default_profile", "profiles"}:
        raise ProfileError("Expected version, optional default_profile, and profiles only")
    if type(config.get("version")) is not int or config["version"] != 1:
        raise ProfileError("Unsupported knowledge configuration version; expected version = 1")
    profiles = config.get("profiles")
    if not isinstance(profiles, dict):
        raise ProfileError("Expected a profiles table")
    for name, profile in profiles.items():
        validate_profile(name, profile)
    if "default_profile" in config:
        default = config["default_profile"]
        if not isinstance(default, str) or default not in profiles:
            raise ProfileError("default_profile must name a configured profile")
    return config


def read_config(path: Path, *, allow_missing: bool = False) -> dict:
    if path.is_symlink():
        raise ProfileError("Use a regular knowledge configuration file, not a symlink")
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "r", encoding="utf-8") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise ProfileError("Knowledge configuration must be a regular file")
            content = stream.read()
    except FileNotFoundError:
        if allow_missing:
            return {"version": 1, "profiles": {}}
        raise SetupRequired("Invoke knowledge-tool-connect now, ask for the default destination, then resume the pending request after setup") from None
    try:
        config = validate_config(tomllib.loads(content))
        if any("token" in p for p in config["profiles"].values()):
            if info.st_uid != os.getuid() or info.st_mode & 0o077:
                raise ProfileError("Inline-token configuration must be owner-owned and private (chmod 600)")
        return config
    except (tomllib.TOMLDecodeError, UnicodeError):
        raise ProfileError("Invalid knowledge TOML; repair it explicitly before proceeding") from None


def resolve(config: dict, name: str | None, transport: str | None = None) -> dict:
    selected = name if name is not None else config.get("default_profile")
    if selected is None:
        raise SetupRequired("Invoke knowledge-tool-connect now, ask which configured profile to use as default, then resume the pending request")
    if selected not in config["profiles"]:
        raise ProfileError("Unknown profile; use list to inspect configured profiles")
    profile = dict(config["profiles"][selected])
    if transport is not None:
        if profile["provider"] not in {"clickup", "notion"}:
            raise ProfileError("Transport selection applies only to remote connections")
        if transport == "api" and not (profile.get("token") or profile.get("token_env") or profile.get("token_file")):
            raise SetupRequired("Invoke knowledge-tool-connect to configure an API credential, then resume the requested transport switch")
        profile["transport"] = transport
        validate_profile(selected, profile)
    return {"profile": selected, **profile}


def encode(config: dict) -> str:
    lines = ["# Private harness configuration. May contain API tokens; never commit this file.", "version = 1"]
    if "default_profile" in config:
        lines.append(f'default_profile = {json.dumps(config["default_profile"])}')
    lines.extend(["", "[profiles]"])
    for name, profile in sorted(config["profiles"].items()):
        lines.extend(["", f"[profiles.{name}]"])
        for key, value in sorted(profile.items()):
            lines.append(f"{key} = {json.dumps(value, ensure_ascii=False)}")
    return "\n".join(lines) + "\n"


def write_atomic(path: Path, config: dict) -> None:
    validate_config(config)
    fd, temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(encode(config))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def mutate(path: Path, args: argparse.Namespace) -> dict:
    profile = None
    if args.command == "put":
        profile = {key: getattr(args, key, None) for key in {"provider", "root"} | REMOTE_FIELDS | DESTINATION_FIELDS | API_FIELDS
                   if getattr(args, key, None) is not None}
        validate_profile(args.name, profile)
    # Validate before creating a lock or parent directory; validate again inside the lock.
    read_config(path, allow_missing=args.command == "put")
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(path.name + ".lock")
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        config = read_config(path, allow_missing=args.command == "put")
        if args.command == "put":
            config["profiles"][args.name] = profile
            if args.default:
                config["default_profile"] = args.name
        elif args.command == "default":
            resolve(config, args.name)
            config["default_profile"] = args.name
        else:
            resolve(config, args.name)
            profile = dict(config["profiles"][args.name])
            if profile["provider"] not in {"clickup", "notion"}:
                raise ProfileError("Credentials and transport apply only to remote connections")
            if args.command == "credentials":
                previous_auth = profile.get("auth_type")
                token = None
                if args.import_current:
                    token = read_token(profile)
                elif args.token_stdin:
                    supplied = sys.stdin.read(16386)
                    if len(supplied) >= 16386:
                        raise ProfileError("Token input exceeds the size limit")
                    token = read_token({"token": supplied.strip()})
                for key in ("token", "token_env", "token_file", "auth_type"):
                    profile.pop(key, None)
                if token is not None:
                    profile["token"] = token
                    if previous_auth is not None:
                        profile["auth_type"] = previous_auth
                profile.update({key: getattr(args, key) for key in ("token_env", "token_file", "auth_type")
                                if getattr(args, key, None) is not None})
            else:
                profile["transport"] = args.transport
            validate_profile(args.name, profile)
            config["profiles"][args.name] = profile
        write_atomic(path, config)
        return resolve(config, args.name)



def redact(value):
    """Keep runtime credentials available internally, never in CLI receipts."""
    if isinstance(value, dict):
        return {key: "[redacted]" if key == "token" else redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    home = Path(os.environ.get("CODEX_HOME") or str(Path.home() / ".codex")).expanduser()
    parser.add_argument("--config", type=Path, default=home / "knowledge.toml")
    commands = parser.add_subparsers(dest="command", required=True)
    put = commands.add_parser("put", help="Save one complete profile; default changes only with --default")
    put.add_argument("name")
    put.add_argument("--provider", choices=sorted(PROVIDERS), required=True)
    for field in sorted((REMOTE_FIELDS | DESTINATION_FIELDS | API_FIELDS | {"root"}) - {"token"}):
        put.add_argument("--" + field.replace("_", "-"))
    put.add_argument("--default", action="store_true")
    default = commands.add_parser("default", help="Persist the default profile")
    default.add_argument("name")
    resolution = commands.add_parser("resolve", help="Resolve routing without provider access")
    resolution.add_argument("--profile")
    resolution.add_argument("--transport", choices=("mcp", "api"))
    credentials = commands.add_parser("credentials", help="Attach or replace an inline credential or reference without printing its value")
    credentials.add_argument("name")
    binding = credentials.add_mutually_exclusive_group(required=True)
    binding.add_argument("--token-env")
    binding.add_argument("--token-file")
    binding.add_argument("--token-stdin", action="store_true", help="Save a token received on stdin into private knowledge.toml")
    binding.add_argument("--import-current", action="store_true", help="Privately import the selected current credential inline")
    credentials.add_argument("--auth-type")
    transport = commands.add_parser("transport", help="Explicitly persist preferred transport")
    transport.add_argument("name")
    transport.add_argument("transport", choices=("mcp", "api"))
    commands.add_parser("list", help="List configured profiles, not connected accounts")
    args = parser.parse_args()
    try:
        if args.command in {"put", "default", "credentials", "transport"}:
            output = mutate(args.config, args)
        else:
            config = read_config(args.config)
            output = resolve(config, args.profile, args.transport) if args.command == "resolve" else {
                "default_profile": config.get("default_profile"), "profiles": config["profiles"]}
        print(json.dumps(redact(output), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except SetupRequired as exc:
        return setup_error(str(exc))
    except (APIError, ProfileError, OSError, UnicodeError) as exc:
        print(f"knowledge_profile: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
