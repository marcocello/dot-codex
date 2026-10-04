"""Implementer regressions for malformed inputs and private state boundaries."""
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "scripts/secondbrain.py"


class StateEdges(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "state"
        self.call("init")

    def call(self, command, payload=None, success=True):
        run = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), command],
                             input=json.dumps(payload) if payload is not None else "",
                             text=True, capture_output=True, timeout=10)
        data = json.loads(run.stdout)
        self.assertEqual(data["ok"], success, run.stdout)
        self.assertEqual(run.returncode == 0, success, run.stderr)
        return data

    def test_private_creation_and_nonfinite_json(self):
        for filename in ("secondbrain.sqlite3", "profile.md", "priorities.md", "rules.md"):
            self.assertEqual(stat.S_IMODE((self.root / filename).stat().st_mode) & 0o077, 0)
        self.call("source-put", {"id": "source", "provider": "test", "scope": "one", "extra": float("nan")}, False)
        self.assertEqual(self.call("sources")["sources"], [])

    def test_no_input_body_in_conflict_and_no_partial_events(self):
        self.call("source-put", {"id": "s", "provider": "test", "scope": "one"})
        event = {"id": "m", "revision": "r", "occurred_at": "2031-01-01T10:00:00Z",
                 "kind": "message", "ref": "synthetic://one/m", "content": {"text": "retained"}}
        self.call("ingest", {"source_id": "s", "expected_cursor": None, "cursor": "c1", "events": [event]})
        invalid = {**event, "id": "second", "content": ["PRIVATE-BODY"]}
        out = self.call("ingest", {"source_id": "s", "expected_cursor": "c1", "cursor": "c2",
                                  "events": [{**event, "id": "new"}, invalid]}, False)
        self.assertNotIn("PRIVATE-BODY", json.dumps(out))
        self.assertEqual([r["id"] for r in self.call("pending")["events"]], ["m"])
        self.assertEqual(self.call("sources")["sources"][0]["cursor"], "c1")

    def test_duplicate_agenda_changes_rollback_and_queries_do_not_consume_stdin(self):
        item = {"id": "goal", "expected_version": 0, "outcome": "Prepare briefing", "state": "open",
                "next_check_at": "2031-01-01T10:00:00Z", "evidence": [], "reason": "User asked"}
        self.call("agenda-put", {"agenda": [item, {**item, "expected_version": 1}]}, False)
        self.assertEqual(self.call("context", {"unexpected": "stdin is not a query payload"})["agenda"], [])

    def test_oversized_evidence_ids_fail_structurally_without_mutation(self):
        query = Path(self.temp.name) / "query.json"
        query.write_text(json.dumps({"seqs": [10**30]}), encoding="utf-8")
        run = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root),
                              "events", "--input", str(query)],
                             text=True, capture_output=True, timeout=10)
        self.assertEqual(run.returncode, 1)
        self.assertFalse(json.loads(run.stdout)["ok"])
        self.assertNotIn("Traceback", run.stderr)
        self.call("apply", {"event_seqs": [10**30], "facts": [], "agenda": []}, False)
        self.assertEqual(self.call("context")["facts"], [])


if __name__ == "__main__":
    unittest.main()
