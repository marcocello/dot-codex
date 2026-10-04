#!/usr/bin/env python3
"""Independent acceptance: only activate the public CLI in fresh processes."""
import concurrent.futures
from datetime import datetime, timedelta
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[4]
CLI = REPO / 'scripts' / 'secondbrain.py'
T0 = '2031-01-01T10:00:00Z'
T1 = '2031-01-01T11:00:00Z'
T2 = '2031-01-01T12:00:00Z'

class CycleAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='secondbrain-acceptance-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'private-state'

    def call(self, command, payload=None, *, ok=True, raw=None, file_input=False):
        args = [sys.executable, str(CLI), '--root', str(self.root), command]
        text = raw if raw is not None else (json.dumps(payload) if payload is not None else None)
        if file_input:
            file = Path(self.temp.name) / 'input.json'
            file.write_text(text, encoding='utf-8')
            args += ['--input', str(file)]
            text = None
        proc = subprocess.run(args, input=text, text=True, capture_output=True, timeout=12)
        try:
            result = json.loads(proc.stdout)
        except Exception:
            self.fail(f'{command}: expected a JSON object, exit={proc.returncode}, stdout={proc.stdout!r}, stderr={proc.stderr!r}')
        self.assertIsInstance(result, dict)
        self.assertIs(result.get('ok'), ok, (command, result, proc.stderr))
        self.assertEqual(proc.returncode == 0, ok, (command, result))
        if not ok:
            self.assertIsInstance(result.get('error'), str)
            self.assertTrue(result['error'])
        return result

    def boot(self):
        self.call('init')
        self.call('source-put', {'id':'wa', 'provider':'whatsapp', 'scope':'synthetic-account/chat-1'})

    def event(self, id='m1', revision='1', **extra):
        return {'id':id, 'revision':revision, 'occurred_at':T0, 'kind':'message',
                'ref':f'synthetic://chat-1/{id}', 'content':{'text':'Can you confirm dinner?'}, **extra}

    def ingest(self, events, expected=None, cursor='c1', **kwargs):
        return self.call('ingest', {'source_id':'wa','expected_cursor':expected,'cursor':cursor,'events':events}, **kwargs)

    def pending(self):
        return self.call('pending')['events']

    def agenda(self, id='invitation', version=0, evidence=None, state='waiting', next_check=T1, **extra):
        return {'id':id,'expected_version':version,'outcome':'Resolve the invitation',
                'state':state,'next_check_at':next_check,'evidence':evidence or [],
                'reason':'A request is waiting for a response', **extra}

    def context(self):
        return self.call('context')

    def prepare_agenda(self):
        self.boot()
        self.ingest([self.event()])
        seq = self.pending()[0]['seq']
        self.call('apply', {'event_seqs':[seq], 'facts':[{'id':'invite','expected_version':0,'text':'An invitation is pending','evidence':[seq]}],
                            'agenda':[self.agenda(evidence=[seq])]})
        return seq

    def start(self, id='reply-1', checked=None, version=1, **kwargs):
        return self.call('action-start', {'id':id,'agenda_id':'invitation','expected_version':version,
                         'kind':'draft','target':'synthetic://chat-1','authorization':'Fixture permits local drafting only',
                         'checked_event_seqs':checked or []}, **kwargs)

    def test_first_use_explicit_root_and_preservation(self):
        self.call('context', ok=False)
        self.assertFalse((self.root/'secondbrain.sqlite3').exists())
        self.call('init')
        self.assertTrue((self.root/'secondbrain.sqlite3').is_file())
        for name in ['profile.md','priorities.md','rules.md']:
            self.assertTrue((self.root/name).is_file())
        (self.root/'profile.md').write_text('User-authored profile: do not replace.', encoding='utf-8')
        self.call('init')
        result = self.context()
        self.assertEqual(result['documents']['profile'], 'User-authored profile: do not replace.')
        for key in ['facts','agenda','actions','sources']:
            self.assertEqual(result[key], [])
        self.call('not-a-command', ok=False)
        self.call('source-put', raw='{broken', ok=False)

    def test_durable_journey_due_resolution_and_irrelevant_evidence(self):
        seq = self.prepare_agenda()
        context = self.context()
        self.assertEqual(context['facts'][0]['evidence'], [seq])
        self.assertEqual(context['agenda'][0]['version'], 1)
        self.assertEqual(self.pending(), [])
        self.assertEqual(self.call('sources')['sources'][0]['cursor'], 'c1')
        self.assertEqual(self.call('due', {'now':T0}, file_input=True)['agenda'], [])
        self.assertEqual([x['id'] for x in self.call('due', {'now':T1}, file_input=True)['agenda']], ['invitation'])
        self.ingest([self.event('m2', kind='outbound', content={'text':'Confirmed, see you there.'}), self.event('m3',content={'text':'Thanks!'})], 'c1', 'c2')
        seqs = [x['seq'] for x in self.pending()]
        self.call('apply', {'event_seqs':seqs, 'facts':[{'id':'invite','expected_version':1,'text':'Invitation resolved','evidence':seqs,'state':'superseded'}],
                            'agenda':[self.agenda(version=1,evidence=[seq]+seqs,state='done',next_check=None)]})
        self.assertEqual(self.pending(), [])
        self.assertEqual(self.call('due', {'now':T2}, file_input=True)['agenda'], [])
        self.assertEqual(self.context()['facts'][0]['state'], 'superseded')
        events = self.call('events', {'seqs':[seq]}, file_input=True)['events']
        self.assertEqual(events[0]['content']['text'], 'Can you confirm dinner?')
        self.assertEqual(self.context()['agenda'][0]['version'], 2)

    def test_replays_revisions_empty_pages_and_atomic_cursors(self):
        self.boot()
        event = self.event()
        self.ingest([event])
        first_seq = self.pending()[0]['seq']
        self.ingest([event], 'c1', 'c2')
        self.assertEqual([x['seq'] for x in self.pending()], [first_seq])
        self.ingest([self.event(revision='2', content={'text':'Dinner moved to 8'})], 'c2', 'c3')
        self.assertEqual(len(self.pending()), 2)
        self.ingest([], 'c3', 'c4')
        before = self.pending()
        self.ingest([self.event('new'), self.event('invalid', occurred_at='2031-01-01T10:00:00')], 'c4','bad',ok=False)
        self.assertEqual(self.pending(), before)
        self.assertEqual(self.call('sources')['sources'][0]['cursor'], 'c4')
        self.ingest([self.event('new')], 'obsolete','bad',ok=False)
        self.ingest([self.event(content={'text':'CONFLICT_PRIVATE_SENTINEL'})], 'c4','bad',ok=False)
        self.assertEqual(self.pending(), before)
        self.assertEqual(self.call('sources')['sources'][0]['cursor'], 'c4')
        self.call('source-put', {'id':'wa','provider':'other','scope':'synthetic-account/chat-1'},ok=False)
        self.call('source-put', {'id':'wa','provider':'whatsapp','scope':'different-account'},ok=False)
        self.call('source-put', {'id':'wa','provider':'whatsapp','scope':'synthetic-account/chat-1','enabled':False})
        self.ingest([], 'c4','bad',ok=False)
        self.assertFalse(self.call('sources')['sources'][0]['enabled'])
        self.call('source-put', {'id':'wa','provider':'whatsapp','scope':'synthetic-account/chat-1','enabled':True})
        self.ingest([self.event('new',occurred_at='2031-01-01T12:00:00+02:00')], 'c4','c5')
        latest = self.pending()[-1]
        normalized = datetime.fromisoformat(latest['occurred_at'].replace('Z', '+00:00'))
        self.assertEqual(normalized.utcoffset(), timedelta(0))
        self.assertEqual(normalized, datetime.fromisoformat('2031-01-01T10:00:00+00:00'))
        self.assertEqual(len(self.call('pending', {'limit':1}, file_input=True)['events']),1)
        self.call('pending', {'limit':0}, file_input=True,ok=False)

    def test_apply_atomic_versions_and_evidence(self):
        self.boot()
        self.ingest([self.event()])
        seq = self.pending()[0]['seq']
        fact = {'id':'fact','expected_version':0,'text':'Sourced fact','evidence':[seq]}
        invalid = self.agenda(evidence=[999999])
        self.call('apply', {'event_seqs':[seq], 'facts':[fact], 'agenda':[invalid]},ok=False)
        self.assertEqual(self.context()['facts'], [])
        self.assertEqual(self.context()['agenda'], [])
        self.assertEqual([x['seq'] for x in self.pending()], [seq])
        self.call('apply', {'event_seqs':[seq], 'facts':[fact], 'agenda':[self.agenda(evidence=[seq])]})
        self.call('apply', {'event_seqs':[seq], 'facts':[], 'agenda':[]},ok=False)
        self.call('agenda-put', {'agenda':[self.agenda(version=0)]},ok=False)
        self.call('agenda-put', {'agenda':[self.agenda('second'),self.agenda(version=0)]},ok=False)
        self.assertEqual([x['id'] for x in self.context()['agenda']], ['invitation'])
        self.ingest([self.event('ignored')], 'c1','c2')
        seq2 = self.pending()[0]['seq']
        self.call('apply', {'event_seqs':[seq2], 'facts':[{**fact,'expected_version':0}], 'agenda':[]},ok=False)
        self.assertEqual([x['seq'] for x in self.pending()], [seq2])
        self.call('apply', {'event_seqs':[seq2], 'facts':[], 'agenda':[]})
        self.assertEqual(self.pending(), [])

    def test_goals_states_and_due_order(self):
        self.call('init')
        self.call('agenda-put', {'agenda':[self.agenda('goal-b',next_check=T1,reason='User priority: prepare career portfolio'),
                                            self.agenda('goal-a',next_check=T1),self.agenda('later',next_check=T2),
                                            self.agenda('ask',state='needs_input',next_check=None),
                                            self.agenda('done',state='done',next_check=None)]})
        self.assertEqual([x['id'] for x in self.call('due',{'now':T1},file_input=True)['agenda']],['goal-a','goal-b'])
        for item in [self.agenda('bad-open',next_check=None),self.agenda('bad-done',state='done'),
                     self.agenda('bad-state',state='invented'),self.agenda('bad-time',next_check='2031-01-01'),
                     self.agenda('bad-reason',reason='')]:
            self.call('agenda-put', {'agenda':[item]},ok=False)
        self.assertEqual(len(self.context()['agenda']),5)
        self.assertEqual(self.call('events')['events'],[])

    def test_freshness_action_claim_and_uncertain_reconciliation(self):
        seq = self.prepare_agenda()
        self.start(checked=[],ok=False)
        self.ingest([self.event(revision='2',content={'text':'Actually cancel the invitation'})], 'c1','c2')
        latest = self.pending()[0]['seq']
        self.start(checked=[seq],ok=False)
        self.start(checked=[latest],version=0,ok=False)
        action = self.start(checked=[latest])['action']
        self.assertEqual(action['state'],'started')
        self.start(checked=[latest],ok=False)
        self.start('other',checked=[latest],ok=False)
        self.call('agenda-put',{'agenda':[self.agenda(version=1,state='done',next_check=None)]},ok=False)
        self.call('action-finish',{'id':'reply-1','state':'uncertain','receipt':'Synthetic provider timed out after acceptance'})
        self.assertEqual(self.context()['actions'][0]['state'],'uncertain')
        self.start('retry',checked=[latest],ok=False)
        self.call('action-finish',{'id':'reply-1','state':'uncertain','receipt':'Synthetic provider timed out after acceptance'})
        self.call('action-finish',{'id':'reply-1','state':'succeeded','receipt':'Reconciled synthetic receipt: remote id 123'})
        self.call('action-finish',{'id':'reply-1','state':'succeeded','receipt':'Reconciled synthetic receipt: remote id 123'})
        self.call('action-finish',{'id':'reply-1','state':'failed','receipt':'Contradictory terminal change'},ok=False)
        self.assertEqual(self.context()['agenda'][0]['state'],'waiting')
        self.call('agenda-put',{'agenda':[self.agenda(version=1,state='done',next_check=None,evidence=[latest])]})
        self.start('after-close',checked=[latest],version=2,ok=False)

    def test_concurrent_action_and_interpretation(self):
        seq = self.prepare_agenda()
        def invoke(id):
            payload={'id':id,'agenda_id':'invitation','expected_version':1,'kind':'draft','target':'synthetic://chat-1',
                     'authorization':'Fixture local-only permission','checked_event_seqs':[seq]}
            return subprocess.run([sys.executable,str(CLI),'--root',str(self.root),'action-start'],input=json.dumps(payload),
                                  text=True,capture_output=True,timeout=12)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(invoke,['race-a','race-b']))
        self.assertEqual(sum(x.returncode==0 for x in results),1,[(x.stdout,x.stderr) for x in results])
        self.assertEqual(len(self.context()['actions']),1)
        winner=self.context()['actions'][0]['id']
        self.call('action-finish',{'id':winner,'state':'failed','receipt':'Verified synthetic no-effect result'})
        self.ingest([self.event('irrelevant')], 'c1','c2')
        event_seq=self.pending()[0]['seq']
        def apply(_):
            return subprocess.run([sys.executable,str(CLI),'--root',str(self.root),'apply'],
                                  input=json.dumps({'event_seqs':[event_seq],'facts':[],'agenda':[]}),
                                  text=True,capture_output=True,timeout=12)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(apply,range(2)))
        self.assertEqual(sum(x.returncode==0 for x in results),1,[(x.stdout,x.stderr) for x in results])
        self.assertEqual(self.pending(),[])

if __name__ == '__main__':
    unittest.main(verbosity=2)
