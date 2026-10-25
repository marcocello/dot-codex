"""Current retrievable payloads, atomic page checkpoints, and recoverable index jobs."""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import sqlite3
import uuid

from .config import ContextError, fingerprint, require


def document_id(source_id, native_id):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, json.dumps([source_id, native_id])))


class Store:
    def __init__(self, root):
        require(sqlite3.sqlite_version_info >= (3, 42, 0),
                "SQLite 3.42+ is required for FTS payload erasure")
        self.root = Path(root)
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        path = self.root / "context.sqlite3"
        require(not path.is_symlink(), "The context database must not be a symlink")
        self.db = sqlite3.connect(path, timeout=15)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA secure_delete=ON")
        version = self.db.execute("PRAGMA user_version").fetchone()[0]
        require(version in (0, 1), "Unsupported context database schema")
        if version == 0:
            require(not self.db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchone(),
                    "Refusing to initialize an unrelated SQLite database")
            self.db.executescript("""
                CREATE TABLE sources(id TEXT PRIMARY KEY, signature TEXT NOT NULL,
                    enabled INTEGER NOT NULL, error TEXT);
                CREATE TABLE checkpoints(source_id TEXT NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
                    stream TEXT NOT NULL, cursor TEXT NOT NULL, metadata TEXT NOT NULL,
                    PRIMARY KEY(source_id,stream));
                CREATE TABLE documents(id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources(id),
                    native_id TEXT NOT NULL, revision TEXT NOT NULL, title TEXT NOT NULL,
                    text TEXT NOT NULL, ref TEXT NOT NULL, occurred_at TEXT NOT NULL,
                    direction TEXT NOT NULL, UNIQUE(source_id,native_id));
                CREATE VIRTUAL TABLE document_fts USING fts5(id UNINDEXED,title,text);
                CREATE TRIGGER doc_insert AFTER INSERT ON documents BEGIN
                    INSERT INTO document_fts VALUES(new.id,new.title,new.text); END;
                CREATE TRIGGER doc_delete AFTER DELETE ON documents BEGIN
                    DELETE FROM document_fts WHERE id=old.id; END;
                CREATE TRIGGER doc_update AFTER UPDATE ON documents BEGIN
                    DELETE FROM document_fts WHERE id=old.id;
                    INSERT INTO document_fts VALUES(new.id,new.title,new.text); END;
                CREATE TABLE index_jobs(id TEXT PRIMARY KEY, revision TEXT);
                CREATE TABLE settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
                PRAGMA user_version=1;
            """)
            self.db.execute("INSERT INTO document_fts(document_fts,rank) VALUES('secure-delete',1)")
        self.db.commit()

    def close(self):
        self.db.close()

    def register(self, sources):
        errors = {}
        with self.db:
            self.db.execute("UPDATE sources SET enabled=0")
            for source in sources:
                old = self.db.execute("SELECT * FROM sources WHERE id=?", (source.id,)).fetchone()
                if old and old["signature"] != source.signature:
                    used = self.db.execute("SELECT 1 FROM checkpoints WHERE source_id=? LIMIT 1", (source.id,)).fetchone()
                    if not used:
                        self.db.execute("UPDATE sources SET signature=?,enabled=?,error=NULL WHERE id=?",
                                        (source.signature, source.enabled, source.id))
                        continue
                    if source.enabled:
                        errors[source.id] = "Source scope changed; disable and forget it, or select a new source id"
                    continue
                self.db.execute("INSERT INTO sources(id,signature,enabled) VALUES(?,?,?) "
                                "ON CONFLICT(id) DO UPDATE SET enabled=excluded.enabled",
                                (source.id, source.signature, source.enabled))
        return errors

    def allowed(self, config):
        return [source.id for source in config.sources if source.enabled and self.db.execute(
            "SELECT 1 FROM sources WHERE id=? AND signature=? AND enabled=1 AND error IS NULL",
            (source.id, source.signature)).fetchone()]

    def checkpoint(self, source, stream):
        row = self.db.execute("SELECT cursor,metadata FROM checkpoints WHERE source_id=? AND stream=?",
                              (source, stream)).fetchone()
        return (row["cursor"], json.loads(row["metadata"])) if row else (None, {})

    def apply_page(self, source, stream, expected, cursor, items, metadata=None):
        require(isinstance(cursor, str) and bool(cursor), "Provider returned an empty checkpoint")
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            require(self.checkpoint(source, stream)[0] == expected, "Stale checkpoint; reread before retry")
            for item in items:
                identity = document_id(source, item["native_id"])
                if item.get("deleted"):
                    self.db.execute("DELETE FROM documents WHERE id=?", (identity,))
                    revision = None
                else:
                    revision = fingerprint(item)
                    old = self.db.execute("SELECT revision FROM documents WHERE id=?", (identity,)).fetchone()
                    if old and old[0] == revision:
                        continue
                    self.db.execute("""INSERT INTO documents VALUES(?,?,?,?,?,?,?,?,?)
                        ON CONFLICT(id) DO UPDATE SET revision=excluded.revision,title=excluded.title,
                        text=excluded.text,ref=excluded.ref,occurred_at=excluded.occurred_at,direction=excluded.direction""",
                        (identity, source, item["native_id"], revision, item["title"], item["text"],
                         json.dumps(item["ref"]), item["occurred_at"], item["direction"]))
                self.db.execute("INSERT INTO index_jobs VALUES(?,?) ON CONFLICT(id) DO UPDATE SET revision=excluded.revision",
                                (identity, revision))
            self.db.execute("INSERT INTO checkpoints VALUES(?,?,?,?) ON CONFLICT(source_id,stream) "
                            "DO UPDATE SET cursor=excluded.cursor,metadata=excluded.metadata",
                            (source, stream, cursor, json.dumps(metadata or {})))
            self.db.execute("UPDATE sources SET error=NULL WHERE id=?", (source,))

    def fail(self, source, message):
        with self.db:
            self.db.execute("UPDATE sources SET error=? WHERE id=?", (message, source))

    def get(self, identity, allowed=None):
        row = self.db.execute("SELECT * FROM documents WHERE id=?", (identity,)).fetchone()
        if not row or (allowed is not None and row["source_id"] not in allowed):
            return None
        result = dict(row)
        result["ref"] = json.loads(result["ref"])
        result["evidence_only"] = True
        return result

    def forget(self, source):
        with self.db:
            identities = [row[0] for row in self.db.execute("SELECT id FROM documents WHERE source_id=?", (source,))]
            for identity in identities:
                self.db.execute("INSERT INTO index_jobs VALUES(?,NULL) ON CONFLICT(id) DO UPDATE SET revision=NULL",
                                (identity,))
            self.db.execute("DELETE FROM documents WHERE source_id=?", (source,))
            self.db.execute("DELETE FROM checkpoints WHERE source_id=?", (source,))
            self.db.execute("DELETE FROM sources WHERE id=?", (source,))
        # FTS delete marks and SQLite free pages must not retain copied message text.
        self.db.execute("INSERT INTO document_fts(document_fts) VALUES('optimize')")
        self.db.commit()
        self.db.execute("VACUUM")
        return len(identities)

    def status(self):
        return {"sources": [dict(row) for row in self.db.execute("SELECT id,enabled,error FROM sources")],
                "documents": self.db.execute("SELECT count(*) FROM documents").fetchone()[0],
                "pending_index": self.db.execute("SELECT count(*) FROM index_jobs").fetchone()[0]}


@contextmanager
def lock(root, name):
    root = Path(root)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = root / f".{name}.lock"
    require(not path.is_symlink(), "Lock path must not be a symlink")
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ContextError(f"Context {name} is busy; retry after the current operation") from None
        yield
    finally:
        os.close(descriptor)
