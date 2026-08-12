#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

sys.dont_write_bytecode = True

from _runtime import load_record, remove_record, terminate_record


def main() -> int:
    record = load_record()
    if not record:
        print(json.dumps({"status": "already_stopped"}))
        return 0
    try:
        stopped = terminate_record(record)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1
    if not stopped:
        print("Photo Drop did not stop within 20 seconds; process was left running", file=sys.stderr)
        return 1
    remove_record()
    print(json.dumps({"status": "stopped", "destination": record.get("destination")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
