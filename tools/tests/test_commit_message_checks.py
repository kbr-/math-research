"""tools/commit_message_checks.py: figures of a framework commit message and conditions of registered claims."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('commit_message_checks', ROOT / 'tools/commit_message_checks.py')
cmc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cmc)


class FigureTest(unittest.TestCase):
    def test_a_figure_needs_each_number_in_a_saved_output_the_commit_carries(self):
        # 16 October 2026: four figures seen on the terminal and saved nowhere.
        message = 'Tool: x\n\nSuite: 1191 tests in 8.5 s; it flags 10 calls, 8 distinct briefs.\n# 99 tests\n'
        files = {'research/results/run/suite.txt': 'Ran 1191 tests in 8.5s: OK',
                 'research/results/run/replay.txt': '10 reviewer briefs flagged'}
        paths = ['tools/x.py', *files]
        self.assertEqual(cmc.unsourced(message, paths, files.get), [])
        self.assertEqual(cmc.unsourced(message.replace('8.5 s', '8.6 s'), paths, files.get), ['8.6 s'])
        self.assertEqual(cmc.unsourced(message, ['tools/x.py'], files.get), ['1191 tests', '8.5 s', '10 calls'])
        # A paragraph naming a file is checked against that file only (the builds' reviewer, 17 October 2026).
        self.assertEqual(cmc.unsourced('Tool: x\n\nIt flags 10 calls (suite.txt).\n', paths, files.get), ['10 calls'])
        self.assertEqual(cmc.unsourced('Tool: x\n\nIt flags 10 calls (replay.txt).\n', paths, files.get), [])
        self.assertEqual(cmc.figures('1514 texts, 56 paragraphs, 13 conditions over 9 commits'),
                         ['1514 texts', '56 paragraphs', '13 conditions', '9 commits'])
        self.assertEqual(cmc.figures('# 3 tests in a comment line\nNo figure here.'), [])
        self.assertEqual(cmc.figures('5 of 15 framework commits; 38 of 1562 commands; 12.6 MB read'),
                         ['5 of 15', '38 of 1562', '12.6 MB'])

    def test_only_framework_commits_are_checked(self):
        self.assertTrue(cmc.is_framework(['tools/a.py', 'research/results/x/out.txt']))
        self.assertTrue(cmc.is_framework(['compute.sh']))
        self.assertFalse(cmc.is_framework(['tools/a.py', 'notebook.html']))       # a research entry's commit
        self.assertFalse(cmc.is_framework(['research/results/x/out.txt']))


class ConditionTest(unittest.TestCase):
    def test_a_dropped_condition_of_a_new_claim_is_listed(self):
        # 16 October 2026: a message dropped "Gamma > 0" and turned "at most" into "about".
        claims = [('thm:tradeoff', 'Over any field, if Gamma=(n/2+1)/K-max(k,2)-3>0, every refutation of size s '
                                   'has ln s >= Gamma^2/(8(n+M)), with at most M extension axioms.')]
        bare = 'Main: tradeoff\n\nthm:tradeoff: every refutation has ln s >= Gamma^2/(8(n+M)), about M axioms.'
        listed = [c for _, c in cmc.dropped_conditions(bare, claims)]
        self.assertEqual(len(listed), 2)
        self.assertTrue(listed[0].startswith('if Gamma'))
        full = ('thm:tradeoff: if Gamma=(n/2+1)/K-max(k,2)-3>0, every refutation has ln s >= Gamma^2/(8(n+M)), '
                'with at most M extension axioms.')
        self.assertEqual(cmc.dropped_conditions(full, claims), [])
        self.assertEqual(cmc.dropped_conditions('A message that names no claim.', claims), [])

    def test_a_dropped_degree_window_in_an_entry_is_listed(self):
        # 17 October 2026: a General statement dropped both degree windows of its claim.
        claims = [('prop:p', '(a) If D >= l+1, the least degree is l. (b) If D >= l + ceil(l/2), it is ceil(l/2).')]
        bare = 'prop:p: the least common degree is \\(\\ell\\), and the combined one \\(\\lceil\\ell/2\\rceil\\).'
        self.assertEqual(len(cmc.dropped_conditions(bare, claims, windows_only=True)), 2)
        full = ('prop:p: degree \\(\\ell\\) when \\(D\\ge\\ell+1\\), and \\(\\lceil\\ell/2\\rceil\\) when '
                '\\(D\\ge\\ell+\\lceil\\ell/2\\rceil\\).')
        self.assertEqual(cmc.dropped_conditions(full, claims, windows_only=True), [])
        # other conditions are left to the reader in an entry
        other = [('prop:q', 'If H > 0 and beta < 1, the bound holds.')]
        self.assertEqual(cmc.dropped_conditions('prop:q: the bound holds.', other, windows_only=True), [])

    def test_new_claims_are_those_absent_from_the_old_index(self):
        old = '{"claims": [{"id": "lem:a", "summary": "A."}]}'
        new = '{"claims": [{"id": "lem:a", "summary": "A."}, {"id": "lem:b", "summary": "B, if c."}]}'
        self.assertEqual(cmc.new_claims(old, new), [('lem:b', 'B, if c.')])
        self.assertEqual(len(cmc.new_claims('', new)), 2)


class SuiteAfterTest(unittest.TestCase):
    def test_shared_code_needs_a_whole_suite_run_after_its_last_edit(self):
        # 17 October 2026: a hook change was committed after its own module's tests only.
        import json
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            top = Path(tmp)
            (top / 'tools/hooks').mkdir(parents=True)
            (top / 'tools/tests').mkdir()
            (top / 'tools/hooks/guard.py').write_text('x = 1\n')
            (top / 'tools/shared.py').write_text('y = 1\n')
            (top / 'tools/user.py').write_text('import shared\n')
            (top / 'tools/alone.py').write_text('z = 1\n')
            (top / 'tools/by-path.py').write_text('w = 1\n')
            (top / 'tools/loader.py').write_text("spec = load(ROOT / 'tools/by-path.py')\n")
            self.assertEqual(cmc.shared_code(['tools/by-path.py'], top), ['tools/by-path.py'])   # loaded by path
            self.assertEqual(cmc.shared_code(['tools/hooks/guard.py', 'tools/shared.py', 'tools/alone.py',
                                              'tools/tests/test_alone.py', 'compute.sh'], top),
                             ['tools/hooks/guard.py', 'tools/shared.py', 'compute.sh'])
            self.assertIn('whole suite', cmc.suite_after(['tools/hooks/guard.py'], top))      # no run yet
            stamp = top / 'tools/tests/.suite-pass.json'
            stamp.write_text(json.dumps({'unix_s': os.stat(top / 'tools/hooks/guard.py').st_mtime + 5}))
            self.assertIsNone(cmc.suite_after(['tools/hooks/guard.py'], top))
            os.utime(top / 'tools/hooks/guard.py', (9e9, 9e9))                               # edited after it
            self.assertIn('tools/hooks/guard.py', cmc.suite_after(['tools/hooks/guard.py'], top))
            self.assertIsNone(cmc.suite_after(['tools/alone.py'], top))                     # its own tests do


if __name__ == '__main__':
    unittest.main()
