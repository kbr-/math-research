import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    'merge_appends', Path(__file__).resolve().parents[1] / 'merge-formalization-appends.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def notebook(*ids, summary='Original', context='Context'):
    return (f'<h1>{context}</h1><p><strong>Formal verification.</strong>{summary}</p>'
            + ''.join(f'<article id="{i}"><p>Proof {i}</p></article>\n' for i in ids)
            + tool.MARKER)


class MergeAppendsTests(unittest.TestCase):
    def test_preserves_both_complete_records_and_explicit_overview(self):
        result = tool.merge_notebook(
            notebook('old'), notebook('old', 'a', summary='A'),
            notebook('old', 'b', summary='B'),
            '<p><strong>Formal verification.</strong>A and B</p>')
        self.assertEqual(list(tool.articles(result)), ['old', 'a', 'b'])
        self.assertIn('<p>Proof old</p>', result)
        self.assertIn('A and B', result)

    def test_changed_history_or_context_refused(self):
        for modified in (notebook('old', 'a').replace('Proof old', 'Changed proof'),
                         notebook('old', 'a', context='Changed context')):
            with self.assertRaises(ValueError):
                tool.merge_notebook(notebook('old'), modified, notebook('old', 'b'))

    def test_different_overviews_require_review(self):
        with self.assertRaises(ValueError):
            tool.merge_notebook(notebook('old'), notebook('old', summary='A'),
                                notebook('old', summary='B'))

    def test_duplicate_ids_and_conflicting_additions_refused(self):
        for branch in (notebook('old', 'new', 'new'),
                       notebook('old', 'new').replace('Proof new', 'Different proof')):
            with self.assertRaises(ValueError):
                tool.merge_notebook(notebook('old'), notebook('old', 'new'), branch)

    def test_index_union_and_conflicting_row_refusal(self):
        base = 'Header\n| `old` | old claim |\n'
        left = base + '| `a` | claim A |\n'
        right = base + '| `b` | claim B |\n'
        result = tool.merge_index(base, left, right)
        self.assertIn('| `a` | claim A |', result)
        self.assertIn('| `b` | claim B |', result)
        for modified in (right.replace('old claim', 'changed'),
                         base + '| `a` | different claim |\n'):
            with self.assertRaises(ValueError):
                tool.merge_index(base, left, modified)

    def test_index_blank_lines_allowed_but_content_and_order_preserved(self):
        base = 'Header\n\n| `old` | old claim |\n'
        left = 'Header\n| `old` | old claim |\n\n| `a` | claim A |\n'
        right = base + '| `b` | claim B |\n'
        result = tool.merge_index(base, left, right)
        self.assertIn('| `a` | claim A |', result)
        self.assertIn('| `b` | claim B |', result)
        for bad in (left.replace('Header', 'Changed header'),
                    left.replace('old claim', 'changed claim'),
                    '| `a` | claim A |\n' + base):
            with self.assertRaises(ValueError):
                tool.merge_index(base, bad, right)

    def test_real_rebase_keeps_staging_and_continuation_manual(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args, check=True):
                return subprocess.run(['git', *args], cwd=root, check=check,
                                      text=True, capture_output=True)
            git('init', '-q', '-b', 'main')
            git('config', 'user.name', 'Tool Test')
            git('config', 'user.email', 'test@example.invalid')
            (root / 'research').mkdir()
            def write(branch=None):
                (root / 'notebook.html').write_text(notebook('old', *([branch] if branch else [])))
                (root / 'research/CLAIM_INDEX.md').write_text(
                    'Header\n| `old` | original |\n' +
                    (f'| `{branch}` | new {branch} |\n' if branch else ''))
                git('add', '.')
                git('commit', '-qm', branch or 'base')
            write()
            git('checkout', '-qb', 'worker')
            write('worker')
            git('checkout', '-q', 'main')
            write('main')
            git('checkout', '-q', 'worker')
            self.assertNotEqual(git('rebase', 'main', check=False).returncode, 0)
            subprocess.run(['python3', str(Path(tool.__file__))], cwd=root,
                           check=True, capture_output=True, text=True)
            self.assertEqual(list(tool.articles((root / 'notebook.html').read_text())),
                             ['old', 'main', 'worker'])
            self.assertIn('UU notebook.html', git('status', '--porcelain').stdout)
            self.assertTrue((root / '.git/rebase-merge').exists())


if __name__ == '__main__':
    unittest.main()
