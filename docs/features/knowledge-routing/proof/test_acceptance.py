"""Independent public boundary: subprocess config and only HTTP edge substitution."""
import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib import request, parse

ROOT = Path(__file__).resolve().parents[4]
PROFILE = ROOT / 'skills/knowledge-config/scripts/knowledge_profile.py'
BOT, WS, SOURCE, PAGE, OTHER = [f'{i:08x}-0000-4000-8000-000000000000' for i in range(1, 6)]
SECRET = 'synthetic-private-never-print'

class Response(io.BytesIO):
    def __init__(self, value): super().__init__(json.dumps(value).encode())
    def getcode(self): return 200

class Proof(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.config = Path(self.tmp.name) / 'knowledge.toml'
        self.calls = []
        self.wrong_workspace = False
        self.wrong_account = False
    def cli(self, *args, code=0):
        p = subprocess.run([sys.executable,str(PROFILE),'--config',str(self.config),*args],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0,p.stdout+p.stderr) if code is None else self.assertEqual(p.returncode,code,p.stdout+p.stderr)
        self.assertNotIn(SECRET,p.stdout+p.stderr)
        return json.loads(p.stdout or p.stderr) if code in (0,3) else p.stderr
    def put(self, provider='clickup', name='work', extra=()):
        return self.cli('put',name,'--provider',provider,'--connection',name,'--account',BOT if provider=='notion' else '42','--workspace-id',WS if provider=='notion' else '7',*extra)
    def test_first_use_connection_only_and_credential_recovery(self):
        self.assertEqual(self.cli('resolve',code=3)['code'],'SETUP_REQUIRED')
        self.put(extra=('--default','--destination','https://app.clickup.com/7/docs/example'))
        saved = self.config.read_bytes()
        r = self.cli('resolve')
        self.assertFalse({'tasks','deals','ideas'} & set(r))
        self.assertEqual(self.cli('resolve','--transport','api',code=3)['code'],'SETUP_REQUIRED')
        self.assertEqual(saved,self.config.read_bytes())
        self.cli('credentials','work','--token-env','UNSET_PROOF_TOKEN')
        listing = self.cli('list')
        self.assertEqual(listing['default_profile'],'work')
        p = listing['profiles']['work']
        self.assertEqual(p.get('transport','mcp'),'mcp')
        self.assertEqual(p['destination'],r['destination'])
        saved = self.config.read_bytes()
        self.assertEqual(self.cli('resolve','--transport','api')['transport'],'api')
        self.assertEqual(saved,self.config.read_bytes())
        self.assertEqual(self.cli('resolve').get('transport','mcp'),'mcp')
        self.cli('transport','work','api')
        self.assertEqual(self.cli('resolve')['transport'],'api')
    def test_isolated_profiles_credential_replacement_and_persist_rejection(self):
        self.put(extra=('--default',))
        self.put(provider='notion',name='other')
        before = self.config.read_bytes()
        self.cli('transport','work','api',code=None)
        self.assertEqual(before,self.config.read_bytes())
        self.cli('credentials','other','--token-env','NOTION_PROOF')
        self.cli('credentials','other','--token-file',str(Path(self.tmp.name)/'uncreated-token'))
        data = self.cli('list')
        self.assertEqual(data['default_profile'],'work')
        self.assertNotIn('token_env',data['profiles']['work'])
        self.assertNotIn('token_env',data['profiles']['other'])
        self.assertEqual(data['profiles']['other']['token_file'],str(Path(self.tmp.name)/'uncreated-token'))
        self.assertFalse((Path(self.tmp.name)/'uncreated-token').exists())
        saved = self.config.read_bytes()
        self.assertEqual(self.cli('resolve','--profile','other','--transport','api')['profile'],'other')
        self.assertEqual(saved,self.config.read_bytes())
    def test_legacy_aliases_and_local_profiles(self):
        self.put(extra=('--tasks','101','--deals','101','--ideas','101','--default'))
        self.cli('credentials','work','--token-env','UNSET_PROOF_TOKEN')
        self.assertEqual(self.cli('resolve','--transport','api')['tasks'],'101')
        self.cli('put','local','--provider','markdown','--root',str(Path(self.tmp.name)/'notes'))
        self.cli('put','off','--provider','none')
        self.assertEqual(self.cli('resolve','--profile','off')['provider'],'none')
        self.assertEqual(self.cli('resolve','--profile','local')['provider'],'markdown')
        self.assertEqual(self.cli('list')['default_profile'],'work')
    def edge(self, opener, req, *args, **kwargs):
        url = parse.urlsplit(req.full_url)
        self.assertEqual(url.scheme,'https')
        self.assertTrue(0 < kwargs.get('timeout',0) <= 60)
        self.assertEqual(req.get_method(),'GET' if not url.path.endswith('/query') else 'POST')
        self.calls.append(url.path)
        if url.netloc=='api.clickup.com':
            self.assertEqual(req.get_header('Authorization'),SECRET)
            p=url.path.removeprefix('/api/v2')
            if p=='/user': data={'user':{'id':99 if self.wrong_account else 42}}
            elif p=='/team': data={'teams':[{'id':'999' if self.wrong_workspace else '7'}]}
            elif p=='/team/7/space': data={'spaces':[{'id':'70'}]}
            elif p=='/list/101': data={'id':'101','space':{'id':'70'}}
            elif p=='/list/101/task': data={'tasks':[{'id':'t1','list':{'id':'101'},'team_id':'7','name':'User structure'}], 'last_page':True}
            else: self.fail('Unexpected ClickUp access '+p)
        else:
            self.assertEqual(url.netloc,'api.notion.com')
            self.assertEqual(req.get_header('Authorization'),'Bearer '+SECRET)
            self.assertEqual(req.get_header('Notion-version'),'2026-03-11')
            p=url.path.removeprefix('/v1')
            if p=='/users/me': data={'object':'user','type':'bot','id':OTHER if self.wrong_account else BOT,'bot':{'workspace_id':OTHER if self.wrong_workspace else WS}}
            elif p=='/data_sources/'+SOURCE: data={'object':'data_source','id':SOURCE,'properties':{'Name':{'id':'title','type':'title','title':{}}}}
            elif p=='/data_sources/'+SOURCE+'/query': data={'object':'list','results':[{'object':'page','id':PAGE,'parent':{'type':'data_source_id','data_source_id':SOURCE},'properties':{}}],'has_more':False,'next_cursor':None}
            else: self.fail('Unexpected Notion access '+p)
        return Response(data)
    def api(self, provider, *args, success=True):
        script=ROOT/f'skills/knowledge-connect/scripts/{provider}_api.py'
        out,err=io.StringIO(),io.StringIO()
        before=self.config.read_bytes()
        original=sys.path[:]
        sys.path.insert(0,str(script.parent))
        try:
            with patch.dict(os.environ,{'ROUTING_PROOF_TOKEN':SECRET}), patch.object(sys,'argv',[str(script),'--config',str(self.config),*args]), patch.object(request.OpenerDirector,'open',lambda opener, req,*a,**kw:self.edge(opener,req,*a,**kw)),contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
                try: runpy.run_path(str(script),run_name='__main__')
                except SystemExit as exc: code=exc.code
                else: code=0
        finally: sys.path[:]=original
        text=out.getvalue()+err.getvalue()
        self.assertNotIn(SECRET,text)
        self.assertEqual(self.config.read_bytes(),before)
        if success: self.assertEqual(code,0,text)
        else: self.assertNotEqual(code,0,text)
        return json.loads(out.getvalue()) if success else text
    def test_provider_connection_only_override_and_explicit_destination(self):
        for provider in ('clickup','notion'):
            with self.subTest(provider=provider):
                self.config.unlink(missing_ok=True)
                self.put(provider=provider,extra=('--default',))
                self.cli('credentials','work','--token-env','ROUTING_PROOF_TOKEN')
                self.calls=[]
                self.api(provider,'check',success=False)
                self.assertFalse(self.calls)
                result=self.api(provider,'--transport','api','check')
                self.assertTrue(result['verified'])
                self.assertFalse(any('/list/' in p or '/data_sources/' in p for p in self.calls))
                self.calls=[]
                result=self.api(provider,'--transport','api','list','101' if provider=='clickup' else SOURCE)
                self.assertTrue(result['complete'])
                self.assertEqual([x['id'] for x in result['tasks' if provider=='clickup' else 'pages']],['t1' if provider=='clickup' else PAGE])
                self.calls=[]
                self.api(provider,'--transport','api','list','tasks',success=False)
                self.assertFalse(self.calls)
                for mismatch in ('wrong_workspace','wrong_account'):
                    setattr(self,mismatch,True)
                    self.calls=[]
                    self.api(provider,'--transport','api','list','101' if provider=='clickup' else SOURCE,success=False)
                    self.assertFalse(any('/list/' in p or '/data_sources/' in p for p in self.calls))
                    setattr(self,mismatch,False)

if __name__=='__main__': unittest.main(verbosity=2)
