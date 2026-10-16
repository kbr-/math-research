"""tools/record_scan.py: a named text check applied over every record entry."""
import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('record_scan', ROOT / 'tools/record_scan.py')
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)

NOTEBOOK = ('<article id="entry-2026-10-15-a"><p>The builds are built in the framework turn right after this.</p>'
            '</article><article id="entry-2026-10-17-b"><p>It is <em>fixed</em> in the next turn.</p>'
            '<p>The rest waits, planned for the turn after this one.</p></article>')


class RecordScanTest(unittest.TestCase):
    def test_a_check_counts_its_matches_per_entry_and_since_a_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            book = Path(tmp) / 'notebook.html'
            book.write_text(NOTEBOOK)
            said = io.StringIO()
            with redirect_stdout(said):
                scan.main(['planned-tense', '--notebook', str(book)])
            lines = said.getvalue().splitlines()
            self.assertEqual([line.split('\t')[0] for line in lines[:-1]],
                             ['entry-2026-10-15-a', 'entry-2026-10-17-b'])
            self.assertIn('2 matches of planned-tense in 2 entries', lines[-1])
            rows, entries = scan.scan(NOTEBOOK, scan.checks()['planned-tense'], since='2026-10-16')
            self.assertEqual((len(rows), entries), (1, 1))
            out = Path(tmp) / 'scan.txt'
            with redirect_stdout(io.StringIO()):
                scan.main(['planned-tense', '--notebook', str(book), '--out', str(out)])
            self.assertIn('2 matches', out.read_text())
            with self.assertRaises(SystemExit), redirect_stdout(io.StringIO()), \
                    unittest.mock.patch('sys.stderr', io.StringIO()):
                scan.main(['planned-tense', '--notebook', str(book), '--out', str(out)])   # never overwrites

    def test_an_unknown_check_is_refused_and_the_list_names_the_checks(self):
        said = io.StringIO()
        with redirect_stdout(said):
            scan.main(['--list'])
        self.assertIn('planned-tense', said.getvalue().split())
        with self.assertRaises(SystemExit), unittest.mock.patch('sys.stderr', io.StringIO()):
            scan.main(['no-such-check'])


import unittest.mock  # noqa: E402  (used in the tests above)

if __name__ == '__main__':
    unittest.main()
