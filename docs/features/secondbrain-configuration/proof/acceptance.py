#!/usr/bin/env python3
"""Independent public-process acceptance for secondbrain.yaml configuration."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import yaml

REPO = Path(__file__).resolve().parents[4]
CONFIG_CLI = REPO / 'scripts/secondbrain_config.py'
STATE_CLI = REPO / 'scripts/secondbrain.py'


class ConfigurationAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='secondbrain-config-proof-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.folder = self.base/'configuration'
        self.folder.mkdir()
        self.config_path = self.folder/'secondbrain.yaml'
        self.root = self.folder/'private-workspace'
        self.caller = self.base/'different-caller'
        self.caller.mkdir()

    def fixture(self):
        return {
            'schema': 1, 'workspace': './private-workspace', 'initial_lookback_minutes': 180,
            'schedules': {'update': {'enabled':False,'every_minutes':15},
                          'review': {'enabled':False,'every_minutes':60}},
            'sources': [
                {'id':'wa','provider':'whatsapp','enabled':True,
                 'scope':{'adapter':'wacli','store':'./wa-store','chats':['synthetic@s.whatsapp.net']}},
                {'id':'repo','provider':'repos','enabled':True,'scope':{'paths':['../project-one','./project-two']}},
                {'id':'mail','provider':'gmail','enabled':False,'scope':{}},
            ],
        }

    def write(self, value=None, text=None):
        self.config_path.write_text(text if text is not None else yaml.safe_dump(value or self.fixture()),encoding='utf-8')

    def run_json(self, args, payload=None, ok=True, cwd=None):
        p=subprocess.run([sys.executable,*map(str,args)],cwd=cwd or self.caller,
                         input=json.dumps(payload) if payload is not None else None,
                         text=True,capture_output=True,timeout=15)
        try: result=json.loads(p.stdout)
        except Exception: self.fail(f'Expected JSON; exit={p.returncode}, stdout={p.stdout!r}, stderr={p.stderr!r}')
        self.assertIsInstance(result,dict)
        self.assertIs(result.get('ok'),ok,(result,p.stderr))
        self.assertEqual(p.returncode,0 if ok else 1,(result,p.stderr))
        if not ok:
            self.assertIsInstance(result.get('error'),str)
            self.assertTrue(result['error'])
            self.assertNotIn('Traceback',p.stdout+p.stderr)
            self.assertNotIn('PRIVATE_VALUE_MUST_NOT_LEAK',p.stdout+p.stderr)
        return result

    def config(self, command, ok=True, path=None, cwd=None):
        return self.run_json([CONFIG_CLI,'--config',path or self.config_path,command],ok=ok,cwd=cwd)

    def state(self,command,payload=None):
        return self.run_json([STATE_CLI,'--root',self.root,command],payload)

    def sources(self):
        return {s['id']:s for s in self.state('sources')['sources']}

    def ingest(self):
        event={'id':'message-1','revision':'v1','occurred_at':'2031-01-01T10:00:00Z',
               'kind':'message','ref':'synthetic://selected-chat/message-1','content':{'text':'Can we meet tomorrow?'}}
        self.state('ingest',{'source_id':'wa','expected_cursor':None,'cursor':'retained-page-1','events':[event]})

    def interval_minutes(self, schedule):
        rule=schedule['rrule']
        self.assertIsInstance(rule,str)
        line=next((line for line in rule.splitlines() if line.startswith('RRULE:')),rule)
        fields=dict(part.split('=',1) for part in line.removeprefix('RRULE:').split(';') if '=' in part)
        frequency=fields.get('FREQ')
        multiplier={'MINUTELY':1,'HOURLY':60,'DAILY':1440}
        self.assertIn(frequency,multiplier,'A repeating minute cadence must remain an interval, not guessed clock times')
        return int(fields.get('INTERVAL','1'))*multiplier[frequency]

    def test_missing_invalid_first_use_and_read_only_show(self):
        self.config('show',ok=False)
        self.config('sync-sources',ok=False)
        self.config('schedule-plan',ok=False)
        self.assertFalse(self.root.exists())
        self.assertEqual(sorted(p.name for p in self.folder.iterdir()),[])
        self.write(text='schema: [broken')
        self.config('sync-sources',ok=False)
        self.assertFalse(self.root.exists())
        self.write()
        shown=self.config('show')['config']
        self.assertEqual(shown['schema'],1)
        self.assertEqual(shown['config_path'],str(self.config_path.resolve()))
        self.assertEqual(shown['workspace'],str(self.root.resolve()))
        self.assertEqual(shown['initial_lookback_minutes'],180)
        self.assertFalse(self.root.exists(),'show must not initialize storage')
        plans=self.config('schedule-plan')['schedules']
        self.assertEqual(len(plans),2)
        self.assertFalse(self.root.exists(),'plan must not initialize or start anything')

    def test_path_resolution_is_config_relative_and_home_expansion(self):
        self.write()
        first=self.config('show')['config']
        second=self.config('show',cwd=REPO)['config']
        self.assertEqual(first,second)
        wa=first['sources'][0]['scope']; repos=first['sources'][1]['scope']
        self.assertEqual(wa['store'],str((self.folder/'wa-store').resolve()))
        self.assertEqual(repos['paths'],[str((self.folder/'../project-one').resolve()),str((self.folder/'project-two').resolve())])
        cfg=self.fixture(); cfg['workspace']='~/synthetic-proof-private';cfg['sources'][0]['scope']['store']='~/synthetic-proof-wacli'
        cfg['sources'][1]['scope']['paths']=['~/synthetic-proof-repo']
        self.write(cfg)
        shown=self.config('show')['config']
        self.assertEqual(shown['workspace'],str(Path('~/synthetic-proof-private').expanduser().resolve()))
        self.assertEqual(shown['sources'][0]['scope']['store'],str(Path('~/synthetic-proof-wacli').expanduser().resolve()))
        self.assertFalse(self.root.exists())

    def test_real_registry_cursor_preservation_disable_remove_reenable(self):
        self.write()
        synced=self.config('sync-sources')['sources']
        self.assertEqual({s['id'] for s in synced},{'wa','repo'})
        self.assertTrue((self.root/'secondbrain.sqlite3').is_file())
        self.ingest()
        original=self.sources()
        raw=self.state('pending')['events']
        self.config('sync-sources')
        self.assertEqual(self.sources(),original)
        self.assertEqual(self.state('pending')['events'],raw)
        cfg=self.fixture();cfg['sources'][0]['enabled']=False;cfg['sources']=[s for s in cfg['sources'] if s['id']!='repo']
        cfg['sources'].append({'id':'zotero','provider':'zotero','enabled':True,'scope':{'library':'synthetic-library'}})
        self.write(cfg);self.config('sync-sources')
        registry=self.sources()
        self.assertFalse(registry['wa']['enabled'])
        self.assertFalse(registry['repo']['enabled'])
        self.assertTrue(registry['zotero']['enabled'])
        self.assertEqual(registry['wa']['cursor'],'retained-page-1')
        self.assertEqual(self.state('pending')['events'],raw)
        cfg['sources'][0]['enabled']=True;self.write(cfg);self.config('sync-sources')
        self.assertTrue(self.sources()['wa']['enabled'])
        self.assertEqual(self.sources()['wa']['cursor'],'retained-page-1')

    def test_unconfigured_placeholders_can_be_selected_later(self):
        cfg=self.fixture()
        for source in cfg['sources']:
            source['enabled']=False
            source['scope']={}
        self.write(cfg)
        self.assertEqual(self.config('sync-sources')['sources'],[])
        self.assertEqual(self.sources(),{})
        selected=self.fixture()['sources'][0]
        cfg['sources'][0]=selected
        self.write(cfg);self.config('sync-sources');self.ingest()
        bound=self.sources()['wa']
        self.assertTrue(bound['enabled'])
        cfg['sources'][0]={'id':'wa','provider':'whatsapp','enabled':False,'scope':{}}
        self.write(cfg);self.config('sync-sources')
        disabled=self.sources()['wa']
        self.assertFalse(disabled['enabled'])
        self.assertEqual(disabled['scope'],bound['scope'])
        self.assertEqual(disabled['cursor'],'retained-page-1')
        cfg['sources'][0]=selected
        self.write(cfg);self.config('sync-sources')
        self.assertTrue(self.sources()['wa']['enabled'])
        self.assertEqual(self.sources()['wa']['cursor'],'retained-page-1')

    def test_scope_provider_conflicts_are_atomic_and_require_new_identity(self):
        self.write();self.config('sync-sources');self.ingest()
        before=self.sources();raw=self.state('pending')['events']
        for field in ['scope','provider']:
            cfg=self.fixture()
            new={'id':'added-first','provider':'clickup','enabled':True,'scope':{'workspace':'synthetic-team'}}
            conflict=copy.deepcopy(cfg['sources'][0])
            if field=='scope': conflict['scope']['chats']=['different@s.whatsapp.net']
            else: conflict.update(provider='notion',scope={'workspace':'synthetic-notion'})
            cfg['sources']=[new,conflict] # Also removes existing repo: removal must roll back too.
            self.write(cfg);self.config('sync-sources',ok=False)
            self.assertEqual(self.sources(),before)
            self.assertEqual(self.state('pending')['events'],raw)
        cfg=self.fixture();cfg['sources'][0]['id']='wa-new';cfg['sources'][0]['scope']['chats']='all'
        self.write(cfg);self.config('sync-sources')
        after=self.sources()
        self.assertFalse(after['wa']['enabled']);self.assertTrue(after['wa-new']['enabled'])
        self.assertEqual(after['wa']['cursor'],'retained-page-1')
        self.assertIsNone(after['wa-new']['cursor'])

    def test_validation_duplicate_unknown_and_unsafe_yaml(self):
        self.write();self.config('sync-sources');self.ingest();before=self.sources()
        invalid=[]
        def variant(label, mutate):
            cfg=self.fixture();mutate(cfg);invalid.append((label,yaml.safe_dump(cfg)))
        variant('unknown root',lambda c:c.update(unexpected='PRIVATE_VALUE_MUST_NOT_LEAK'))
        variant('wrong schema',lambda c:c.update(schema=2))
        variant('empty workspace',lambda c:c.update(workspace=''))
        variant('noninteger lookback',lambda c:c.update(initial_lookback_minutes=True))
        variant('zero lookback',lambda c:c.update(initial_lookback_minutes=0))
        variant('zero interval',lambda c:c['schedules']['update'].update(every_minutes=0))
        variant('bool interval',lambda c:c['schedules']['review'].update(every_minutes=True))
        variant('string enabled',lambda c:c['schedules']['update'].update(enabled='yes'))
        variant('unknown schedule',lambda c:c['schedules'].update(extra={'enabled':False,'every_minutes':1}))
        variant('unknown job key',lambda c:c['schedules']['review'].update(extra='PRIVATE_VALUE_MUST_NOT_LEAK'))
        variant('duplicate id',lambda c:c['sources'].append(copy.deepcopy(c['sources'][0])))
        variant('empty id',lambda c:c['sources'][0].update(id=''))
        variant('unknown provider',lambda c:c['sources'][0].update(provider='PRIVATE_VALUE_MUST_NOT_LEAK'))
        variant('unknown source key',lambda c:c['sources'][0].update(extra='PRIVATE_VALUE_MUST_NOT_LEAK'))
        variant('enabled empty scope',lambda c:c['sources'][0].update(scope={}))
        variant('scope not object',lambda c:c['sources'][0].update(scope='PRIVATE_VALUE_MUST_NOT_LEAK'))
        variant('wrong whatsapp adapter',lambda c:c['sources'][0]['scope'].update(adapter='whatsapp-bot'))
        variant('missing whatsapp store',lambda c:c['sources'][0]['scope'].pop('store'))
        variant('empty chats',lambda c:c['sources'][0]['scope'].update(chats=[]))
        variant('empty repos',lambda c:c['sources'][1]['scope'].update(paths=[]))
        invalid.append(('duplicate YAML key',yaml.safe_dump(self.fixture())+'workspace: PRIVATE_VALUE_MUST_NOT_LEAK\n'))
        invalid.append(('duplicate nested key',yaml.safe_dump(self.fixture()).replace('every_minutes: 15','every_minutes: 15\n    every_minutes: 16')))
        invalid.append(('unsafe tag','!!python/object/apply:os.system ["PRIVATE_VALUE_MUST_NOT_LEAK"]'))
        for label,text in invalid:
            with self.subTest(label=label):
                self.write(text=text);self.config('sync-sources',ok=False)
                self.assertEqual(self.sources(),before)

    def test_independent_native_schedule_payloads_and_scope_gate(self):
        cfg=self.fixture();self.write(cfg)
        paused=self.config('schedule-plan')['schedules']
        self.assertEqual([s['status'] for s in paused],['PAUSED','PAUSED'])
        self.assertEqual([self.interval_minutes(s) for s in paused],[15,60])
        self.assertNotEqual(paused[0]['name'],paused[1]['name'])
        cfg['schedules']['update']['enabled']=True;cfg['schedules']['review']['enabled']=True;self.write(cfg)
        active=self.config('schedule-plan')['schedules']
        self.assertEqual([s['status'] for s in active],['ACTIVE','ACTIVE'])
        self.assertEqual([s['name'] for s in active],[s['name'] for s in paused])
        for schedule,skill in zip(active,['secondbrain-update','secondbrain-review']):
            self.assertEqual(schedule['kind'],'heartbeat')
            self.assertIn(str(self.config_path.resolve()),schedule['prompt'])
            self.assertIn(skill,schedule['prompt'])
            self.assertTrue(schedule['name'])
        self.assertEqual(active,self.config('schedule-plan',cwd=REPO)['schedules'])
        cfg['schedules']['update']['every_minutes']=7;self.write(cfg)
        changed=self.config('schedule-plan')['schedules']
        self.assertEqual(self.interval_minutes(changed[0]),7)
        self.assertEqual(changed[1],active[1],'Update cadence must not change review job')
        cfg['schedules']['review']['every_minutes']=90;self.write(cfg)
        changed_again=self.config('schedule-plan')['schedules']
        self.assertEqual(self.interval_minutes(changed_again[1]),90)
        self.assertEqual(changed_again[0],changed[0])
        other_path=self.folder/'other-config.yaml';other_path.write_text(self.config_path.read_text())
        other=self.config('schedule-plan',path=other_path)['schedules']
        self.assertTrue(set(s['name'] for s in other).isdisjoint(s['name'] for s in changed_again))
        for source in cfg['sources']:source['enabled']=False
        self.write(cfg);self.config('schedule-plan',ok=False)
        for job in cfg['schedules'].values():job['enabled']=False
        self.write(cfg)
        self.assertEqual([s['status'] for s in self.config('schedule-plan')['schedules']],['PAUSED','PAUSED'])
        self.assertFalse(self.root.exists(),'No planning operation may initialize or activate runtime')

    def test_tracked_template_is_valid_paused_and_safe_to_copy(self):
        template=REPO/'secondbrain.template.yaml'
        self.assertTrue(template.is_file())
        self.config_path.write_bytes(template.read_bytes())
        normalized=self.config('show')['config']
        self.assertEqual(normalized['schema'],1)
        self.assertTrue(all(not s['enabled'] for s in normalized['sources']))
        self.assertEqual(normalized['schedules'],{'update':{'enabled':False,'every_minutes':15},'review':{'enabled':False,'every_minutes':60}})
        schedules=self.config('schedule-plan')['schedules']
        self.assertEqual([s['status'] for s in schedules],['PAUSED','PAUSED'])
        self.assertFalse(self.root.exists())
        check=subprocess.run(['git','check-ignore','--no-index','secondbrain.yaml'],cwd=REPO,text=True,capture_output=True,timeout=5)
        self.assertEqual(check.returncode,0,'Private secondbrain.yaml must be ignored')


if __name__ == '__main__':
    unittest.main(verbosity=2)
