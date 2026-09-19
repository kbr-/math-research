import copy
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from claim_attention import reconcile, decide, load, save, brief, latest, fingerprint


class AttentionTest(unittest.TestCase):
    def setUp(self):
        self.data={'claims':[dict(id='thm:one',summary='A candidate',assessment='Working proof',
            record='[Source](https://example.org/proof)',mathematical_status='working_proof',
            formalization={'status':'not_started'},reviews={},
            significance=dict(category='independent_result',novelty='candidate',
                publication_status='candidate',rationale='Potentially useful.',next_action='Audit novelty.'))],
            'relationships':[]}
        self.empty={'version':1,'events':[]}

    def test_candidate_idempotence_and_decisions_survive_reload(self):
        history,added=reconcile(self.data,self.empty)
        self.assertEqual(added,['thm:one'])
        again,added=reconcile(self.data,history)
        self.assertEqual(again,history);self.assertEqual(added,[])
        for state in ('reviewed','actioned','dismissed'):
            history=decide(self.data,history,'thm:one',state,'Recorded review decision.')
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);save(root,self.data,history)
                restored=load(root)
            self.assertEqual(reconcile(self.data,restored),(history,[]))
            self.assertEqual(latest(history)['thm:one']['state'],state)
        self.assertEqual(len(history['events']),4)

    def test_correction_reopens_even_when_no_longer_a_candidate(self):
        history,_=reconcile(self.data,self.empty)
        history=decide(self.data,history,'thm:one','actioned','User informed.')
        self.data['claims'][0]['significance'].update(novelty='known',publication_status='not_applicable')
        self.data['relationships']=[dict(id='fix',type='corrects',
            source={'namespace':'historical','id':'fix'},
            target={'namespace':'current','id':'thm:one'},scope='Only one parameter range.')]
        changed,added=reconcile(self.data,history)
        self.assertEqual(added,['thm:one'])
        self.assertEqual(changed['events'][:2],history['events'])
        self.assertEqual(latest(changed)['thm:one']['state'],'pending')

    def test_dates_do_not_reopen_but_evidence_does(self):
        c=self.data['claims'][0]
        c['reviews']={'significance':{'state':'reviewed','date':'2026-09-19','evidence':[{'sha256':'a'}]}}
        before=fingerprint(self.data,c)
        c['reviews']['significance']['date']='2026-09-20'
        self.assertEqual(before,fingerprint(self.data,c))
        c['reviews']['significance']['evidence'][0]['sha256']='b'
        self.assertNotEqual(before,fingerprint(self.data,c))

    def test_unknown_can_be_flagged_without_inventing_novelty(self):
        c=self.data['claims'][0]
        c['significance']=None;c['reviews']={'significance':{'state':'pending'}}
        self.assertEqual(reconcile(self.data,self.empty)[1],['thm:one'])
        c['significance']={'category':'route_specific','novelty':'not_claimed','publication_status':'not_applicable'}
        c['reviews']={}
        self.assertEqual(reconcile(self.data,self.empty)[1],[])
        history=decide(self.data,self.empty,'thm:one','pending','Unexpected obstacle needs attention.')
        self.assertEqual(latest(history)['thm:one']['state'],'pending')

    def test_bounded_resume_and_bad_decisions(self):
        self.data['claims']=[dict(copy.deepcopy(self.data['claims'][0]),id=f'thm:{i}') for i in range(8)]
        history,_=reconcile(self.data,self.empty)
        text=brief(self.data,history)
        self.assertEqual(text.count('\n- '),3)
        self.assertIn('5 further items omitted',text)
        with self.assertRaises(ValueError):decide(self.data,history,'missing','dismissed','Reason')
        with self.assertRaises(ValueError):decide(self.data,history,'thm:0','dismissed','')


if __name__=='__main__':unittest.main()
