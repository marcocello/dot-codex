#!/usr/bin/env python3
"""Independent acceptance via real CLI processes and durable state read-back."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest

HARNESS = Path(__file__).resolve().parents[4]
SCRIPTS = HARNESS / "scripts"
PYTHON = sys.executable
FEATURE = "docs/features/sample"
OWNER = "acceptance-fixture-implementer"


def execute(root, script, *args, timeout=12):
    return subprocess.run(
        [PYTHON, str(SCRIPTS / script), *map(str, args)], cwd=root,
        capture_output=True, text=True, timeout=timeout,
    )


def read_json(path):
    return json.loads(path.read_text())


class Repository:
    def __init__(self):
        self.temp = tempfile.TemporaryDirectory(prefix="completion-acceptance-")
        self.root = Path(self.temp.name).resolve()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.feature = self.root / FEATURE
        self.proof = self.feature / "proof"
        self.proof.mkdir(parents=True)
        self.write(".gitignore", "ignored-config.txt\n__pycache__/\n")
        self.write("README.md", "# Disposable acceptance repository\n")
        self.write("app.py", "print('application-ok')\n")
        self.write("test_app.py", "# Fixture regression input\n")
        self.write("fixture.json", '{"value": "ordinary"}\n')
        self.write("ignored-config.txt", "private-synthetic-value-before\n")
        self.write(FEATURE + "/FEATURE.md", "# Sample accepted behavior\nThe public app prints application-ok.\n")
        self.write(FEATURE + "/PROOF.md", "# Sample proof\nExecute the application and assert its public output.\n")
        self.write(FEATURE + "/proof/helper.txt", "Independent determining fixture\n")
        self.runner = self.proof / "run.sh"
        self.runner.write_text(
            "#!/bin/sh\nset -eu\n"
            f"test \"$({shlex.quote(PYTHON)} app.py)\" = application-ok\n"
            "printf 'proof stdout\\n'\nprintf 'proof stderr\\n' >&2\n"
        )
        self.runner.chmod(0o755)
        self.status = self.root / "docs/features/status.json"
        self.set_state("active")
        subprocess.run(["git", "add", "app.py"], cwd=self.root, check=True)

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    def set_state(self, state, proof_run=None):
        self.status.write_text(json.dumps({"version": 2, "features": [{
            "id": "sample", "feature_dir": FEATURE, "priority": 1,
            "status": state, "owner": OWNER if state == "active" else None,
            "proof_run": proof_run, "notes": "",
        }]}) + "\n")

    def relative(self, path):
        return Path(path).relative_to(self.root).as_posix()

    def capture(self, *, kind="proof", code=None, target=None, include=(), timeout="3"):
        args = ["--feature-dir", FEATURE, "--timeout-seconds", timeout,
                "--note", "independent completion acceptance", "--kind", kind]
        if target is not None:
            args += ["--target", target]
        for path in include:
            args += ["--include", path]
        if kind == "regression":
            args += ["--", PYTHON, "-c", code or "print('regression-ok')"]
        completed = execute(self.root, "proof_run_capture.py", *args)
        area = "proof" if kind == "proof" else "tests"
        runs = sorted((self.feature / area / "runs").glob("*"))
        return completed, runs[-1] if runs else None

    def review(self, run, *, regressions=(), implementer=OWNER,
               author="acceptance-fixture-author", reviewer="acceptance-fixture-reviewer",
               verdict="PASS", summary="Reviewed accepted behavior against retained execution."):
        args = ["review", "--root", str(self.root), "--proof-run", self.relative(run),
                "--implementer", implementer, "--author", author, "--reviewer", reviewer,
                "--verdict", verdict, "--summary", summary]
        for regression in regressions:
            args += ["--regression-run", self.relative(regression)]
        return execute(self.root, "verification_receipt.py", *args)

    def transition(self, before="active", after="done", run=None, owner=OWNER):
        args = ["--root", str(self.root), "--id", "sample", "--owner", owner,
                "--from", before, "--to", after]
        if run is not None:
            args += ["--proof-run", self.relative(run)]
        return execute(self.root, "feature_status.py", *args)


class CompletionAcceptance(unittest.TestCase):
    def repo(self):
        fixture = Repository()
        self.addCleanup(fixture.temp.cleanup)
        return fixture

    def passes(self, completed):
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def rejects(self, completed):
        self.assertNotEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def capture_pass(self, repo, **kwargs):
        completed, run = repo.capture(**kwargs)
        self.passes(completed)
        self.assertIsNotNone(run, "capture did not retain an attempt")
        self.assertEqual(read_json(run / "result.json")["status"], "PASS")
        return run

    def reviewed(self, repo, **kwargs):
        run = self.capture_pass(repo, **kwargs)
        self.passes(repo.review(run))
        return run

    def completion_rejected_unchanged(self, repo, run, owner=OWNER):
        before = repo.status.read_bytes()
        self.rejects(repo.transition(run=run, owner=owner))
        self.assertEqual(repo.status.read_bytes(), before, "rejection changed lifecycle state or ownership")

    def test_successful_receipt_backed_completion_and_reopening(self):
        repo = self.repo()
        run = self.reviewed(repo)
        receipt = read_json(run / "review.json")
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertEqual(receipt["proof_run"], repo.relative(run))
        self.assertEqual(receipt["target"], "local-worktree")
        self.assertEqual({receipt[key] for key in ("implementer", "author", "reviewer")},
                         {OWNER, "acceptance-fixture-author", "acceptance-fixture-reviewer"})
        self.assertTrue(receipt["summary"].strip())
        self.assertTrue(receipt["proof_digest"])
        self.passes(repo.transition(run=run))
        entry = read_json(repo.status)["features"][0]
        self.assertEqual((entry["status"], entry["owner"], entry["proof_run"]),
                         ("done", None, repo.relative(run)))
        self.passes(repo.transition(before="done", after="active"))
        repo.write("app.py", "print('application-changed')\n")
        self.completion_rejected_unchanged(repo, run)

    def test_capture_metadata_determinism_scope_target_and_no_source_dump(self):
        repo = self.repo()
        first = self.capture_pass(repo, target="local-test-service")
        second = self.capture_pass(repo, target="local-test-service")
        left, right = read_json(first / "result.json"), read_json(second / "result.json")
        manifest = read_json(second / "candidate.json")
        canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(right["candidate_digest"], hashlib.sha256(canonical).hexdigest())
        self.assertEqual(left["candidate_digest"], right["candidate_digest"])
        self.assertEqual(manifest["version"], 1)
        self.assertEqual(manifest["selection"], "git-visible+acceptance")
        self.assertEqual(manifest["feature_dir"], FEATURE)
        self.assertEqual(manifest["include"], [])
        self.assertIn("app.py", manifest["files"])
        self.assertIn("test_app.py", manifest["files"])
        self.assertIn(FEATURE + "/proof/helper.txt", manifest["files"])
        self.assertNotIn("ignored-config.txt", manifest["files"])
        self.assertNotIn("docs/features/status.json", manifest["files"])
        self.assertFalse(any("/runs/" in path for path in manifest["files"]))
        for path in (second / "candidate.json", second / "result.json", second / "attempt-start.json"):
            self.assertNotIn("private-synthetic-value-before", path.read_text())
            self.assertNotIn("print('application-ok')", path.read_text())
        for name in ("result.json", "attempt-start.json"):
            value = read_json(second / name)
            self.assertEqual(value["target"], "local-test-service")
            self.assertEqual(value["evidence_version"], 1)
            self.assertEqual(value["candidate_digest"], right["candidate_digest"])
        self.assertEqual((second / "stdout.txt").read_text(), "proof stdout\n")
        self.assertEqual((second / "stderr.txt").read_text(), "proof stderr\n")
        self.passes(repo.review(second))
        self.passes(repo.transition(run=second))

    def test_missing_receipt_or_fingerprint_cannot_complete(self):
        for missing in ("review.json", "candidate.json"):
            with self.subTest(missing=missing):
                repo = self.repo()
                run = self.reviewed(repo)
                (run / missing).unlink()
                self.completion_rejected_unchanged(repo, run)
        repo = self.repo()
        run = self.capture_pass(repo)
        result = read_json(run / "result.json")
        result.pop("candidate_digest", None)
        (run / "result.json").write_text(json.dumps(result))
        self.rejects(repo.review(run))
        self.completion_rejected_unchanged(repo, run)

    def test_source_acceptance_test_fixture_edits_additions_and_deletions_stale(self):
        mutations = [
            ("app.py", "print('application-changed')\n"),
            ("test_app.py", "# materially changed regression\n"),
            ("fixture.json", '{"value":"changed"}\n'),
            (FEATURE + "/FEATURE.md", "# Different accepted behavior\n"),
            (FEATURE + "/PROOF.md", "# Different assertions\n"),
            (FEATURE + "/proof/run.sh", "#!/bin/sh\nexit 0\n"),
            (FEATURE + "/proof/helper.txt", "Changed determining helper\n"),
            ("new-module.py", "new_content = True\n"),
            ("app.py", None),
            ("fixture.json", None),
        ]
        for path, replacement in mutations:
            with self.subTest(path=path, deleted=replacement is None):
                repo = self.repo()
                run = self.reviewed(repo)
                if replacement is None:
                    (repo.root / path).unlink()
                else:
                    repo.write(path, replacement)
                self.rejects(repo.review(run))
                self.completion_rejected_unchanged(repo, run)

    def test_in_run_candidate_or_selected_snapshot_change_converts_zero_to_failure(self):
        cases = [
            "from pathlib import Path; Path('app.py').write_text('changed')",
            f"from pathlib import Path; Path('{FEATURE}/proof/helper.txt').write_text('changed')",
            f"from pathlib import Path; runs=sorted(Path('{FEATURE}/tests/runs').iterdir()); (runs[-1]/'FEATURE.md').write_text('altered snapshot')",
        ]
        for code in cases:
            with self.subTest(code=code):
                repo = self.repo()
                completed, run = repo.capture(kind="regression", code=code)
                self.rejects(completed)
                result = read_json(run / "result.json")
                self.assertEqual(result["runner_returncode"], 0)
                self.assertEqual(result["status"], "FAIL")
                self.assertTrue(result.get("candidate_changes") or result.get("input_changes"))
        repo = self.repo()
        repo.runner.write_text("#!/bin/sh\nset -eu\nprintf changed > app.py\n")
        completed, run = repo.capture()
        self.rejects(completed)
        result = read_json(run / "result.json")
        self.assertEqual(result["runner_returncode"], 0)
        self.assertEqual(result["status"], "FAIL")

    def test_explicit_ignored_inputs_are_bound_without_dumping_values(self):
        repo = self.repo()
        run = self.reviewed(repo)
        repo.write("ignored-config.txt", "private-synthetic-value-after\n")
        self.passes(repo.transition(run=run))
        self.passes(repo.transition(before="done", after="active"))
        run = self.reviewed(repo, include=("ignored-config.txt",))
        manifest = read_json(run / "candidate.json")
        self.assertIn("ignored-config.txt", manifest["include"])
        self.assertIn("ignored-config.txt", manifest["files"])
        self.assertNotIn("private-synthetic-value-after", (run / "candidate.json").read_text())
        repo.write("ignored-config.txt", "private-synthetic-value-final\n")
        self.rejects(repo.review(run))
        self.completion_rejected_unchanged(repo, run)

    def test_regressions_pass_current_target_matched_and_cannot_replace_proof(self):
        repo = self.repo()
        proof = self.capture_pass(repo)
        regression = self.capture_pass(repo, kind="regression")
        self.passes(repo.review(proof, regressions=(regression,)))
        receipt = read_json(proof / "review.json")
        self.assertEqual(receipt["regressions"][0]["run"], repo.relative(regression))
        self.assertTrue(receipt["regressions"][0]["digest"])
        self.completion_rejected_unchanged(repo, regression)
        relocated = repo.proof / "runs/zz-regression-disguised-as-proof"
        shutil.copytree(regression, relocated)
        self.rejects(repo.review(relocated))
        self.completion_rejected_unchanged(repo, relocated)
        shutil.rmtree(relocated)
        self.passes(repo.transition(run=proof))

    def test_failed_stale_or_different_target_regressions_cannot_support_pass(self):
        for condition in ("failed", "stale", "target"):
            with self.subTest(condition=condition):
                repo = self.repo()
                if condition == "failed":
                    completed, regression = repo.capture(kind="regression", code="raise SystemExit(9)")
                    self.rejects(completed)
                else:
                    regression = self.capture_pass(repo, kind="regression", target="other-target" if condition == "target" else None)
                if condition == "stale":
                    repo.write("fixture.json", '{"value":"new-candidate"}\n')
                proof = self.capture_pass(repo)
                self.rejects(repo.review(proof, regressions=(regression,)))
                self.completion_rejected_unchanged(repo, proof)

    def test_changed_bound_evidence_and_receipt_prevent_completion(self):
        for artifact in ("stdout.txt", "result.json", "candidate.json", "review.json", "regression"):
            with self.subTest(artifact=artifact):
                repo = self.repo()
                proof = self.capture_pass(repo)
                regression = self.capture_pass(repo, kind="regression")
                self.passes(repo.review(proof, regressions=(regression,)))
                target = regression / "stdout.txt" if artifact == "regression" else proof / artifact
                if target.suffix == ".json":
                    value = read_json(target)
                    if artifact == "review.json":
                        value["summary"] = "An altered review rationale"
                    elif artifact == "result.json":
                        value["command"] = ["different-command"]
                    else:
                        value["feature_dir"] = "docs/features/some-other-feature"
                    target.write_text(json.dumps(value))
                else:
                    target.write_text("altered retained output\n")
                self.completion_rejected_unchanged(repo, proof)

    def test_distinct_attribution_and_actual_verdict_are_required(self):
        repo = self.repo()
        proof = self.capture_pass(repo)
        for kwargs in ({"author": OWNER}, {"reviewer": OWNER},
                       {"reviewer": "acceptance-fixture-author"}, {"summary": " "}):
            with self.subTest(kwargs=kwargs):
                self.rejects(repo.review(proof, **kwargs))
        self.passes(repo.review(proof, verdict="FAIL", summary="A material accepted case remains uncovered."))
        self.assertEqual(read_json(proof / "review.json")["verdict"], "FAIL")
        self.completion_rejected_unchanged(repo, proof)
        self.passes(repo.review(proof, implementer="another-implementer"))
        self.completion_rejected_unchanged(repo, proof)

    def test_newer_failed_or_unfinished_official_attempt_invalidates_older_pass(self):
        for newer in ("failed", "unfinished"):
            with self.subTest(newer=newer):
                repo = self.repo()
                proof = self.reviewed(repo)
                if newer == "failed":
                    repo.write("app.py", "raise SystemExit(4)\n")
                    completed, failed = repo.capture()
                    self.rejects(completed)
                    self.assertEqual(read_json(failed / "result.json")["status"], "FAIL")
                    repo.write("app.py", "print('application-ok')\n")
                else:
                    unfinished = repo.proof / "runs/zz-started-unfinished"
                    unfinished.mkdir()
                    (unfinished / "attempt-start.json").write_text('{"status":"STARTED","kind":"proof"}\n')
                self.rejects(repo.review(proof))
                self.completion_rejected_unchanged(repo, proof)
                self.assertEqual(read_json(proof / "result.json")["status"], "PASS")

    def test_historical_inventory_is_readable_but_reopened_completion_requires_current_evidence(self):
        repo = self.repo()
        old = repo.proof / "runs/20200101T000000000000Z"
        old.mkdir(parents=True)
        (old / "result.json").write_text('{"status":"PASS","returncode":0}\n')
        repo.set_state("done", repo.relative(old))
        repo.write("app.py", "print('unrelated present-day state')\n")
        self.passes(execute(repo.root, "gate.py", "--root", repo.root, "--profile", "other"))
        self.passes(repo.transition(before="done", after="active"))
        self.completion_rejected_unchanged(repo, old)

    def test_draft_only_registration_and_nonempty_structural_readiness(self):
        repo = self.repo()
        repo.status.write_text('{"version":2,"features":[]}\n')
        (repo.feature / "PROOF.md").unlink()
        shutil.rmtree(repo.proof)
        self.passes(repo.transition(before="new", after="draft"))
        self.passes(execute(repo.root, "gate.py", "--root", repo.root, "--profile", "other"))
        before = repo.status.read_bytes()
        self.rejects(repo.transition(before="draft", after="ready"))
        self.assertEqual(repo.status.read_bytes(), before)
        repo.write(FEATURE + "/PROOF.md", "   \n")
        repo.write(FEATURE + "/proof/run.sh", "#!/bin/sh\nexit 0\n")
        repo.runner.chmod(0o755)
        self.rejects(repo.transition(before="draft", after="ready"))
        repo.write(FEATURE + "/PROOF.md", "# Meaningful proof contract\n")
        repo.runner.chmod(0o644)
        self.rejects(repo.transition(before="draft", after="ready"))
        repo.runner.chmod(0o755)
        self.passes(repo.transition(before="draft", after="ready"))
        repo.write(FEATURE + "/FEATURE.md", " \n")
        self.rejects(repo.transition(before="ready", after="active"))
        self.assertEqual(read_json(repo.status)["features"][0]["status"], "ready")
        other = self.repo()
        other.status.write_text('{"version":2,"features":[]}\n')
        other.write(FEATURE + "/FEATURE.md", "\n")
        self.rejects(other.transition(before="new", after="draft"))

    def test_owner_is_preserved_on_rejected_transition(self):
        repo = self.repo()
        proof = self.reviewed(repo)
        self.completion_rejected_unchanged(repo, proof, owner="unrelated-task")
        self.assertEqual(read_json(repo.status)["features"][0]["owner"], OWNER)
        self.passes(repo.transition(run=proof))

    def test_failure_timeout_and_interruption_evidence_and_child_cleanup(self):
        repo = self.repo()
        failed, failed_run = repo.capture(kind="regression", code="import sys; print('kept-out'); print('kept-err',file=sys.stderr); raise SystemExit(7)")
        self.assertEqual(failed.returncode, 7, failed.stderr)
        self.assertEqual(read_json(failed_run / "result.json")["status"], "FAIL")
        self.assertEqual((failed_run / "stdout.txt").read_text(), "kept-out\n")
        self.assertEqual((failed_run / "stderr.txt").read_text(), "kept-err\n")
        timed, timed_run = repo.capture(kind="regression", code="import time; print('waiting',flush=True); time.sleep(20)", timeout="0.15")
        self.assertEqual(timed.returncode, 124, timed.stdout + timed.stderr)
        result = read_json(timed_run / "result.json")
        self.assertEqual(result["status"], "TIMEOUT")
        with self.assertRaises(ProcessLookupError):
            os.kill(result["runner_pid"], 0)
        command = [PYTHON, str(SCRIPTS / "proof_run_capture.py"), "--feature-dir", FEATURE,
                   "--timeout-seconds", "8", "--note", "interruption acceptance", "--kind", "regression",
                   "--", PYTHON, "-c", "import time; print('interrupt-ready',flush=True); time.sleep(20)"]
        process = subprocess.Popen(command, cwd=repo.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            ready = False
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                runs = sorted((repo.feature / "tests/runs").glob("*"))
                output = runs[-1] / "stdout.txt" if runs else None
                if output and output.exists() and "interrupt-ready" in output.read_text():
                    ready = True
                    break
                if process.poll() is not None:
                    break
                time.sleep(0.02)
            self.assertTrue(ready, "real child never reached the interruption point")
            process.send_signal(signal.SIGTERM)
            stdout, stderr = process.communicate(timeout=8)
            self.assertEqual(process.returncode, 128 + signal.SIGTERM, stdout + stderr)
            result = read_json(runs[-1] / "result.json")
            self.assertEqual(result["status"], "INTERRUPTED")
            with self.assertRaises(ProcessLookupError):
                os.kill(result["runner_pid"], 0)
        finally:
            if process.poll() is None:
                process.terminate()
                process.communicate(timeout=8)
        self.assertTrue((failed_run / "result.json").exists(), "later attempts erased earlier failure")


if __name__ == "__main__":
    unittest.main(verbosity=2)
