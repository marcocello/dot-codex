"""Exercise clean-checkout proof setup without changing historical evidence."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

FEATURE = Path(__file__).resolve().parents[1]


class RetainedFixtures(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='retained-fixtures-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / 'trials'
        shutil.copytree(FEATURE / 'evidence/trials', self.root, ignore=shutil.ignore_patterns('vendor'))

    def run_proof(self):
        return subprocess.run(['bash', str(FEATURE / 'proof/run.sh'), str(self.root)],
                              capture_output=True, text=True, timeout=20)

    def test_clean_checkout_restores_original_fixture_bytes(self):
        result = self.run_proof()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in ('baseline-integration', 'candidate-integration'):
            base = self.root / name
            relative = 'fixture/vendor/archivebox.py'
            expected = json.loads((base / 'inputs.json').read_text())[relative]
            self.assertEqual(hashlib.sha256((base / relative).read_bytes()).hexdigest(), expected)

    def test_existing_modified_fixture_is_retained_and_rejected(self):
        target = self.root / 'baseline-integration/fixture/vendor/archivebox.py'
        target.parent.mkdir()
        target.write_text('changed fixture\n')
        result = self.run_proof()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_text(), 'changed fixture\n')
        self.assertIn('changed fixture/vendor/archivebox.py', result.stderr)

    def test_missing_observations_are_not_generated(self):
        trace = self.root / 'candidate-review/trace.md'
        trace.unlink()
        result = self.run_proof()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(trace.exists())

    def test_recorded_hash_mismatch_refuses_restoration(self):
        record = self.root / 'baseline-integration/inputs.json'
        values = json.loads(record.read_text())
        values['fixture/vendor/archivebox.py'] = '0' * 64
        record.write_text(json.dumps(values))
        result = self.run_proof()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('does not match the recorded vendor hashes', result.stderr)
        for name in ('baseline-integration', 'candidate-integration'):
            self.assertFalse((self.root / name / 'fixture/vendor/archivebox.py').exists())


if __name__ == '__main__':
    unittest.main()
