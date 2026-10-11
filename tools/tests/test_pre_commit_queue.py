import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
REVIEW = ('<article id="r1" data-kind="review" data-route="step"><h4>Outside leads</h4><ul>'
          '<li>One. <strong>Test.</strong> Passed.</li><li>Two. <strong>Test.</strong> Passed.</li></ul></article>')


def notebook(articles, queue):
    section = '' if queue is None else ('<section id="lead-queue"><ol>'
                                        + ''.join(f'<li data-lead="{i}">{i}</li>' for i in queue) + '</ol></section>')
    return ('<li data-route-item="step">x</li>' + section + '<section id="research-record">' + ''.join(articles)
            + '</section>\n')


def closing(item, ident='d'):
    return (f'<article id="{ident}" data-kind="research" data-route="step" data-lead="{item}"><p><strong>Follow-up.'
            '</strong> Closed: x.</p></article>')


class PreCommitQueueTest(unittest.TestCase):
    """The shared pre-commit hook runs lead_queue.py check on each staged notebook that holds a queue or held one,
    against HEAD, or HEAD's parent when the commit amends; it skips with a notice where the tool lacks the check
    command or the commit amends the root commit, and does nothing where the tool is missing."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git('init', '-q')
        shutil.copy(TOOLS / 'git-hooks' / 'pre-commit', self.root / '.git' / 'hooks' / 'pre-commit')
        self.nb = self.root / 'notebook.html'
        (self.root / 'README').write_text('x\n')                       # a HEAD to compare with
        self.git('add', 'README')
        self.git('commit', '-qm', 'start')

    def git(self, *args):
        return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *args], cwd=self.root,
                              capture_output=True, text=True)

    def commit(self, body, *flags):
        self.nb.write_text(body)
        self.git('add', '-A')
        return self.git('commit', '-qm', 'x', *flags)

    def install_tool(self, source=None):
        (self.root / 'tools').mkdir(exist_ok=True)
        shutil.copy(TOOLS / 'branch_extension.py', self.root / 'tools' / 'branch_extension.py')
        if source is None:
            shutil.copy(TOOLS / 'lead_queue.py', self.root / 'tools' / 'lead_queue.py')
        else:
            (self.root / 'tools' / 'lead_queue.py').write_text(source)

    def install_context_tool(self, budget):
        (self.root / 'tools').mkdir(exist_ok=True)
        for name in ('notebook_context.py', 'notebook-excerpt.py', 'notebooks.py', 'recovery_evidence.py'):
            shutil.copy(TOOLS / name, self.root / 'tools' / name)
        (self.root / 'research').mkdir(exist_ok=True)
        (self.root / 'research' / 'context-budgets.json').write_text(budget)
        self.git('add', 'tools', 'research')

    def test_refuses_a_staged_notebook_over_a_hard_budget(self):
        self.install_context_tool('{"version": 1, "hard_multiplier": 1.5, "characters_per_word": 12, '
                                  '"total_soft_words": 100, "regions": {"@intro": 2}}')
        self.assertEqual(self.commit(notebook([REVIEW], None)).returncode, 0)    # "x": one word
        refused = self.commit(notebook([REVIEW], None).replace('>x<', '>one two three four<'))
        self.assertEqual(refused.returncode, 1)
        self.assertIn("Commit refused: notebook.html's living sections exceed a hard budget", refused.stderr)
        self.assertIn('notebook.html: notebook context hard limit exceeded', refused.stdout + refused.stderr)
        self.git('reset', '-q', 'notebook.html')
        (self.root / 'other.html').write_text('one two three four five six')         # no notebook
        self.git('add', 'other.html')
        self.assertEqual(self.git('commit', '-qm', 'x').returncode, 0)

    def test_refuses_when_the_budget_cannot_be_checked(self):
        self.install_context_tool('{"version": 2}')
        refused = self.commit(notebook([REVIEW], None))
        self.assertEqual(refused.returncode, 1)
        self.assertIn('Unknown context-budget configuration', refused.stderr)

    def test_inert_without_the_tool(self):
        result = self.commit(notebook([REVIEW], ['r1:9']))
        self.assertEqual((result.returncode, result.stderr), (0, ''))

    def test_passes_a_valid_queue_change_and_refuses_a_wrong_one(self):
        self.install_tool()
        self.assertEqual(self.commit(notebook([REVIEW], ['r1:1', 'r1:2'])).returncode, 0)
        refused = self.commit(notebook([REVIEW, closing('r1:1')], ['r1:1', 'r1:2']))   # the closed head stays
        self.assertEqual(refused.returncode, 1)
        self.assertIn('Commit refused: the lead queue check failed for notebook.html', refused.stderr)
        self.assertIn('Queue update', refused.stderr)
        self.assertEqual(self.commit(notebook([REVIEW, closing('r1:1')], ['r1:2'])).returncode, 0)

    def test_an_amend_is_checked_against_the_parent(self):
        self.install_tool()
        self.assertEqual(self.commit(notebook([REVIEW], ['r1:1', 'r1:2'])).returncode, 0)
        broken = self.commit(notebook([REVIEW, closing('r1:1')], ['r1:1', 'r1:2']), '--no-verify')
        self.assertEqual(broken.returncode, 0)
        # against HEAD this changes the queue with no new entry; against HEAD's parent it is the entry's update
        fixed = self.commit(notebook([REVIEW, closing('r1:1')], ['r1:2']), '--amend')
        self.assertEqual(fixed.returncode, 0, fixed.stderr)
        self.assertEqual(self.commit(notebook([REVIEW, closing('r1:1')], ['r1:1']), '--amend').returncode, 1)

    def test_a_removed_section_is_checked(self):
        self.install_tool()
        self.assertEqual(self.commit(notebook([REVIEW], ['r1:1', 'r1:2'])).returncode, 0)
        self.assertEqual(self.commit(notebook([REVIEW], None)).returncode, 1)

    def test_an_older_tool_is_skipped_with_a_notice(self):
        self.install_tool('import sys\nprint("usage", file=sys.stderr)\nsys.exit(2)\n')
        result = self.commit(notebook([REVIEW], ['r1:9']))
        self.assertEqual(result.returncode, 0)
        self.assertIn('has no check command yet', result.stderr)

    def test_without_a_commit_to_compare_with_it_is_skipped_with_a_notice(self):
        self.install_tool()
        self.git('update-ref', '-d', 'HEAD')                             # back to an unborn branch
        for flags, queue in (((), ['r1:9']), (('--amend',), ['r1:8'])):  # the first commit, then an amend of it
            with self.subTest(flags=flags):
                result = self.commit(notebook([REVIEW], queue), *flags)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('no commit to compare with', result.stderr)

    def test_a_notebook_without_a_queue_is_not_checked(self):
        self.install_tool('import sys\nsys.exit(1)\n')                  # would refuse anything it checked
        self.assertEqual(self.commit(notebook([REVIEW], None)).returncode, 0)


if __name__ == '__main__':
    unittest.main()
