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
            for relative in ['app/frontend/package-lock.json', 'app/backend/uv.lock',
                             'app/backend/migrations/versions/0001_create_notes.py',
                             '.vscode/tasks.json', 'deployments/prod/k8s/migrate.json', '.env.example',
                             'pipelines/backend/check.sh', 'pipelines/frontend/check.sh',
                             'deployments/dev/Caddyfile', 'deployments/prod/Caddyfile.production']:
                self.assertTrue((target / relative).is_file(), relative)
            for old in ['backend', 'frontend', 'deploy']:
                self.assertFalse((target / old).exists(), old)
            self.assertFalse((target / '.env').exists())
            for omitted in ['Makefile', 'PRODUCT.md', 'README.md']:
                self.assertFalse((target / omitted).exists(), omitted)
            self.assertTrue((target / 'deployments/prod/k8s/README.md').is_file())
            documented = Path(directory) / 'documented project'
            requested = subprocess.run([sys.executable, str(SCRIPT), str(documented), '--readme'], capture_output=True)
            self.assertEqual(requested.returncode, 0, requested.stderr)
            self.assertTrue((documented / 'README.md').is_file())
            self.assertFalse((documented / 'Makefile').exists())
            self.assertFalse((documented / 'PRODUCT.md').exists())
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
            # Missing environments must fail without creating misleading empty output.
            other = render[:-1] + [str(target / 'build/k8s-dev'), '--environment', 'dev']
            self.assertNotEqual(subprocess.run(other, capture_output=True).returncode, 0)
            self.assertFalse((target / 'build/k8s-dev').exists())
            source = target / 'deployments/dev/k8s'
            source.mkdir()
            manifest = {'kind': 'ConfigMap', 'metadata': {'name': 'dev-only'},
                        'data': {'environment': 'dev'}}
            (source / 'dev.json').write_text(json.dumps(manifest))
            subprocess.run(other, check=True, capture_output=True)
            rendered = json.loads((target / 'build/k8s-dev/dev.json').read_text())
            self.assertEqual(rendered['data']['environment'], 'dev')
            self.assertEqual(rendered['metadata']['namespace'], 'test-app')
            self.assertEqual(len(list((target / 'build/k8s-dev').glob('*.json'))), 1)
            subprocess.run(['git', 'init', '-q', str(target)], check=True)
            for relative in ['app/frontend/src/App.tsx', 'app/backend/uv.lock', '.env.example',
                             'deployments/prod/k8s/web-config.json', '.vscode/tasks.json',
                             'pipelines/backend/check.sh', 'pipelines/frontend/check.sh']:
                self.assertEqual(subprocess.run(['git','check-ignore',relative],cwd=target,
                                                capture_output=True).returncode, 1, relative)
            for relative in ['.env', 'app/frontend/node_modules/x.js', 'build/k8s/backend.json',
                             '.venv/lib/example.py']:
                self.assertEqual(subprocess.run(['git','check-ignore',relative],cwd=target,
                                                capture_output=True).returncode, 0, relative)


if __name__ == '__main__':
    unittest.main()
