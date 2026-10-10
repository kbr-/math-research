"""stand_reasons.py counts, from git, how added entries stand to their notebook's Where we stand."""
import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import stand_reasons as tool

SIDE = 'research/branches/side/notebook.html'


def notebook(stand, *entries):
    return (f'<section id="where-we-stand"><p>{stand}</p></section>\n<section id="research-record">\n'
            + ''.join(entries) + '</section>\n')


def entry(ident, reason=None):
    paragraph = f'<p><strong>Where we stand.</strong> Unchanged: {reason}</p>\n' if reason else ''
    return f'<article class="research-entry" id="{ident}" data-kind="research">\n<p>Body.</p>\n{paragraph}</article>\n'


class StandReasonsTest(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.git('init', '-q')
        (self.root / SIDE).parent.mkdir(parents=True)
        self.entries = {'notebook.html': [], SIDE: []}
        self.commit({'notebook.html': 'start', SIDE: 'start'})                      # the base: no entry

    def git(self, *arguments):
        return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *arguments], cwd=self.root,
                              capture_output=True, text=True, check=True).stdout.strip()

    def commit(self, stands, added=()):
        """A commit that sets the given notebooks' Where we stand and adds (notebook, entry) pairs; its hash."""
        for path, text in added:
            self.entries[path].append(text)
        for path, stand in stands.items():
            (self.root / path).write_text(notebook(stand, *self.entries[path]))
        self.git('add', '-A')
        self.git('commit', '-qm', 'x')
        return self.git('rev-parse', 'HEAD')

    def run_tool(self, *arguments):
        out = io.StringIO()
        with mock.patch.object(tool, 'ROOT', self.root), contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            status = tool.main(list(arguments))
        return status, out.getvalue().splitlines()

    def test_entries_are_counted_by_what_their_commit_did_to_the_section_and_reasons_are_grouped(self):
        base = self.git('rev-parse', 'HEAD')
        first = self.commit({'notebook.html': 'moved'}, [('notebook.html', entry('a'))])
        self.commit({'notebook.html': 'moved'}, [('notebook.html', entry('b', 'only a lemma, &amp; no\n  more'))])
        self.commit({'notebook.html': 'moved'}, [('notebook.html', entry('c', 'only a lemma, &amp; no more'))])
        self.commit({'notebook.html': 'moved'}, [('notebook.html', entry('d'))])
        # A commit that changes the notebook and adds no entry is not counted.
        self.commit({'notebook.html': 'moved again'})
        status, lines = self.run_tool(f'{base}..HEAD')
        self.assertEqual((status, lines), (0, [
            'notebook.html: 4 entries added; 1 with Where we stand changed; 2 with a reason; 1 with neither',
            '  2 x only a lemma, & no more',
            'Read 5 commits, 10 notebook versions, 0 MB']))
        # The range is followed: without its first commit, the entry that commit added is not counted.
        self.assertEqual(self.run_tool(f'{first}..HEAD')[1][0],
                         'notebook.html: 3 entries added; 0 with Where we stand changed; 2 with a reason; 1 with neither')

    def test_each_notebook_has_its_own_line_and_one_can_be_chosen(self):
        base = self.git('rev-parse', 'HEAD')
        (self.root / 'page.html').write_text(notebook('a page', entry('p')))        # no notebook: not read
        self.commit({'notebook.html': 'moved', SIDE: 'start'},
                    [('notebook.html', entry('a')), (SIDE, entry('s1', 'a check')), (SIDE, entry('s2', 'a proof'))])
        self.commit({SIDE: 'side moved'}, [(SIDE, entry('s3'))])
        status, lines = self.run_tool(f'{base}..HEAD')
        self.assertEqual(lines[:4], [
            'notebook.html: 1 entries added; 1 with Where we stand changed; 0 with a reason; 0 with neither',
            f'{SIDE}: 3 entries added; 1 with Where we stand changed; 2 with a reason; 0 with neither',
            '  1 x a check', '  1 x a proof'])
        self.assertEqual(self.run_tool(f'{base}..HEAD', '--notebook', SIDE)[1][0], lines[1])
        self.assertEqual(len(self.run_tool(f'{base}..HEAD', '--notebook', SIDE)[1]), 4)

    def test_a_range_git_cannot_read_is_reported(self):
        status, lines = self.run_tool('no-such-revision..HEAD')
        self.assertEqual(status, 1)
        self.assertIn('stand_reasons: ', lines[0])


if __name__ == '__main__':
    unittest.main()
