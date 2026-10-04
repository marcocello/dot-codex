"""Exercise generation as a user: preservation, private config and render boundaries."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/scaffold.py'


class ScaffoldTests(unittest.TestCase):
    def test_generate_and_refuse_to_replace_existing_work(self):
        with tempfile.TemporaryDirectory(prefix='scaffold test ') as directory:
            target = Path(directory) / 'new project'
            run = subprocess.run([sys.executable, str(SCRIPT), str(target)], capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            for relative in ['frontend/app/package-lock.json', 'backend/uv.lock',
                             'backend/migrations/versions/0001_create_notes.py',
                             '.vscode/tasks.json', 'deploy/k8s/migrate.json', '.env.example']:
                self.assertTrue((target / relative).is_file(), relative)
            self.assertFalse((target / '.env').exists())
            sentinel = target / 'my-work.txt'
            sentinel.write_text('preserve')
            retry = subprocess.run([sys.executable, str(SCRIPT), str(target)], capture_output=True)
            self.assertNotEqual(retry.returncode, 0)
            self.assertEqual(sentinel.read_text(), 'preserve')
            alias = Path(directory) / 'alias'
            alias.symlink_to(target, target_is_directory=True)
            self.assertNotEqual(subprocess.run([sys.executable, str(SCRIPT), str(alias)],
                                              capture_output=True).returncode, 0)
            setup = [sys.executable, str(target / 'scripts/setup.py')]
            subprocess.run(setup, check=True, capture_output=True)
            env = (target / '.env').read_bytes()
            subprocess.run(setup, check=True, capture_output=True)
            self.assertEqual((target / '.env').read_bytes(), env)
            self.assertEqual((target / '.env').stat().st_mode & 0o777, 0o600)
            render = [sys.executable, str(target / 'scripts/render_k8s.py'),
                      '--backend-image', 'registry.example/backend:r1', '--web-image',
                      'registry.example/web:r1', '--domain', 'app.example.com', '--namespace',
                      'test-app', '--release', 'r1', '--ingress-class', 'nginx',
                      '--output', str(target / 'build/k8s')]
            subprocess.run(render, check=True, capture_output=True)
            manifests = [json.loads(path.read_text()) for path in (target/'build/k8s').glob('*.json')]
            self.assertTrue(all(item['metadata']['namespace'] == 'test-app' for item in manifests))
            job = next(item for item in manifests if item['kind'] == 'Job')
            self.assertEqual(job['metadata']['name'], 'migrate-r1')
            self.assertEqual(job['spec']['template']['spec']['containers'][0]['image'],
                             'registry.example/backend:r1')
            self.assertNotEqual(subprocess.run(render, capture_output=True).returncode, 0)
            subprocess.run(['git', 'init', '-q', str(target)], check=True)
            for relative in ['frontend/app/src/App.tsx', 'backend/uv.lock', '.env.example',
                             'deploy/k8s/web-config.json', '.vscode/tasks.json']:
                self.assertEqual(subprocess.run(['git','check-ignore',relative],cwd=target,
                                                capture_output=True).returncode, 1, relative)
            for relative in ['.env', 'frontend/app/node_modules/x.js', 'build/k8s/backend.json',
                             '.venv/lib/example.py']:
                self.assertEqual(subprocess.run(['git','check-ignore',relative],cwd=target,
                                                capture_output=True).returncode, 0, relative)


if __name__ == '__main__':
    unittest.main()
