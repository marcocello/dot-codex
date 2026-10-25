"""Validate explicit provider scopes without reading credentials or enabling sources."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import tomllib


class ContextError(Exception):
    """An operator-facing error that must not include provider payloads or tokens."""


def require(condition, message):
    if not condition:
        raise ContextError(message)


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def instant(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(parsed.tzinfo is not None, "since must include a timezone")
        return parsed.astimezone(timezone.utc)
    except (AttributeError, ValueError):
        raise ContextError("since must be an ISO timestamp with a timezone") from None


def path_value(value, parent):
    require(isinstance(value, str) and bool(value), "Expected an explicit filesystem path")
    path = Path(value).expanduser()
    return (parent / path).resolve() if not path.is_absolute() else path.resolve()


@dataclass(frozen=True)
class Source:
    id: str
    provider: str
    enabled: bool
    scope: dict

    @property
    def signature(self):
        return fingerprint({"provider": self.provider, "scope": self.scope})


@dataclass(frozen=True)
class Configuration:
    path: Path
    workspace: Path
    model: str
    every_seconds: int
    sources: tuple[Source, ...]
    backend: str = "qdrant"
    pinecone_index: str = ""
    pinecone_namespace: str = ""
    api_key_file: str = ""


def load(path):
    path = Path(path).expanduser().resolve()
    try:
        data = tomllib.loads(path.read_text())
    except (OSError, tomllib.TOMLDecodeError):
        raise ContextError("Cannot read context configuration; copy context.template.toml and select scopes") from None
    require(set(data) <= {"schema", "workspace", "search", "sources", "sync_every_seconds"},
            "Unknown context configuration field")
    require(type(data.get("schema")) is int and data["schema"] == 1, "Unsupported configuration schema")
    workspace = path_value(data.get("workspace"), path.parent)
    require(workspace != path.parent, "Use a dedicated private workspace directory")
    interval = data.get("sync_every_seconds", 300)
    require(type(interval) is int and interval >= 30, "sync_every_seconds must be at least 30")
    search = data.get("search", {})
    require(isinstance(search, dict) and set(search) <= {"model", "backend", "pinecone_index", "pinecone_namespace", "api_key_file"}, "Unknown search configuration")
    model = search.get("model", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    require(isinstance(model, str) and 1 <= len(model) <= 200, "Select an embedding model")
    backend = search.get("backend", "qdrant")
    require(backend in {"qdrant", "pinecone"}, "Select qdrant or pinecone")
    index, namespace, key_file = (search.get(key, "") for key in ("pinecone_index", "pinecone_namespace", "api_key_file"))
    if backend == "pinecone":
        require(isinstance(index, str) and re.fullmatch(r"[a-z0-9][a-z0-9-]{0,44}", index), "Select a Pinecone index")
        require(isinstance(namespace, str) and re.fullmatch(r"[a-zA-Z0-9_-]{8,128}", namespace), "Select a dedicated Pinecone namespace of 8 to 128 characters")
        if key_file:
            key_file = str(path_value(key_file, path.parent))
    raw_sources = data.get("sources", [])
    require(isinstance(raw_sources, list), "sources must be an array of tables")
    sources = []
    for item in raw_sources:
        require(isinstance(item, dict) and set(item) == {"id", "provider", "enabled", "scope"},
                "Each source needs id, provider, enabled, and scope")
        identity, provider, enabled = item["id"], item["provider"], item["enabled"]
        require(isinstance(identity, str) and re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", identity), "Invalid source id")
        require(identity not in {source.id for source in sources}, "Duplicate source id")
        require(provider in {"microsoft_graph", "wacli"}, "Unsupported ingestion provider; live tools use harness plugins")
        require(type(enabled) is bool, "enabled must be true or false")
        scope = item["scope"]
        require(isinstance(scope, dict), "scope must be a table")
        if enabled:
            validate_scope(provider, scope, path.parent)
        sources.append(Source(identity, provider, enabled, scope))
    return Configuration(path, workspace, model, interval, tuple(sources), backend, index, namespace, key_file)


def validate_scope(provider, scope, parent):
    require("since" in scope, "Enabled sources require an explicit since timestamp")
    instant(scope["since"])
    if provider == "wacli":
        require(set(scope) <= {"store", "chats", "since", "binary"} and {"store", "chats"} <= set(scope),
                "wacli scope requires store, chats, and since")
        scope["store"] = str(path_value(scope["store"], parent))
        chats = scope["chats"]
        require(isinstance(chats, list) and bool(chats) and all(
            isinstance(chat, str) and re.fullmatch(r"[^\s@]+@(s\.whatsapp\.net|g\.us|lid|c\.us)", chat)
            for chat in chats), "Select explicit WhatsApp chat JIDs")
        scope["chats"] = sorted(set(chats))
        binary = scope.get("binary", "wacli")
        require(isinstance(binary, str) and bool(binary), "Invalid wacli binary")
        if "/" in binary:
            scope["binary"] = str(path_value(binary, parent))
    else:
        require(set(scope) == {"account", "client_id", "tenant_id", "folders", "since"},
                "Microsoft scope requires account, client_id, tenant_id, folders, and since")
        require(isinstance(scope["account"], str) and "@" in scope["account"], "Select one mailbox account")
        require(isinstance(scope["client_id"], str) and re.fullmatch(r"[a-fA-F0-9-]{36}", scope["client_id"]),
                "Set the Microsoft public-client application ID")
        require(isinstance(scope["tenant_id"], str) and re.fullmatch(r"[a-zA-Z0-9.-]+", scope["tenant_id"]),
                "Set the Microsoft tenant ID or organizations")
        folders = scope["folders"]
        require(isinstance(folders, list) and bool(folders) and all(
            isinstance(folder, str) and bool(folder) and len(folder) <= 512 for folder in folders),
            "Select explicit mail-folder IDs or well-known names")
        scope["folders"] = sorted(set(folders))
