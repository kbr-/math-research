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
        reason = route_judge.refusal(DRAFT.replace('SAID', said), NOTEBOOK, asker('detour'), io.StringIO())
        self.assertIn('detour', reason)
        taken = said + ' Not taken because its lemma is needed first by the construction itself.'
        self.assertIsNone(route_judge.refusal(DRAFT.replace('SAID', taken), NOTEBOOK, asker('detour'),
                                              io.StringIO()))

    def test_on_route_passes_and_the_record_reaches_the_judge(self):
        ask = asker('on-route')
        said = 'The restoring-drift construction is built and tested here, the most direct step.'
        self.assertIsNone(route_judge.refusal(DRAFT.replace('SAID', said), NOTEBOOK, ask, io.StringIO()))
        self.assertIn('restoring-drift flow', ask.prompt)
        self.assertIn('Latest review, Decision', ask.prompt)

    def test_an_outage_lets_the_append_through_with_a_notice(self):
        def down(prompt, timeout):
            raise haiku_judge.Failed('no answer within 90 s')
        notice = io.StringIO()
        said = 'The restoring-drift construction is the most direct step; this entry builds it.'
        self.assertIsNone(route_judge.refusal(DRAFT.replace('SAID', said), NOTEBOOK, down, notice))
        self.assertIn('not consulted', notice.getvalue())


if __name__ == '__main__':
    unittest.main()
