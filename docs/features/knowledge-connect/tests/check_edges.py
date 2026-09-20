"""Supporting CLI edge regressions, separate from frozen acceptance."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location("acceptance_edge", ROOT / "docs/features/knowledge-connect/proof/test_acceptance.py")
edge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(edge)


class Edges(edge.Proof):
    def test_workspace_mismatch_before_sources(self):
        self.special = lambda m,r,b: {'object':'user','id':edge.BOT,'type':'bot','bot':{'workspace_id':edge.OTHER}} if r == '/users/me' else None
        self.invoke('check',success=False)
        self.assertEqual([r for _,r,_ in self.calls], ['/users/me'])

    def test_incomplete_query_never_returns_complete(self):
        self.special = lambda m,r,b: {'object':'list','results':[],'has_more':False,'next_cursor':None,'request_status':{'type':'incomplete','incomplete_reason':'query_result_limit_reached'}} if r.endswith('/query') else None
        self.invoke('list','tasks',success=False)

    def test_malformed_readback_retains_known_id(self):
        self.special = lambda m,r,b: {**self.page, 'properties':{'Name':{'type':'title','title':[{'text':None}]}}} if r == '/pages/'+edge.PAGE and m == 'GET' else None
        _,_,text = self.invoke('create','tasks','--data-file',self.payload({'Name':'Wanted'}),success=False)
        self.assertIn(edge.PAGE,text)
        self.assertEqual(sum(m=='POST' and r=='/pages' for m,r,b in self.calls),1)

    def test_empty_option_is_not_verified_as_null(self):
        self.special = lambda m,r,b: {**self.page, 'properties':{**self.page['properties'],'Status':{'type':'status','status':{}}}} if r == '/pages/'+edge.PAGE and m == 'GET' else None
        _,_,text = self.invoke('create','tasks','--data-file',self.payload({'Name':'Wanted','Status':None}),success=False)
        self.assertIn(edge.PAGE,text)

    def test_discover_requires_no_configuration(self):
        self.config.unlink()
        _,result,_ = self.invoke('discover','--token-env','KNOWLEDGE_PROOF_TOKEN')
        self.assertEqual(result, {'account':edge.BOT,'workspace_id':edge.WS})
        self.assertEqual([r for _,r,_ in self.calls], ['/users/me'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
