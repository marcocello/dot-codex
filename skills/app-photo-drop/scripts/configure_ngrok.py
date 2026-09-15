#!/usr/bin/env python3
from __future__ import annotations

import getpass
import json
import sys

sys.dont_write_bytecode = True

from _credentials import (
    CredentialError,
    TOKEN_URL,
    delete_stored_ngrok_authtoken,
    find_ngrok_credential,
    store_ngrok_authtoken,
)


USAGE = "Usage: configure_ngrok.py [--check|--delete]"


def status() -> int:
    try:
        configured = find_ngrok_credential()
    except CredentialError as error:
        print(json.dumps({"status": "invalid", "message": str(error)}))
        return 2
    payload = {"status": "configured", "source": configured[1]} if configured else {"status": "missing"}
    print(json.dumps(payload))
    return 0 if configured else 1


def configure() -> int:
    if not sys.stdin.isatty():
        print("An interactive terminal is required so the authtoken stays hidden.", file=sys.stderr)
        return 2
    print("Configure Photo Drop's ngrok agent authtoken.")
    print(f"Open: {TOKEN_URL}")
    try:
        token = getpass.getpass("Paste ngrok agent authtoken (input hidden): ")
        store_ngrok_authtoken(token)
    except (CredentialError, EOFError, KeyboardInterrupt) as error:
        print(f"\nCredential was not saved: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"status": "configured"}))
    return 0


def main() -> int:
    arguments = sys.argv[1:]
    if arguments == ["--check"]:
        return status()
    if arguments == ["--delete"]:
        try:
            removed = delete_stored_ngrok_authtoken()
        except CredentialError as error:
            print(json.dumps({"status": "invalid", "message": str(error)}))
            return 2
        print(json.dumps({"status": "removed" if removed else "missing"}))
        return 0
    if arguments:
        print(USAGE, file=sys.stderr)
        print("Authtokens are accepted only through the hidden interactive prompt.", file=sys.stderr)
        return 2
    return configure()


if __name__ == "__main__":
    raise SystemExit(main())
