"""Public CLI and provider-boundary acceptance for private context retrieval."""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest


CHAT = "15550000001@s.whatsapp.net"
OTHER = "15550000002@s.whatsapp.net"
WHEN = "2026-10-24T10:00:00Z"
MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def cli(config, command, *args, ok=True):
    result = subprocess.run([sys.executable, "-m", "secondbrain_context", command,
                             "--config", str(config), *args], text=True, capture_output=True)
    if ok:
        assert result.returncode == 0, result.stderr + result.stdout
    return result, json.loads(result.stdout) if result.stdout.strip() else None


@pytest.fixture
def archive(tmp_path):
    store = tmp_path / "wacli"
    store.mkdir()
    db = sqlite3.connect(store / "wacli.db")
    db.execute("""CREATE TABLE messages(chat_jid TEXT, msg_id TEXT, sender_jid TEXT,
        ts INTEGER, display_text TEXT, text TEXT, from_me INTEGER, deleted_at INTEGER,
        payload_purged_at INTEGER, PRIMARY KEY(chat_jid,msg_id))""")
    import datetime
    at = int(datetime.datetime.fromisoformat(WHEN.replace("Z", "+00:00")).timestamp())
    for chat, mid, text, direction in [
        (CHAT, "m1", "The automobile is parked near the railway station.", 0),
        (CHAT, "m2", "I will send the travel itinerary tomorrow.", 1),
        (OTHER, "private", "This excluded conversation must remain private.", 0),
    ]:
        db.execute("INSERT INTO messages VALUES(?,?,?,?,?,?,?,?,?)",
                   (chat, mid, chat, at, text, text, direction, None, None))
    db.commit()
    db.close()
    journal = tmp_path / "journal.json"
    changes = [change(1, CHAT, "m1"), change(2, CHAT, "m2"), change(3, OTHER, "private")]
    journal.write_text(json.dumps({"changes": changes}))
    binary = tmp_path / "wacli-fixture"
    binary.write_text(f"#!{sys.executable}\n" + '''import json, pathlib, sys
args = sys.argv[1:]
assert args[:2] == ['--read-only', '--json']
assert args[2] == '--store'
assert args[4:6] == ['messages', 'changes']
store = pathlib.Path(args[3])
fixture = json.loads((store.parent / 'journal.json').read_text())
if fixture.get('fail'):
    sys.stderr.write('fixture journal unavailable')
    sys.exit(3)
if '--checkpoint' in args:
    end = max((c['sequence'] for c in fixture['changes']), default=0)
    print(json.dumps({'success':True,'data':{'store_id':'fixture-store','changes':[],
        'has_more':False,'next_checkpoint':f'checkpoint:{end}'},'error':None}))
    sys.exit(0)
since = args[args.index('--since')+1]
start = 0 if since == 'beginning' else int(since.split(':')[-1])
limit = int(args[args.index('--limit')+1])
changes = [c for c in fixture['changes'] if c['sequence'] > start]
page = changes[:limit]
end = page[-1]['sequence'] if page else start
print(json.dumps({'success':True,'data':{'store_id':'fixture-store','changes':page,
    'has_more':len(changes)>len(page),'next_checkpoint':f'checkpoint:{end}'},'error':None}))
''')
    binary.chmod(0o700)
    config = tmp_path / "context.toml"
    config.write_text(f'''schema = 1
workspace = {json.dumps(str(tmp_path / "memory"))}
sync_every_seconds = 300
[search]
model = "{MODEL}"
[[sources]]
id = "whatsapp"
provider = "wacli"
enabled = true
[sources.scope]
store = {json.dumps(str(store))}
binary = {json.dumps(str(binary))}
chats = ["{CHAT}"]
since = "2026-10-20T00:00:00Z"
''')
    return config, store, journal


def change(seq, chat, mid, operation="upsert", **extra):
    return dict(sequence=seq, chat_jid=chat, msg_id=mid, operation=operation,
                recorded_at=WHEN, message_time=WHEN, **extra)


def test_scope_restart_retry_and_delete(archive):
    config, store, journal = archive
    before = hashlib.sha256((store / "wacli.db").read_bytes()).hexdigest()
    _, first = cli(config, "sync", "--no-index", "--page-size", "1")
    assert first["ok"]
    _, result = cli(config, "search", "travel", "--mode", "text")
    assert len(result["results"]) == 1
    hit = result["results"][0]
    assert hit["direction"] == "sent"
    assert hit["ref"]["chat_jid"] == CHAT
    assert hit["ref"]["message_id"] == "m2"
    assert cli(config, "search", "excluded", "--mode", "text")[1]["results"] == []
    cli(config, "sync", "--no-index")
    assert len(cli(config, "search", "automobile", "--mode", "text")[1]["results"]) == 1
    assert hashlib.sha256((store / "wacli.db").read_bytes()).hexdigest() == before
    journal.write_text(json.dumps({"changes": [], "fail": True}))
    failed, _ = cli(config, "sync", "--no-index", ok=False)
    assert failed.returncode != 0
    assert cli(config, "search", "automobile", "--mode", "text")[1]["results"] == []
    workspace = config.parent / "memory/context.sqlite3"
    db = sqlite3.connect(workspace)
    assert db.execute("SELECT cursor FROM checkpoints").fetchone()[0] == "checkpoint:3"
    db.close()
    with sqlite3.connect(store / "wacli.db") as db:
        db.execute("UPDATE messages SET deleted_at=1, display_text='', text='' WHERE msg_id='m2'")
    journal.write_text(json.dumps({"changes": [change(4, CHAT, "m2", "delete", reason="hard_purge")]}))
    cli(config, "sync", "--no-index")
    assert cli(config, "search", "itinerary", "--mode", "text")[1]["results"] == []
    result, _ = cli(config, "read", hit["id"], ok=False)
    assert result.returncode != 0
    with sqlite3.connect(workspace) as db:
        assert "itinerary" not in " ".join(str(row) for row in db.execute("SELECT * FROM documents"))


def test_disabled_changed_scope_and_erasure(archive):
    config, _, _ = archive
    cli(config, "sync", "--no-index")
    hit = cli(config, "search", "automobile", "--mode", "text")[1]["results"][0]
    original = config.read_text()
    config.write_text(original.replace(CHAT, OTHER))
    assert cli(config, "search", "automobile", "--mode", "text")[1]["results"] == []
    assert cli(config, "sync", "--no-index", ok=False)[0].returncode != 0
    config.write_text(original.replace("enabled = true", "enabled = false"))
    assert cli(config, "read", hit["id"], ok=False)[0].returncode != 0
    cli(config, "forget", "whatsapp", "--confirm")
    with sqlite3.connect(config.parent / "memory/context.sqlite3") as db:
        assert db.execute("SELECT count(*) FROM documents").fetchone()[0] == 0


def test_disabled_first_run_does_not_lock_unselected_scope(archive):
    config, _, _ = archive
    selected = config.read_text()
    config.write_text(selected.replace("enabled = true", "enabled = false"))
    cli(config, "sync", "--no-index")
    config.write_text(selected)
    cli(config, "sync", "--no-index")
    assert cli(config, "search", "automobile", "--mode", "text")[1]["results"]


def test_real_semantic_search_and_mcp(archive):
    config, _, _ = archive
    cli(config, "sync")
    _, result = cli(config, "search", "Where is the car?", "--mode", "semantic")
    assert result["results"][0]["ref"]["message_id"] == "m1"
    assert result["results"][0]["evidence_only"] is True
    _, italian = cli(config, "search", "Dove si trova la macchina?", "--mode", "semantic")
    assert italian["results"][0]["ref"]["message_id"] == "m1"

    async def check_mcp():
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        parameters = StdioServerParameters(command=sys.executable,
            args=["-m", "secondbrain_context", "mcp", "--config", str(config)])
        async with stdio_client(parameters) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                tools = (await session.list_tools()).tools
                assert {tool.name for tool in tools} == {"search_context", "read_context"}
                assert all(tool.annotations.readOnlyHint for tool in tools)
                result = await session.call_tool("search_context", {"query": "car", "mode": "semantic"})
                assert not result.isError
                data = result.structuredContent
                assert data["results"][0]["ref"]["message_id"] == "m1"
                read = await session.call_tool("read_context", {"document_id": data["results"][0]["id"]})
                assert not read.isError
                assert "railway station" in read.structuredContent["document"]["text"]
                config.write_text(config.read_text().replace("enabled = true", "enabled = false"))
                hidden = await session.call_tool("search_context", {"query": "car", "mode": "text"})
                assert not hidden.isError and hidden.structuredContent["results"] == []
    asyncio.run(check_mcp())
    cli(config, "forget", "whatsapp", "--confirm")
    from qdrant_client import QdrantClient
    vectors = QdrantClient(path=str(config.parent / "memory/vectors"))
    assert vectors.count("context").count == 0
    vectors.close()


def test_index_failure_keeps_collected_pages_for_retry(archive):
    config, _, _ = archive
    cli(config, "sync", "--no-index")
    original = config.read_text()
    config.write_text(original.replace(MODEL, "unsupported-model"))
    failed, result = cli(config, "index", ok=False)
    assert failed.returncode != 0
    with sqlite3.connect(config.parent / "memory/context.sqlite3") as db:
        assert db.execute("SELECT cursor FROM checkpoints").fetchone()[0] == "checkpoint:3"
        assert db.execute("SELECT count(*) FROM index_jobs").fetchone()[0] == 2
    config.write_text(original)
    assert cli(config, "search", "automobile", "--mode", "text")[1]["results"]
