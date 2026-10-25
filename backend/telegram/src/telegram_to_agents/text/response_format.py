"""Small display helpers for temporary Telegram progress."""

from __future__ import annotations

_SHELL_TOOLS = frozenset({"bash", "powershell", "cmd", "sh", "zsh", "shell"})
_TOOL_LABELS = {
    "toolsearch": "Search",
    "searchtool": "Search",
    "webfetch": "Web fetch",
    "websearch": "Web search",
}


def normalize_tool_name(name: str) -> str:
    """Return a compact Telegram label for a native-harness tool name."""
    lower = name.lower()
    if lower in _SHELL_TOOLS:
        return "Shell"
    return _TOOL_LABELS.get(lower, name)
