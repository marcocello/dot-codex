"""Unsafe network edge only; execute the complete requested CLI in a subprocess."""
import io
import json
import os
from pathlib import Path
import runpy
import sys
from urllib import error, request
from urllib.parse import urlparse

state_path = Path(os.environ['DELETE_PROOF_STATE'])
script = Path(sys.argv[1])
args = sys.argv[2:]
class Response(io.BytesIO):
    def __init__(self, body, status=200):
        super().__init__(body)
        self.status = status
    def getcode(self):
        return self.status

def open_edge(self, req, *args, **kwargs):
    state = json.loads(state_path.read_text())
    method = req.get_method()
    path = urlparse(req.full_url).path
    assert req.full_url.startswith('https://api.clickup.com/api/v2/'), 'Unexpected API origin/version'
    assert req.get_header('Authorization') == os.environ['DELETE_PROOF_TOKEN'], 'Wrong credential supplied'
    state['requests'].append([method, path])
    state_path.write_text(json.dumps(state))
    mode = state['mode']
    def fail(code):
        raise error.HTTPError(req.full_url, code, 'private provider detail', {}, io.BytesIO(b'private provider body'))
    if path == '/api/v2/user':
        if mode == 'auth401': fail(401)
        body = {'user': {'id': 43 if mode == 'identity' else 42}}
    elif path == '/api/v2/team':
        body = {'teams': [{'id': 82 if mode == 'workspace' else 81}]}
    elif path == '/api/v2/team/81/space':
        body = {'spaces': [{'id': 91}]}
    elif path == '/api/v2/list/101':
        if mode == 'list403': fail(403)
        body = {'id':101,'space': {'id':92 if mode == 'list_workspace' else 91}}
    elif path in ('/api/v2/task/t123', '/api/v2/task/sub123'):
        if method == 'DELETE':
            if mode == 'delete429': fail(429)
            if mode == 'delete500': fail(500)
            if mode == 'delete_timeout': raise TimeoutError('private timeout detail')
            state['exists'] = False
            state_path.write_text(json.dumps(state))
            if mode == 'delete_malformed': return Response(b'[]')
            return Response(b'{}' if mode == 'json_success' else b'', 200 if mode == 'json_success' else 204)
        assert method == 'GET', 'Unexpected task mutation'
        if not state['exists']:
            if mode.startswith('post') and mode[4:].isdigit(): fail(int(mode[4:]))
            if mode == 'post_timeout': raise TimeoutError('private timeout detail')
            if mode == 'post_malformed': return Response(b'not json')
            if mode == 'post_shape': return Response(b'[]')
            if mode != 'still_visible': fail(404)
        if mode == 'pre404': fail(404)
        if mode == 'task403': fail(403)
        body = {'id':path.rsplit('/',1)[1], 'team_id':82 if mode == 'task_workspace' else 81,
                'list':{'id':102 if mode == 'task_list' else 101}, 'parent': 'parent1' if 'sub123' in path else None}
        if mode == 'task_identity': body['id'] = 'other'
    else:
        raise AssertionError('Unexpected outbound request: '+method+' '+path)
    return Response(json.dumps(body).encode())

request.OpenerDirector.open = open_edge
sys.path.insert(0, str(script.parent))
sys.argv = [str(script), *args]
runpy.run_path(str(script), run_name='__main__')
