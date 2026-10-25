#!/usr/bin/env python3
"""Inspect or explicitly create a compatible Pinecone index, using the app runtime."""
import argparse
import json
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--cloud", default="aws")
    parser.add_argument("--region", default="eu-west-1")
    args = parser.parse_args()
    from secondbrain_context.config import load
    from secondbrain_context.index import Embeddings
    from pinecone import Pinecone, ServerlessSpec
    config = load(args.config)
    if config.backend != "pinecone":
        return 0
    path = Path(config.api_key_file) if config.api_key_file else None
    if path and path.exists() and (path.is_symlink() or path.stat().st_mode & 0o077):
        raise ValueError("Private credentials required")
    key = os.environ.get("PINECONE_API_KEY") or (path.read_text().strip() if path and path.exists() else "")
    dimension = len(Embeddings(config).query("dimension"))
    with Pinecone(api_key=key, timeout=30) as pc:
        exists = pc.has_index(config.pinecone_index)
        if not exists and not args.create:
            print(json.dumps({"exists": False, "dimension": dimension}))
            return 3
        if not exists:
            # The v10 SDK retains this documented compatibility interface for BYO dense vectors.
            pc.create_index(name=config.pinecone_index, dimension=dimension, metric="cosine",
                            spec=ServerlessSpec(cloud=args.cloud, region=args.region), timeout=180)
        index = pc.describe_index(config.pinecone_index)
        if index.dimension != dimension or str(index.metric).lower() != "cosine" or not index.status.ready:
            raise ValueError("Existing index is incompatible or unavailable")
        print(json.dumps({"exists": True, "dimension": dimension, "ready": True}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        print("Pinecone setup failed; verify private credentials, index dimension, metric, account and region", file=sys.stderr)
        raise SystemExit(2)
