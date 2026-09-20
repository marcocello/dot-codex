"""Workspace-scoped ClickUp v3 Docs operations; writes are never retried."""
from urllib.parse import urlencode

from clickup_http import APIError, identity, object_list, segment


class Docs:
    def __init__(self, client):
        self.client = client
        self.workspace = client.profile['workspace_id']
        self.base = f'/workspaces/{segment(self.workspace)}/docs'

    def call(self, method, suffix='', body=None, **options):
        return self.client.http.call(method, self.base + suffix, body, version='v3', **options)

    def scoped(self, value, doc_id=None, page_id=None):
        if not isinstance(value, dict):
            raise APIError('Malformed Docs resource')
        resource_id = identity(value)
        if str(value.get('workspace_id')) != self.workspace:
            raise APIError('Docs workspace mismatch')
        if doc_id is not None and value.get('doc_id') != doc_id:
            raise APIError('Page document mismatch')
        if page_id is not None and resource_id != page_id:
            raise APIError('Docs resource identity mismatch')
        return value

    def get_doc(self, doc_id):
        return self.scoped(self.call('GET', '/' + segment(doc_id)), page_id=doc_id)

    def search(self):
        docs, seen = {}, set()
        cursor = None
        for _ in range(1000):
            query = {'limit': 100, 'deleted': 'false'}
            if cursor is not None:
                query['cursor'] = cursor
            data = self.call('GET', '?' + urlencode(query))
            for doc in object_list(data, 'docs'):
                self.scoped(doc)
                docs[identity(doc)] = doc
            cursor = data.get('next_cursor')
            if cursor is None or cursor == '':
                return {'docs': list(docs.values()), 'complete': True,
                        'coverage': 'accessible non-deleted Docs returned by workspace search'}
            if not isinstance(cursor, str) or cursor in seen:
                raise APIError('Invalid or repeated Docs cursor; results incomplete')
            seen.add(cursor)
        raise APIError('Docs pagination limit reached; results incomplete')

    def pages(self, doc_id, *, content=False, content_format='text/md'):
        self.get_doc(doc_id)
        path = 'pages' if content else 'page_listing'
        query = {'max_page_depth': -1}
        if content:
            query['content_format'] = content_format
        pages = self.call('GET', f'/{segment(doc_id)}/{path}?' + urlencode(query), response_type=list)
        pending = list(pages)
        seen = set()
        while pending:
            page = self.scoped(pending.pop(), doc_id)
            pid = identity(page)
            if pid in seen:
                raise APIError('Duplicate page identity in Docs tree')
            seen.add(pid)
            children = page.get('pages', [])
            if not isinstance(children, list):
                raise APIError('Malformed nested page tree')
            pending.extend(children)
        return pages

    def get_page(self, doc_id, page_id, content_format='text/md'):
        self.get_doc(doc_id)
        query = urlencode({'content_format': content_format})
        return self.scoped(self.call('GET', f'/{segment(doc_id)}/pages/{segment(page_id)}?{query}'), doc_id, page_id)

    def create_doc(self, body):
        if not isinstance(body, dict) or set(body) - {'name', 'parent', 'visibility', 'create_page'}:
            raise APIError('Unsupported Doc payload')
        if not isinstance(body.get('name'), str) or not body['name'].strip():
            raise APIError('Doc creation requires a nonempty name')
        # Require an explicit visibility, avoiding the provider default.
        if body.get('visibility') not in ('PUBLIC', 'PRIVATE', 'PERSONAL', 'HIDDEN'):
            raise APIError('Doc creation requires explicit visibility')
        if 'create_page' in body and type(body['create_page']) is not bool:
            raise APIError('create_page must be boolean')
        parent = body.get('parent')
        if parent is not None:
            if (not isinstance(parent, dict) or set(parent) != {'id', 'type'}
                    or type(parent['type']) is not int or parent['type'] not in (4, 5, 6, 7, 12)):
                raise APIError('Invalid Doc parent')
            pid = segment(parent['id'])
            if parent['type'] in (7, 12):
                if pid != self.workspace:
                    raise APIError('Doc parent workspace mismatch')
            else:
                from clickup_api import spaces
                allowed = {identity(space) for archived in (False, True)
                           for space in spaces(self.client.http, self.workspace, archived=archived)}
                if parent['type'] == 4:
                    sid = pid
                else:
                    kind = 'folder' if parent['type'] == 5 else 'list'
                    meta = self.client.http.call('GET', f'/{kind}/{pid}')
                    if identity(meta) != pid:
                        raise APIError('Doc parent identity mismatch')
                    sid = str(meta.get('space', {}).get('id'))
                if sid not in allowed:
                    raise APIError('Doc parent is outside selected workspace')
        known = None
        try:
            created = self.call('POST', body=body)
            known = identity(created)
            self.scoped(created, page_id=known)
            doc = self.get_doc(known)
            if doc.get('name') != body['name'] or ('parent' in body and doc.get('parent') != parent):
                raise APIError('Doc read-back differs from requested fields')
            # The schema exposes only public, not the four-way visibility value.
            if doc.get('public') is not (body['visibility'] == 'PUBLIC'):
                raise APIError('Doc public flag differs from requested visibility')
            return {'verified': False, 'document': doc,
                    'verification_gap': 'API exposes public only; exact visibility cannot be read back'}
        except (APIError, KeyError, TypeError, ValueError) as exc:
            self.unverified('document', known, exc)

    def mutate_page(self, doc_id, body, page_id=None):
        validate_page(body, create=page_id is None)
        self.get_doc(doc_id)
        fmt = body.get('content_format', 'text/md')
        before = self.get_page(doc_id, page_id, fmt) if page_id else None
        if before and before.get('protected'):
            raise APIError('Page is protected; no edit attempted')
        parent = body.get('parent_page_id')
        if parent is not None:
            self.get_page(doc_id, parent, fmt)
        expected = {k: v for k, v in body.items() if k not in ('content_format', 'content_edit_mode')}
        if before:
            # Also verify omitted content/name/subtitle remain intact.
            for key in ('name', 'content', 'sub_title'):
                if key not in expected and key in before:
                    expected[key] = before[key]
            if 'content' in body:
                mode = body.get('content_edit_mode', 'replace')
                if mode != 'replace':
                    old = before.get('content')
                    if not isinstance(old, str):
                        raise APIError('Cannot verify append/prepend without existing content')
                    expected['content'] = old + body['content'] if mode == 'append' else body['content'] + old
            if 'parent_page_id' in before:
                expected['parent_page_id'] = before['parent_page_id']
        known = page_id
        try:
            if page_id is None:
                created = self.call('POST', f'/{segment(doc_id)}/pages', body)
                known = identity(created)
                self.scoped(created, doc_id, known)
            else:
                self.call('PUT', f'/{segment(doc_id)}/pages/{segment(page_id)}', body, allow_empty=True)
            page = self.get_page(doc_id, known, fmt)
            for key, value in expected.items():
                if page.get(key) != value:
                    raise APIError(f'Page read-back did not verify {key}')
            return {'verified': True, 'page': page}
        except (APIError, KeyError, TypeError, ValueError) as exc:
            self.unverified(f'page in Doc {doc_id}', known, exc)

    @staticmethod
    def unverified(kind, known, exc):
        detail = str(exc) if isinstance(exc, APIError) else 'Malformed provider response'
        raise APIError(f'Write unverified for {kind} {known or "(identity unknown)"}: {detail}. Inspect before retrying; not retried') from None


def validate_page(body, *, create):
    allowed = {'name', 'sub_title', 'content', 'content_format'}
    allowed.add('parent_page_id' if create else 'content_edit_mode')
    if not isinstance(body, dict) or not body or set(body) - allowed:
        raise APIError('Payload must contain only supported page fields')
    if any(not isinstance(v, str) for v in body.values()):
        raise APIError('Page fields must be strings')
    if (create or 'name' in body) and not body.get('name', '').strip():
        raise APIError('Page name must be nonempty')
    if body.get('content_format', 'text/md') not in ('text/md', 'text/plain'):
        raise APIError('Unsupported page content format')
    if body.get('content_edit_mode', 'replace') not in ('replace', 'append', 'prepend'):
        raise APIError('Unsupported page edit mode')
    if 'content_edit_mode' in body and 'content' not in body:
        raise APIError('Page edit mode requires content')
    if not set(body) & {'name', 'content', 'sub_title', 'parent_page_id'}:
        raise APIError('No page values supplied')
    if 'parent_page_id' in body:
        segment(body['parent_page_id'])


def add_commands(commands):
    for name in ('docs-search', 'doc-get', 'doc-create', 'pages-list', 'pages-get', 'page-get', 'page-create', 'page-update'):
        command = commands.add_parser(name)
        if name not in ('docs-search', 'doc-create'):
            command.add_argument('doc_id')
        if name in ('page-get', 'page-update'):
            command.add_argument('page_id')
        if name in ('pages-get', 'page-get'):
            command.add_argument('--content-format', choices=('text/md', 'text/plain'), default='text/md')
        if name in ('doc-create', 'page-create', 'page-update'):
            from pathlib import Path
            command.add_argument('--data-file', type=Path, required=True)


def execute(client, args, read_json):
    docs = Docs(client)
    name = args.command
    if name == 'docs-search':
        output = docs.search()
    elif name == 'doc-get':
        output = {'document': docs.get_doc(args.doc_id)}
    elif name == 'doc-create':
        output = docs.create_doc(read_json(args.data_file))
    elif name in ('pages-list', 'pages-get'):
        output = {'doc_id': args.doc_id, 'pages': docs.pages(args.doc_id, content=name == 'pages-get',
                  content_format=getattr(args, 'content_format', 'text/md')), 'complete': True}
    elif name == 'page-get':
        output = {'page': docs.get_page(args.doc_id, args.page_id, args.content_format)}
    else:
        output = docs.mutate_page(args.doc_id, read_json(args.data_file), getattr(args, 'page_id', None))
    return {**client.context(), **output}
