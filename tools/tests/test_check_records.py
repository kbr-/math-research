import contextlib
import datetime
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

TOOL = Path(__file__).resolve().parents[1] / 'check_records.py'
spec = importlib.util.spec_from_file_location('check_records', TOOL)
check_records = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_records)


class UntimedCountsTest(unittest.TestCase):
    def test_a_passing_count_needs_a_duration_on_its_line(self):
        untimed = check_records.untimed_counts
        self.assertEqual(untimed('The package passes 1059 tests on Python 3.12 and on 3.14.'), ['passes 1059 tests'])
        self.assertEqual(untimed('11 model tests pass on SQLite; `1 passed` there; 2,347 passed at the tip.'),
                         ['11 model tests pass', '1 passed', '2,347 passed'])
        self.assertEqual(untimed('The suite passed 155 tests, and 3 tests passed again.'),
                         ['passed 155 tests', '3 tests passed'])
        for timed in ('The package passes 1059 tests in 34.4 s on Python 3.12.', '1078 passed in 10.05s', '12 tests pass (2 minutes).',
                      'Ran in 300 ms: 4 passed.', '9 tests pass, 1 min.'):
            self.assertEqual(untimed(timed), [], timed)
        # No count of passing tests: nothing to time.
        for other in ('The tests pass.', 'It has 1059 tests.', 'Version 3 passed review.', 'Step 12 tests the pass.'):
            self.assertEqual(untimed(other), [], other)

    def test_the_tool_reports_an_untimed_count_in_a_file_it_is_given(self):
        with tempfile.TemporaryDirectory() as scratch:
            record = Path(scratch) / 'RECORD.md'
            record.write_text('Fine: 5 passed in 2 s.\nNot fine: the suite passes 7 tests.\n')
            result = subprocess.run([sys.executable, str(TOOL), str(record)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(result.stdout.splitlines(), [
                f"{record}:2: test count without the run's time (say how long the run took): passes 7 tests",
                '1 files, 1 findings'])
            record.write_text('Fine: 5 passed in 2 s.\n')
            result = subprocess.run([sys.executable, str(TOOL), str(record)], capture_output=True, text=True)
            self.assertEqual((result.returncode, result.stdout), (0, '1 files, 0 findings\n'))




TODAY = datetime.date(2026, 9, 29)
CREDIT = '<span data-generated="finish-turn-producer-v1">Produced by Claude Code (claude-opus-5-5, low).</span>'


class NotebookChecksTest(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)

    def run_tool(self, *arguments):
        """(exit status, the findings' kinds and texts, the summary line) of the tool on `arguments`, its
        repository being the scratch directory."""
        out = io.StringIO()
        with mock.patch.object(check_records, 'ROOT', self.root), mock.patch.object(sys, 'argv', ['x', *arguments]), \
                mock.patch.object(check_records, 'PROJECTS', self.root / 'none'), contextlib.redirect_stdout(out), \
                self.assertRaises(SystemExit) as stopped:
            check_records.main()
        *found, summary = out.getvalue().splitlines()
        return stopped.exception.code, [line.split(': ', 1)[1] for line in found], summary

    def notebook(self, *lines):
        path = self.root / 'notebook.html'
        path.write_text(''.join(line + '\n' for line in lines))
        return str(path)

    def test_a_status_line_may_be_300_characters_and_the_producer_credit_is_not_counted(self):
        def meta(length, credit=''):
            return f'<p class="entry-meta">{"x" * length}{credit}</p>'
        self.assertEqual(self.run_tool(self.notebook(meta(300), meta(290, ' ' + CREDIT)))[:2], (0, []))
        status, found, _ = self.run_tool(self.notebook(meta(300), meta(301), meta(301, ' ' + CREDIT)))
        self.assertEqual((status, found), (1, ['long status line: ' + 'x' * 100] * 2))
        # Each is reported at its own line, also after lines that hold no status line.
        path = self.notebook('<p>one</p>', meta(301), '', '<p>two</p>', meta(10), meta(302))
        out = io.StringIO()
        with mock.patch.object(sys, 'argv', ['x', path]), contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            check_records.main()
        self.assertEqual([line.split(':')[1] for line in out.getvalue().splitlines()[:-1]], ['2', '6'])
        self.assertEqual(check_records.status_text('Status: refuted. <em>Two</em> states&#39; codes. ' + CREDIT),
                         "Status: refuted. Two states' codes.")

    def test_an_entry_dated_after_today_is_flagged(self):
        dates = check_records.future_entry_dates
        self.assertEqual(dates('<article class="research-entry" id="entry-2026-09-30-third" data-kind="research">', TODAY), ['2026-09-30'])
        for date in ('2026-09-29', '2026-09-01', '2025-12-31'):
            self.assertEqual(dates(f'<article id="entry-{date}-x">', TODAY), [])
        self.assertEqual(dates('<a href="#entry-2026-09-30-x">the entry</a>, due 2027-01-04', TODAY), [])
        today, tomorrow = datetime.date.today(), datetime.date.today() + datetime.timedelta(days=1)
        status, found, _ = self.run_tool(self.notebook(f'<article id="entry-{today}-a">', f'<article id="entry-{tomorrow}-b">'))
        self.assertEqual((status, found), (1, [f'entry dated after today: {tomorrow}']))

    def test_a_character_reference_without_its_ampersand_is_flagged_in_a_notebook(self):
        status, found, _ = self.run_tool(self.notebook('the budget&#39;s share, 2&nbsp;s', 'the budget#39;s share, 2 nbsp;s'))
        self.assertEqual((status, found), (1, ['character reference without its &: #39;', 'character reference without its &: nbsp;']))
        record = self.root / 'NOTES.md'
        record.write_text('issue #12; and a stray nbsp; in Markdown\n')
        self.assertEqual(self.run_tool(str(record))[:2], (0, []))

    def test_with_no_path_the_side_notebooks_are_read_too(self):
        side = self.root / 'research' / 'branches' / 'covering' / 'notebook.html'
        side.parent.mkdir(parents=True)
        side.write_text('fixed in 757a6cdde\n')
        self.notebook('fine')
        status, found, summary = self.run_tool()
        self.assertEqual((status, found, summary), (1, ['commit hash: 757a6cdde'], '2 files, 1 findings'))

    def test_the_curve_name_is_no_commit_hash(self):
        hashes = lambda text: [m.group(0) for m in check_records.HASH.finditer(text)]
        self.assertEqual(hashes('fixed in 4b4c36a, see 757a6cdde'), ['4b4c36a', '757a6cdde'])
        self.assertEqual(hashes("generateKeyPairSync('ed25519') and an ed25519 key"), [])
        self.assertEqual(hashes('commit ed25519abc'), ['ed25519abc'])


class BrokenEntityTest(unittest.TestCase):
    def test_references_that_lost_their_ampersand_are_found_and_whole_ones_and_prose_are_not(self):
        broken = check_records.broken_entities
        self.assertEqual(broken('to stay within the section budget#39;s budget'), ['#39;'])
        self.assertEqual(broken('growing on paid search (quot;spend nothing'), ['quot;'])
        self.assertEqual(broken('states&#39; codes, &quot;quoted&quot;, 2&ndash;3, &#x27;, issue #12; while; sandwich;'), [])
        self.assertEqual(broken('see note #3; then'), [])
        # A word that ends in a reference's name is a word: only a name with no letter before it is a lost reference.
        self.assertEqual(broken('a lamp; a stamp; (amp; nbsp;'), ['amp;', 'nbsp;'])


if __name__ == '__main__':
    unittest.main()
