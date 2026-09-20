#!/usr/bin/env python3
"""Independent public-CLI proof; every credential is synthetic."""
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[4]
CLI = ROOT / 'skills/knowledge-connect/scripts/knowledge_profile.py'
TOKEN = 'synthetic_inline_acceptance_42'

class Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'knowledge.toml'
        self.env = dict(os.environ, INLINE_PROOF_TOKEN=TOKEN)
        self.runcli('put', 'work', '--provider', 'clickup', '--connection', 'clickup-work', '--account', '42', '--workspace-id', '81', '--default')
        self.runcli('put', 'off', '--provider', 'none')

    def runcli(self, *args, input=None, ok=True, script=CLI):
        result = subprocess.run([sys.executable, str(script), '--config', str(self.path), *args], input=input, text=True, capture_output=True, env=self.env, timeout=8)
        self.assertNotIn(TOKEN, result.stdout + result.stderr)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        return result

    def stored(self):
        return tomllib.loads(self.path.read_text())

    def install(self):
        return self.runcli('credentials', 'work', '--token-stdin', input='  '+TOKEN+'\n')

    def test_inline_persistence_redaction_and_restart(self):
        before = self.stored()
        result = self.install()
        self.assertEqual(result['token'], '[redacted]')
        stored = self.stored()
        self.assertEqual(stored['profiles']['work']['token'], TOKEN)
        self.assertEqual(stored['default_profile'], before['default_profile'])
        self.assertEqual(stored['profiles']['off'], before['profiles']['off'])
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)
        self.assertNotIn('transport', stored['profiles']['work'])
        self.assertEqual(self.runcli('list')['profiles']['work']['token'], '[redacted]')
        self.assertEqual(self.runcli('resolve')['token'], '[redacted]')
        self.assertEqual(self.runcli('resolve', '--transport', 'api')['token'], '[redacted]')
        self.assertEqual(self.runcli('transport', 'work', 'api')['token'], '[redacted]')
        self.assertEqual(self.runcli('default', 'work')['token'], '[redacted]')
        self.runcli('put', 'other', '--provider', 'none')
        self.assertEqual(self.stored()['profiles']['work']['token'], TOKEN)
        for launcher in (ROOT / 'scripts/knowledge_profile.py', ROOT / 'skills/knowledge-config/scripts/knowledge_profile.py'):
            self.assertEqual(self.runcli('resolve', script=launcher)['token'], '[redacted]')

    def test_import_reference_and_preserve_other_profile(self):
        self.runcli('credentials', 'work', '--token-env', 'INLINE_PROOF_TOKEN', '--auth-type', 'oauth')
        self.runcli('credentials', 'work', '--import-current')
        profile = self.stored()['profiles']['work']
        self.assertEqual(profile['token'], TOKEN)
        self.assertEqual(profile['auth_type'], 'oauth')
        self.assertNotIn('token_env', profile)
        private = Path(self.tmp.name) / 'private-token'
        private.write_text(TOKEN+'\n')
        private.chmod(0o600)
        self.runcli('put', 'second', '--provider', 'clickup', '--connection', 'clickup-second', '--account', '43', '--workspace-id', '82', '--token-file', str(private))
        self.runcli('credentials', 'second', '--import-current')
        self.assertTrue(private.exists())
        stored = self.stored()
        self.assertEqual(stored['profiles']['second']['token'], TOKEN)
        self.assertEqual(stored['profiles']['work'], profile)
        self.assertEqual(stored['default_profile'], 'work')
        self.runcli('credentials', 'second', '--import-current')
        self.assertEqual(self.stored(), stored)

    def test_invalid_input_and_conflicts_are_atomic(self):
        before = self.path.read_bytes()
        for value in ('', '   \n', 'inside space', 'bad\x00value', 'bad\x7fvalue', 'nonasciié', 'x'*16385):
            self.runcli('credentials', 'work', '--token-stdin', input=value, ok=False)
            self.assertEqual(self.path.read_bytes(), before)
        self.runcli('credentials', 'work', '--token-stdin', '--token-env', 'INLINE_PROOF_TOKEN', input=TOKEN, ok=False)
        self.runcli('credentials', 'work', '--import-current', '--token-file', '/absent', ok=False)
        self.runcli('credentials', 'work', '--token', 'synthetic-argv', ok=False)
        self.assertEqual(self.path.read_bytes(), before)
        self.runcli('credentials', 'work', '--import-current', ok=False)
        self.assertEqual(self.path.read_bytes(), before)
        self.runcli('credentials', 'off', '--token-stdin', input=TOKEN, ok=False)

    def test_reference_replaces_inline_and_unsafe_config_rejected(self):
        self.install()
        self.runcli('credentials', 'work', '--token-env', 'INLINE_PROOF_TOKEN')
        self.assertNotIn('token', self.stored()['profiles']['work'])
        self.install()
        self.path.chmod(0o644)
        self.runcli('resolve', ok=False)
        self.runcli('credentials', 'work', '--import-current', ok=False)
        self.path.chmod(0o600)
        original = self.path.with_name('original.toml')
        self.path.rename(original)
        self.path.symlink_to(original)
        self.runcli('resolve', ok=False)
        self.path.unlink()
        os.mkfifo(self.path)
        self.runcli('resolve', ok=False)

    def test_inline_used_by_public_api_clients(self):
        self.install()
        self.runcli('transport', 'work', 'api')
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('api_edge.py')), str(self.path), 'clickup'], text=True, capture_output=True, env=self.env, timeout=8)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(TOKEN, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)['verified'])
        bot='11111111-1111-4111-8111-111111111111'
        workspace='22222222-2222-4222-8222-222222222222'
        self.runcli('put', 'notion', '--provider', 'notion', '--connection', 'notion-work', '--account', bot, '--workspace-id', workspace)
        self.runcli('credentials', 'notion', '--token-stdin', input=TOKEN)
        self.runcli('transport', 'notion', 'api')
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('api_edge.py')), str(self.path), 'notion'], text=True, capture_output=True, env=self.env, timeout=8)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(TOKEN, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)['verified'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
