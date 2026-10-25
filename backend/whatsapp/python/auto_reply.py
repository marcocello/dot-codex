"""Application message policy. WhatsApp transport stays in Node/Baileys."""

import json
import sys

GREETING = "🤖 hey I am the AI assistant of Marco"


def handle_message(event: dict) -> dict:
    """Decide using event['text'], event['message'], and sender/chat metadata."""
    if event.get("event") != "incoming_message":
        return {"action": "ignore"}
    return {"action": "reply", "text": GREETING}


def main() -> None:
    """Serve correlated JSON requests for the lifetime of the local worker."""
    for line in sys.stdin:
        request = json.loads(line)
        decision = handle_message(request["event"])
        print(json.dumps({"id": request["id"], "decision": decision}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
