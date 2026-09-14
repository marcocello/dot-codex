#!/usr/bin/env python3
"""Acceptance through installed CLI subprocesses and durable read-back."""
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest

REPO = Path(__file__).resolve().parents[4]
CAPTURE = REPO / 'scripts/proof_run_capture'
STATUS = REPO / 'scripts/feature_status'
PYTHON = sys.executable


class CaptureAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='capture-acceptance-')
        self.root = Path(self.temp.name).resolve()
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.feature = self.root / 'docs/features/sample'
        (self.feature / 'proof').mkdir(parents=True)
        (self.feature / 'FEATURE.md').write_text('# Sample accepted behavior\n')
        (self.feature / 'PROOF.md').write_text('# Sample proof contract\n')
        self.runner = self.feature / 'proof/run.sh'
        self.runner.write_text('#!/bin/sh\npwd\nprintf "proof output\\n"\n')
        self.runner.chmod(0o755)
        self.base = [str(CAPTURE), '--feature-dir', 'docs/features/sample', '--timeout-seconds', '4', '--note', 'acceptance note']

    def tearDown(self):
        self.temp.cleanup()

    def invoke(self, args=(), timeout=12, cwd=None):
        return subprocess.run(self.base + list(args), cwd=cwd or self.root, capture_output=True, text=True, timeout=timeout)

    def runs(self, kind):
        return sorted((self.feature / ('proof' if kind == 'proof' else 'tests') / 'runs').glob('*'))

    def result(self, kind):
        runs = self.runs(kind)
        self.assertTrue(runs, f'no retained {kind} attempt')
        return runs[-1], json.loads((runs[-1] / 'result.json').read_text())

    def regression(self, code, *args):
        return self.invoke(['--kind', 'regression', '--', PYTHON, '-c', code, *args])

    def assert_pass(self, completed):
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_regression_argv_context_and_separate_storage(self):
        cwd = self.root / 'sub dir'
        cwd.mkdir()
        args = ['space value', '$(touch UNWANTED)', ';touch UNWANTED', '', 'quote"and\'apostrophe', '--flag', 'λ']
        code = 'import json,os,sys; print(json.dumps({"argv":sys.argv[1:],"cwd":os.getcwd()})); print("separate error",file=sys.stderr)'
        command = [PYTHON, '-c', code, *args]
        self.assert_pass(self.invoke(['--kind', 'regression', '--cwd', 'sub dir', '--', *command]))
        run, result = self.result('regression')
        start = json.loads((run / 'attempt-start.json').read_text())
        for metadata in [start, result]:
            self.assertEqual(metadata['kind'], 'regression')
            self.assertEqual(metadata['command'], command)
            self.assertEqual(metadata['cwd'], str(cwd))
            self.assertTrue(metadata['started_at'])
            self.assertTrue(metadata['runtime'])
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['returncode'], 0)
        self.assertGreaterEqual(result['duration_seconds'], 0)
        self.assertEqual(json.loads((run / 'stdout.txt').read_text()), {'argv':args,'cwd':str(cwd)})
        self.assertEqual((run / 'stderr.txt').read_text(), 'separate error\n')
        self.assertEqual((run / 'notes.md').read_text().strip(), 'acceptance note')
        for name in ['FEATURE.md', 'PROOF.md']:
            self.assertEqual((run / name).read_bytes(), (self.feature / name).read_bytes())
        self.assertFalse((run / 'run.sh').exists())
        self.assertFalse((cwd / 'UNWANTED').exists())
        self.assertFalse(self.runs('proof'))
        self.assert_pass(self.regression('print("again")'))
        self.assertEqual(len(self.runs('regression')), 2)
        self.assertEqual(json.loads((run / 'stdout.txt').read_text())['argv'], args)

    def test_default_and_explicit_proof_compatibility(self):
        for args in [[], ['--kind', 'proof']]:
            self.assert_pass(self.invoke(args))
            run, result = self.result('proof')
            self.assertEqual(result['kind'], 'proof')
            self.assertEqual(result['cwd'], str(self.root))
            self.assertIn(str(self.root), (run / 'stdout.txt').read_text())
            self.assertEqual((run / 'run.sh').read_bytes(), self.runner.read_bytes())
            self.assertEqual(result['status'], 'PASS')
        self.assertEqual(len(self.runs('proof')), 2)
        self.assertFalse(self.runs('regression'))

    def test_regression_without_runner(self):
        self.runner.unlink()
        self.assert_pass(self.regression('print("without runner")'))
        _, result = self.result('regression')
        self.assertEqual(result['cwd'], str(self.root))
        child = self.root / 'nested'
        child.mkdir()
        self.assert_pass(self.invoke(['--kind','regression','--',PYTHON,'-c','import os; print(os.getcwd())'], cwd=child))
        run, _ = self.result('regression')
        self.assertEqual((run / 'stdout.txt').read_text().strip(), str(self.root))

    def test_failures_and_timeout(self):
        failed = self.regression('import sys; print("kept output"); print("kept error",file=sys.stderr); sys.exit(7)')
        self.assertEqual(failed.returncode, 7, failed.stderr)
        run, result = self.result('regression')
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['returncode'], 7)
        self.assertIn('kept output', (run / 'stdout.txt').read_text())
        self.assertIn('kept error', (run / 'stderr.txt').read_text())
        missing = self.invoke(['--kind','regression','--','./executable-does-not-exist'])
        self.assertNotEqual(missing.returncode, 0)
        _, result = self.result('regression')
        self.assertEqual(result['status'], 'FAIL')
        timed = self.invoke(['--timeout-seconds','0.15','--kind','regression','--',PYTHON,'-c','import time; print("before timeout",flush=True); time.sleep(20)'])
        self.assertEqual(timed.returncode, 124, timed.stderr)
        run, result = self.result('regression')
        self.assertEqual(result['status'], 'TIMEOUT')
        self.assertIn('before timeout', (run / 'stdout.txt').read_text())
        with self.assertRaises(ProcessLookupError):
            os.kill(result['runner_pid'], 0)
        self.assertEqual(len(self.runs('regression')), 3)

    def test_interruption(self):
        process = subprocess.Popen(self.base + ['--kind','regression','--',PYTHON,'-c','import time; print("ready",flush=True); time.sleep(20)'], cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                runs = self.runs('regression')
                if runs and (runs[-1] / 'stdout.txt').exists() and 'ready' in (runs[-1] / 'stdout.txt').read_text():
                    break
                if process.poll() is not None:
                    break
                time.sleep(.02)
            self.assertIsNone(process.poll(), 'capture exited before interruption')
            run = self.runs('regression')[-1]
            self.assertTrue((run / 'attempt-start.json').exists())
            self.assertFalse((run / 'result.json').exists())
            process.send_signal(signal.SIGTERM)
            process.communicate(timeout=8)
            self.assertEqual(process.returncode, 128 + signal.SIGTERM)
            _, result = self.result('regression')
            self.assertEqual(result['status'], 'INTERRUPTED')
            with self.assertRaises(ProcessLookupError):
                os.kill(result['runner_pid'], 0)
        finally:
            if process.poll() is None:
                process.terminate()
                process.communicate(timeout=8)

    def test_input_changes(self):
        for retained in [False, True]:
            with self.subTest(retained=retained):
                path = "sorted(Path('docs/features/sample/tests/runs').iterdir())[-1]/'FEATURE.md'" if retained else "Path('docs/features/sample/FEATURE.md')"
                completed = self.regression(f'from pathlib import Path; p={path}; p.write_text("changed")')
                self.assertNotEqual(completed.returncode, 0)
                _, result = self.result('regression')
                self.assertEqual(result['status'], 'FAIL')
                self.assertIn(('retained/' if retained else '')+'FEATURE.md', result['input_changes'])

    def test_invalid_requests_execute_nothing(self):
        bad = [
            ['--kind','regression'], ['--kind','proof','--','touch','SIDE_EFFECT'],
            ['--cwd','.'], ['--kind','regression','--cwd','missing','--','touch','SIDE_EFFECT'],
        ]
        for value in ['0','-1','nan','inf','-inf']:
            bad.append(['--timeout-seconds='+value,'--kind','regression','--','touch','SIDE_EFFECT'])
        for args in bad:
            with self.subTest(args=args):
                completed = self.invoke(args)
                self.assertNotEqual(completed.returncode, 0)
                self.assertFalse((self.root/'SIDE_EFFECT').exists())
                self.assertFalse(self.runs('regression'))
                self.assertFalse(self.runs('proof'))

    def test_containment(self):
        external = Path(tempfile.mkdtemp(prefix='capture-outside-')).resolve()
        try:
            inside = self.root/'inside'
            inside.mkdir()
            link = self.root/'linked'
            link.symlink_to(inside, target_is_directory=True)
            for cwd in [str(external), 'linked']:
                self.assertNotEqual(self.invoke(['--kind','regression','--cwd',cwd,'--',PYTHON,'-c','print(1)']).returncode, 0)
            feature = self.feature/'FEATURE.md'
            original = feature.read_bytes()
            feature.unlink()
            feature.symlink_to(inside/'input')
            (inside/'input').write_bytes(original)
            self.assertNotEqual(self.regression('print(1)').returncode, 0)
            feature.unlink()
            feature.write_bytes(original)
            tests = self.feature/'tests'
            tests.symlink_to(inside, target_is_directory=True)
            self.assertNotEqual(self.regression('print(1)').returncode, 0)
            tests.unlink()
            tests.mkdir()
            (tests/'runs').symlink_to(external, target_is_directory=True)
            self.assertNotEqual(self.regression('print(1)').returncode, 0)
            self.assertEqual(list(external.iterdir()), [])
            self.assertFalse(self.runs('proof'))
        finally:
            shutil.rmtree(external)

    def write_active(self):
        payload = {'version':2, 'features':[{'id':'sample','feature_dir':'docs/features/sample','priority':1,'status':'active','owner':'proof-author','proof_run':None,'notes':''}]}
        (self.root/'docs/features/status.json').write_text(json.dumps(payload))

    def complete(self, run):
        return subprocess.run([str(STATUS),'--root',str(self.root),'--id','sample','--owner','proof-author','--from','active','--to','done','--proof-run',run.relative_to(self.root).as_posix()], capture_output=True,text=True,timeout=8)

    def test_completion_boundary(self):
        self.assert_pass(self.invoke())
        proof, _ = self.result('proof')
        self.write_active()
        self.assert_pass(self.complete(proof))
        before = (self.root/'docs/features/status.json').read_bytes()
        self.assert_pass(self.regression('print("newer regression")'))
        regression, _ = self.result('regression')
        self.assertEqual((self.root/'docs/features/status.json').read_bytes(), before)
        self.write_active()
        self.assert_pass(self.complete(proof))
        self.write_active()
        self.assertNotEqual(self.complete(regression).returncode, 0)
        self.assertEqual(json.loads((self.root/'docs/features/status.json').read_text())['features'][0]['status'], 'active')
        relocated = self.feature/'proof/runs/zz-relocated-regression'
        shutil.copytree(regression, relocated)
        self.assertNotEqual(self.complete(relocated).returncode, 0, 'relocated regression must not become official proof')
        shutil.rmtree(relocated)
        historical = json.loads((proof/'result.json').read_text())
        historical.pop('kind', None)
        (proof/'result.json').write_text(json.dumps(historical))
        self.assert_pass(self.complete(proof))


if __name__ == '__main__':
    unittest.main(verbosity=2)
