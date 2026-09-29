"""review-followups.py lists exactly the open passed bridges and leads the finisher will demand."""
import importlib.util
from pathlib import Path
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location('review_followups', TOOLS / 'review-followups.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def review(ident, route, leads, bridges, extra=''):
    li = lambda outcome: f'<li>item. <strong>Answers.</strong> x. <strong>Test.</strong> {outcome}.</li>'
    return (f'<article id="{ident}" data-kind="review" data-route="{route}">'
            '<h4>Outside leads</h4><ul>' + ''.join(li(o) for o in leads) + '</ul>'
            '<h4>Absurd bridges</h4><ul>' + ''.join(li(o) for o in bridges) + '</ul>' + extra + '</article>')


def notebook(*articles):
    return '<section id="research-record"><h2>R</h2>' + ''.join(articles) + '</section>'


CLOSE = ('<h4>Lead follow-up</h4><ul><li data-lead="r1:2">Tried. <strong>Follow-up.</strong> Closed: no.</li></ul>')


class ReviewFollowupsTests(unittest.TestCase):
    def test_lists_open_passed_items_of_the_route_only(self):
        body = notebook(review('r1', 'x', ['Passed', 'Passed', 'Falsified'], ['Not run: no', 'Passed']),
                        review('r2', 'x', ['Passed', 'Falsified', 'Falsified'], ['Falsified', 'Falsified'], CLOSE),
                        review('q1', 'y', ['Passed', 'Passed', 'Passed'], ['Passed', 'Passed']))
        html = tool.followups(body, 'x')
        self.assertIn('<li data-bridge="r1:2">No new work', html)
        self.assertIn('<li data-lead="r1:1">', html)
        self.assertIn('<li data-lead="r2:1">', html)
        self.assertNotIn('data-bridge="r1:1"', html)  # not run
        self.assertNotIn('data-lead="r1:2"', html)   # closed by r2
        self.assertNotIn('q1', html)                 # another route
        self.assertLess(html.index('Bridge follow-up'), html.index('Lead follow-up'))

    def test_notes_replace_the_default_and_are_checked(self):
        body = notebook(review('r1', 'x', ['Passed', 'Falsified', 'Falsified'], ['Falsified', 'Falsified']))
        note = 'Developed here. <strong>Follow-up.</strong> Developed.'
        self.assertIn(f'<li data-lead="r1:1">{note}</li>', tool.followups(body, 'x', {'lead:r1:1': note}))
        with self.assertRaisesRegex(ValueError, 'lacks'):
            tool.followups(body, 'x', {'lead:r1:1': 'no outcome'})
        with self.assertRaisesRegex(ValueError, 'not open'):
            tool.followups(body, 'x', {'bridge:r1:1': note})

    def test_nothing_open_prints_nothing(self):
        self.assertEqual(tool.followups(notebook(), 'x'), '')


if __name__ == '__main__':
    unittest.main()
