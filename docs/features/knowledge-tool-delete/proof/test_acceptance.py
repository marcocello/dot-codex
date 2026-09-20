import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[4]
CANON = ROOT/'skills/knowledge-tool-connect/scripts'
OLD = ROOT/'skills/knowledge-connect/scripts'
EDGE = Path(__file__).with_name('api_edge.py')
TOKEN = 'pk_synthetic_delete_acceptance_only'

class Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.config = self.home/'knowledge.toml'
        self.state = self.home/'remote.json'
        self.env = {**os.environ, 'CODEX_HOME':str(self.home), 'DELETE_PROOF_TOKEN':TOKEN,
                    'DELETE_PROOF_STATE':str(self.state)}
    def cli(self, script, *args, stdin=None, edge=False):
        cmd = [sys.executable]
        if edge: cmd += [str(EDGE)]
        result = subprocess.run(cmd+[str(script), *args], env=self.env, input=stdin,
                                text=True, capture_output=True, timeout=15)
        self.assertNotIn(TOKEN, result.stdout+result.stderr)
        self.assertNotIn('private provider body',result.stdout+result.stderr)
        return result
    def profile(self, transport='api', inline=True):
        result = self.cli(CANON/'knowledge_profile.py', 'put', 'work', '--provider','clickup',
                          '--connection','test-clickup','--account','42','--workspace-id','81',
                          '--tasks','101','--transport',transport,'--token-env','DELETE_PROOF_TOKEN','--default')
        self.assertEqual(result.returncode,0,result.stderr)
        if inline:
            result=self.cli(CANON/'knowledge_profile.py','credentials','work','--token-stdin',stdin=TOKEN)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['token'],'[redacted]')
    def remote(self, mode):
        self.state.write_text(json.dumps({'mode':mode,'exists':True,'requests':[]}))
    def delete(self, destination='101', task='t123', script=CANON/'clickup_api.py', override=False):
        return self.cli(script,*(['--transport','api'] if override else []),'delete',destination,task,edge=True)
    def observed(self):
        return json.loads(self.state.read_text())
    def test_first_use_routes_to_new_skill(self):
        for script in (CANON/'knowledge_profile.py', OLD/'knowledge_profile.py', ROOT/'scripts/knowledge_profile.py'):
            with self.subTest(script=script):
                result=self.cli(script,'resolve')
                self.assertNotEqual(result.returncode,0)
                self.assertEqual(json.loads(result.stderr)['skill'],'knowledge-tool-connect')
    def test_discoverability_and_compatibility(self):
        self.assertTrue((CANON.parent/'SKILL.md').is_file())
        self.assertFalse((OLD.parent/'SKILL.md').exists())
        self.assertTrue(OLD.is_symlink())
        inventory=tomllib.loads((ROOT/'skills.toml').read_text())['skills']
        self.assertEqual(sum(x['name']=='knowledge-tool-connect' for x in inventory),1)
        self.assertFalse(any(x['name']=='knowledge-connect' for x in inventory))
        self.profile()
        before=self.config.read_bytes()
        for directory in (CANON,OLD,ROOT/'skills/knowledge-config/scripts',ROOT/'scripts'):
            result=self.cli(directory/'knowledge_profile.py','resolve')
            self.assertEqual(result.returncode,0,result.stderr)
            data=json.loads(result.stdout)
            self.assertEqual(data['profile'],'work')
            self.assertEqual(data['workspace_id'],'81')
            self.assertEqual(data['token'],'[redacted]')
        self.assertEqual(self.config.read_bytes(),before)
        self.assertEqual(self.config.stat().st_mode & 0o777,0o600)
    def test_verified_task_subtask_and_legacy_success(self):
        self.profile()
        for script,task,destination,mode in ((CANON/'clickup_api.py','t123','101','ok'),
            (CANON/'clickup_api.py','sub123','tasks','ok'),(OLD/'clickup_api.py','t123','101','json_success'),
            (ROOT/'skills/knowledge-config/scripts/clickup_api.py','t123','tasks','ok')):
            with self.subTest(script=script,task=task,mode=mode):
                self.remote(mode)
                result=self.delete(destination,task,script)
                self.assertEqual(result.returncode,0,result.stderr)
                data=json.loads(result.stdout)
                self.assertEqual((data['task_id'],data['deleted'],data['verified']),(task,True,True))
                self.assertEqual((data['profile'],data['account'],data['workspace_id']),('work','42','81'))
                state=self.observed()
                self.assertFalse(state['exists'])
                endpoint='/api/v2/task/'+task
                calls=[x for x in state['requests'] if x[1]==endpoint]
                self.assertEqual(calls,[['GET',endpoint],['DELETE',endpoint],['GET',endpoint]])
    def test_mcp_preference_requires_explicit_override_and_is_preserved(self):
        self.profile(transport='mcp',inline=False)
        self.remote('ok')
        before=self.config.read_bytes()
        denied=self.delete()
        self.assertNotEqual(denied.returncode,0)
        self.assertEqual(self.observed()['requests'],[])
        allowed=self.delete(override=True)
        self.assertEqual(allowed.returncode,0,allowed.stderr)
        self.assertEqual(self.config.read_bytes(),before)
    def test_preflight_failures_never_mutate(self):
        self.profile()
        for mode in ('identity','auth401','workspace','list_workspace','list403','task_identity','task_workspace','task_list','task403','pre404'):
            with self.subTest(mode=mode):
                self.remote(mode)
                result=self.delete()
                self.assertNotEqual(result.returncode,0)
                state=self.observed()
                self.assertTrue(state['exists'])
                self.assertFalse(any(x[0]=='DELETE' for x in state['requests']))
        for destination,task in (('../101','t123'),('101','../t123'),('101','t123?x=y')):
            with self.subTest(destination=destination,task=task):
                self.remote('ok')
                result=self.delete(destination,task)
                self.assertNotEqual(result.returncode,0)
                self.assertFalse(any(x[0]=='DELETE' for x in self.observed()['requests']))
    def test_failed_or_uncertain_deletion_never_retries_or_claims_verified(self):
        self.profile()
        modes=('delete429','delete500','delete_timeout','delete_malformed','still_visible',
               'post401','post403','post429','post500','post_timeout','post_malformed','post_shape')
        for mode in modes:
            with self.subTest(mode=mode):
                self.remote(mode)
                result=self.delete()
                self.assertNotEqual(result.returncode,0,result.stdout)
                self.assertIn('unverified',result.stderr.lower())
                self.assertIn('t123',result.stderr)
                self.assertEqual(sum(x[0]=='DELETE' for x in self.observed()['requests']),1)
                self.assertNotIn('"verified": true',result.stdout.lower())
                if mode.startswith('delete'):
                    self.assertEqual(sum(x[0]=='GET' and x[1]=='/api/v2/task/t123' for x in self.observed()['requests']),1)

if __name__=='__main__': unittest.main(verbosity=2)
