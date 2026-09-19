import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import fossick
from claim_attention import sync, decide, save


class FossickTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        subprocess.run(['git','init','-q'],cwd=self.root,check=True)
        subprocess.run(['git','-c','user.name=Test','-c','user.email=test@example.invalid','commit','--allow-empty','-qm','Base'],cwd=self.root,check=True)
        self.data={'claims':[],'relationships':[]}
        self.rows=[dict(id=f'entry-{i}',fingerprint=str(i)*64,source_sha256=str(i)*64,
            normalization='test',claims=[],title='Fixture',status='Context',preview='No mathematics.') for i in range(1,4)]
        self.mock=patch.object(fossick,'inventory',side_effect=lambda root:(self.data,copy.deepcopy(self.rows)))
        self.mock.start();self.addCleanup(self.mock.stop)
        self.serial=0

    def output(self):
        self.serial+=1;return self.root/f'report-{self.serial}.json'

    def assessed(self,b):
        for row in b['items']:
            row.update(disposition='no_candidate',note='Software-only fixture; no result to register.')
        return b

    def test_twice_and_append_only_suffix(self):
        b,_=fossick.prepare(self.root)
        fossick.complete(self.root,self.assessed(b),self.output())
        s=fossick.read_state(self.root)
        self.assertEqual(s['ended_at'],'entry-3')
        repeat,_=fossick.prepare(self.root)
        self.assertEqual(repeat['items'],[]);self.assertEqual(repeat['remaining'],0)
        self.rows.append(dict(self.rows[0],id='entry-4'))
        nxt,_=fossick.prepare(self.root)
        self.assertEqual([r['id'] for r in nxt['items']],['entry-4'])

    def test_partial_completion_retry_and_stale_writer(self):
        b,_=fossick.prepare(self.root)
        self.assertIsNone(fossick.read_state(self.root)['ended_at'])
        stale=copy.deepcopy(b)
        b['items'][0].update(disposition='no_candidate',note='Operational fixture.')
        report=fossick.complete(self.root,b,self.output())
        self.assertEqual(report['ended_at'],'entry-1')
        before=fossick.read_state(self.root)
        self.assertEqual(fossick.complete(self.root,b,self.output()),report)
        self.assertEqual(fossick.read_state(self.root),before)
        with self.assertRaises(ValueError):fossick.complete(self.root,self.assessed(stale),self.output())
        rest,_=fossick.prepare(self.root)
        self.assertEqual([r['id'] for r in rest['items']],['entry-2','entry-3'])
        fossick.complete(self.root,self.assessed(rest),self.output())
        self.assertEqual(fossick.read_state(self.root)['ended_at'],'entry-3')

    def test_changed_old_item_and_inserted_item(self):
        b,_=fossick.prepare(self.root);fossick.complete(self.root,self.assessed(b),self.output())
        self.rows[0]['fingerprint']='f'*64
        self.rows.insert(1,dict(self.rows[0],id='entry-inserted'))
        nxt,_=fossick.prepare(self.root)
        self.assertEqual([r['id'] for r in nxt['items']],['entry-1','entry-inserted'])
        self.assertEqual(nxt['revisits'],1);self.assertIsNone(nxt['ended_at'])

    def test_missing_and_changed_active_input_fail(self):
        b,_=fossick.prepare(self.root)
        self.rows[0]['fingerprint']='f'*64
        with self.assertRaises(ValueError):fossick.complete(self.root,self.assessed(b),self.output())
        self.assertIsNone(fossick.read_state(self.root)['ended_at'])
        self.rows.pop()
        with self.assertRaises(ValueError):fossick.prepare(self.root)

    def test_candidate_and_negative_result_handoff(self):
        c=dict(id='obs:negative',summary='Counterexample',assessment='Scoped refutation',record='[Proof](https://example.org)',
            mathematical_status='refutation',formalization={},reviews={},
            significance=dict(category='negative_result',novelty='unknown',publication_status='not_applicable',rationale='General obstruction.',next_action='Audit prior art.'))
        self.data['claims']=[c];self.rows=self.rows[:1];self.rows[0]['claims']=[c['id']]
        b,_=fossick.prepare(self.root);b['items'][0].update(disposition='candidate_linked',note='Scope warrants an audit.',attention=[c['id']])
        with self.assertRaises(ValueError):fossick.complete(self.root,b,self.output())
        h,_=sync(self.root,self.data)
        fossick.complete(self.root,b,self.output())
        h=decide(self.data,h,c['id'],'reviewed','Awaiting expert comparison.');save(self.root,self.data,h)
        c['assessment']='Correction narrows the scope';self.rows[0]['fingerprint']='f'*64
        h,added=sync(self.root,self.data)
        self.assertEqual(added,[c['id']]);self.assertEqual(h['events'][-1]['state'],'pending')
        self.assertEqual(fossick.prepare(self.root)[0]['revisits'],1)

    def test_divergent_branch_does_not_reset_progress(self):
        fossick.prepare(self.root)
        subprocess.run(['git','checkout','--orphan','other','-q'],cwd=self.root,check=True)
        subprocess.run(['git','-c','user.name=Test','-c','user.email=test@example.invalid','commit','--allow-empty','-qm','Other'],cwd=self.root,check=True)
        with self.assertRaises(ValueError):fossick.prepare(self.root)

    def test_resume_summary_never_runs_a_scan(self):
        with patch.object(fossick,'inventory',side_effect=AssertionError('Resume must not scan')):
            self.assertEqual(fossick.brief(self.root),'Fossick: not started.\n')
        fossick.prepare(self.root)
        with patch.object(fossick,'inventory',side_effect=AssertionError('Resume must not scan')):
            self.assertIn('3 pending',fossick.brief(self.root))

    def test_independent_candidate_requires_explicit_attention(self):
        c=dict(id='thm:positive',summary='Candidate theorem',assessment='Working proof',record='[Proof](https://example.org)',
            mathematical_status='working_proof',formalization={},reviews={},
            significance=dict(category='independent_result',novelty='candidate',publication_status='candidate',rationale='Potential benchmark.',next_action='Expert audit.'))
        self.data['claims']=[c];self.rows=self.rows[:1];self.rows[0]['claims']=[c['id']]
        b,_=fossick.prepare(self.root);b['items'][0].update(disposition='candidate_linked',note='Potential benchmark, not certified novel.',attention=[c['id']])
        with self.assertRaises(ValueError):fossick.complete(self.root,b,self.output())
        sync(self.root,self.data)
        fossick.complete(self.root,b,self.output())
        self.assertEqual(fossick.prepare(self.root)[0]['remaining'],0)


class RealInventoryTest(unittest.TestCase):
    def test_normalized_decoration_and_relationship_changes(self):
        from claim_registry import upgrade,import_markdown,HEADER
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'research/claims').mkdir(parents=True)
            data=upgrade(import_markdown('# Index\n\n'+HEADER+'| `obs:a` | A | Working | [Proof](../notebook.html#entry-a) |\n'))
            path=root/'research/claims/index.json';path.write_text(json.dumps(data))
            book=root/'notebook.html'
            base='<section id="research-record"><article id="entry-a"><h3>Fixture</h3><p class="entry-meta">Working.</p><!-- TIMING test --></article></section>'
            book.write_text(base);_,rows=fossick.inventory(root)
            book.write_text(base.replace('<!-- TIMING test -->','<div data-generated="finish-turn-timing-v1" class="timing-report" data-session="test">Timing</div>'))
            self.assertEqual(rows[0]['fingerprint'],fossick.inventory(root)[1][0]['fingerprint'])
            book.write_text(base.replace('Working.','Corrected.'))
            self.assertNotEqual(rows[0]['fingerprint'],fossick.inventory(root)[1][0]['fingerprint'])
            book.write_text(base)
            data['relationships']=[dict(id='dep',type='depends_on',source=dict(namespace='current',id='obs:a',locator=None),
                target=dict(namespace='external',id='external:fixture',locator='https://example.org/theorem'),
                evidence=['https://example.org/theorem'],review_status='unreviewed',scope='Fixture dependency.',review=None)]
            path.write_text(json.dumps(data))
            self.assertNotEqual(rows[0]['fingerprint'],fossick.inventory(root)[1][0]['fingerprint'])
            from resume import bundle, FILES
            for name in FILES:
                f=root/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text('Fixture rules.\n')
            fossick.save_state(root,fossick.read_state(root))
            before=(root/fossick.STATE).read_bytes()
            with patch.object(fossick,'inventory',side_effect=AssertionError('Resume must not scan')):
                self.assertTrue(any(label=='Fossick progress' and body=='Fossick: not started.\n'
                                    for label,body,_,_ in bundle(root)))
            self.assertEqual((root/fossick.STATE).read_bytes(),before)


if __name__=='__main__':unittest.main()
