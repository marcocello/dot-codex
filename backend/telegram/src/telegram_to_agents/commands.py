"""Closed Telegram command surface for the native-harness gateway."""

from __future__ import annotations


def get_bot_commands() -> list[tuple[str, str]]:
    """Return every supported command and no removed agent-framework commands."""
    return [
        ("start", "Open native harness gateway"),
        ("new", "Start a new native session"),
        ("reset", "Start a new native session"),
        ("stop", "Stop the active turn"),
        ("stop_all", "Stop all active turns"),
        ("interrupt", "Interrupt active work"),
        ("status", "Show the current native session"),
        ("where", "Show chat and project"),
        ("leave", "Leave current group"),
        ("showfiles", "Show recent Telegram files"),
        ("info", "Show gateway information"),
        ("help", "Show available commands"),
        ("restart", "Restart the gateway"),
    ]
