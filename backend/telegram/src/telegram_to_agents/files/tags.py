"""POSIX file-tag parsing and MIME detection."""

from __future__ import annotations

import mimetypes
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

import filetype as _filetype

FILE_PATH_RE = re.compile(r"<file:([^>]+)>")


def extract_file_paths(text: str) -> list[str]:
    """Return all ``<file:/path>`` references from *text*."""
    return FILE_PATH_RE.findall(text)


def path_from_file_tag(file_tag: str) -> Path:
    """Convert one ``<file:...>`` payload to a local filesystem path.

    Handles plain paths and ``file:`` URIs.
    """
    value = file_tag.strip()
    if not value:
        return Path(value)

    parsed = urlparse(value)
    if parsed.scheme == "file":
        if parsed.netloc and parsed.path:
            # file://server/share/path or file://C:/Users/...
            value = f"//{parsed.netloc}{parsed.path}"
        elif parsed.netloc:
            value = f"//{parsed.netloc}"
        else:
            value = parsed.path or ""

    value = unquote(value)
    return Path(value)


def guess_mime(path: Path | str) -> str:
    """Guess MIME type using magic bytes first, then extension fallback.

    Uses the ``filetype`` library for binary format detection (images, audio,
    video, archives).  Falls back to ``mimetypes`` for text-based formats
    (source code, SVG, plain text) that lack magic byte signatures.
    """
    kind = _filetype.guess(str(path))
    if kind is not None:
        return str(kind.mime)

    suffix = Path(path).suffix.lower()
    overrides = {
        ".js": "application/javascript",
        ".py": "text/x-python",
        ".ts": "application/x-typescript",
        ".webp": "image/webp",
    }
    if suffix in overrides:
        return overrides[suffix]

    return mimetypes.guess_type(str(path))[0] or "application/octet-stream"
