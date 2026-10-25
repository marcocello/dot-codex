"""Explicit local collection and retrieval; no automatic account or service activation."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import sys
import threading

from .config import ContextError, load, require


def emit(value):
    print(json.dumps(value, ensure_ascii=False), flush=True)


def execute(args, config):
    from .index import update_index
    from .service import read, search, synchronize
    from .store import Store, lock
    if args.command == "doctor":
        return {"ok": True, "workspace": str(config.workspace), "model": config.model,
                "sources": [{"id": source.id, "provider": source.provider, "enabled": source.enabled}
                            for source in config.sources],
                "notice": "Configuration checked. Live credentials, provider access, and sync freshness were not checked."}
    if args.command == "login":
        from .auth import MicrosoftAuth
        selected = [source for source in config.sources if source.id == args.source and source.enabled]
        require(len(selected) == 1 and selected[0].provider == "microsoft_graph",
                "Select one enabled Microsoft source with --source")
        MicrosoftAuth(config, selected[0]).login()
        return {"ok": True, "source": selected[0].id}
    if args.command in ("sync", "watch"):
        if args.source:
            require(any(source.id == args.source and source.enabled for source in config.sources),
                    "--source must select an enabled source")
        if args.command == "sync":
            return synchronize(config, source_id=args.source, max_pages=args.max_pages,
                               page_size=args.page_size, index=not args.no_index)
        stop = threading.Event()
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda *_: stop.set())
        while not stop.is_set():
            current = load(config.path)
            emit(synchronize(current, source_id=args.source, max_pages=args.max_pages,
                             page_size=args.page_size, index=not args.no_index))
            stop.wait(current.every_seconds)
        return {"ok": True, "stopped": True}
    if args.command == "search":
        return search(config, args.value, args.limit, args.mode)
    if args.command == "read":
        return read(config, args.value)
    store = Store(config.workspace)
    try:
        if args.command == "status":
            return {"ok": True, **store.status()}
        if args.command == "index":
            indexed = update_index(config, store, args.limit)
            return {"ok": True, "indexed": indexed, **store.status()}
        if args.command == "forget":
            require(args.confirm, "Source erasure requires --confirm")
            require(args.value and any(source.id == args.value for source in config.sources)
                    and not any(source.id == args.value and source.enabled for source in config.sources),
                    "Disable the selected source in configuration before erasing it")
            from .auth import clear_cache
            with lock(config.workspace, "source-" + args.value):
                count = store.forget(args.value)
                clear_cache(config, args.value)
                # Drain all outstanding deletions so a successful erasure includes derived vectors.
                while store.db.execute("SELECT 1 FROM index_jobs WHERE revision IS NULL LIMIT 1").fetchone():
                    update_index(config, store, 1000, delete_only=True)
            return {"ok": True, "erased_documents": count}
        raise ContextError("Unsupported command")
    finally:
        store.close()


def main(argv=None):
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("doctor", "login", "sync", "watch", "status", "index", "search", "read", "forget", "mcp"))
    parser.add_argument("value", nargs="?")
    parser.add_argument("--config", type=Path,
                        default=Path(os.environ.get("SECONDBRAIN_CONTEXT_CONFIG", "~/projects/.secondbrain/context.toml")))
    parser.add_argument("--source")
    parser.add_argument("--mode", choices=("text", "semantic", "hybrid"), default="hybrid")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--max-pages", type=int, default=20)
    parser.add_argument("--page-size", type=int, default=500)
    parser.add_argument("--no-index", action="store_true")
    parser.add_argument("--confirm", action="store_true")
    args = parser.parse_intermixed_args(argv)
    try:
        require(1 <= args.max_pages <= 100 and 1 <= args.page_size <= 1000,
                "Use 1..100 max-pages and 1..1000 page-size")
        require(1 <= args.limit <= (1000 if args.command == "index" else 50), "Invalid result limit")
        config = load(args.config)
        if args.command == "mcp":
            from .mcp_server import serve
            serve(config.path)
            return 0
        result = execute(args, config)
        emit(result)
        return 0 if result["ok"] else 1
    except ContextError as error:
        emit({"ok": False, "error": str(error)})
        return 2
    except KeyboardInterrupt:
        return 130
    except Exception:
        # Third-party errors can contain bearer tokens, message bodies, and signed model URLs.
        emit({"ok": False, "error": "Context operation failed; check local dependencies and provider setup. Saved checkpoints and index jobs remain available."})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
