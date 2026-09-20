"""Child-process transport fixture: real CLI, fake unsafe HTTPS edge only."""
import io, json, os, runpy, sys, urllib.error, urllib.parse, urllib.request
from pathlib import Path
from unittest.mock import patch

state_path = Path(os.environ['PROOF_STATE'])
state = json.loads(state_path.read_text())
mode = state.get('mode', '')

def save():
    state_path.write_text(json.dumps(state))

def open_edge(self, req, *args, **kwargs):
    url = urllib.parse.urlsplit(req.full_url)
    assert url.scheme == 'https' and url.netloc == 'api.clickup.com'
    assert url.path.startswith('/api/v2/')
    timeout = kwargs.get('timeout', args[0] if args else None)
    assert isinstance(timeout, (int, float)) and 0 < timeout <= 120
    method = req.get_method()
    data = json.loads(req.data) if req.data else None
    p = url.path.removeprefix('/api/v2')
    q = urllib.parse.parse_qs(url.query)
    state.setdefault('requests', []).append({'path': p, 'method': method, 'query': q, 'data': data, 'auth': req.get_header('Authorization')})
    save()
    if mode in ['401','403','429']:
        raise urllib.error.HTTPError(req.full_url, int(mode), 'private-body-SECRET', {}, io.BytesIO(b'private-body-SECRET'))
    if mode == 'timeout':
        raise TimeoutError('private-body-SECRET')
    if mode == 'malformed':
        return io.BytesIO(b'not JSON private-body-SECRET')
    out = None
    if p == '/user':
        out = {'user': {'id': 99 if mode == 'account' else 42, 'username': 'Synthetic', 'email': 'synthetic@example.test'}}
    elif p == '/team':
        out = {'teams': [{'id': '8' if mode == 'workspace' else '7', 'name': 'Proof workspace'}]}
    elif p == '/team/7/space':
        out = {'spaces': [{'id': '70', 'name': 'Proof space', 'team_id': '7'}]}
    elif p == '/space/70':
        out = {'id':'70', 'team_id':'7', 'name':'Proof space'}
    elif p == '/space/70/folder':
        out = {'folders': [{'id':'80','name':'Folder','lists':[{'id':'101','name':'Tasks'}]}]}
    elif p in ['/space/70/list', '/folder/80/list']:
        out = {'lists': [{'id':'101','name':'Tasks'}, {'id':'102','name':'Deals'}, {'id':'103','name':'Ideas'}]}
    elif p.startswith('/list/') and p.endswith('/field'):
        out = {'fields': [{'id':'f-text','name':'Note','type':'short_text'}, {'id':'f-number','name':'Amount','type':'number'}, {'id':'f-drop','name':'Choice','type':'drop_down','type_config':{'options':[{'id':'opt-a','name':'A','orderindex':0}]}}, {'id':'f-unsupported','name':'Relation','type':'tasks'}]}
    elif p.startswith('/list/') and p.endswith('/task'):
        lid = p.split('/')[2]
        if method == 'POST':
            assert data.get('check_required_custom_fields') is True
            task = {'id':'new1','team_id':'7','list':{'id':lid},'custom_fields':[], **{k:v for k,v in data.items() if k != 'check_required_custom_fields'}}
            if 'markdown_content' in task: task['description'] = task['markdown_content']
            state['tasks']['new1'] = task
            save()
            if mode == 'write-timeout': raise TimeoutError('private-body-SECRET')
            out = task
        else:
            assert q.get('include_closed') == ['true'] and q.get('subtasks') == ['true'] and q.get('include_timl') == ['true']
            page = int(q.get('page', ['0'])[0])
            archived = q.get('archived', ['false'])[0]
            task = state['tasks']['t1']
            if mode == 'repeat': out = {'tasks':[task], 'last_page':False}
            elif mode == 'page-fail' and page == 1: raise urllib.error.HTTPError(req.full_url,503,'bad',{},io.BytesIO(b'SECRET'))
            elif mode == 'no-last-page': out = {'tasks':[task] if page == 0 else []}
            elif archived == 'true': out = {'tasks':[state['tasks']['t3']], 'last_page':True}
            else: out = {'tasks':[task] if page == 0 else [state['tasks']['t2']], 'last_page':page >= 1}
    elif p.startswith('/list/'):
        lid = p.split('/')[2]
        out = {'id':lid, 'name':'List '+lid, 'space':{'id':'90' if mode == 'list' else '70'}, 'statuses':[{'status':'to do'},{'status':'done'}]}
    elif p.startswith('/task/'):
        tid = p.split('/')[2]
        task = state['tasks'].get(tid)
        if task is None: raise urllib.error.HTTPError(req.full_url,404,'missing',{},io.BytesIO(b'SECRET'))
        if '/field/' in p:
            fid = p.split('/')[-1]
            state['tasks'][tid]['custom_fields'] = [{'id':fid,'value':data['value']}]
            save()
            out = {}
        elif method == 'PUT':
            state['tasks'][tid].update(data)
            save()
            if mode == 'write-timeout': raise TimeoutError('private-body-SECRET')
            out = state['tasks'][tid]
        else:
            out = json.loads(json.dumps(task))
            if mode == 'task': out['list'] = {'id':'999'}
            if mode == 'task-workspace': out['team_id'] = '999'
            mutations = [r for r in state['requests'] if r['method'] in ('PUT','POST')]
            if mutations and mode == 'readback-fail': raise urllib.error.HTTPError(req.full_url,503,'failed',{},io.BytesIO(b'SECRET'))
            if mutations and mode == 'readback-mismatch': out.update(name='Wrong', custom_fields=[{'id':'f-text','value':'Wrong'}])
    assert out is not None, (method, p, q)
    return io.BytesIO(json.dumps(out).encode())

script, *argv = sys.argv[1:]
sys.argv = [script, *argv]
sys.path.insert(0, str(Path(script).parent))
with patch.object(urllib.request.OpenerDirector, 'open', open_edge):
    runpy.run_path(script, run_name='__main__')
