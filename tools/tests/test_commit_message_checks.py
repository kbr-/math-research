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

    def test_new_claims_are_those_absent_from_the_old_index(self):
        old = '{"claims": [{"id": "lem:a", "summary": "A."}]}'
        new = '{"claims": [{"id": "lem:a", "summary": "A."}, {"id": "lem:b", "summary": "B, if c."}]}'
        self.assertEqual(cmc.new_claims(old, new), [('lem:b', 'B, if c.')])
        self.assertEqual(len(cmc.new_claims('', new)), 2)


if __name__ == '__main__':
    unittest.main()
