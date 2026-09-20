import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DIR = Path(__file__).resolve().parent
RESOLVER = ROOT / 'skills/knowledge-config/scripts/knowledge_profile.py'
API = ROOT / 'skills/knowledge-config/scripts/clickup_api.py'
SECRET = 'proof-SYNTHETIC-only-SECRET'

class Acceptance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = self.root / 'knowledge.toml'
        self.state = self.root / 'state.json'
        self.env = dict(os.environ, PROOF_TOKEN=SECRET, PROOF_STATE=str(self.state))
        self.reset()
    def reset(self, mode=''):
        self.state.write_text(json.dumps({'mode':mode,'tasks':{f't{i}':{'id':f't{i}','name':f'Task {i}','description':'Keep me','team_id':'7','list':{'id':'101'},'custom_fields':[]} for i in range(1,4)},'requests':[]}))
    def calls(self): return json.loads(self.state.read_text())['requests']
    def runcli(self, script, *args, ok=True, env=None):
        command = [sys.executable]
        if script == API: command += [str(DIR / 'http_edge.py')]
        result = subprocess.run(command+[str(script),'--config',str(self.config),*map(str,args)],capture_output=True,text=True,env=env or self.env,timeout=20)
        self.assertNotIn(SECRET, result.stdout+result.stderr)
        self.assertNotIn('private-body-SECRET', result.stdout+result.stderr)
        if ok: self.assertEqual(result.returncode,0,result.stderr)
        else: self.assertNotEqual(result.returncode,0,result.stdout)
        return result
    def setup_api(self, *extra):
        return self.runcli(RESOLVER,'put','work','--provider','clickup','--transport','api','--token-env','PROOF_TOKEN','--connection','direct','--account','42','--workspace-id','7','--tasks','101','--deals','102','--ideas','103','--default',*extra)
    def payload(self, value):
        path = self.root / 'payload.json'; path.write_text(json.dumps(value)); return path
    def test_setup_signal_restart_none_and_override(self):
        for cli in (RESOLVER, ROOT/'scripts/knowledge_profile.py', API):
            r = self.runcli(cli, 'check' if cli == API else 'resolve',ok=False)
            self.assertEqual(r.returncode,3)
            error = json.loads(r.stderr)
            self.assertEqual(error['code'],'SETUP_REQUIRED'); self.assertEqual(error['skill'],'knowledge-config')
        self.runcli(RESOLVER,'put','off','--provider','none')
        self.assertEqual(self.runcli(RESOLVER,'resolve',ok=False).returncode,3)
        self.runcli(RESOLVER,'default','off')
        self.assertEqual(json.loads(self.runcli(RESOLVER,'resolve').stdout)['provider'],'none')
        self.setup_api()
        self.runcli(RESOLVER,'resolve','--profile','off')
        self.assertEqual(json.loads(self.runcli(RESOLVER,'resolve').stdout)['profile'],'work')
        self.assertNotEqual(self.runcli(RESOLVER,'resolve','--profile','absent',ok=False).returncode,3)
        self.config.write_text('broken = [')
        self.assertNotEqual(self.runcli(RESOLVER,'resolve',ok=False).returncode,3)
    def test_credentials_configuration_and_isolation(self):
        self.setup_api(); original=self.config.read_bytes()
        self.runcli(RESOLVER,'put','bad','--provider','clickup','--transport','api','--token-env','PROOF_TOKEN','--token-file',str(self.root/'token'),'--connection','direct','--account','42','--workspace-id','7','--tasks','101','--deals','102','--ideas','103',ok=False)
        self.assertEqual(self.config.read_bytes(),original)
        self.assertNotIn(SECRET,self.config.read_text())
        no_secret=dict(self.env); no_secret.pop('PROOF_TOKEN')
        self.runcli(API,'check',ok=False,env=no_secret); self.assertEqual(self.calls(),[])
        self.runcli(RESOLVER,'put','mcp','--provider','clickup','--connection','connector','--account','label','--workspace-id','7','--tasks','101','--deals','102','--ideas','103','--default')
        self.runcli(API,'check',ok=False); self.assertEqual(self.calls(),[])
    def test_discover_and_check(self):
        self.runcli(API,'discover','--token-env','PROOF_TOKEN','--workspace-id','7')
        self.assertIn('/user',[r['path'] for r in self.calls()])
        self.assertIn('/team/7/space',[r['path'] for r in self.calls()])
        self.setup_api(); self.reset()
        self.assertTrue(json.loads(self.runcli(API,'check').stdout)['verified'])
        self.assertTrue(all(r['auth']==SECRET for r in self.calls()))
        self.setup_api('--auth-type','oauth'); self.reset(); self.runcli(API,'check')
        self.assertTrue(all(r['auth']=='Bearer '+SECRET for r in self.calls()))
    def test_private_token_file(self):
        token=self.root/'secret'; token.write_text(SECRET); token.chmod(0o600)
        self.runcli(API,'discover','--token-file',token)
        token.chmod(0o644); self.reset()
        self.runcli(API,'discover','--token-file',token,ok=False); self.assertEqual(self.calls(),[])
        token.chmod(0o600); link=self.root/'link'; link.symlink_to(token)
        self.runcli(API,'discover','--token-file',link,ok=False); self.assertEqual(self.calls(),[])
    def test_scope_stops_content_access(self):
        self.setup_api()
        for mode in ('account','workspace','list'):
            with self.subTest(mode=mode):
                self.reset(mode); self.runcli(API,'list','tasks',ok=False)
                paths=[r['path'] for r in self.calls()]
                self.assertFalse(any('/task' in p for p in paths))
                if mode=='account': self.assertEqual(paths,['/user'])
        for mode in ('task','task-workspace'):
            self.reset(mode); self.runcli(API,'update','tasks','t1','--data-file',self.payload({'name':'Changed'}),ok=False)
            self.assertTrue(all(r['method']=='GET' for r in self.calls()))
    def test_complete_pagination_and_failures(self):
        self.setup_api()
        result=json.loads(self.runcli(API,'list','tasks').stdout)
        self.assertTrue(result['complete'])
        self.assertEqual({t['id'] for t in result['tasks']},{'t1','t2','t3'})
        calls=[r for r in self.calls() if r['path']=='/list/101/task']
        self.assertTrue(any(r['query'].get('page')==['1'] for r in calls))
        self.assertTrue(any(r['query'].get('archived')==['true'] for r in calls))
        self.reset('no-last-page'); self.assertTrue(json.loads(self.runcli(API,'list','tasks').stdout)['complete'])
        for mode in ('repeat','page-fail'):
            self.reset(mode); self.runcli(API,'list','tasks',ok=False)
    def test_mutation_and_readback(self):
        self.setup_api()
        for command, args, data in [('create',[],{'name':'New','description':'Text','status':'to do','priority':2}),('update',['t1'],{'name':'Changed'})]:
            self.reset(); result=json.loads(self.runcli(API,command,'tasks',*args,'--data-file',self.payload(data)).stdout)
            self.assertTrue(result['verified'])
            calls=self.calls(); writes=[r for r in calls if r['method'] in ('POST','PUT')]
            self.assertEqual(len(writes),1)
            tid='new1' if command=='create' else 't1'
            self.assertEqual(calls[-1]['path'],'/task/'+tid); self.assertEqual(calls[-1]['method'],'GET')
            saved=json.loads(self.state.read_text())['tasks'][tid]
            self.assertEqual(saved['name'],data['name'])
            if command=='update': self.assertEqual(saved['description'],'Keep me')
        for data in ({'name':'X','custom_fields':[]},{'name':'X','status':'unknown'},{'name':'X','priority':9},{'name':7},{'name':'X','description':'a','markdown_content':'b'}):
            self.reset(); self.runcli(API,'create','tasks','--data-file',self.payload(data),ok=False)
            self.assertTrue(all(r['method']=='GET' for r in self.calls()))
    def test_custom_fields_and_rejections(self):
        self.setup_api()
        self.runcli(API,'fields','tasks')
        for fid,value in [('f-text','Changed'),('f-number',12),('f-drop','opt-a')]:
            self.reset(); out=json.loads(self.runcli(API,'set-field','tasks','t1','--field-id',fid,'--value-file',self.payload(value)).stdout)
            self.assertTrue(out['verified']); self.assertEqual(self.calls()[-1]['path'],'/task/t1')
            self.assertEqual(json.loads(self.state.read_text())['tasks']['t1']['custom_fields'][0]['value'],value)
        for fid,value in [('f-drop','unknown'),('f-unsupported',[]),('unknown','X')]:
            self.reset(); self.runcli(API,'set-field','tasks','t1','--field-id',fid,'--value-file',self.payload(value),ok=False)
            self.assertTrue(all(r['method']=='GET' for r in self.calls()))
    def test_failure_no_success_no_retry(self):
        self.setup_api()
        for mode in ('401','403','429','timeout','malformed'):
            self.reset(mode); self.runcli(API,'check',ok=False); self.assertEqual(len(self.calls()),1)
        for mode in ('write-timeout','readback-fail','readback-mismatch'):
            self.reset(mode)
            result=self.runcli(API,'update','tasks','t1','--data-file',self.payload({'name':'Changed'}),ok=False)
            self.assertIn('t1',result.stderr)
            self.assertEqual(len([r for r in self.calls() if r['method']=='PUT']),1)

if __name__=='__main__': unittest.main(verbosity=2)
