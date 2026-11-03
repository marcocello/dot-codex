"""Exercise the real capture CLI against legacy and paginated app history."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
CAPTURE = ROOT / "skills/harness-capture-interactions/scripts/capture_interactions.py"

SERVER = '''#!/usr/bin/env python3
import json, os, sys
scenario = json.load(open(os.environ["CAPTURE_SCENARIO"]))
for line in sys.stdin:
    message = json.loads(line)
    if "id" not in message:
        continue
    method, params = message["method"], message.get("params", {})
    error = None
    if method == "initialize":
        result = {}
    elif method == "thread/list":
        assert params["archived"] is False and params["sourceKinds"] == ["vscode"]
        result = {"data": scenario["threads"], "nextCursor": None}
    elif method == "thread/read":
        thread = next(t for t in scenario["threads"] if t["id"] == params["threadId"])
        result = {"thread": thread}
    elif method == "thread/turns/list":
        assert params["itemsView"] == "full" and params["sortDirection"] == "asc"
        pages = scenario["pages"].get(params["threadId"])
        if pages is None:
            error = {"message": "history unavailable"}
            result = {}
        else:
            position = int(params.get("cursor", "0"))
            result = pages[position]
    else:
        raise AssertionError(method)
    response = {"id": message["id"], "error": error} if error else {"id": message["id"], "result": result}
    print(json.dumps(response), flush=True)
'''


def user(text):
    return {"type": "userMessage", "id": "user-" + text, "content": [{"type": "text", "text": text}]}


def assistant(text, phase="final_answer"):
    return {"type": "agentMessage", "id": "agent-" + text, "text": text, "phase": phase}


def turn(identity, items, status="completed"):
    return {"id": identity, "status": status, "itemsView": "full", "items": items,
            "startedAt": 1700000000, "completedAt": 1700000001}


class CaptureJourney(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.server = self.root / "codex"
        self.server.write_text(SERVER)
        self.server.chmod(0o700)
        self.scenario = {"threads": [], "pages": {}}
        self.scenario_path = self.root / "scenario.json"
        self.environment = dict(os.environ, CAPTURE_SCENARIO=str(self.scenario_path))

    def add_thread(self, identity, pages=None, **extra):
        thread = {"id": identity, "cwd": str(self.root), "path": str(self.root / (identity + ".jsonl")),
                  "historyMode": "paginated", "title": "Example", **extra}
        self.scenario["threads"].append(thread)
        if pages is not None:
            self.scenario["pages"][identity] = pages
        return thread

    def capture(self, *args, expected=0):
        self.scenario_path.write_text(json.dumps(self.scenario))
        result = subprocess.run([sys.executable, str(CAPTURE), *args, "--project-root", str(self.root),
                                 "--codex-bin", str(self.server), "--workspace-state", str(self.root / "state.json")],
                                env=self.environment, capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def record_path(self, identity):
        return self.root / "docs/interactions/threads" / (identity + ".json")

    def record(self, identity):
        return json.loads(self.record_path(identity).read_text())

    def test_paginated_cli_reads_all_pages_filters_and_retains(self):
        secret = "ghp_" + "a" * 36
        items = [user("<skill>INJECTED_SKILL</skill>\nHello " + secret),
                 {"type": "reasoning", "content": "HIDDEN_REASONING"},
                 {"type": "commandExecution", "aggregatedOutput": "TOOL_OUTPUT"},
                 assistant("Working", "commentary"), assistant("Done"),
                 user("Again"), user("Again")]
        thread = self.add_thread("migrated", [
            {"data": [turn("one", items)], "nextCursor": "1"},
            {"data": [turn("empty", []), turn("pending", [user("UNFINISHED")], "inProgress")], "nextCursor": None},
        ])
        self.scenario["threads"].append(dict(thread))  # Duplicate legacy session metadata.
        self.add_thread("other-project", [], cwd=str(self.root / "unrelated"))
        result = self.capture()
        self.assertIn("captured=1", result.stdout)
        self.assertIn("unavailable=0", result.stdout)
        record = self.record("migrated")
        self.assertEqual([t["id"] for t in record["turns"]], ["one"])
        self.assertEqual([m["text"] for m in record["turns"][0]["messages"]],
                         ["Hello [REDACTED:github_token]", "Working", "Done", "Again", "Again"])
        self.assertEqual(record["capture"]["incomplete_turn_ids"], ["pending"])
        self.assertEqual(record["capture"]["omitted_empty_turn_ids"], ["empty"])
        self.assertIn("started_at", record["turns"][0])
        for excluded in [secret, "INJECTED_SKILL", "HIDDEN_REASONING", "TOOL_OUTPUT", "UNFINISHED"]:
            self.assertNotIn(excluded, json.dumps(record))
        self.assertFalse(self.record_path("other-project").exists())
        before = self.record_path("migrated").stat().st_mtime_ns
        self.assertIn("unchanged=1", self.capture().stdout)
        self.assertEqual(before, self.record_path("migrated").stat().st_mtime_ns)
        self.scenario["pages"]["migrated"][1]["data"][-1]["status"] = "completed"
        self.assertIn("updated=1", self.capture("current", "--task-id", "migrated").stdout)
        self.assertEqual(len(self.record("migrated")["turns"]), 2)
        saved = self.record_path("migrated").read_bytes()
        self.scenario["threads"] = []
        self.capture()
        self.assertEqual(saved, self.record_path("migrated").read_bytes())

    def test_failed_history_preserves_existing_record(self):
        self.add_thread("migrated", [{"data": [turn("one", [user("Keep")])], "nextCursor": None}])
        self.capture()
        saved = self.record_path("migrated").read_bytes()
        del self.scenario["pages"]["migrated"]
        self.assertIn("unavailable=1", self.capture(expected=1).stdout)
        self.assertEqual(saved, self.record_path("migrated").read_bytes())

    def test_summary_and_cursor_cycles_fail_without_overwriting(self):
        for page in [
            {"data": [{**turn("one", [user("Incomplete page")]), "itemsView": "summary"}], "nextCursor": None},
            {"data": [], "nextCursor": "0"},
        ]:
            self.scenario = {"threads": [], "pages": {}}
            self.add_thread("broken", [page])
            self.capture(expected=1)
            self.assertFalse(self.record_path("broken").exists())

    def test_empty_and_interrupted_turns(self):
        self.add_thread("empty", [{"data": [turn("empty", [])], "nextCursor": None}])
        self.add_thread("aborted", [{"data": [turn("stopped", [user("PRIVATE_PENDING")], "interrupted")], "nextCursor": None}])
        self.assertIn("empty=1", self.capture().stdout)
        self.assertFalse(self.record_path("empty").exists())
        self.assertEqual(self.record("aborted")["turns"], [])
        self.assertNotIn("PRIVATE_PENDING", self.record_path("aborted").read_text())

    def test_legacy_cli_deduplicates_response_mirrors_and_excludes_context(self):
        thread = self.add_thread("legacy", historyMode="legacy")
        def event(kind, payload):
            return {"type": kind, "timestamp": "2026-01-01T00:00:00Z", "payload": payload}
        values = [event("session_meta", {"id": "legacy", "cwd": str(self.root)}),
                  event("event_msg", {"type": "task_started", "turn_id": "one"}),
                  event("response_item", {"type": "message", "role": "user", "content": [
                      {"type": "input_text", "text": "<environment_context>INJECTED</environment_context>"},
                      {"type": "input_text", "text": "Hello"}],
                      "internal_chat_message_metadata_passthrough": {"content_item_kinds": ["context", "user.text"]}}),
                  event("event_msg", {"type": "user_message", "message": "Hello"}),
                  event("event_msg", {"type": "agent_message", "message": "Done", "phase": "final_answer"}),
                  event("event_msg", {"type": "task_complete", "turn_id": "one"})]
        Path(thread["path"]).write_text("\n".join(json.dumps(v) for v in values))
        self.capture()
        self.assertEqual([m["text"] for m in self.record("legacy")["turns"][0]["messages"]], ["Hello", "Done"])
        self.assertNotIn("INJECTED", self.record_path("legacy").read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
