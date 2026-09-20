"""Exercise the real urllib redirect chain with only the HTTP response faked."""
import email.message
import io
import os
from pathlib import Path
import sys
from unittest.mock import patch
from urllib.response import addinfourl

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'skills/knowledge-connect/scripts'))
from clickup_http import APIError, Transport

calls = []
def redirect_response(opener, req, data=None):
    calls.append(req.full_url)
    headers = email.message.Message()
    headers['Location'] = 'https://unrelated.example.test/token-recipient'
    response = addinfourl(io.BytesIO(b''), headers, req.full_url, 302)
    response.msg = 'Found'
    return response

with patch.dict(os.environ, {'REDIRECT_TEST_TOKEN': 'synthetic-only'}):
    transport = Transport({'token_env': 'REDIRECT_TEST_TOKEN'})
    with patch('urllib.request.OpenerDirector._open', redirect_response):
        try:
            transport.call('GET', '/user')
        except APIError as exc:
            assert '302' in str(exc)
        else:
            raise AssertionError('Redirect should not produce successful API response')
assert calls == ['https://api.clickup.com/api/v2/user'], calls
print('Real urllib redirect refusal: PASS; no second request')
