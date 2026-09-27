from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

RUNNER = Path(__file__).resolve().parent / 'run.py'


class SuiteTimeLimit(unittest.TestCase):
    """run.py fails a run that exceeds its wall-time limit and names the slowest tests."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        shutil.copy2(RUNNER, root / 'run.py')
        (root / 'test_slow.py').write_text('import time, unittest\nclass Slow(unittest.TestCase):\n'
                                           '    def test_sleeps(self):\n        time.sleep(0.5)\n')
        (root / 'test_fast.py').write_text('import unittest\nclass Fast(unittest.TestCase):\n'
                                           '    def test_returns(self):\n        pass\n')
        self.root = root

    def run_suite(self, limit):
        return subprocess.run([sys.executable, 'run.py', '-j', '2', '--limit', str(limit)], cwd=self.root,
                              capture_output=True, text=True, timeout=30)

    def test_over_the_limit_fails_and_names_the_slowest_test(self):
        result = self.run_suite(0.2)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('TOO SLOW', result.stdout)
        slowest = result.stdout.split('Slowest tests:')[1].splitlines()[1]
        self.assertIn('test_slow.Slow.test_sleeps', slowest)

    def test_within_the_limit_passes(self):
        result = self.run_suite(30)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('Ran 2 tests', result.stdout)
        self.assertNotIn('TOO SLOW', result.stdout)


class SkippedTests(unittest.TestCase):
    """run.py lists each skipped test with its reason, and counts them in its summary."""

    def test_skips_are_listed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copy2(RUNNER, root / 'run.py')
            (root / 'test_skip.py').write_text('import unittest\nclass Needs(unittest.TestCase):\n'
                                               '    def test_tool(self):\n        self.skipTest("tool missing")\n'
                                               '    def test_runs(self):\n        pass\n')
            result = subprocess.run([sys.executable, 'run.py', '-j', '2'], cwd=root, capture_output=True,
                                    text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('Skipped test_skip.Needs.test_tool: tool missing', result.stdout)
        self.assertIn('OK, 1 skipped', result.stdout)


if __name__ == '__main__':
    unittest.main()
