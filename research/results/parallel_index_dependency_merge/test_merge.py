import copy,importlib.util,json,tempfile,unittest,sys
from pathlib import Path
D=Path(__file__).parent;sys.path.insert(0,str(D))
import merge as m
class MergerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=m.load();cls.man=json.loads((D/'manifest-reviewed.json').read_text());cls.rev=cls.man['input_revision']
 def run_patch(self,p):
  with tempfile.TemporaryDirectory(dir=D) as t:
   path=Path(t)/'patch.json';path.write_text(json.dumps(p))
   return m.merge(self.data,dict(self.man),[path])
 def test_normalized_identity_and_alias(self):
  e=copy.deepcopy(self.data['relationships'][0]);e['target']={'namespace':'external','id':'BIKPRS-1996-simulation','locator':'source'}
  n=m.normalized(e);self.assertEqual(n['target']['id'],'BIKPRS-audited-source-inputs');self.assertTrue(n['id'].endswith('external:BIKPRS-audited-source-inputs'));self.assertNotEqual(e['target'],n['target'])
 def test_stale_core_rejected(self):
  base=json.loads((m.R/'research/results/parallel_index_dependencies_680_end/patch_680_698.json').read_text());base['claims']=base['claims'][:1];base['relationships']=[];base['claims'][0]['source_fields_sha256']='0'*64
  _,r=self.run_patch(base);self.assertTrue(any(c['kind']=='claim_source' for c in r['conflicts']))
 def test_candidate_fingerprint_rejected(self):
  c=json.loads((m.R/self.man['candidates'][0]).read_text())['candidates'][0]
  _,r=self.run_patch({'base_revision':self.rev,'candidate_decisions':[{'candidate_id':c['id'],'candidate_sha256':'0'*64,'state':'rejected','reason':'test'}]})
  self.assertTrue(any(c['kind']=='candidate_decision' for c in r['conflicts']))
 def test_real_scope_conflict_preserves_canonical(self):
  e=copy.deepcopy(self.data['relationships'][0]);eid=m.normalized(e)['id'];old=e['scope'];e['scope']='Unsupported different proof role for safety test.'
  out,r=self.run_patch({'relationships':[e]})
  self.assertTrue(any(c['kind']=='edge_scope_collision' for c in r['conflicts']));self.assertEqual(next(a for a in out['relationships'] if a['id']==eid)['scope'],old)
 def test_canonical_deletion_refused(self):
  e=self.data['relationships'][0];out,r=self.run_patch({'remove_proposed_edge_ids':[e['id']]})
  self.assertTrue(any(c['kind']=='amendment_would_remove_canonical' for c in r['conflicts']));self.assertIn(m.normalized(e)['id'],{a['id'] for a in out['relationships']})
 def test_output_cannot_target_registry(self):
  with self.assertRaises(ValueError):m.safe_output(m.REGISTRY)
 def test_nonrelationship_fields_preserved(self):
  data=copy.deepcopy(self.data);data['claims'][0]['mathematical_status']='conditional';new=copy.deepcopy(data['claims'][0]);new['id']='test:new-root-record';data['claims'].append(new)
  out,_=m.merge(data,dict(self.man),[])
  self.assertEqual(out['claims'],data['claims']);self.assertEqual(len(out['claims']),len(data['claims']))
 def test_authorized_pending_resolution_preserves_audit(self):
  p=json.loads((m.R/'research/results/parallel_index_correction_endpoints/inventory-resolutions.json').read_text());p['claims']=[r for r in p['claims'] if r['id']=='lem:dense-labels-satisfied'];cid=p['claims'][0]['id']
  data=copy.deepcopy(self.data);c=next(c for c in data['claims'] if c['id']==cid);old=c['reviews']['relationships'];old['state']='pending';old['note']='Coordinator question for this exact integration test';old['next_action']='Merge reviewed outgoing inventory';status=c['mathematical_status']
  man=dict(self.man);man['resolve_pending_reviews']={cid:m.digest(old)}
  with tempfile.TemporaryDirectory(dir=D) as t:
   path=Path(t)/'patch.json';path.write_text(json.dumps(p));out,r=m.merge(data,man,[path])
  new=next(c for c in out['claims'] if c['id']==cid);self.assertEqual(new['mathematical_status'],status);self.assertEqual(new['reviews']['relationships']['state'],'reviewed');self.assertTrue({a['target'] for a in old['evidence']} <= {a['target'] for a in new['reviews']['relationships']['evidence']})
 def test_new_pending_question_requires_exact_authorization(self):
  p=json.loads((m.R/'research/results/parallel_index_correction_endpoints/inventory-resolutions.json').read_text());p['claims']=[r for r in p['claims'] if r['id']=='lem:dense-labels-satisfied'];cid=p['claims'][0]['id'];data=copy.deepcopy(self.data);c=next(c for c in data['claims'] if c['id']==cid);c['reviews']['relationships']['state']='pending';c['reviews']['relationships']['note']='New unrelated ownership question';c['reviews']['relationships']['next_action']='Resolve it'
  with tempfile.TemporaryDirectory(dir=D) as t:
   path=Path(t)/'patch.json';path.write_text(json.dumps(p));out,r=m.merge(data,dict(self.man),[path])
  self.assertTrue(any(a['kind']=='newer_pending_review' and a['id']==cid for a in r['conflicts']));self.assertEqual(next(c for c in out['claims'] if c['id']==cid)['reviews']['relationships']['state'],'pending')
if __name__=='__main__':unittest.main()
