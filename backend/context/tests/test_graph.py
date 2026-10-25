"""Real HTTP adapter/worker with only the Microsoft provider replaced."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from secondbrain_context.config import load
from secondbrain_context.providers import GraphClient
from secondbrain_context.service import read, search, synchronize
from secondbrain_context.store import Store


ACCOUNT = "selected@example.test"


def message(identity, subject, body):
    return {"id": identity, "subject": subject,
            "body": {"contentType": "html", "content": body},
            "from": {"emailAddress": {"address": "alice@example.test"}},
            "receivedDateTime": "2026-10-24T10:00:00Z",
            "webLink": "https://outlook.office.com/mail/inbox/id/" + identity}


@contextmanager
def graph_server():
    state = {"mode": "initial", "account": ACCOUNT, "requests": []}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_GET(self):
            state["requests"].append(self.path)
            assert self.headers["Authorization"] == "Bearer fixture-token"
            code = 200
            if self.path.startswith("/broken/"):
                code, body = 503, {"error": {"message": "provider unavailable"}}
            elif self.path.startswith("/v1.0/me?"):
                body = {"id": "mailbox-1", "mail": state["account"], "userPrincipalName": state["account"]}
            elif state["mode"] == "redirect":
                body = {"value": [], "@odata.nextLink": "https://untrusted.example/steal-token"}
            elif state["mode"] == "fail" and "page=2" in self.path:
                code, body = 503, {"error": {"message": "private upstream details"}}
            elif state["mode"] == "expired":
                code, body = 410, {"error": {"code": "syncStateNotFound"}}
            elif state["mode"] == "cap":
                body = {"value": [message(str(n), "bulk", "message") for n in range(5000)],
                        "@odata.deltaLink": state["base"] + "/me/mailFolders/inbox/messages/delta?deltaToken=complete"}
            elif "deltaToken=complete" in self.path:
                if state["mode"] == "change":
                    body = {"value": [{"id": "m1", "@removed": {"reason": "deleted"}},
                            message("m2", "Updated meeting", "The schedule changed to Friday.")],
                            "@odata.deltaLink": state["base"] + "/me/mailFolders/inbox/messages/delta?deltaToken=changed"}
                else:
                    body = {"value": [], "@odata.deltaLink": state["base"] + self.path[len('/v1.0'):]}
            elif "page=2" in self.path:
                body = {"value": [message("m2", "Travel planning", "<p>Train leaves on Thursday.</p><script>untrusted script</script>")],
                        "@odata.deltaLink": state["base"] + "/me/mailFolders/inbox/messages/delta?deltaToken=complete"}
            else:
                body = {"value": [message("m1", "Invoice payment", "Please pay the invoice on Monday.")],
                        "@odata.nextLink": state["base"] + "/me/mailFolders/inbox/messages/delta?page=2"}
            payload = json.dumps(body).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    state["base"] = f"http://127.0.0.1:{server.server_port}/v1.0"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield state
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def config_for(tmp_path):
    path = tmp_path / "graph.toml"
    path.write_text(f'''schema=1
workspace={json.dumps(str(tmp_path / 'memory'))}
[[sources]]
id="outlook"
provider="microsoft_graph"
enabled=true
[sources.scope]
account="{ACCOUNT}"
client_id="00000000-0000-0000-0000-000000000001"
tenant_id="organizations"
folders=["inbox"]
since="2026-10-20T00:00:00Z"
''')
    return load(path)


def run(config, state, max_pages=20):
    return synchronize(config, index=False, max_pages=max_pages,
                       graph_factory=lambda _: GraphClient(lambda: "fixture-token", state["base"]))


def test_pagination_retry_update_and_delete(tmp_path):
    config = config_for(tmp_path)
    with graph_server() as state:
        state["mode"] = "fail"
        result = run(config, state)
        assert not result["ok"]
        store = Store(config.workspace)
        assert store.checkpoint("outlook", "inbox")[0].endswith("page=2")
        assert store.status()["documents"] == 1
        store.close()
        state["mode"] = "initial"
        assert run(config, state)["ok"]
        result = search(config, "Thursday", mode="text")
        assert result["results"][0]["ref"]["message_id"] == "m2"
        assert "untrusted script" not in result["results"][0]["text"]
        assert run(config, state)["ok"]
        store = Store(config.workspace)
        assert store.status()["documents"] == 2
        store.close()
        state["mode"] = "change"
        assert run(config, state)["ok"]
        assert search(config, "invoice", mode="text")["results"] == []
        assert search(config, "Friday", mode="text")["results"][0]["ref"]["url"].startswith("https://outlook.office.com")


def test_account_and_continuation_scope_are_enforced(tmp_path):
    config = config_for(tmp_path)
    with graph_server() as state:
        state["account"] = "someone-else@example.test"
        assert not run(config, state)["ok"]
        assert all("mailFolders" not in path for path in state["requests"])
        state["account"] = ACCOUNT
        state["mode"] = "redirect"
        assert not run(config, state)["ok"]
        store = Store(config.workspace)
        assert store.checkpoint("outlook", "inbox")[0] is None
        assert store.status()["documents"] == 0
        store.close()


def test_expired_delta_preserves_checkpoint(tmp_path):
    config = config_for(tmp_path)
    with graph_server() as state:
        assert run(config, state)["ok"]
        store = Store(config.workspace)
        previous = store.checkpoint("outlook", "inbox")[0]
        store.close()
        state["mode"] = "expired"
        result = run(config, state)
        assert not result["ok"]
        assert "expired" in result["sources"][0]["error"]
        store = Store(config.workspace)
        assert store.checkpoint("outlook", "inbox")[0] == previous
        store.close()


def test_one_unavailable_source_does_not_stop_another(tmp_path):
    from dataclasses import replace
    from secondbrain_context.config import Source
    config = config_for(tmp_path)
    source = config.sources[0]
    config = replace(config, sources=(Source("unavailable", source.provider, True, source.scope), source))
    with graph_server() as state:
        origin = state["base"].removesuffix("/v1.0")
        result = synchronize(config, index=False, graph_factory=lambda selected:
            GraphClient(lambda: "fixture-token", state["base"] if selected.id == "outlook" else origin + "/broken"))
        assert not result["ok"]
        assert [item["ok"] for item in result["sources"]] == [False, True]
        assert search(config, "invoice", mode="text")["results"][0]["source_id"] == "outlook"


def test_filtered_initial_cap_is_explicit(tmp_path):
    config = config_for(tmp_path)
    with graph_server() as state:
        state["mode"] = "cap"
        result = run(config, state)
        assert not result["ok"]
        assert "5,000" in result["sources"][0]["error"]
        store = Store(config.workspace)
        assert store.checkpoint("outlook", "inbox")[0] is None
        assert store.status()["documents"] == 0
        store.close()
