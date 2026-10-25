"""Delegated Microsoft device authentication with a private local token cache."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile

from .config import ContextError, require
from .store import lock

SCOPES = ["https://graph.microsoft.com/Mail.Read", "https://graph.microsoft.com/User.Read"]


class MicrosoftAuth:
    def __init__(self, config, source):
        import msal
        self.root = config.workspace / "auth"
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.path = self.root / f"{source.id}.json"
        require(not self.path.is_symlink(), "Token cache must not be a symlink")
        self.source = source
        self.cache = msal.SerializableTokenCache()
        self.app = None

    def initialize(self):
        import msal
        if self.path.exists():
            try:
                self.cache.deserialize(self.path.read_text())
            except (OSError, ValueError):
                raise ContextError("Microsoft token cache is unreadable; sign in again") from None
        try:
            self.app = msal.PublicClientApplication(
                self.source.scope["client_id"],
                authority="https://login.microsoftonline.com/" + self.source.scope["tenant_id"],
                token_cache=self.cache)
        except (ValueError, OSError):
            raise ContextError("Cannot initialize Microsoft authentication; check tenant/client configuration") from None

    def save(self):
        if self.cache.has_state_changed:
            descriptor, temporary = tempfile.mkstemp(prefix=".cache-", dir=self.root)
            try:
                with os.fdopen(descriptor, "w") as target:
                    target.write(self.cache.serialize())
                os.replace(temporary, self.path)
            finally:
                Path(temporary).unlink(missing_ok=True)

    def token(self):
        with lock(self.root, self.source.id):
            self.initialize()
            accounts = self.app.get_accounts(username=self.source.scope["account"])
            if not accounts:
                # A verified mailbox address can differ from the account's sign-in UPN.
                cached = self.app.get_accounts()
                accounts = cached if len(cached) == 1 else []
            result = self.app.acquire_token_silent(SCOPES, account=accounts[0]) if accounts else None
            self.save()
        require(result and "access_token" in result,
                "Microsoft sign-in is required; run context login --source SOURCE with this configuration")
        return result["access_token"]

    def login(self):
        with lock(self.root, self.source.id):
            self.initialize()
            flow = self.app.initiate_device_flow(scopes=SCOPES)
            require("user_code" in flow and "message" in flow,
                    "Microsoft device login could not start; enable public-client flows in the application")
            print(flow["message"], file=sys.stderr, flush=True)
            result = self.app.acquire_token_by_device_flow(flow)
            require("access_token" in result, "Microsoft sign-in failed or expired; check tenant consent and retry")
            from .providers import GraphClient
            client = GraphClient(lambda: result["access_token"])
            try:
                client.verify_account(self.source.scope["account"])
            finally:
                client.close()
            self.save()


def clear_cache(config, source_id):
    path = config.workspace / "auth" / f"{source_id}.json"
    require(not path.is_symlink(), "Token cache must not be a symlink")
    path.unlink(missing_ok=True)
