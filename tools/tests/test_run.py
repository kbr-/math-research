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


class LongestFirst(unittest.TestCase):
    """run.py starts the tests the previous run found slowest first, and unknown tests before those."""

    def test_cold_run_uses_declared_costs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copy2(RUNNER, root / 'run.py')
            log = root / 'order.txt'
            for name, hint in (('a_unknown', ''), ('b_costly', '    expected_seconds = 6.0\n')):
                (root / f'test_{name}.py').write_text(
                    f'import unittest\nclass T(unittest.TestCase):\n{hint}    def test_it(self):\n'
                    f'        with open({str(log)!r}, "a") as log: log.write("{name}\\n")\n')
            result = subprocess.run([sys.executable, 'run.py', '-j', '1'], cwd=root,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(log.read_text().split(), ['b_costly', 'a_unknown'])

    def test_order_follows_the_previous_durations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copy2(RUNNER, root / 'run.py')
            log = root / 'order.txt'
            for name, seconds in (('a_quick', 0), ('b_slow', 0.3), ('c_middle', 0.1)):
                (root / f'test_{name}.py').write_text(
                    f'import time, unittest\nclass T(unittest.TestCase):\n    def test_it(self):\n'
                    f'        open({str(log)!r}, "a").write("{name}\\n"); time.sleep({seconds})\n')
            run = lambda: subprocess.run([sys.executable, 'run.py', '-j', '1'], cwd=root, capture_output=True,
                                         text=True, timeout=30)
            self.assertEqual(run().returncode, 0)
            self.assertEqual(log.read_text().split(), ['a_quick', 'b_slow', 'c_middle'])   # discovery order
            (root / 'test_d_new.py').write_text('import unittest\nclass T(unittest.TestCase):\n'
                                                f'    def test_it(self):\n        open({str(log)!r}, "a")'
                                                '.write("d_new\\n")\n')
            log.unlink()
            self.assertEqual(run().returncode, 0)
            self.assertEqual(log.read_text().split(), ['d_new', 'b_slow', 'c_middle', 'a_quick'])


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
