#!/usr/bin/env python3
"""Independent black-box acceptance; no implementation validator is an oracle."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HARNESS = Path(__file__).resolve().parents[4]
SCRIPTS = HARNESS / 'scripts'


class JourneyFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='shared-journey-acceptance-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.run_command(['git', 'init', '-q'])
        self.write('src/journey.txt', 'journey-v1\n')
        self.write('src/access.txt', 'access-v1\n')
        self.write('src/unrelated.txt', 'unrelated-v1\n')
        self.write('docs/features/status.json', json.dumps({'version': 2, 'features': []}))
        self.package('journey', 'src/journey.txt', 'journey-v1')
        self.package('access', 'src/access.txt', 'access-v1')
        self.feature('case', {'AC1': ['docs/verification/journey'], 'AC2': ['docs/verification/access']})
        self.feature('closure', {'AC1': ['docs/verification/journey']})

    def write(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
        return path

    def read(self, relative):
        return json.loads((self.root / relative).read_text())

    def run_command(self, argv, ok=True):
        result = subprocess.run([str(x) for x in argv], cwd=self.root, text=True, capture_output=True, timeout=30)
        if ok:
            self.assertEqual(result.returncode, 0, f'{argv}\n{result.stdout}\n{result.stderr}')
        else:
            self.assertNotEqual(result.returncode, 0, f'Unexpected success: {argv}\n{result.stdout}')
        return result

    def cli(self, script, *args, ok=True):
        return self.run_command([sys.executable, SCRIPTS / script, *args], ok)

    def package(self, name, source, expected):
        base = f'docs/verification/{name}'
        self.write(f'{base}/PROOF.md', f'# {name}\nChecks the observed source fixture through its executable runner.\n')
        runner = self.write(f'{base}/proof/run.sh', '#!/usr/bin/env bash\nset -euo pipefail\n' +
                            f'test "$(cat {source})" = "{expected}"\n')
        runner.chmod(0o755)

    def feature(self, name, criteria):
        base = f'docs/features/{name}'
        self.write(f'{base}/FEATURE.md', '# Feature\n\n## Acceptance criteria\n' +
                   ''.join(f'- {key}: Observable {key} outcome.\n' for key in criteria))
        self.write(f'{base}/COVERAGE.json', json.dumps({'version': 1, 'criteria': criteria}))
        self.status(name, 'new', 'draft')
        self.status(name, 'draft', 'ready')

    def status(self, name, before, after, *args, ok=True, owner='implementer'):
        return self.cli('feature_status.py', '--root', self.root, '--id', name, '--owner', owner,
                        '--from', before, '--to', after, *args, ok=ok)

    def implement(self, name):
        self.status(name, 'ready', 'active')
        self.status(name, 'active', 'implemented')
        entry = next(x for x in self.read('docs/features/status.json')['features'] if x['id'] == name)
        self.assertEqual((entry['status'], entry['owner'], entry['proof_run']), ('implemented', None, None))

    def capture(self, package, *args, ok=True, legacy=False):
        base = f'docs/features/{package}' if legacy else f'docs/verification/{package}'
        flag = '--feature-dir' if legacy else '--package-dir'
        self.cli('proof_run_capture.py', flag, self.root / base, '--timeout-seconds', '8', '--note',
                 'Disposable behavioral acceptance fixture', *args, ok=ok)
        area = 'tests' if '--kind' in args else 'proof'
        runs = sorted((self.root / base / area / 'runs').iterdir())
        self.assertTrue(runs)
        return runs[-1].relative_to(self.root).as_posix()

    def captures(self):
        return [self.capture('journey', '--scope', 'src/journey.txt'),
                self.capture('access', '--scope', 'src/access.txt')]

    def round(self, runs, *, name='round-one', features=('case', 'closure'), ok=True, author='author', extra=()):
        args = ['--root', self.root, '--round', name, '--implementer', 'implementer', '--author', author,
                '--reviewer', 'reviewer', '--verdict', 'PASS', '--summary', 'Independent fixture review']
        for feature in features:
            args += ['--feature', feature]
        for run in runs:
            args += ['--proof-run', run]
        self.cli('verification_receipt.py', 'round', *args, *extra, ok=ok)
        return f'docs/verification/rounds/{name}/review.json'


class JourneyVerification(JourneyFixture):
    def test_shared_journey_completes_two_features_without_own_runners(self):
        self.implement('case')
        self.implement('closure')
        runs = self.captures()
        receipt = self.round(runs)
        for feature in ('case', 'closure'):
            self.assertFalse((self.root / f'docs/features/{feature}/proof/run.sh').exists())
            self.status(feature, 'implemented', 'done', '--round-review', receipt)
            entry = next(x for x in self.read('docs/features/status.json')['features'] if x['id'] == feature)
            self.assertEqual(entry['proof_run'], receipt)
        self.assertTrue(all((self.root / run / 'result.json').exists() for run in runs))

    def test_unmapped_criterion_and_unavailable_check_cannot_complete(self):
        self.implement('case')
        self.implement('closure')
        runs = self.captures()
        coverage = self.read('docs/features/case/COVERAGE.json')
        self.write('docs/features/case/COVERAGE.json', json.dumps({'version': 1, 'criteria': {}}))
        self.round(runs, ok=False)
        coverage['criteria']['AC3'] = ['docs/verification/external']
        self.write('docs/features/case/COVERAGE.json', json.dumps(coverage))
        self.package('external', 'src/external.txt', 'external-live')
        self.round(runs, ok=False)

    def test_scoped_freshness_and_unaffected_evidence_reuse(self):
        self.implement('case')
        self.implement('closure')
        runs = self.captures()
        self.write('src/unrelated.txt', 'unrelated-v2\n')
        self.round(runs, name='unrelated-change')
        self.write('src/journey.txt', 'journey-v1\n\n')
        self.round(runs, name='stale-journey', ok=False)
        runs[0] = self.capture('journey', '--scope', 'src/journey.txt')
        self.round(runs, name='reused-access')

    def test_included_ignored_input_is_binding(self):
        self.implement('case')
        self.implement('closure')
        self.write('.gitignore', 'private-fixture.txt\n')
        self.write('private-fixture.txt', 'one')
        runs = [self.capture('journey', '--scope', 'src/journey.txt', '--include', 'private-fixture.txt'),
                self.capture('access', '--scope', 'src/access.txt')]
        self.round(runs)
        self.write('private-fixture.txt', 'two')
        self.round(runs, name='changed-input', ok=False)

    def test_newer_failed_and_unfinished_attempts_supersede_pass(self):
        self.implement('case')
        self.implement('closure')
        runs = self.captures()
        runner = self.root / 'docs/verification/journey/proof/run.sh'
        original = runner.read_text()
        runner.write_text(original + 'exit 7\n')
        self.capture('journey', '--scope', 'src/journey.txt', ok=False)
        runner.write_text(original)
        self.round(runs, ok=False)
        runs[0] = self.capture('journey', '--scope', 'src/journey.txt')
        self.round(runs, name='recovered')
        self.write('docs/verification/journey/proof/runs/99999999T999999Z/attempt-start.json', '{}')
        self.round(runs, name='unfinished', ok=False)

    def test_wrong_target_and_completion_owner_rejected(self):
        self.implement('case')
        self.implement('closure')
        runs = [self.capture('journey', '--scope', 'src/journey.txt', '--target', 'local-a'),
                self.capture('access', '--scope', 'src/access.txt', '--target', 'local-b')]
        self.round(runs, ok=False)
        runs[1] = self.capture('access', '--scope', 'src/access.txt', '--target', 'local-a')
        self.round(runs, name='same-author', author='implementer')
        receipt = self.round(runs)
        self.status('case', 'implemented', 'done', '--round-review', receipt, owner='other-task', ok=False)

    def test_coverage_receipt_and_evidence_tampering_block_completion(self):
        self.implement('case')
        self.implement('closure')
        runs = self.captures()
        receipt = self.round(runs)
        coverage_path = self.root / 'docs/features/case/COVERAGE.json'
        original = coverage_path.read_text()
        coverage = json.loads(original)
        coverage['criteria']['AC2'] = ['docs/verification/journey']
        coverage_path.write_text(json.dumps(coverage))
        self.status('case', 'implemented', 'done', '--round-review', receipt, ok=False)
        coverage_path.write_text(original)
        receipt_path = self.root / receipt
        original_receipt = receipt_path.read_text()
        value = json.loads(original_receipt)
        value['summary'] = 'Altered after review'
        receipt_path.write_text(json.dumps(value))
        self.status('case', 'implemented', 'done', '--round-review', receipt, ok=False)
        receipt_path.write_text(original_receipt)
        with (self.root / runs[0] / 'stdout.txt').open('a') as output:
            output.write('Altered retained output\n')
        self.status('case', 'implemented', 'done', '--round-review', receipt, ok=False)

    def test_round_binds_candidate_after_review(self):
        self.implement('case')
        self.implement('closure')
        receipt = self.round(self.captures())
        self.cli('verification_receipt.py', 'check-round', '--root', self.root, '--round-review', receipt)
        self.write('src/journey.txt', 'changed-after-review\n')
        self.cli('verification_receipt.py', 'check-round', '--root', self.root, '--round-review', receipt, ok=False)
        self.status('case', 'implemented', 'done', '--round-review', receipt, ok=False)

    def test_directory_scope_tracks_additions_and_deletions(self):
        self.implement('case')
        self.implement('closure')
        self.write('src/selected/config.txt', 'configuration-v1\n')
        runs = [self.capture('journey', '--scope', 'src/journey.txt', '--scope', 'src/selected'),
                self.capture('access', '--scope', 'src/access.txt')]
        self.round(runs, name='initial-directory')
        added = self.write('src/selected/added.txt', 'new determining input\n')
        self.round(runs, name='added-input', ok=False)
        runs[0] = self.capture('journey', '--scope', 'src/journey.txt', '--scope', 'src/selected')
        self.round(runs, name='recaptured-directory')
        added.unlink()
        self.round(runs, name='deleted-input', ok=False)
        runs[0] = self.capture('journey', '--scope', 'src/journey.txt', '--scope', 'src/selected')
        self.round(runs, name='recaptured-deletion')

    def test_historical_inventory_survives_later_candidate_changes(self):
        self.write('.gitignore', '__pycache__/\n')
        self.implement('case')
        self.implement('closure')
        receipt = self.round(self.captures())
        for feature in ('case', 'closure'):
            self.status(feature, 'implemented', 'done', '--round-review', receipt)
        before = (self.root / 'docs/features/status.json').read_bytes()
        self.write('src/journey.txt', 'subsequent-implementation\n')
        self.cli('gate.py', '--root', self.root, '--profile', 'other')
        self.assertEqual((self.root / 'docs/features/status.json').read_bytes(), before)
        self.cli('verification_receipt.py', 'check-round', '--root', self.root, '--round-review', receipt, ok=False)
        self.assertTrue((self.root / receipt).is_file())

    def test_implemented_can_reopen_without_claiming_verification(self):
        self.implement('case')
        self.status('case', 'implemented', 'active')
        self.status('case', 'active', 'implemented')
        self.status('case', 'implemented', 'blocked')
        self.status('case', 'blocked', 'draft')

    def test_legacy_own_proof_and_regression_completion(self):
        base = 'docs/features/legacy'
        self.write(f'{base}/FEATURE.md', '# Existing legacy feature\n')
        self.write(f'{base}/PROOF.md', '# Existing own proof\n')
        runner = self.write(f'{base}/proof/run.sh', '#!/usr/bin/env bash\nset -euo pipefail\ntest -f src/journey.txt\n')
        runner.chmod(0o755)
        self.status('legacy', 'new', 'draft')
        self.status('legacy', 'draft', 'ready')
        self.status('legacy', 'ready', 'active')
        proof = self.capture('legacy', legacy=True)
        regression = self.capture('legacy', '--kind', 'regression', '--', sys.executable, '-c', 'print("regression executed")', legacy=True)
        self.cli('verification_receipt.py', 'review', '--root', self.root, '--proof-run', proof,
                 '--regression-run', regression, '--implementer', 'implementer', '--author', 'author',
                 '--reviewer', 'reviewer', '--verdict', 'PASS', '--summary', 'Legacy completion review')
        self.status('legacy', 'active', 'done', '--proof-run', proof)


if __name__ == '__main__':
    unittest.main(verbosity=2)
