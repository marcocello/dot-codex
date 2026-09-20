"""Independent black-box acceptance for the public knowledge profile CLI."""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
CLI = ROOT / 'scripts' / 'knowledge_profile.py'


class Profiles(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.config = self.home / 'knowledge.toml'

    def invoke(self, *args, ok=True, explicit=True):
        env = dict(os.environ, CODEX_HOME=str(self.home))
        command = [sys.executable, str(CLI)]
        if explicit:
            command += ['--config', str(self.config)]
        result = subprocess.run(command + list(args), env=env, text=True,
                                capture_output=True, timeout=15)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertTrue((result.stderr + result.stdout).strip(), 'Actionable error required')
        return result

    def remote(self, name, provider='clickup', default=False, account='team-account'):
        args = ['put', name, '--provider', provider, '--connection', name + '-connector',
                '--account', account, '--workspace-id', name + '-workspace',
                '--tasks', name + '-tasks', '--deals', name + '-deals', '--ideas', name + '-ideas']
        if default:
            args.append('--default')
        return self.invoke(*args)

    def unchanged_failure(self, *args):
        before = self.config.read_bytes()
        self.invoke(*args, ok=False)
        self.assertEqual(self.config.read_bytes(), before)

    def test_first_use_then_persistent_default_and_override(self):
        self.invoke('resolve', ok=False, explicit=False)
        self.assertFalse(self.config.exists())
        self.remote('work')
        self.invoke('resolve', ok=False)
        self.assertIsNone(self.invoke('list').get('default_profile'))
        self.invoke('default', 'work')
        work = self.invoke('resolve', explicit=False)
        self.assertEqual(work['profile'], 'work')
        for key, value in {'provider': 'clickup', 'connection': 'work-connector',
                           'account': 'team-account', 'workspace_id': 'work-workspace',
                           'tasks': 'work-tasks', 'deals': 'work-deals', 'ideas': 'work-ideas'}.items():
            self.assertEqual(work[key], value)
        self.remote('personal', provider='notion', account='personal-account')
        before = self.config.read_bytes()
        personal = self.invoke('resolve', '--profile', 'personal')
        self.assertEqual(personal['profile'], 'personal')
        self.assertEqual(personal['provider'], 'notion')
        self.assertEqual(self.config.read_bytes(), before)
        self.assertEqual(self.invoke('resolve', explicit=False), work)
        self.invoke('default', 'personal')
        self.assertEqual(self.invoke('resolve', explicit=False)['profile'], 'personal')

    def test_multiple_accounts_replace_isolated_profile(self):
        self.remote('work', default=True)
        self.remote('other', account='second-account')
        listing = self.invoke('list')
        self.assertEqual(listing['default_profile'], 'work')
        self.assertEqual(set(listing['profiles']), {'work', 'other'})
        self.assertEqual(self.invoke('resolve', '--profile', 'other')['account'], 'second-account')
        self.invoke('put', 'work', '--provider', 'none')
        after = self.invoke('list')
        self.assertEqual(after['default_profile'], 'work')
        self.assertEqual(after['profiles']['other'], listing['profiles']['other'])
        self.assertEqual(after['profiles']['work'], {'provider': 'none'})
        self.assertEqual(self.invoke('resolve')['provider'], 'none')

    def test_markdown_none_and_no_routing_side_effect(self):
        root = self.home / 'notes space'
        self.invoke('put', 'local', '--provider', 'markdown', '--root', str(root), '--default')
        self.assertEqual(self.invoke('resolve')['root'], str(root))
        self.assertFalse(root.exists(), 'Routing must not create knowledge content')
        self.invoke('put', 'disabled', '--provider', 'none', '--default')
        self.assertEqual(self.invoke('resolve'), {'profile': 'disabled', 'provider': 'none'})
        self.unchanged_failure('resolve', '--profile', 'missing')
        self.unchanged_failure('default', 'missing')

    def test_invalid_put_preserves_durable_configuration(self):
        self.remote('work', default=True)
        for args in [('put', 'bad', '--provider', 'unknown'),
                     ('put', 'bad', '--provider', 'clickup'),
                     ('put', 'bad', '--provider', 'markdown', '--root', 'relative/notes'),
                     ('put', 'bad', '--provider', 'notion', '--connection', '...',
                      '--account', 'account', '--workspace-id', 'workspace', '--tasks', 'tasks',
                      '--deals', 'deals', '--ideas', 'ideas')]:
            with self.subTest(args=args):
                self.unchanged_failure(*args)
        self.assertEqual(self.invoke('resolve')['profile'], 'work')

    def test_invalid_config_never_repaired_or_replaced_implicitly(self):
        fixtures = ['not toml [', 'version = 99\n',
                    'version = 1\ndefault_profile = "missing"\n[profiles.x]\nprovider = "none"\n',
                    'version = 1\n[profiles.x]\nprovider = "mystery"\n',
                    'version = 1\n[profiles.x]\nprovider = "markdown"\nroot = "relative"\n',
                    'version = 1\n[profiles.x]\nprovider = "clickup"\n']
        for fixture in fixtures:
            with self.subTest(fixture=fixture):
                self.config.write_text(fixture)
                for args in [('resolve',), ('list',), ('put', 'new', '--provider', 'none', '--default')]:
                    self.unchanged_failure(*args)

    def test_concurrent_writers_preserve_all_profiles(self):
        self.invoke('put', 'base', '--provider', 'none', '--default')
        def write(index):
            self.invoke('put', f'parallel-{index}', '--provider', 'none')
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(write, range(16)))
        listing = self.invoke('list')
        self.assertEqual(set(listing['profiles']), {'base'} | {f'parallel-{i}' for i in range(16)})
        self.assertEqual(listing['default_profile'], 'base')
        self.assertEqual(self.invoke('resolve')['profile'], 'base')


if __name__ == '__main__':
    unittest.main(verbosity=2)
