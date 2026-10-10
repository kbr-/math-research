"""notebook-append.py inserts after the last record article and replaces the next step."""
import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
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
    '<strong>Downstream.</strong> Through thm:downstream-transfer the target gives the statement wanted '
    'at every parameter. '
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

    def test_a_dollar_sign_or_a_character_reference_without_its_ampersand_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'entry contains a dollar sign'):
            tool.append(NOTEBOOK, '<article id="a3">where $x$ is odd</article>')
        self.assertIn(r'where \(x\) is odd', tool.append(NOTEBOOK, r'<article id="a3">where \(x\) is odd</article>'))
        with self.assertRaisesRegex(ValueError, r'entry has character references without their & \(#39;, nbsp;\)'):
            tool.append(NOTEBOOK, '<article id="a3">the budget#39;s share, 2 nbsp;s, 2 nbsp;m</article>')
        self.assertIn('budget&#39;s', tool.append(NOTEBOOK, '<article id="a3">the budget&#39;s share, 2&nbsp;s</article>'))
        with self.assertRaisesRegex(ValueError, r'next step has character references without their & \(quot;\)'):
            tool.append(NOTEBOOK, '<article id="a3">three</article>', '<p>the (quot;new) step</p>')

    def test_a_next_step_that_parks_an_open_goal_is_refused(self):
        entry, task = '<article id="a3">three</article>', '<article id="a3" data-kind="task">three</article>'
        opened = '<section id="open-statements"><ol><li>Statement one is open.</li></ol></section>' + NOTEBOOK
        proved = '<section id="open-statements"><p>The goal is proved.</p></section>' + NOTEBOOK
        waits = '<p>Research <em>waits</em> for your decision on the route.</p>'
        with self.assertRaisesRegex(ValueError, r'the next step parks the goal \("Research  waits"\)'):
            tool.append(opened, entry, waits)
        # A proved goal, a notebook that lists no statements, and a task's entry may wait.
        for source, appended in ((proved, entry), (NOTEBOOK, entry), (opened, task)):
            self.assertIn('waits', tool.append(source, appended, waits))
        # A step that turns to another statement, or names work that waits without being a wait, is research.
        for step in ('<p>Switch to statement two: prove the transfer lemma for odd fields.</p>',
                     '<p>Prove the bound; the write-up can wait until then.</p>'):
            self.assertIn(step, tool.append(opened, entry, step))
        with self.assertRaisesRegex(ValueError, 'next step contains a dollar sign'):
            tool.append(NOTEBOOK, entry, '<p>Costs $5.</p>')

    def test_an_entry_is_refused_while_where_we_stand_is_as_committed_unless_a_reason_is_given(self):
        def notebook(stand):
            return f'<section id="where-we-stand"><p>{stand}</p></section>' + NOTEBOOK
        entry = '<article id="a3">\n<h3>Three</h3>\n<p class="entry-meta">Status: finite check.</p>\n<p>Body.</p>\n</article>'
        with self.assertRaisesRegex(ValueError, 'Where we stand is unchanged since the last commit'):
            tool.append(notebook('old'), entry, committed=notebook('old'))
        with self.assertRaisesRegex(ValueError, 'Where we stand is unchanged'):
            tool.append(notebook('old'), entry, committed=notebook('old'), reason='  ')
        kept = tool.append(notebook('old'), entry, committed=notebook('old'), reason='a check of <one> case & no more ')
        self.assertIn('<p class="entry-meta">Status: finite check.</p>\n<p><strong>Where we stand.</strong> Unchanged: '
                      'a check of &lt;one&gt; case &amp; no more</p>\n<p>Body.</p>', kept)
        # Without a status line the paragraph ends the entry.
        self.assertIn('three\n<p><strong>Where we stand.</strong> Unchanged: why</p>\n</article>',
                      tool.append(notebook('old'), '<article id="a3">three</article>', committed=notebook('old'), reason='why'))
        # A changed section, a notebook not yet committed and one without the section take the entry as it is.
        for source, committed in ((notebook('new'), notebook('old')), (notebook('old'), None), (NOTEBOOK, NOTEBOOK)):
            for reason in (None, 'why'):
                self.assertNotIn('Where we stand.</strong>', tool.append(source, entry, committed=committed, reason=reason))

    def test_a_branch_s_own_checks_run_after_the_generic_ones(self):
        entry = '<article id="a3">three</article>'
        with tempfile.TemporaryDirectory() as directory:
            tools = Path(directory)
            self.assertIn(entry, tool.append(NOTEBOOK, entry, tools=tools))
            (tools / 'append_checks.py').write_text(
                'def check(source, entry, next_html):\n'
                '    open(__file__ + ".ran", "a").write(entry + "|" + str(next_html) + "\\n")\n'
                '    if "three" in entry:\n        raise ValueError("this branch takes no entry about three")\n')
            ran = tools / 'append_checks.py.ran'
            with self.assertRaisesRegex(ValueError, 'this branch takes no entry about three'):
                tool.append(NOTEBOOK, entry, '<p>new</p>', tools=tools)
            self.assertEqual(ran.read_text(), entry + '|<p>new</p>\n')
            self.assertIn('four', tool.append(NOTEBOOK, '<article id="a4">four</article>', tools=tools))
            # An entry both would refuse is refused by the generic check, and the module is not asked.
            ran.unlink()
            with self.assertRaisesRegex(ValueError, 'dollar sign'):
                tool.append(NOTEBOOK, '<article id="a3">three for $3</article>', tools=tools)
            self.assertFalse(ran.exists())

    def test_the_command_reads_the_committed_notebook_and_records_the_reason(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = '<section id="where-we-stand"><p>old</p></section>' + NOTEBOOK
            (root / 'notebook.html').write_text(source)
            entry = root / 'draft.html'
            entry.write_text('<article id="a3">three</article>')
            git = lambda *args: subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *args], cwd=root,
                                               capture_output=True, text=True, check=True)
            git('init', '-q'); git('add', 'notebook.html'); git('commit', '-qm', 'x')

            def run(*arguments):
                with mock.patch.object(tool, 'ROOT', root), mock.patch.object(tool, 'selected', return_value={'source': 'notebook.html'}), \
                        mock.patch.object(sys, 'argv', ['notebook-append.py', str(entry), *arguments]), \
                        contextlib.redirect_stdout(io.StringIO()):
                    tool.main()
            with self.assertRaisesRegex(SystemExit, 'Where we stand is unchanged since the last commit'):
                run()
            self.assertEqual((root / 'notebook.html').read_text(), source)
            run('--stand-unchanged', 'only a lemma')
            self.assertIn('three\n<p><strong>Where we stand.</strong> Unchanged: only a lemma</p>\n</article>',
                          (root / 'notebook.html').read_text())

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
