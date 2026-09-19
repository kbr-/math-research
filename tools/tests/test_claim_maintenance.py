import copy
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
TOOLS=Path(__file__).resolve().parents[1];sys.path.insert(0,str(TOOLS))
from claim_registry import import_markdown, upgrade, HEADER
from claim_reviews import make_review, Evidence, FIELDS
from claim_maintenance import maintenance


class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);(self.root/'research').mkdir()
        (self.root/'research/source.md').write_text('Precise source statement and proof.')
        self.data=upgrade(import_markdown('# Index\n\n'+HEADER+
            '| `lem:a` | A | Working proof | [Proof](source.md) |\n'))
        self.data['topic_definitions']=[{'id':'pc','title':'PC','description':'Polynomial calculus.'}]
        self.empty=copy.deepcopy(self.data);self.empty['claims']=[]

    def complete(self,data,claim,fields=FIELDS):
        if 'mathematical_status' in fields:claim['mathematical_status']='working_proof'
        if 'topics' in fields:claim['topics']=['pc']
        if 'formalization' in fields:
            claim['formalization']={'status':'not_started','scope':'Not assigned for this new result.',
                                    'references':['source.md'],'artifacts':[]}
        if 'significance' in fields:
            claim['significance']={'category':'route_specific','rationale':'Local bridge for the recorded method.',
                                  'novelty':'not_claimed','publication_status':'not_applicable',
                                  'references':['source.md'],'next_action':None}
        for field in fields:
            claim['reviews'][field]=make_review(data,claim,field,['source.md'],revision='a'*40,
                date='2026-09-19',reviewer='Test',note='Source reviewed with the recorded scope.',
                evidence=Evidence(self.root))

    def check(self,before,after,changed=()):return maintenance(before,after,self.root,changed)

    def test_new_claim_requires_every_field_but_backlog_is_not_blocked(self):
        self.assertTrue(self.check(self.data,self.data)['passed'])
        self.assertFalse(self.check(self.empty,self.data)['passed'])
        self.complete(self.data,self.data['claims'][0])
        self.assertTrue(self.check(self.empty,self.data)['passed'])

    def test_enrichment_checks_touched_field_without_requiring_backlog(self):
        before=copy.deepcopy(self.data);c=self.data['claims'][0]
        self.complete(self.data,c,['topics'])
        self.assertTrue(self.check(before,self.data)['passed'])
        c['reviews']['topics']['value_sha256']='0'*64
        self.assertFalse(self.check(before,self.data)['passed'])

    def test_changed_statement_requires_fresh_complete_dispositions(self):
        self.complete(self.data,self.data['claims'][0]);before=copy.deepcopy(self.data)
        self.data['claims'][0]['summary']='Corrected statement'
        self.assertFalse(self.check(before,self.data)['passed'])
        self.complete(self.data,self.data['claims'][0])
        self.assertTrue(self.check(before,self.data)['passed'])

    def test_formalization_update_needs_its_review(self):
        self.complete(self.data,self.data['claims'][0]);before=copy.deepcopy(self.data)
        c=self.data['claims'][0];c['formalization']['scope']='Verified special case, full claim still open.'
        self.assertFalse(self.check(before,self.data)['passed'])
        c['reviews']['formalization']=make_review(self.data,c,'formalization',['source.md'],
            revision='b'*40,date='2026-09-19',reviewer='Test',note='Scope update reviewed.',evidence=Evidence(self.root))
        self.assertTrue(self.check(before,self.data)['passed'])

    def test_correction_requires_target_status_acknowledgment(self):
        self.complete(self.data,self.data['claims'][0]);before=copy.deepcopy(self.data)
        c=copy.deepcopy(self.data['claims'][0]);c['id']='lem:correction';self.data['claims'].append(c)
        self.data['relationships']=[{'id':'fix','source':{'namespace':'current','id':c['id'],'locator':None},
            'target':{'namespace':'current','id':'lem:a','locator':None},'type':'corrects','scope':'Bound only.',
            'evidence':['source.md'],'review_status':'reviewed','review':{'note':'Corrected bound.'}}]
        self.complete(self.data,c)
        self.complete(self.data,self.data['claims'][0],['relationships'])
        self.assertFalse(self.check(before,self.data)['passed'])
        self.data['claims'][0]['reviews']['mathematical_status']['note']='Old scope remains working with the separately recorded correction.'
        self.assertTrue(self.check(before,self.data)['passed'])

    def test_pending_question_is_explicit_not_fake_completion(self):
        c=self.data['claims'][0];self.complete(self.data,c)
        c['significance']=None
        c['reviews']['significance']=make_review(self.data,c,'significance',['source.md'],
            revision='a'*40,date='2026-09-19',reviewer='Test',state='pending',
            note='Possible independent finite-field theorem; novelty not resolved.',
            next_action='Compare the stated field hypotheses with the cited theorem.',evidence=Evidence(self.root))
        self.assertTrue(self.check(self.empty,self.data)['passed'])
        self.assertEqual(self.check(self.empty,self.data)['coverage']['significance']['pending'],1)

    def test_changed_source_detected_without_index_edit(self):
        self.complete(self.data,self.data['claims'][0]);before=copy.deepcopy(self.data)
        (self.root/'research/source.md').write_text('Changed scope.')
        self.assertFalse(self.check(before,self.data,['research/source.md'])['passed'])
        self.assertTrue(self.check(before,self.data)['passed']) # old stale backlog remains reported

    def test_parallel_complete_additions_keep_the_contract(self):
        spec=importlib.util.spec_from_file_location('merge',TOOLS/'merge-formalization-appends.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        a=copy.deepcopy(self.data);b=copy.deepcopy(self.data);b['claims'][0]['id']='lem:b'
        self.complete(a,a['claims'][0]);self.complete(b,b['claims'][0])
        import json
        merged=module.merge_registry(*(json.dumps(d) for d in (self.empty,a,b)))
        if isinstance(merged,str):merged=json.loads(merged)
        self.assertTrue(self.check(self.empty,merged)['passed'])

if __name__=='__main__':unittest.main()
