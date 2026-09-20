"""Docs contract tests using synthetic data; no credentials or live mutations."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from clickup_docs import Docs
from clickup_http import APIError, Transport
import clickup_api


class Fake:
    def __init__(self):
        self.profile = {'workspace_id': '7', 'account': '42', 'profile': 'test'}
        self.http = self
        self.calls = []
        self.doc = {'id': 'doc-1', 'workspace_id': 7, 'name': 'Documentazione'}
        self.parent = {'id': 'page-1', 'workspace_id': 7, 'doc_id': 'doc-1', 'name': 'Transcripts', 'content': 'keep'}
        self.pages = {'page-1': self.parent}
        self.fail_read = False
        self.corrupt = False
        self.repeat_cursor = False

    def context(self):
        return self.profile

    def call(self, method, path, body=None, **kwargs):
        self.calls.append((method, path, copy.deepcopy(body), kwargs))
        url = urlparse(path)
        if url.path == '/workspaces/7/docs':
            if 'cursor' not in parse_qs(url.query) or self.repeat_cursor:
                return {'docs': [self.doc], 'next_cursor': 'two'}
            return {'docs': []}
        if url.path.endswith('/page_listing'):
            return [dict(self.parent, pages=[dict(self.parent, id='page-2', parent_page_id='page-1')])]
        if url.path.endswith('/pages') and method == 'POST':
            page = dict(self.parent, **{k: v for k, v in body.items() if k != 'content_format'})
            page['id'] = 'new-page'
            if self.corrupt:
                page['content'] = 'truncated'
            self.pages['new-page'] = page
            return copy.deepcopy(page)
        if '/pages/' in url.path:
            pid = url.path.split('/')[-1]
            if method == 'PUT':
                page = self.pages[pid]
                for k in ('name', 'sub_title'):
                    if k in body:
                        page[k] = body[k]
                if 'content' in body:
                    mode = body.get('content_edit_mode', 'replace')
                    old = page['content']
                    page['content'] = {'replace': body['content'], 'append': old + body['content'], 'prepend': body['content'] + old}[mode]
                return {}
            if self.fail_read and pid == 'new-page':
                raise APIError('Read timed out')
            return copy.deepcopy(self.pages[pid])
        return copy.deepcopy(self.doc)


class DocsTests(unittest.TestCase):
    def setUp(self):
        self.client = Fake()
        self.docs = Docs(self.client)

    def test_verbatim_child_creation(self):
        text = 'Andrea: perché?\nMarco: sì — ecco.\n'
        result = self.docs.mutate_page('doc-1', {'name': 'Meeting', 'parent_page_id': 'page-1', 'content': text, 'content_format': 'text/plain'})
        self.assertTrue(result['verified'])
        self.assertEqual(result['page']['content'], text)
        self.assertEqual(result['page']['parent_page_id'], 'page-1')
        self.assertEqual(self.client.parent['content'], 'keep')
        self.assertEqual(sum(c[0] == 'POST' for c in self.client.calls), 1)
        self.assertIn('content_format=text%2Fplain', self.client.calls[-1][1])

    def test_tree_and_cursor_pagination(self):
        self.assertEqual(self.docs.pages('doc-1')[0]['pages'][0]['id'], 'page-2')
        self.assertTrue(self.docs.search()['complete'])
        self.assertTrue(any('cursor=two' in c[1] for c in self.client.calls))
        self.client.repeat_cursor = True
        with self.assertRaisesRegex(APIError, 'repeated'):
            self.docs.search()

    def test_cross_workspace_and_parent_rejected_before_write(self):
        for key, value in [('workspace_id', 8), ('doc_id', 'other-doc')]:
            with self.subTest(key=key):
                self.client.parent[key] = value
                with self.assertRaises(APIError):
                    self.docs.mutate_page('doc-1', {'name': 'x', 'parent_page_id': 'page-1'})
                self.assertFalse(any(c[0] == 'POST' for c in self.client.calls))
                self.client.parent[key] = 7 if key == 'workspace_id' else 'doc-1'

    def test_uncertain_write_retains_id_and_does_not_retry(self):
        for flag in ('fail_read', 'corrupt'):
            with self.subTest(flag=flag):
                self.setUp()
                setattr(self.client, flag, True)
                with self.assertRaisesRegex(APIError, 'new-page.*not retried'):
                    self.docs.mutate_page('doc-1', {'name': 'x', 'content': 'original'})
                self.assertEqual(sum(c[0] == 'POST' for c in self.client.calls), 1)

    def test_partial_edit_and_append_preserve_fields(self):
        result = self.docs.mutate_page('doc-1', {'content': '\nnew', 'content_edit_mode': 'append'}, 'page-1')
        self.assertEqual(result['page']['content'], 'keep\nnew')
        self.assertEqual(result['page']['name'], 'Transcripts')
        result = self.docs.mutate_page('doc-1', {'name': 'Renamed'}, 'page-1')
        self.assertEqual(result['page']['content'], 'keep\nnew')
        self.assertTrue(result['verified'])
        self.client.parent['protected'] = True
        count = len(self.client.calls)
        with self.assertRaisesRegex(APIError, 'protected'):
            self.docs.mutate_page('doc-1', {'name': 'x'}, 'page-1')
        self.assertFalse(any(c[0] == 'PUT' for c in self.client.calls[count:]))

    def test_cli_and_identity_checks_without_list_dependencies(self):
        args = clickup_api.parser().parse_args(['page-create', 'doc-1', '--data-file', '/tmp/input.json'])
        self.assertEqual(args.doc_id, 'doc-1')
        class IdentityHTTP:
            def __init__(self, profile): pass
            def call(self, method, path):
                return {'user': {'id': 42}} if path == '/user' else {'teams': [{'id': 7}]}
        profile = dict(self.client.profile, provider='clickup', transport='api', tasks='999')
        with patch.object(clickup_api, 'Transport', IdentityHTTP):
            self.assertEqual(clickup_api.Client(profile, docs=True).lists, {})
            with self.assertRaisesRegex(APIError, 'account mismatch'):
                clickup_api.Client(dict(profile, account='43'), docs=True)

    def test_doc_creation_reports_visibility_gap(self):
        doc = dict(self.client.doc, public=False, parent={'id': '7', 'type': 12})
        with patch.object(self.docs, 'call', return_value=doc) as call:
            result = self.docs.create_doc({'name': 'Documentazione', 'visibility': 'PRIVATE', 'parent': {'id': '7', 'type': 12}})
            self.assertFalse(result['verified'])
            self.assertEqual([c.args[0] for c in call.call_args_list], ['POST', 'GET'])
            self.assertEqual(result['document']['id'], 'doc-1')
        with self.assertRaisesRegex(APIError, 'workspace mismatch'):
            self.docs.create_doc({'name': 'x', 'visibility': 'PRIVATE', 'parent': {'id': '8', 'type': 12}})
        self.assertEqual(self.client.calls, [])

    def test_cli_transcript_copy_through_http_boundary(self):
        import contextlib
        import io
        import tempfile
        from urllib import request
        fixture = self.client
        class Response(io.BytesIO):
            def getcode(self): return 200
        class Opener:
            def open(self, req, timeout):
                path = req.full_url.split('api.clickup.com', 1)[1]
                if path == '/api/v2/user':
                    value = {'user': {'id': 42}}
                elif path == '/api/v2/team':
                    value = {'teams': [{'id': 7}]}
                else:
                    self_path = path.removeprefix('/api/v3')
                    body = json.loads(req.data) if req.data else None
                    value = fixture.call(req.method, self_path, body)
                return Response(json.dumps(value).encode())
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / 'knowledge.toml'
            config.write_text('version = 1\ndefault_profile = "test"\n[profiles.test]\nprovider = "clickup"\nconnection = "api-test"\naccount = "42"\nworkspace_id = "7"\ntransport = "api"\ntoken_env = "DOCS_TEST_TOKEN"\n')
            payload = root / 'page.json'
            payload.write_text(json.dumps({'name': 'Meeting', 'parent_page_id': 'page-1', 'content': 'Verbatim è\n', 'content_format': 'text/plain'}))
            argv = ['clickup_api.py', '--config', str(config), 'page-create', 'doc-1', '--data-file', str(payload)]
            out = io.StringIO()
            with patch.dict('os.environ', {'DOCS_TEST_TOKEN': 'synthetic-only'}), patch.object(request, 'build_opener', return_value=Opener()), patch.object(sys, 'argv', argv), contextlib.redirect_stdout(out):
                code = clickup_api.main()
            self.assertEqual(code, 0)
            result = json.loads(out.getvalue())
            self.assertTrue(result['verified'])
            self.assertEqual(result['page']['content'], 'Verbatim è\n')
            self.assertEqual(result['workspace_id'], '7')

    def test_transport_v3_arrays_empty_and_v2_compatibility(self):
        class Response:
            def __init__(self, raw): self.raw = raw
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def getcode(self): return 200
            def read(self, limit): return self.raw
        class Opener:
            raw = b'[]'
            def open(self, req, timeout):
                self.url = req.full_url
                return Response(self.raw)
        http = Transport.__new__(Transport)
        http.authorization = 'synthetic'
        http.opener = Opener()
        self.assertEqual(http.call('GET', '/workspaces/7/docs/doc-1/page_listing', version='v3', response_type=list), [])
        self.assertIn('/api/v3/', http.opener.url)
        with self.assertRaises(APIError): http.call('GET', '/user')
        http.opener.raw = b'{}'
        self.assertEqual(http.call('GET', '/user'), {})
        self.assertTrue(http.opener.url.endswith('/api/v2/user'))
        http.opener.raw = b''
        self.assertEqual(http.call('PUT', '/workspaces/7/docs/doc-1/pages/p1', version='v3', allow_empty=True), {})
        with self.assertRaises(APIError): http.call('GET', '/user')


if __name__ == '__main__':
    unittest.main()
