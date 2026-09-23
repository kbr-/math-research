import copy
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from claim_attention import reconcile, decide, load, save, brief, latest, fingerprint, overview, current, STATES


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
        self.assertEqual(text.count('\n- '),8)
        self.assertIn('8 headline and 0 automatically queued',text)
        text=brief(self.data,history,limit=3)
        self.assertEqual(text.count('\n- '),3)
        self.assertIn('5 further headline items omitted',text)
        with self.assertRaises(ValueError):decide(self.data,history,'missing','dismissed','Reason')
        with self.assertRaises(ValueError):decide(self.data,history,'thm:0','dismissed','')

    def test_automatic_tools_are_grouped_after_headline_results(self):
        tool=dict(copy.deepcopy(self.data['claims'][0]),id='lem:a-tool',summary='A reusable tool')
        tool['significance']=dict(category='general_tool',novelty='unknown',publication_status='not_applicable')
        self.data['claims'].append(tool)
        history,added=reconcile(self.data,self.empty)
        self.assertEqual(sorted(added),['lem:a-tool','thm:one'])
        text=overview(self.data,history)
        self.assertLess(text.index('## Pending: headline results'),text.index('### One'))
        self.assertLess(text.index('## Pending: automatically queued'),text.index('### A tool'))
        self.assertLess(text.index('### One'),text.index('## Pending: automatically queued'))
        summary=brief(self.data,history)
        self.assertIn('1 headline and 1 automatically queued',summary)
        self.assertNotIn('lem:a-tool',summary)
        groups={i['claim']:(i['state'],i['group']) for i in current(self.data,history)['items']}
        self.assertEqual(groups,{'thm:one':('pending','headline'),'lem:a-tool':('pending','automatic')})
        # An agent's explicit flag promotes a tool to the headline group.
        history=decide(self.data,history,'lem:a-tool','pending','Broadly reusable; worth a look.')
        self.assertIn('- lem:a-tool',brief(self.data,history))

    def test_readable_layout_for_every_attention_state(self):
        history, _ = reconcile(self.data, self.empty)
        for state in STATES:
            with self.subTest(state=state):
                history = decide(self.data, history, 'thm:one', state, 'Keep the exact scope.', 'user')
                text = overview(self.data, history)
                title = 'Pending: headline results' if state == 'pending' else state.capitalize()
                self.assertIn(f'## {title}\n\n', text)
                self.assertIn('\n\n### One\n', text)
                self.assertIn('**Claim:** [thm:one](<https://example.org/proof>)\n\nA candidate\n', text)
                self.assertIn('**Significance:** `independent_result` · **Novelty:** `candidate`', text)
                self.assertIn('**Why it matters:** Potentially useful.\n\n', text)
                self.assertIn('**Decision (user):** Keep the exact scope.\n\n', text)
                self.assertIn('**Next:** Audit novelty.\n', text)

    def test_entry_separators_and_review_fallbacks_preserve_data(self):
        first = self.data['claims'][0]
        first['significance'] = None
        first['record'] = ''
        first['reviews'] = {'significance': {'state': 'pending', 'note': 'Needs review.',
                                            'next_action': 'Check the source.'}}
        second = copy.deepcopy(first)
        second.update(id='thm:PHP-field-scope', summary='Full second statement.')
        second['reviews'] = {'significance': {'state': 'pending'}}
        self.data['claims'].append(second)
        history, _ = reconcile(self.data, self.empty)
        original = copy.deepcopy((self.data, history))
        text = overview(self.data, history)
        self.assertEqual((self.data, history), original)
        self.assertEqual(text.count('\n---\n'), 1)
        self.assertIn('### PHP field scope\n', text)
        self.assertIn('**Claim:** thm:one\n', text)
        self.assertIn('**Significance:** `unassessed` · **Novelty:** `unknown`', text)
        self.assertIn('**Why it matters:** Needs review.', text)
        self.assertIn('**Why it matters:** Pending assessment.', text)
        self.assertIn('**Next:** Check the source.', text)
        self.assertEqual(text.count('**Next:**'), 1)


if __name__=='__main__':unittest.main()
