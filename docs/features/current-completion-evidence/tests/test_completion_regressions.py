"""Implementer regressions complement, but do not replace, independent acceptance."""
import importlib.util
from pathlib import Path
import shutil
import unittest

spec = importlib.util.spec_from_file_location("completion_acceptance_fixture", Path(__file__).parents[1] / "proof/acceptance.py")
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


class CompletionRegressions(unittest.TestCase):
    def repo(self):
        repo = fixture.Repository()
        self.addCleanup(repo.temp.cleanup)
        return repo

    def passes(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def rejected_without_write(self, repo, proof):
        before = repo.status.read_bytes()
        result = repo.transition(run=proof)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(repo.status.read_bytes(), before)

    def test_newer_matching_failed_and_unfinished_regressions_block_completion(self):
        command = "from pathlib import Path; raise SystemExit(int(Path('ignored-config.txt').read_text()))"
        for state in ("failed", "unfinished"):
            with self.subTest(state=state):
                repo = self.repo()
                repo.write("ignored-config.txt", "0")
                result, proof = repo.capture()
                self.passes(result)
                result, support = repo.capture(kind="regression", code=command)
                self.passes(result)
                self.passes(repo.review(proof, regressions=(support,)))
                if state == "failed":
                    repo.write("ignored-config.txt", "1")
                    result, _ = repo.capture(kind="regression", code=command)
                    self.assertNotEqual(result.returncode, 0)
                else:
                    newer = support.parent / "zz-unfinished"
                    newer.mkdir()
                    shutil.copyfile(support / "attempt-start.json", newer / "attempt-start.json")
                self.rejected_without_write(repo, proof)

    def test_unrelated_failed_regression_does_not_invalidate_selected_support(self):
        repo = self.repo()
        result, proof = repo.capture()
        self.passes(result)
        result, support = repo.capture(kind="regression", code="print('selected check')")
        self.passes(result)
        self.passes(repo.review(proof, regressions=(support,)))
        result, _ = repo.capture(kind="regression", code="raise SystemExit(8)")
        self.assertNotEqual(result.returncode, 0)
        self.passes(repo.transition(run=proof))

    def test_cross_feature_support_requires_matching_input_coverage(self):
        for ignored_acceptance in (False, True):
            with self.subTest(ignored_acceptance=ignored_acceptance):
                repo = self.repo()
                supporting_feature = "docs/features/support"
                shutil.copytree(repo.feature, repo.root / supporting_feature)
                if ignored_acceptance:
                    with (repo.root / ".gitignore").open("a") as stream:
                        stream.write(supporting_feature + "/proof/helper.txt\n")
                result, proof = repo.capture()
                self.passes(result)
                result = fixture.execute(
                    repo.root, "proof_run_capture.py", "--feature-dir", supporting_feature,
                    "--kind", "regression", "--timeout-seconds", "3", "--note", "shared candidate check",
                    "--", fixture.PYTHON, "-c",
                    "from pathlib import Path; assert Path('docs/features/support/proof/helper.txt').read_text().strip()",
                )
                self.passes(result)
                support = sorted((repo.root / supporting_feature / "tests/runs").iterdir())[-1]
                result = repo.review(proof, regressions=(support,))
                if ignored_acceptance:
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertFalse((proof / "review.json").exists())
                else:
                    self.passes(result)
                    self.passes(repo.transition(run=proof))

    def test_newer_passing_matching_regression_resolves_failure(self):
        repo = self.repo()
        command = "from pathlib import Path; raise SystemExit(int(Path('ignored-config.txt').read_text()))"
        repo.write("ignored-config.txt", "0")
        result, proof = repo.capture()
        self.passes(result)
        result, support = repo.capture(kind="regression", code=command)
        self.passes(result)
        self.passes(repo.review(proof, regressions=(support,)))
        repo.write("ignored-config.txt", "1")
        result, _ = repo.capture(kind="regression", code=command)
        self.assertNotEqual(result.returncode, 0)
        self.rejected_without_write(repo, proof)
        repo.write("ignored-config.txt", "0")
        result, _ = repo.capture(kind="regression", code=command)
        self.passes(result)
        self.passes(repo.transition(run=proof))

    def test_blocked_discovery_does_not_need_placeholder_acceptance(self):
        repo = self.repo()
        (repo.feature / "PROOF.md").unlink()
        shutil.rmtree(repo.proof)
        self.passes(repo.transition(after="blocked"))
        self.passes(fixture.execute(repo.root, "gate.py", "--root", repo.root, "--profile", "other"))
        self.assertNotEqual(repo.transition(before="blocked", after="ready").returncode, 0)

    def test_new_completion_rechecks_nonempty_active_contracts(self):
        for name in ("FEATURE.md", "PROOF.md"):
            with self.subTest(name=name):
                repo = self.repo()
                (repo.feature / name).write_text(" \n\t")
                result, proof = repo.capture()
                self.passes(result)
                self.passes(repo.review(proof))
                self.rejected_without_write(repo, proof)

    def test_directory_fallback_skips_local_dependencies_and_records_review_provenance(self):
        repo = self.repo()
        shutil.rmtree(repo.root / ".git")
        for directory in (".venv", "node_modules", "vendor"):
            repo.write(directory + "/dependency.txt", "large irrelevant installed dependency")
        result, proof = repo.capture()
        self.passes(result)
        manifest = fixture.read_json(proof / "candidate.json")
        self.assertEqual(manifest["selection"], "directory+acceptance")
        self.assertFalse(any(path.startswith((".venv/", "node_modules/", "vendor/")) for path in manifest["files"]))
        self.passes(repo.review(proof))
        receipt = fixture.read_json(proof / "review.json")
        self.assertTrue(receipt["reviewed_at"].endswith("+00:00"))
        self.assertEqual(receipt["candidate_digest"], fixture.read_json(proof / "result.json")["candidate_digest"])
        result, included = repo.capture(include=("vendor",))
        self.passes(result)
        self.assertIn("vendor/dependency.txt", fixture.read_json(included / "candidate.json")["files"])

    def test_capture_retains_support_for_other_contained_feature_paths(self):
        repo = self.repo()
        repo.feature.rename(repo.root / "feature-package")
        for _ in range(2):
            result = fixture.execute(repo.root, "proof_run_capture.py", "--feature-dir", "feature-package",
                                     "--note", "compatible contained feature path", "--timeout-seconds", "3")
            self.passes(result)
        runs = sorted((repo.root / "feature-package/proof/runs").iterdir())
        self.assertEqual(fixture.read_json(runs[0] / "candidate.json"), fixture.read_json(runs[1] / "candidate.json"))

    def test_repository_root_feature_does_not_force_ignored_nonacceptance_inputs(self):
        repo = self.repo()
        for name in ("FEATURE.md", "PROOF.md", "proof"):
            (repo.feature / name).rename(repo.root / name)
        result = fixture.execute(repo.root, "proof_run_capture.py", "--feature-dir", ".",
                                 "--note", "root feature scope", "--timeout-seconds", "3")
        self.passes(result)
        run = sorted((repo.root / "proof/runs").iterdir())[-1]
        manifest = fixture.read_json(run / "candidate.json")
        self.assertNotIn("ignored-config.txt", manifest["files"])
        self.assertIn("proof/helper.txt", manifest["files"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
