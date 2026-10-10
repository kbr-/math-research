"""notebook-append.py inserts after the last record article and replaces the next step."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location('notebook_append', TOOLS / 'notebook-append.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

NOTEBOOK = ('<section id="proposed-next-step">\n<h2>Proposed next step</h2>\n<p>old</p>\n</section>\n'
            '<section id="research-record">\n<h2>Record</h2>\n<article id="a1">one</article>\n'
            '<article id="a2">two</article>\n</section>\n<footer></footer>')

REPORTS = ('<p><strong>New mathematics.</strong> The general statement was checked with its '
           'original hypotheses.</p><p><strong>Goal progress.</strong> The required implication '
           'is still open after the completed test.</p>')
ARCHITECTURE = '<h4>Architecture review</h4>' + ''.join(
    f'<p><strong>{label}.</strong> Core: a substantive comparison of the goal, available '
    'results and their degree budgets. <a href="review.txt">Evidence</a>. '
    '<strong>Power.</strong> The recorded ceilings leave the outcomes apart at the sizes reachable. '
    '<strong>Record search.</strong> Searched the registry for the terms of the test; no recorded '
    'claim answers it.</p>'
    for label in ('Necessary target', 'Extra requirements', 'Independent alternative',
                  'Rank normalization', 'Decision', 'Decisive test'))


def routed(history=''):
    return ('<li data-route-item="general-step">Route</li>' +
            '<section id="proposed-next-step"><h2>Proposed next step</h2><p>old</p></section>' +
            '<section id="research-record">' + history + '</section>')


def draft(kind='research', extra='', content=''):
    return (f'<article id="new" data-kind="{kind}" data-route="general-step" '
            f'data-obligation="open-goal" data-goal-progress="unchanged" {extra}>' +
            REPORTS + content + '</article>')


class NotebookAppendTests(unittest.TestCase):
    def test_first_article_follows_record_heading_and_introduction(self):
        source = ('<section id="research-record">\n<h2>Research record</h2>\n'
                  '<p>Record introduction.</p>\n</section>\n<footer></footer>')
        out = tool.append(source, '<article id="first">first entry</article>')
        self.assertLess(out.index('</h2>'), out.index('<article'))
        self.assertLess(out.index('Record introduction.'), out.index('<article'))
        self.assertLess(out.index('</article>'), out.index('</section>'))
        self.assertTrue(out.endswith('<footer></footer>'))

    def test_appends_after_last_article_and_replaces_next_step(self):
        out = tool.append(NOTEBOOK, '<article id="a3">three</article>\n', '<p>new</p>')
        self.assertIn('<article id="a2">two</article>\n<article id="a3">three</article>\n</section>', out)
        self.assertIn('<h2>Proposed next step</h2>\n<p>new</p>\n</section>', out)
        self.assertNotIn('<p>old</p>', out)

    def test_accepts_attributes_before_the_anchor(self):
        out = tool.append(NOTEBOOK, '<article class="research-entry" id="a3" data-kind="review">three</article>')
        self.assertIn('<article id="a2">two</article>\n<article class="research-entry" id="a3"', out)
        with self.assertRaisesRegex(ValueError, 'already present'):
            tool.append(NOTEBOOK, '<article class="research-entry" id="a2">dup</article>')

    def test_keeps_next_step_without_option(self):
        out = tool.append(NOTEBOOK, '<article id="a3">three</article>')
        self.assertIn('<p>old</p>', out)

    def test_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'already present'):
            tool.append(NOTEBOOK, '<article id="a2">dup</article>')
        with self.assertRaisesRegex(ValueError, 'one <article'):
            tool.append(NOTEBOOK, '<p>not an article</p>')
        with self.assertRaisesRegex(ValueError, 'research-record'):
            tool.append('<p>none</p>', '<article id="x">x</article>')

    def test_pending_architecture_requires_link_inside_outcome(self):
        source = routed('<article id="review" data-kind="review" data-route="general-step">' +
                        ARCHITECTURE + '</article>')
        outside = '<p>Question: <a href="#review">previous review</a>.</p>'
        outcome = ('<p><strong>Architecture test.</strong> The attempted construction failed '
                   'its stated general test and changes the next action.</p>')
        with self.assertRaisesRegex(ValueError, 'Architecture test must'):
            tool.append(source, draft(content=outside + outcome))
        linked = outcome.replace('The attempted', '<a href="#review">The attempted</a>')
        self.assertIn(linked, tool.append(source, draft(content=linked)))

    def test_goal_review_requires_across_goal_before_append(self):
        history = ''
        for block in range(2):
            history += (f'<article id="r{block}" data-kind="review" '
                        'data-route="general-step" data-open-items="3"></article>')
            history += ''.join(f'<article id="e{block}-{i}" data-kind="research" '
                               'data-route="general-step"></article>' for i in range(6))
        entry = draft('review', 'data-scope="goal" data-open-items="3"', ARCHITECTURE)
        with self.assertRaisesRegex(ValueError, 'Across the goal'):
            tool.append(routed(history), entry)
        across = ('<h4>Across the goal</h4><ul><li>Binary: unchanged, six cycles.</li>'
                  '<li>All-prime: unchanged, zero cycles.</li></ul>')
        self.assertIn(across, tool.append(routed(history), entry.replace('</article>', across + '</article>')))

    def test_registration_waits_but_finalizer_still_checks_it(self):
        entry = draft(extra='data-claims="lem:new-result"').replace(
            'data-goal-progress="unchanged"', 'data-goal-progress="advanced"').replace(
            'The required implication', 'The claim lem:new-result advances the required implication')
        checks = tool.reporting_checks()
        with mock.patch.object(checks, 'registered_status', side_effect=AssertionError('too early')):
            result = tool.append(routed(), entry)
        position = result.index('<article')
        with mock.patch.object(checks, 'registered_status', return_value={}):
            with self.assertRaisesRegex(ValueError, 'Advanced Goal progress'):
                checks.validate_progress(result, position, result.index('</article>', position))

    def test_cli_reporting_failure_does_not_write_notebook_or_next_step(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = routed()
            notebook = root / 'notebook.html'
            notebook.write_text(source)
            entry = root / 'draft.html'
            entry.write_text('<article id="new" data-kind="research" data-route="general-step">bad</article>')
            nxt = root / 'next.html'
            nxt.write_text('<p>replacement</p>')
            with mock.patch.object(tool, 'ROOT', root), \
                 mock.patch.object(tool, 'selected', return_value={'source': 'notebook.html'}), \
                 mock.patch.object(sys, 'argv', ['notebook-append.py', str(entry), '--next', str(nxt)]):
                with self.assertRaisesRegex(SystemExit, 'data-obligation'):
                    tool.main()
            self.assertEqual(notebook.read_text(), source)


if __name__ == '__main__':
    unittest.main()
