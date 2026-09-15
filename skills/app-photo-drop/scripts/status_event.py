#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

sys.dont_write_bytecode = True

from _runtime import load_record, process_alive, read_json_url


def main() -> int:
    record = load_record()
    if not record:
        print(json.dumps({"status": "stopped"}))
        return 0
    try:
        pid = int(record["pid"])
    except (KeyError, TypeError, ValueError):
        print(json.dumps({"status": "stale", "record": record}))
        return 1
    if not process_alive(pid):
        print(json.dumps({"status": "stale", "record": record}))
        return 1
    session = read_json_url(f"{record.get('admin_url', '')}/api/session")
    print(json.dumps({"status": "running", **record, "session": session}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
