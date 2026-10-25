"""Rebuildable local vectors. Qdrant payloads contain identities, never message text."""
from __future__ import annotations

import uuid
import json
from dataclasses import replace

from .config import ContextError
from .store import lock

COLLECTION = "context"


class Embeddings:
    def __init__(self, config):
        from fastembed import TextEmbedding
        self.model = TextEmbedding(model_name=config.model, cache_dir=str(config.workspace / "models"), threads=2)

    def passages(self, texts):
        return [vector.tolist() for vector in self.model.passage_embed(texts)]

    def query(self, text):
        return next(self.model.query_embed(text)).tolist()


def chunks(text):
    for start in range(0, max(len(text), 1), 900):
        yield text[start:start + 1000] or "(empty message)"


class QdrantIndex:
    def __init__(self, config, store):
        from qdrant_client import QdrantClient, models
        self.config, self.store, self.models = config, store, models
        self.client = QdrantClient(path=str(config.workspace / "vectors"))
        self._embedder = None

    @property
    def embedder(self):
        if self._embedder is None:
            self._embedder = Embeddings(self.config)
        return self._embedder

    def close(self):
        self.client.close()

    def ensure_collection(self):
        row = self.store.db.execute("SELECT value FROM settings WHERE key='embedding_model'").fetchone()
        if row and row[0] == self.config.model and self.client.collection_exists(COLLECTION):
            return
        vector = self.embedder.query("dimension")
        if self.client.collection_exists(COLLECTION):
            self.client.delete_collection(COLLECTION)
        self.client.create_collection(COLLECTION, vectors_config=self.models.VectorParams(
            size=len(vector), distance=self.models.Distance.COSINE))
        with self.store.db:
            self.store.db.execute("INSERT INTO settings VALUES('embedding_model',?) "
                                  "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (self.config.model,))
            self.store.db.execute("INSERT OR REPLACE INTO index_jobs SELECT id,revision FROM documents")

    def write(self, document, vectors):
        points = [self.models.PointStruct(
            id=str(uuid.uuid5(uuid.UUID(document["id"]), str(number))), vector=vector,
            payload={"document_id": document["id"], "source_id": document["source_id"],
                     "revision": document["revision"], "chunk": number})
            for number, vector in enumerate(vectors)]
        self.client.upsert(COLLECTION, points, wait=True)

    def delete(self, identity):
        if self.client.collection_exists(COLLECTION):
            self.client.delete(COLLECTION, points_selector=self.models.FilterSelector(
                filter=self.models.Filter(must=[self.models.FieldCondition(
                    key="document_id", match=self.models.MatchValue(value=identity))])), wait=True)

    def drain(self, limit=100, *, delete_only=False):
        if not delete_only:
            self.prepare_projection()
        if not delete_only and self.store.db.execute("SELECT 1 FROM documents LIMIT 1").fetchone():
            self.ensure_collection()
        selection = " WHERE revision IS NULL" if delete_only else ""
        jobs = self.store.db.execute("SELECT id,revision FROM index_jobs" + selection + " LIMIT ?", (limit,)).fetchall()
        indexed = 0
        for job in jobs:
            document = self.store.get(job["id"])
            self.erase_everywhere(job["id"])
            if document:
                texts = list(chunks(document["title"] + "\n" + document["text"]))
                vectors = self.embedder.passages(texts)
                self.write(document, vectors)
            with self.store.db:
                self.store.db.execute("DELETE FROM index_jobs WHERE id=? AND revision IS ?",
                                      (job["id"], job["revision"]))
            indexed += 1
        return indexed

    def projection(self):
        return {key: getattr(self.config, key) for key in ("backend", "pinecone_index", "pinecone_namespace", "api_key_file")}

    def history(self):
        row = self.store.db.execute("SELECT value FROM settings WHERE key='projection_history'").fetchone()
        return json.loads(row[0]) if row else []

    def prepare_projection(self):
        desired = self.projection()
        row = self.store.db.execute("SELECT value FROM settings WHERE key='active_projection'").fetchone()
        if row and json.loads(row[0]) == desired:
            return
        history = self.history()
        if not history and (self.config.workspace / "vectors").exists():
            # Remember the original pre-adapter local projection when migrating an existing workspace.
            history.append({"backend": "qdrant", "pinecone_index": "", "pinecone_namespace": "", "api_key_file": ""})
        if desired not in history:
            history.append(desired)
        with self.store.db:
            for key, value in (("projection_history", history), ("active_projection", desired)):
                self.store.db.execute("INSERT INTO settings VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, json.dumps(value)))
            self.store.db.execute("INSERT OR REPLACE INTO index_jobs SELECT id,revision FROM documents")

    def erase_everywhere(self, identity):
        self.delete(identity)
        for projection in self.history():
            if projection == self.projection():
                continue
            config = replace(self.config, **projection)
            # Qdrant projections share the same local directory; do not open it twice.
            if config.backend == "qdrant" and self.config.backend == "qdrant":
                continue
            old = VectorIndex(config, self.store)
            try:
                old.delete(identity)
            finally:
                old.close()

    def search(self, query, allowed, limit):
        if not allowed or not self.client.collection_exists(COLLECTION):
            return []
        row = self.store.db.execute("SELECT value FROM settings WHERE key='embedding_model'").fetchone()
        if not row or row[0] != self.config.model:
            raise ContextError("Embedding model changed; run context index to rebuild vectors")
        result = self.client.query_points(COLLECTION, query=self.embedder.query(query),
            query_filter=self.models.Filter(must=[self.models.FieldCondition(
                key="source_id", match=self.models.MatchAny(any=allowed))]),
            limit=min(limit * 5, 250), with_payload=True)
        output, seen = [], set()
        for point in result.points:
            payload = point.payload or {}
            document = self.store.get(payload.get("document_id"), allowed)
            if document and document["revision"] == payload.get("revision") and document["id"] not in seen:
                seen.add(document["id"])
                output.append(document)
        return output[:limit]


class PineconeIndex(QdrantIndex):
    """Remote vectors only; SQLite remains the authority for readable evidence."""
    def __init__(self, config, store):
        import os
        from pathlib import Path
        from pinecone import Pinecone
        self.config, self.store = config, store
        self._embedder = None
        row = store.db.execute("SELECT value FROM settings WHERE key='vector_owner'").fetchone()
        self.owner = row[0] if row else str(uuid.uuid4())
        if not row:
            with store.db:
                store.db.execute("INSERT INTO settings VALUES('vector_owner',?)", (self.owner,))
        key = os.environ.get("PINECONE_API_KEY", "")
        if not key and config.api_key_file:
            path = Path(config.api_key_file)
            if path.is_symlink() or path.stat().st_mode & 0o077:
                raise ContextError("Pinecone credential file must be a private regular file")
            key = path.read_text().strip()
        if not key:
            raise ContextError("Pinecone API key is missing")
        self.control = Pinecone(api_key=key, timeout=30)
        try:
            self.description = self.control.describe_index(config.pinecone_index)
            self.client = self.control.Index(host=self.description.host)
        except Exception:
            self.control.close()
            raise ContextError("Pinecone index is unavailable; verify account, region and configured index") from None

    def close(self):
        self.client.close()
        self.control.close()

    def ensure_collection(self):
        if not self.description.status.get("ready"):
            raise ContextError("Pinecone index is not ready")
        dimension = len(self.embedder.query("dimension"))
        if self.description.dimension != dimension or str(self.description.metric).lower() != "cosine":
            raise ContextError("Pinecone index dimension/metric differs from the selected embedding model; select a compatible index")
        row = self.store.db.execute("SELECT value FROM settings WHERE key='pinecone_model' ").fetchone()
        desired = json.dumps([self.config.pinecone_index, self.config.pinecone_namespace, self.config.model])
        if row and row[0] != desired and json.loads(row[0])[:2] == json.loads(desired)[:2]:
            raise ContextError("Model changed in an existing Pinecone namespace; select a new namespace and rebuild")
        with self.store.db:
            self.store.db.execute("INSERT INTO settings VALUES('pinecone_model',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (desired,))

    def delete(self, identity):
        self.client.delete(namespace=self.config.pinecone_namespace,
                           filter={"$and": [{"document_id": {"$eq": identity}}, {"workspace_id": {"$eq": self.owner}}]})

    def write(self, document, vectors):
        payload = [{"id": str(uuid.uuid5(uuid.UUID(self.owner), document["id"] + ":" + str(number))), "values": vector,
                    "metadata": {"document_id": document["id"], "source_id": document["source_id"], "revision": document["revision"], "chunk": number,
                                 "workspace_id": self.owner}}
                   for number, vector in enumerate(vectors)]
        # Bound provider requests without changing deterministic point identities.
        for start in range(0, len(payload), 100):
            self.client.upsert(vectors=payload[start:start + 100], namespace=self.config.pinecone_namespace)

    def search(self, query, allowed, limit):
        if not allowed:
            return []
        desired = json.dumps([self.config.pinecone_index, self.config.pinecone_namespace, self.config.model])
        row = self.store.db.execute("SELECT value FROM settings WHERE key='pinecone_model'").fetchone()
        if not row or row[0] != desired:
            raise ContextError("Pinecone projection changed; run context index before semantic search")
        result = self.client.query(vector=self.embedder.query(query), namespace=self.config.pinecone_namespace,
                                   top_k=min(limit * 5, 250), filter={"$and": [{"source_id": {"$in": allowed}}, {"workspace_id": {"$eq": self.owner}}]}, include_metadata=True)
        output, seen = [], set()
        for point in result.matches:
            payload = point.metadata or {}
            document = self.store.get(payload.get("document_id"), allowed)
            if document and document["revision"] == payload.get("revision") and document["id"] not in seen:
                seen.add(document["id"])
                output.append(document)
        return output[:limit]


def VectorIndex(config, store):
    return PineconeIndex(config, store) if config.backend == "pinecone" else QdrantIndex(config, store)


def update_index(config, store, limit=100, *, delete_only=False):
    with lock(config.workspace, "index"):
        index = VectorIndex(config, store)
        try:
            return index.drain(limit, delete_only=delete_only)
        finally:
            index.close()
