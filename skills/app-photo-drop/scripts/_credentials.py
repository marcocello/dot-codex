#!/usr/bin/env python3
from __future__ import annotations

import os
import platform
import re
import stat
from collections.abc import Mapping
from pathlib import Path
from typing import Iterable

from _runtime import RUNTIME_ROOT


TOKEN_URL = "https://dashboard.ngrok.com/get-started/your-authtoken"
CREDENTIAL_DIR = RUNTIME_ROOT / "credentials"
NGROK_TOKEN_FILE = CREDENTIAL_DIR / "ngrok-authtoken"
MAX_CONFIG_BYTES = 1024 * 1024
_PLAIN_TOKEN = re.compile(r"^[A-Za-z0-9._-]+$")
_MAPPING_LINE = re.compile(r"^( *)([A-Za-z0-9_-]+)\s*:\s*(.*)$")


class CredentialError(ValueError):
    pass


def configure_command() -> str:
    return f"python3 {Path(__file__).with_name('configure_ngrok.py')}"


def missing_credential_message() -> str:
    return (
        "No ngrok agent authtoken was found in the environment, Photo Drop state, or standard ngrok config. "
        f"Get it from {TOKEN_URL}, then run: {configure_command()}"
    )


def resolve_ngrok_authtoken(environment: Mapping[str, str] | None = None) -> str:
    token, _ = resolve_ngrok_credential(environment)
    return token


def resolve_ngrok_credential(
    environment: Mapping[str, str] | None = None,
    *,
    system_paths: Iterable[Path] | None = None,
) -> tuple[str, str]:
    found = find_ngrok_credential(environment, system_paths=system_paths)
    if found is None:
        raise CredentialError(missing_credential_message())
    return found


def find_ngrok_credential(
    environment: Mapping[str, str] | None = None,
    *,
    system_paths: Iterable[Path] | None = None,
) -> tuple[str, str] | None:
    source = os.environ if environment is None else environment
    inherited = source.get("NGROK_AUTHTOKEN", "").strip()
    if inherited:
        return inherited, "environment"
    stored = read_stored_ngrok_authtoken()
    if stored:
        return stored, "photo_drop"
    paths = tuple(system_paths) if system_paths is not None else default_ngrok_config_paths(
        environment=source
    )
    system = read_system_ngrok_authtoken(paths)
    if system:
        return system[0], "ngrok_config"
    return None


def default_ngrok_config_paths(
    *,
    home: Path | None = None,
    platform_name: str | None = None,
    environment: Mapping[str, str] | None = None,
) -> tuple[Path, ...]:
    source = os.environ if environment is None else environment
    user_home = Path.home() if home is None else Path(home)
    current_platform = platform.system() if platform_name is None else platform_name
    if current_platform == "Darwin":
        current = user_home / "Library" / "Application Support" / "ngrok" / "ngrok.yml"
    elif current_platform == "Windows":
        local_app_data = source.get("LOCALAPPDATA", "").strip()
        current = (
            Path(local_app_data) / "ngrok" / "ngrok.yml"
            if local_app_data
            else user_home / "AppData" / "Local" / "ngrok" / "ngrok.yml"
        )
    else:
        current = user_home / ".config" / "ngrok" / "ngrok.yml"
    return current, user_home / ".ngrok2" / "ngrok.yml"


def read_system_ngrok_authtoken(paths: Iterable[Path]) -> tuple[str, Path] | None:
    for candidate in paths:
        path = Path(candidate)
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            continue
        except OSError as error:
            raise CredentialError(f"Cannot inspect standard ngrok config: {error}") from error
        _require_private_system_config(path, metadata)
        text = _read_system_config(path, metadata)
        token = parse_ngrok_authtoken(text, path)
        if token:
            return token, path
    return None


def parse_ngrok_authtoken(text: str, source: Path) -> str | None:
    del source
    version: str | None = None
    top_level: str | None = None
    agent_value: str | None = None
    seen_agent = False
    mapping_stack: list[tuple[int, str]] = []
    child_indents: dict[tuple[str, ...], int] = {}
    for raw_line in text.lstrip("\ufeff").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if "\t" in raw_line:
            if "authtoken" in raw_line:
                raise CredentialError("Standard ngrok config has malformed credential indentation")
            continue
        matched = _MAPPING_LINE.fullmatch(raw_line)
        if not matched:
            if "authtoken" in raw_line:
                raise CredentialError("Standard ngrok config has a malformed credential field")
            continue
        indentation, key, raw_value = matched.groups()
        depth = len(indentation)
        while mapping_stack and depth <= mapping_stack[-1][0]:
            mapping_stack.pop()
        parent_path = tuple(item[1] for item in mapping_stack)
        if depth and not parent_path:
            if key == "authtoken":
                raise CredentialError("Standard ngrok config has malformed credential indentation")
            continue
        if parent_path:
            expected_indent = child_indents.setdefault(parent_path, depth)
            if depth != expected_indent:
                if key == "authtoken":
                    raise CredentialError("Standard ngrok config has malformed credential indentation")
                continue
        if depth == 0:
            if key == "version":
                if version is not None:
                    raise CredentialError("Standard ngrok config has duplicate version fields")
                version = _parse_yaml_scalar(raw_value, "version")
            elif key == "agent":
                if seen_agent:
                    raise CredentialError("Standard ngrok config has duplicate agent fields")
                seen_agent = True
                if _without_comment(raw_value):
                    raise CredentialError("Standard ngrok config has a non-mapping agent field")
            elif key == "authtoken":
                if top_level is not None:
                    raise CredentialError("Standard ngrok config has duplicate credential fields")
                top_level = _parse_yaml_scalar(raw_value, "credential")
        elif key == "authtoken" and parent_path == ("agent",):
            if agent_value is not None:
                raise CredentialError("Standard ngrok config has duplicate credential fields")
            agent_value = _parse_yaml_scalar(raw_value, "credential")

        if not _without_comment(raw_value):
            mapping_stack.append((depth, key))

    normalized_version = version.strip('"\'') if version else None
    if normalized_version == "3":
        if top_level is not None:
            raise CredentialError("Version 3 ngrok config has a credential in the wrong location")
        return agent_value
    if normalized_version in (None, "2"):
        if agent_value is not None:
            raise CredentialError("Legacy ngrok config has a credential in the wrong location")
        return top_level
    if top_level is not None or agent_value is not None:
        raise CredentialError("Unsupported ngrok config version for credential discovery")
    return None


def _parse_yaml_scalar(raw_value: str, label: str) -> str:
    value = _without_comment(raw_value)
    if not value:
        raise CredentialError(f"Standard ngrok config has a non-scalar {label} field")
    if value.startswith('"'):
        if len(value) < 2 or not value.endswith('"'):
            raise CredentialError(f"Standard ngrok config has a malformed {label} scalar")
        scalar = value[1:-1]
    elif value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise CredentialError(f"Standard ngrok config has a malformed {label} scalar")
        scalar = value[1:-1].replace("''", "'")
    else:
        scalar = value
    if not scalar or not _PLAIN_TOKEN.fullmatch(scalar):
        raise CredentialError(f"Standard ngrok config has an invalid {label} scalar")
    return scalar


def _without_comment(raw_value: str) -> str:
    quote: str | None = None
    escaped = False
    for index, character in enumerate(raw_value):
        if escaped:
            escaped = False
            continue
        if character == "\\" and quote == '"':
            escaped = True
            continue
        if character in ('"', "'"):
            if quote is None:
                quote = character
            elif quote == character:
                quote = None
            continue
        if character == "#" and quote is None:
            return raw_value[:index].strip()
    return raw_value.strip()


def _read_system_config(path: Path, expected: os.stat_result) -> str:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise CredentialError(f"Cannot read standard ngrok config: {error}") from error
    stream_opened = False
    try:
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (expected.st_dev, expected.st_ino):
            raise CredentialError("Standard ngrok config changed while being opened")
        if opened.st_size > MAX_CONFIG_BYTES:
            raise CredentialError("Standard ngrok config is too large")
        with os.fdopen(descriptor, "r", encoding="utf-8") as stream:
            stream_opened = True
            content = stream.read(MAX_CONFIG_BYTES + 1)
        if len(content.encode("utf-8")) > MAX_CONFIG_BYTES:
            raise CredentialError("Standard ngrok config is too large")
        return content
    except UnicodeError as error:
        raise CredentialError("Standard ngrok config is not valid UTF-8") from error
    except OSError as error:
        raise CredentialError(f"Cannot read standard ngrok config: {error}") from error
    finally:
        if not stream_opened:
            try:
                os.close(descriptor)
            except OSError:
                pass


def _require_private_system_config(path: Path, metadata: os.stat_result) -> None:
    if stat.S_ISLNK(metadata.st_mode):
        raise CredentialError(f"Refusing symlinked standard ngrok config: {path}")
    if not stat.S_ISREG(metadata.st_mode):
        raise CredentialError(f"Standard ngrok config is not a regular file: {path}")
    if os.name != "nt":
        actual = stat.S_IMODE(metadata.st_mode)
        if actual != 0o600:
            raise CredentialError(f"Standard ngrok config is not private; run: chmod 600 {path}")
        if hasattr(os, "getuid") and metadata.st_uid != os.getuid():
            raise CredentialError(f"Standard ngrok config is not owned by the current user: {path}")


def read_stored_ngrok_authtoken() -> str | None:
    if not NGROK_TOKEN_FILE.exists():
        return None
    _require_private_path(CREDENTIAL_DIR, 0o700, "directory")
    _require_private_path(NGROK_TOKEN_FILE, 0o600, "file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(NGROK_TOKEN_FILE, flags)
    except OSError as error:
        raise CredentialError(f"Cannot read stored ngrok credential: {error}") from error
    try:
        with os.fdopen(descriptor, "r", encoding="utf-8") as stream:
            token = stream.read().strip()
    except OSError as error:
        raise CredentialError(f"Cannot read stored ngrok credential: {error}") from error
    if not token:
        raise CredentialError(f"Stored ngrok credential is empty; rerun: {configure_command()}")
    return token


def store_ngrok_authtoken(token: str) -> None:
    cleaned = token.strip()
    if not cleaned or any(character in cleaned for character in "\r\n\0"):
        raise CredentialError("The ngrok agent authtoken is empty or invalid")
    _prepare_private_directory()
    temporary = CREDENTIAL_DIR / f".ngrok-authtoken-{os.getpid()}.tmp"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        descriptor = os.open(temporary, flags, 0o600)
    except OSError as error:
        raise CredentialError(f"Cannot create private ngrok credential: {error}") from error
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(cleaned)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, NGROK_TOKEN_FILE)
        os.chmod(NGROK_TOKEN_FILE, 0o600)
    finally:
        temporary.unlink(missing_ok=True)


def delete_stored_ngrok_authtoken() -> bool:
    if not CREDENTIAL_DIR.exists() and not CREDENTIAL_DIR.is_symlink():
        return False
    _require_private_path(CREDENTIAL_DIR, 0o700, "directory")
    if not NGROK_TOKEN_FILE.exists() and not NGROK_TOKEN_FILE.is_symlink():
        return False
    _require_private_path(NGROK_TOKEN_FILE, 0o600, "file")
    try:
        NGROK_TOKEN_FILE.unlink()
    except OSError as error:
        raise CredentialError(f"Cannot delete stored ngrok credential: {error}") from error
    return True


def _prepare_private_directory() -> None:
    if CREDENTIAL_DIR.is_symlink():
        raise CredentialError(f"Refusing symlinked credential directory: {CREDENTIAL_DIR}")
    try:
        CREDENTIAL_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(CREDENTIAL_DIR, 0o700)
    except OSError as error:
        raise CredentialError(f"Cannot prepare private ngrok credential directory: {error}") from error


def _require_private_path(path: Path, expected: int, label: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise CredentialError(f"Cannot inspect ngrok credential {label}: {error}") from error
    if stat.S_ISLNK(metadata.st_mode):
        raise CredentialError(f"Refusing symlinked ngrok credential {label}: {path}")
    actual = stat.S_IMODE(metadata.st_mode)
    if actual != expected:
        raise CredentialError(
            f"Stored ngrok credential {label} is not private; run: chmod {expected:o} {path}"
        )
