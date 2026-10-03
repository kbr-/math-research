import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import notebook_links as nl  # noqa: E402


class NotebookLinksTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / 'repo'
        (Path(tmp.name) / 'outside.txt').write_text('not ours')     # a real file beside the repository
        (self.root / 'research/results').mkdir(parents=True)
        (self.root / 'research/results/out.txt').write_text('answer')
        (self.root / 'research/branches/side').mkdir(parents=True)
        self.nb = self.root / 'research/branches/side/notebook.html'

    def links(self, *hrefs):
        return ''.join(f'<a class="x" href="{h}">l</a>' for h in hrefs)

    def test_check_lists_links_that_do_not_resolve_from_the_root(self):
        text = self.links('research/results/out.txt', '../../results/out.txt', '#anchor', 'https://example.org/',
                          'private/brief.md', '/abs/path', 'research/results/gone.txt', '../../results/out.txt')
        self.assertEqual(nl.unresolved(text, self.root), ['../../results/out.txt', 'research/results/gone.txt'])

    def test_fix_rewrites_folder_relative_links_to_root_paths(self):
        text = self.links('../../results/out.txt#part', '../../../research/results/out.txt?q=1',
                          'research/results/out.txt', '../../results/gone.txt', '../../../../outside.txt')
        fixed, count = nl.fix(text, self.nb, self.root)
        self.assertEqual(count, 2)
        self.assertEqual(fixed, self.links('research/results/out.txt#part', 'research/results/out.txt?q=1',
                                           'research/results/out.txt', '../../results/gone.txt',
                                           '../../../../outside.txt'))
        self.assertEqual(nl.unresolved(fixed, self.root), ['../../results/gone.txt', '../../../../outside.txt'])

    def test_fix_leaves_every_other_tag_alone(self):
        text = '<link href="../../results/out.txt"><a href="../../results/out.txt">x</a>'
        self.assertEqual(nl.fix(text, self.nb, self.root),
                         ('<link href="../../results/out.txt"><a href="research/results/out.txt">x</a>', 1))


    def test_the_command_resolves_from_the_notebooks_own_repository(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.nb.write_text(self.links('../../results/out.txt'))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(nl.main(['notebook_links.py', 'check', str(self.nb)]), 1)
            self.assertEqual(nl.main(['notebook_links.py', 'fix', str(self.nb)]), 0)
        self.assertIn('1 links rewritten', out.getvalue())
        self.assertEqual(self.nb.read_text(), self.links('research/results/out.txt'))


if __name__ == '__main__':
    unittest.main()
