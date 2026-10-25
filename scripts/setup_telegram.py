#!/usr/bin/env python3
"""Read-only bot authentication check; never send a Telegram message."""
import json
from pathlib import Path
import sys


def main():
    import httpx
    from telegram_to_agents.config import AgentConfig
    path = Path(sys.argv[1])
    if path.is_symlink() or path.stat().st_mode & 0o077:
        raise ValueError("Private configuration required")
    config = AgentConfig.model_validate(json.loads(path.read_text()))
    with httpx.Client(timeout=30, follow_redirects=False) as client:
        result = client.get("https://api.telegram.org/bot" + config.telegram_token + "/getMe")
        if result.status_code != 200 or result.json().get("ok") is not True:
            raise ValueError("Telegram authentication failed")
    print("Telegram bot identity verified; delivery requires a message from an allowed user")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("Telegram verification failed; check private token, configuration and network", file=sys.stderr)
        raise SystemExit(2)
