"""File-name sanitization and collision-safe dated storage."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

_UNSAFE_CHARS_RE = re.compile(r'[/\\<>:"|?*\x00]')


def sanitize_filename(name: str) -> str:
    """Remove path separators, null bytes, and unsafe portable-name characters."""
    name = _UNSAFE_CHARS_RE.sub("_", name)
    while "__" in name:
        name = name.replace("__", "_")
    return name.strip("_. ")[:120] or "file"


def prepare_destination(base_dir: Path, file_name: str) -> Path:
    """Create date directory and return a non-colliding destination path."""
    day_dir = base_dir / datetime.now(tz=UTC).strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)

    dest = day_dir / file_name
    if dest.exists():
        stem, suffix = dest.stem, dest.suffix
        counter = 1
        while dest.exists():
            dest = day_dir / f"{stem}_{counter}{suffix}"
            counter += 1
    return dest
