from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[4] if 'docs/features/' in str(Path(__file__)) else Path.cwd()
BRAIN = Path(os.environ.get('SECOND_BRAIN_REPO', str(ROOT.parent / 'secondbrain')))
VAULT = Path(os.environ.get('OBSIDIAN_VAULT', str(Path.home() / 'ObsidianVault')))

class SplitAcceptance(unittest.TestCase):
    def fixture(self, temporary):
        source = Path(temporary) / "coding checkout with spaces"
        source.mkdir()
        shutil.copy2(ROOT / 'install.sh', source / 'install.sh')
        shutil.copy2(ROOT / 'config.template.toml', source / 'config.template.toml')
        skill = source / 'skills/coding-repair'; skill.mkdir(parents=True)
        (skill / 'SKILL.md').write_text('---\nname: coding-repair\ndescription: Repair code.\n---\n')
        home = Path(temporary) / 'home'; home.mkdir()
        return source.resolve(), home.resolve(), dict(os.environ, HOME=str(home.resolve()), CODEX_HOME='/unused')

    def install(self, source, env, *args):
        return subprocess.run(['bash', str(source / 'install.sh'), *args], env=env, text=True, capture_output=True)

    def test_H1_fresh_repeated_install_and_existing_skills(self):
        with tempfile.TemporaryDirectory() as t:
            source, home, env = self.fixture(t)
            user = home / '.agents/skills/other'; user.mkdir(parents=True)
            (user / 'SKILL.md').write_text('keep me')
            for _ in range(2):
                result = self.install(source, env)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((home / '.codex').resolve(), source)
            self.assertEqual((home / '.agents/skills/coding-repair').resolve(), source / 'skills/coding-repair')
            self.assertEqual((user / 'SKILL.md').read_text(), 'keep me')
            (source / 'config.toml').write_text('model = "private-choice"\n')
            self.assertEqual(self.install(source, env).returncode, 0)
            self.assertEqual((source / 'config.toml').read_text(), 'model = "private-choice"\n')
            exported = self.install(source, env, '--print-env')
            value = subprocess.check_output(['bash', '-c', exported.stdout + '\nprintf "%s" "$CODEX_HOME"'], env=env, text=True)
            self.assertEqual(value, str(source))
            self.assertFalse((source / '.venv').exists())

    def test_H1_conflicts_preserve_existing_home_and_skill(self):
        with tempfile.TemporaryDirectory() as t:
            source, home, env = self.fixture(t)
            existing = home / '.codex'; existing.mkdir(); (existing / 'auth.json').write_text('sentinel')
            self.assertNotEqual(self.install(source, env).returncode, 0)
            self.assertEqual((existing / 'auth.json').read_text(), 'sentinel')
            self.assertFalse((home / '.agents').exists())
        with tempfile.TemporaryDirectory() as t:
            source, home, env = self.fixture(t)
            conflict = home / '.agents/skills/coding-repair'; conflict.mkdir(parents=True)
            (conflict / 'SKILL.md').write_text('other owner')
            self.assertNotEqual(self.install(source, env).returncode, 0)
            self.assertEqual((conflict / 'SKILL.md').read_text(), 'other owner')
            self.assertFalse((home / '.codex').exists())

    def test_H2_independent_inventories_and_source_boundaries(self):
        captured = json.loads(Path(__file__).with_name('secondbrain-inputs.json').read_text())['files']
        for name, expected in captured.items():
            self.assertEqual(hashlib.sha256((BRAIN / name).read_bytes()).hexdigest(), expected, name)
        for root in [ROOT, BRAIN]:
            manifest = root / ('skills/manifest.toml' if root == BRAIN else 'skills.toml')
            data = tomllib.loads(manifest.read_text())
            owned = {e['path'] for e in data['skills'] if e['kind'] == 'owned'}
            actual = {p.parent.name for p in (root / 'skills').glob('*/SKILL.md') if not p.parent.name.startswith('.')}
            self.assertTrue(owned <= actual, (root, owned - actual))
            for name in owned:
                self.assertTrue((root / 'skills' / name / 'SKILL.md').is_file())
            status = json.loads((root / 'docs/features/status.json').read_text())
            for entry in status['features']:
                self.assertTrue((root / entry['feature_dir'] / 'FEATURE.md').is_file(), entry['id'])
        self.assertFalse((ROOT / 'backend').exists())
        self.assertFalse((ROOT / 'deployments').exists())
        self.assertFalse((ROOT / 'scripts/secondbrain.py').exists())
        self.assertFalse((ROOT / 'skills/secondbrain-update').exists())
        self.assertTrue((BRAIN / '.git').is_dir())
        brain_names = {e['name'] for e in tomllib.loads((BRAIN / 'skills/manifest.toml').read_text())['skills']}
        self.assertFalse(any(n.startswith('coding-') for n in brain_names))

    def test_H3_profile_is_private_and_does_not_repoint_coding(self):
        with tempfile.TemporaryDirectory() as t:
            home = Path(t); coding = home / '.codex'; coding.mkdir()
            (coding / 'auth.json').write_text('do not copy')
            state = home / 'private-state'
            env = dict(os.environ, HOME=str(home), CODEX_HOME=str(coding), SECOND_BRAIN_STATE=str(state))
            code = 'import os; from pathlib import Path; from setup_agent import apply; apply(Path(os.environ["BRAIN_SOURCE"]), "agent", dict(os.environ))'
            for _ in range(2):
                result = subprocess.run([sys.executable, '-c', code], env=dict(env, PYTHONPATH=str(BRAIN / 'scripts'), BRAIN_SOURCE=str(BRAIN)), capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(coding.is_symlink())
            self.assertEqual((coding / 'auth.json').read_text(), 'do not copy')
            profile = state / 'codex'
            self.assertTrue((profile / 'config.toml').is_file())
            self.assertTrue((profile / 'AGENTS.md').is_file())
            self.assertFalse((profile / 'auth.json').exists())
            self.assertFalse((home / '.zshenv').exists())
            self.assertEqual((state / 'workspace/.agents/skills').resolve(), BRAIN / 'skills')
            self.assertEqual((profile / 'skills').resolve(), BRAIN / 'skills')

    def test_H3_entrypoint_and_backend_help(self):
        env = dict(os.environ, CODEX_HOME=str(BRAIN / '.unused-test-profile'), PYTHONPATH=os.pathsep.join([str(BRAIN / 'backend/context/src'), str(BRAIN / 'backend/telegram/src')]))
        result = subprocess.run(['bash', str(BRAIN / 'secondbrain.sh'), '--help'], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        python = BRAIN / '.venv/bin/python'
        self.assertTrue(python.is_file())
        helper = subprocess.run([str(python), str(BRAIN / 'scripts/install_service.py'), '--help'], env=env, capture_output=True, text=True)
        self.assertEqual(helper.returncode, 0, helper.stderr)
        for module in ['secondbrain_context.cli', 'telegram_to_agents']:
            result = subprocess.run([str(python), '-m', module, '--help'], cwd=BRAIN, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_H3_container_definition_uses_private_profile(self):
        with tempfile.TemporaryDirectory() as t:
            state = Path(t).resolve()
            code = '''import json, os
from pathlib import Path
from setup_docker import definition
state = Path(os.environ['TEST_STATE'])
value = definition(Path(os.environ['BRAIN_SOURCE']), state,
    {'components':['telegram'], 'memory':{'backend':'qdrant'}}, state / 'build')
print(json.dumps(value))
'''
            result = subprocess.run([sys.executable, '-c', code], env=dict(os.environ,
                PYTHONPATH=str(BRAIN / 'scripts'), BRAIN_SOURCE=str(BRAIN), TEST_STATE=str(state)),
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            gateway = json.loads(result.stdout)['services']['telegram']
            self.assertEqual(gateway['environment']['CODEX_HOME'], str(state / 'codex'))
            mounted = [v['source'] for v in gateway['volumes'] if 'source' in v]
            self.assertIn(str(state), mounted)
            self.assertIn(str(BRAIN), mounted)
            self.assertNotIn(str(ROOT), mounted)

    def test_H3_native_profile_discovers_personal_skills(self):
        result = subprocess.run([str(BRAIN / '.venv/bin/python'), str(Path(__file__).with_name('check_discovery.py'))],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_H5_one_entrypoint_and_supported_layout(self):
        self.assertEqual(sorted(p.name for p in BRAIN.glob('*.sh')), ['secondbrain.sh'])
        for name in ['config.template.toml', 'context.template.toml', 'secondbrain.template.yaml', 'skills.toml', 'instructions.md', 'dot-codex.sh']:
            self.assertFalse((BRAIN / name).exists(), name)
        for name in ['codex.toml', 'context.toml', 'instructions.md']:
            self.assertTrue((BRAIN / 'deployments/templates' / name).is_file(), name)
        self.assertFalse((BRAIN / 'scripts/secondbrain.py').exists())
        self.assertFalse((BRAIN / 'scripts/secondbrain_config.py').exists())
        self.assertFalse((BRAIN / 'scripts/setup_harness.py').exists())
        self.assertFalse((BRAIN / 'scripts/setup_service.py').exists())

    def test_H5_template_staging_and_agent_setup(self):
        with tempfile.TemporaryDirectory() as t:
            code = '''import os
from pathlib import Path
from setup_docker import stage_sources
from setup_components import effective
from setup_host import setup
from setup_support import SetupError
from setup_export import setup_files
from service_credentials import load_credentials
from unittest.mock import patch
import cli
root = Path(os.environ['BRAIN_SOURCE'])
exported = set(setup_files(root))
assert {'secondbrain.sh','scripts/cli.py','scripts/setup_agent.py','skills/manifest.toml','deployments/templates/codex.toml'} <= exported
assert not {'dot-codex.sh','secondbrain.template.yaml','scripts/secondbrain.py','scripts/secondbrain_config.py'} & exported
stage = stage_sources(root, Path(os.environ['TEST_STAGE']))
credentials = stage / 'synthetic-credentials.json'
credentials.write_text('{"TEST_TOKEN":"fixture"}')
credentials.chmod(0o600)
assert load_credentials(credentials) == {'TEST_TOKEN':'fixture'}
credentials.chmod(0o644)
try:
    load_credentials(credentials)
except ValueError:
    pass
else:
    raise AssertionError('Unsafe service credential permissions accepted')
for name in ['codex.toml','context.toml','instructions.md']:
    assert (stage / 'deployments/templates' / name).read_bytes() == (root / 'deployments/templates' / name).read_bytes()
assert effective(['telegram']) == {'telegram','agent','codex'}
try:
    effective(['harness'])
except SetupError:
    pass
else:
    raise AssertionError('Removed component remains accepted')
try:
    setup(root, stage, {}, interactive=False)
except SetupError:
    pass
else:
    raise AssertionError('Removed native setup fallback remains accepted')
calls = []
def record(command, **kwargs):
    calls.append((list(map(str, command)), kwargs)); return 0
state = (stage / 'private-state').resolve()
with patch.dict(os.environ, {'SECOND_BRAIN_STATE':str(state)}), patch.object(cli, 'run', record), patch.object(cli, 'executable', lambda name: name):
    assert cli.main(['context','status']) == 0
    command, options = calls[-1]
    assert command[-2:] == ['--config',str(state / 'context.toml')]
    assert options['env']['CODEX_HOME'] == str(state / 'codex')
    assert cli.main(['telegram']) == 0
    assert calls[-1][1]['env']['TELEGRAM_TO_AGENTS_HOME'] == str(state / 'telegram')
'''
            result = subprocess.run([sys.executable, '-c', code], env=dict(os.environ,
                PYTHONPATH=str(BRAIN / 'scripts'), BRAIN_SOURCE=str(BRAIN), TEST_STAGE=t), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_H4_artifacts_verified_at_vault_destination(self):
        manifest = json.loads((VAULT / 'Dot-codex/Repository split/artifacts.json').read_text())
        self.assertGreater(len(manifest['files']), 0)
        for item in manifest['files']:
            target = VAULT / 'Dot-codex' / item['destination']
            self.assertTrue(target.is_file(), item['destination'])
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), item['sha256'], item['destination'])
        for relative in manifest['moved_roots']:
            self.assertFalse((ROOT / relative).exists(), relative)
        self.assertTrue((VAULT / 'Dot-codex/Repository split/Recovery/source-before.tar.gz').is_file())

if __name__ == '__main__': unittest.main()
