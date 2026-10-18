import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import haiku_judge
import route_judge

NOTEBOOK = ('<section id="where-we-stand"><p>The conjecture is open.</p></section>'
            '<section id="open-statements"><ol><li>core open</li></ol></section>'
            '<section id="proposed-next-step"><p>Build the restoring-drift flow and test its tails.</p></section>'
            '<article id="r" data-kind="review"><h4>Obstacle</h4><p>No construction has the drift.</p><h4>A</h4>'
            '<p><strong>Decision.</strong> The next entry builds the restoring-drift flow.</p></article>')
DRAFT = ('<article id="e" data-kind="research"><h3>One more exclusion</h3>'
         '<p><strong>Question.</strong> Does a further class of flows fail?</p>'
         '<p><strong>Shortest route.</strong> SAID</p></article>')


def asker(verdict):
    def ask(prompt, timeout):
        ask.prompt = prompt
        return {'verdict': verdict, 'shortest': 'build the restoring-drift flow', 'reason': 'it excludes instead'}
    return ask


class RouteJudgeTest(unittest.TestCase):
    def test_a_draft_without_a_shortest_route_paragraph_is_refused_without_asking(self):
        def never(prompt, timeout):
            raise AssertionError('the judge was asked')
        reason = route_judge.refusal(DRAFT.replace('<p><strong>Shortest route.</strong> SAID</p>', ''), NOTEBOOK,
                                     never, io.StringIO())
        self.assertIn('Shortest route', reason)

    def test_a_detour_is_refused_unless_the_paragraph_says_not_taken_with_a_reason(self):
        said = 'The restoring-drift construction is the most direct step; this entry excludes another class.'
        reason = route_judge.refusal(DRAFT.replace('SAID', said), NOTEBOOK, asker('detour'), io.StringIO(), every=1)
        self.assertIn('detour', reason)
        taken = said + ' Not taken because its lemma is needed first by the construction itself.'
        self.assertIsNone(route_judge.refusal(DRAFT.replace('SAID', taken), NOTEBOOK, asker('detour'),
                                              io.StringIO(), every=1))
        # 18 October 2026: "Not taken." opening a sentence of reasons was refused while "Not taken:" passed.
        stopped = 'Not taken. The direct route is the ramp, which the next entry builds before any other step.'
        self.assertIsNone(route_judge.refusal(DRAFT.replace('SAID', stopped), NOTEBOOK, asker('detour'),
                                              io.StringIO(), every=1))
        bare = 'Not taken. Later.'
        self.assertIn('detour', route_judge.refusal(DRAFT.replace('SAID', said + ' ' + bare), NOTEBOOK,
                                                    asker('detour'), io.StringIO(), every=1))

    def test_the_two_research_entries_before_the_draft_reach_the_judge(self):
        # the user, 17 October 2026: "give it the last 3 entries then"
        old = ''.join(f'<article id="o{i}" data-kind="research"><h3>Entry {i}</h3>'
                      f'<p><strong>Question.</strong> Question {i}?</p></article>' for i in range(3))
        ask = asker('on-route')
        said = 'The restoring-drift construction is built and tested here, the most direct step.'
        route_judge.refusal(DRAFT.replace('SAID', said), NOTEBOOK + old, ask, io.StringIO(), every=1)
        self.assertNotIn('Entry 0', ask.prompt)
        self.assertLess(ask.prompt.index('Entry 1'), ask.prompt.index('Entry 2'))
        self.assertLess(ask.prompt.index('Entry 2'), ask.prompt.index('One more exclusion'))

    def test_the_judge_reads_every_third_research_entry_only(self):
        # the user, 17 October 2026: "Make it run once per 3 cycles"
        said = 'The restoring-drift construction is the most direct step; this entry excludes another class.'
        research = '<article id="x" data-kind="research"></article>'
        for before, judged in ((0, False), (1, False), (2, True), (3, False), (5, True)):
            with self.subTest(before=before):
                notice = io.StringIO()
                reason = route_judge.refusal(DRAFT.replace('SAID', said), NOTEBOOK + research * before,
                                             asker('detour'), notice)
                self.assertEqual(reason is not None, judged)
                if not judged:
                    self.assertIn('not run on research entry', notice.getvalue())

    def test_a_missing_shortest_route_is_refused_off_the_cadence_too(self):
        reason = route_judge.refusal(DRAFT.replace('<p><strong>Shortest route.</strong> SAID</p>', ''), NOTEBOOK,
                                     asker('on-route'), io.StringIO())
        self.assertIn('Shortest route', reason)

    def test_on_route_passes_and_the_record_reaches_the_judge(self):
        ask = asker('on-route')
        said = 'The restoring-drift construction is built and tested here, the most direct step.'
        self.assertIsNone(route_judge.refusal(DRAFT.replace('SAID', said), NOTEBOOK, ask, io.StringIO(), every=1))
        self.assertIn('restoring-drift flow', ask.prompt)
        self.assertIn('Latest review, Decision', ask.prompt)

    def test_an_outage_lets_the_append_through_with_a_notice(self):
        def down(prompt, timeout):
            raise haiku_judge.Failed('no answer within 90 s')
        notice = io.StringIO()
        said = 'The restoring-drift construction is the most direct step; this entry builds it.'
        self.assertIsNone(route_judge.refusal(DRAFT.replace('SAID', said), NOTEBOOK, down, notice, every=1))
        self.assertIn('not consulted', notice.getvalue())


class CarriedVerdictTest(unittest.TestCase):
    def test_a_stored_detour_on_an_earlier_entry_must_be_answered_by_the_next(self):
        # 18 October 2026: the judge returned "detour" five times on one entry, naming the step its own Follow-up
        # left untaken; the next entry is to meet that verdict before it is written (judge-shortest-carried).
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / 'last.json'
            quiet = io.StringIO()
            judged = DRAFT.replace('id="e"', 'id="earlier"').replace('SAID', 'Taken: one more class excluded.')
            detour = {'verdict': 'detour', 'shortest': 'build the drift flow', 'reason': 'it excludes'}
            route_judge.save_verdict(judged, detour, store, 'a.html')
            self.assertEqual(route_judge.last_verdict(store, 'a.html')['anchor'], 'earlier')
            bare = DRAFT.replace('SAID', 'The entry builds another exclusion of the same class.')
            self.assertIn('read the last judged entry (earlier',
                          route_judge.carried_refusal(bare, store, 'a.html', quiet))
            # Another notebook's entries are not held to this notebook's verdict.
            self.assertIsNone(route_judge.carried_refusal(bare, store, 'b.html', quiet))
            # "Taken" with too short a reason does not answer it; the same entry rewritten is the judge's own.
            self.assertIsNotNone(route_judge.carried_refusal(DRAFT.replace('SAID', 'Taken: yes.'), store, 'a.html', quiet))
            self.assertIsNone(route_judge.carried_refusal(bare.replace('id="e"', 'id="earlier"'), store, 'a.html', quiet))
            for said in ('Not taken: the drift flow waits for its smallest case, which this entry computes.',
                         'Taken: the drift flow is built here and its tails are tested on two sizes.'):
                with self.subTest(said=said):
                    route_judge.save_verdict(judged, detour, store, 'a.html')
                    answering = DRAFT.replace('SAID', said)
                    self.assertIsNone(route_judge.carried_refusal(answering, store, 'a.html', quiet))
                    # Checking clears nothing: a draft refused later by another check must still answer.
                    self.assertIsNotNone(route_judge.last_verdict(store, 'a.html'))
                    # A review answering in its own paragraph clears nothing either.
                    review = answering.replace('data-kind="research"', 'data-kind="review"')
                    self.assertFalse(route_judge.clear_answered(review, store, 'a.html', quiet))
                    # The appended answering entry clears it: the entry after it is not held to it again.
                    self.assertTrue(route_judge.clear_answered(answering, store, 'a.html', quiet))
                    self.assertIsNone(route_judge.last_verdict(store, 'a.html'))
                    self.assertIsNone(route_judge.carried_refusal(bare, store, 'a.html', quiet))
            # An unanswering entry, once appended, leaves the verdict stored.
            route_judge.save_verdict(judged, detour, store, 'a.html')
            self.assertFalse(route_judge.clear_answered(bare, store, 'a.html', quiet))
            self.assertIsNotNone(route_judge.last_verdict(store, 'a.html'))
            self.assertIsNone(route_judge.carried_refusal(bare, Path(tmp) / 'none.json', 'a.html', quiet))
            # A stored verdict other than a detour carries nothing.
            route_judge.save_verdict(judged, {'verdict': 'on route', 'shortest': 'x', 'reason': 'y'}, store, 'a.html')
            self.assertIsNone(route_judge.carried_refusal(bare, store, 'a.html', quiet))

    def test_a_store_that_cannot_be_written_is_reported(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            blocker = Path(tmp) / 'file'
            blocker.write_text('x')
            notice = io.StringIO()
            route_judge.save_verdict(DRAFT, {'verdict': 'detour'}, blocker / 'last.json', 'a.html', notice)
            self.assertIn('verdict not stored', notice.getvalue())

    def test_refusal_reads_no_store_unless_one_is_passed(self):
        # The store is the caller's, so a machine's stored verdict never reaches a test.
        quiet = io.StringIO()
        said = DRAFT.replace('SAID', 'The entry builds another exclusion of the same class, and more words.')
        self.assertIsNone(route_judge.refusal(said, NOTEBOOK, ask=asker('on route'), notice=quiet, every=1))


if __name__ == '__main__':
    unittest.main()
