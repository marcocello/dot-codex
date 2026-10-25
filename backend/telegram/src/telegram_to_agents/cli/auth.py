"""Native Codex and Claude availability/login detection."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from enum import StrEnum, unique
from pathlib import Path
from typing import Literal


@unique
class AuthStatus(StrEnum):
    AUTHENTICATED = "authenticated"
    INSTALLED = "installed"
    NOT_FOUND = "not_found"


@dataclass(frozen=True, slots=True)
class AuthResult:
    provider: str
    status: AuthStatus


def check_codex_auth() -> AuthResult:
    """Check the native Codex CLI without reading or printing credentials."""
    binary = shutil.which("codex")
    if not binary:
        return AuthResult("codex", AuthStatus.NOT_FOUND)
    try:
        result = subprocess.run(
            [binary, "login", "status"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return AuthResult("codex", AuthStatus.INSTALLED)
    if result.returncode == 0:
        return AuthResult("codex", AuthStatus.AUTHENTICATED)
    auth_file = Path.home() / ".codex" / "auth.json"
    return AuthResult(
        "codex",
        AuthStatus.AUTHENTICATED if auth_file.is_file() else AuthStatus.INSTALLED,
    )


def check_claude_auth() -> AuthResult:
    """Ask the native Claude CLI for its login state."""
    binary = shutil.which("claude")
    if not binary:
        return AuthResult("claude", AuthStatus.NOT_FOUND)
    try:
        result = subprocess.run(
            [binary, "auth", "status"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        data = json.loads(result.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return AuthResult("claude", AuthStatus.INSTALLED)
    status = AuthStatus.AUTHENTICATED if data.get("loggedIn") is True else AuthStatus.INSTALLED
    return AuthResult("claude", status)


def check_auth(provider: Literal["codex", "claude"]) -> AuthResult:
    """Check only the harness selected during onboarding."""
    return check_codex_auth() if provider == "codex" else check_claude_auth()
