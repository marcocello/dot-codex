"""Independent public CLI proof; only HTTP is synthetic."""
import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib import request, error

ROOT = Path(__file__).resolve().parents[4]
CLI = ROOT / 'skills/knowledge-connect/scripts/notion_api.py'
BOT, WS, TASKS, DEALS, IDEAS, PAGE, OTHER = [f'{n:08x}-0000-4000-8000-000000000000' for n in range(1, 8)]
SECRET = 'proof-private-token-never-print'
SCHEMA = {'Name': {'id':'title','type':'title','title':{}}, 'Status': {'id':'s','type':'status','status':{'options':[{'id':'open','name':'Open'}]}}, 'Done': {'id':'d','type':'checkbox','checkbox':{}}}

class Response:
    def __init__(self, data): self.data = json.dumps(data).encode()
    def read(self, *args): return self.data
    def getcode(self): return 200
    def __enter__(self): return self
    def __exit__(self, *args): pass

class Proof(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.config = Path(self.tmp.name) / 'knowledge.toml'
        self.config.write_text('version = 1\ndefault_profile = "work"\n[profiles.work]\nprovider = "notion"\nconnection = "proof"\ntransport = "api"\ntoken_env = "KNOWLEDGE_PROOF_TOKEN"\n' + ''.join(f'{k} = "{v}"\n' for k,v in {'account':BOT,'workspace_id':WS,'tasks':TASKS,'deals':DEALS,'ideas':IDEAS}.items()))
        self.before = self.config.read_bytes()
        self.calls = []
        self.page = {'object':'page','id':PAGE,'parent':{'type':'data_source_id','data_source_id':TASKS},'properties':{'Name':{'type':'title','title':[{'type':'text','text':{'content':'Existing'},'plain_text':'Existing'}]}}}
        self.special = None
    def edge(self, opener, req, *args, **kwargs):
        self.assertTrue(req.full_url.startswith('https://api.notion.com/v1/'))
        self.assertEqual(req.get_header('Authorization'), 'Bearer ' + SECRET)
        self.assertEqual(req.get_header('Notion-version'), '2026-03-11')
        self.assertTrue(0 < kwargs.get('timeout', 0) <= 60)
        route = req.full_url.split('/v1',1)[1]
        body = json.loads(req.data) if req.data else None
        self.calls.append((req.get_method(), route, body))
        if self.special:
            result = self.special(req.get_method(), route, body)
            if result is not None: return Response(result)
        if route == '/users/me': return Response({'object':'user','id':BOT,'type':'bot','bot':{'workspace_id':WS,'owner':{'type':'workspace','workspace':True}}})
        if route.startswith('/data_sources/') and req.get_method() == 'GET':
            return Response({'object':'data_source','id':route.rsplit('/',1)[1], 'properties':SCHEMA})
        if route == '/pages/' + PAGE and req.get_method() == 'GET': return Response(self.page)
        if route.endswith('/query'): return Response({'object':'list','results':[self.page],'has_more':False,'next_cursor':None})
        if (route == '/pages' and req.get_method() == 'POST') or (route == '/pages/' + PAGE and req.get_method() == 'PATCH'):
            if route == '/pages': self.assertEqual(body['parent']['data_source_id'], TASKS)
            self.page['properties'].update(body['properties'])
            return Response(self.page)
        self.fail('Unexpected HTTP operation ' + req.get_method() + ' ' + route)
    def invoke(self, *args, success=True):
        out, err = io.StringIO(), io.StringIO()
        original_path = sys.path[:]
        sys.path.insert(0, str(CLI.parent))
        try:
            with patch.dict(os.environ, {'KNOWLEDGE_PROOF_TOKEN':SECRET}), patch.object(sys, 'argv', [str(CLI),'--config',str(self.config),*args]), patch.object(request.OpenerDirector, 'open', lambda opener, req, *a, **kw: self.edge(opener, req, *a, **kw)), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                try: runpy.run_path(str(CLI), run_name='__main__')
                except SystemExit as exc: code = exc.code
                else: code = 0
        finally: sys.path[:] = original_path
        combined = out.getvalue() + err.getvalue()
        self.assertNotIn(SECRET, combined)
        if self.config.exists(): self.assertEqual(self.config.read_bytes(), self.before)
        if success: self.assertEqual(code, 0, combined)
        else: self.assertNotEqual(code, 0, combined)
        return code, json.loads(out.getvalue()) if out.getvalue().strip().startswith('{') else {}, combined
    def payload(self, value):
        path = Path(self.tmp.name) / 'data.json'
        path.write_text(json.dumps(value))
        return str(path)
    def test_setup_required(self):
        self.config.unlink()
        code, _, text = self.invoke('list','tasks',success=False)
        self.assertEqual(code,3)
        self.assertIn('SETUP_REQUIRED',text)
        self.assertFalse(self.calls)
    def test_identity_check_fields_and_wrong_transport(self):
        _, result, _ = self.invoke('check')
        self.assertTrue(result['verified'])
        self.assertEqual({r.split('/')[-1] for m,r,b in self.calls if r.startswith('/data_sources/')}, {TASKS,DEALS,IDEAS})
        _, result, _ = self.invoke('fields','tasks')
        self.assertEqual(result['properties'],SCHEMA)
        self.calls.clear()
        self.special = lambda m,r,b: {'object':'user','id':OTHER,'type':'bot','bot':{'workspace_id':WS}} if r == '/users/me' else None
        self.invoke('check',success=False)
        self.assertEqual([r for _,r,_ in self.calls],['/users/me'])
        self.config.write_text(self.config.read_text().replace('transport = "api"\ntoken_env = "KNOWLEDGE_PROOF_TOKEN"\n',''))
        self.before = self.config.read_bytes()
        self.calls.clear()
        self.invoke('check',success=False)
        self.assertFalse(self.calls)
    def test_pagination_and_broken_cursor(self):
        def pages(m,r,b):
            if r.endswith('/query'):
                self.assertEqual(b['page_size'],100)
                return {'object':'list','results':[self.page] if not b.get('start_cursor') else [],'has_more':not bool(b.get('start_cursor')), 'next_cursor':'cursor-two' if not b.get('start_cursor') else None}
        self.special = pages
        _, result, _ = self.invoke('list','tasks')
        self.assertTrue(result['complete'])
        self.assertEqual([p['id'] for p in result['pages']],[PAGE])
        self.assertEqual([b.get('start_cursor') for m,r,b in self.calls if r.endswith('/query')],[None,'cursor-two'])
        self.special = lambda m,r,b: {'object':'list','results':[],'has_more':True,'next_cursor':None} if r.endswith('/query') else None
        self.invoke('list','tasks',success=False)
    def test_create_update_and_separate_readback(self):
        for command in [('create','tasks'),('update','tasks',PAGE)]:
            self.calls.clear()
            _, result, _ = self.invoke(*command,'--data-file',self.payload({'Name':'New title','Status':'Open','Done':True}))
            self.assertTrue(result['verified'])
            self.assertEqual(result['page']['id'],PAGE)
            write_indices = [i for i,(m,r,b) in enumerate(self.calls) if r.startswith('/pages') and m in {'PATCH','POST'}]
            self.assertEqual(len(write_indices),1)
            self.assertIn(('GET','/pages/'+PAGE,None),self.calls[write_indices[0]+1:])
        self.calls.clear()
        self.special = lambda m,r,b: {**self.page,'properties':{'Name':{'type':'title','title':[{'text':{'content':'Wrong'}}]}}} if m == 'GET' and r == '/pages/'+PAGE else None
        _, _, text = self.invoke('create','tasks','--data-file',self.payload({'Name':'Wanted'}),success=False)
        self.assertIn(PAGE,text)
        self.assertEqual(sum(m=='POST' and r=='/pages' for m,r,b in self.calls),1)
    def test_scope_and_invalid_schema_block_writes(self):
        self.page['parent']['data_source_id'] = OTHER
        self.invoke('update','tasks',PAGE,'--data-file',self.payload({'Name':'Danger'}),success=False)
        self.assertFalse(any(m in {'PATCH','POST'} for m,r,b in self.calls))
        self.page['parent']['data_source_id'] = TASKS
        for payload in [{'Missing':'value'},{'Status':'Unconfigured'},{'Done':'yes'}]:
            self.calls.clear()
            self.invoke('create','tasks','--data-file',self.payload({'Name':'Invalid',**payload}),success=False)
            self.assertFalse(any(m in {'PATCH','POST'} for m,r,b in self.calls))
    def test_http_failure_no_retry_or_body_leak(self):
        for status in (401,403,429):
            self.calls.clear()
            def fail(m,r,b): raise error.HTTPError('https://api.notion.com/v1/users/me',status,SECRET,{},io.BytesIO(SECRET.encode()))
            self.special = fail
            self.invoke('check',success=False)
            self.assertEqual(len(self.calls),1)

if __name__ == '__main__': unittest.main(verbosity=2)
