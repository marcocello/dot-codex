"""Fake only urllib HTTP response edge; execute complete provider CLI."""
import io
import json
import os
from pathlib import Path
import runpy
import sys
import urllib.request

root = Path(__file__).resolve().parents[4]
config, provider = sys.argv[1:]
expected = os.environ['INLINE_PROOF_TOKEN']
class Response(io.BytesIO):
    def getcode(self):
        return 200

def open_edge(self, request, *args, **kwargs):
    expected_auth = expected if provider == 'clickup' else 'Bearer '+expected
    assert request.get_header('Authorization') == expected_auth, 'Inline authorization not delivered to provider'
    url = request.full_url
    if url == 'https://api.clickup.com/api/v2/user':
        body = {'user': {'id': 42}}
    elif url == 'https://api.clickup.com/api/v2/team':
        body = {'teams': [{'id': 81}]}
    elif url == 'https://api.notion.com/v1/users/me':
        body = {'object':'user','id':'11111111-1111-4111-8111-111111111111','type':'bot','bot':{'workspace_id':'22222222-2222-4222-8222-222222222222'}}
    else:
        raise AssertionError('Unexpected outbound request')
    return Response(json.dumps(body).encode())

urllib.request.OpenerDirector.open = open_edge
script = root / 'skills/knowledge-connect/scripts' / (provider+'_api.py')
sys.path.insert(0, str(script.parent))
sys.argv = [str(script), '--config', config, '--profile', 'work' if provider == 'clickup' else 'notion', 'check']
runpy.run_path(str(script), run_name='__main__')
