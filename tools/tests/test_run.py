import os
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
        # A slow run says what the machine did meanwhile, so that it can be told from one slowed by others.
        # Inside the computation slice the figure is the whole slice's, and the line says so.
        self.assertRegex(result.stdout, r"\nCPU during the run: \d+ s in (the run's own control group|the shared "
                                        r"computation slice \(this run and any other session's jobs in it\)), \d+ s by other "
                                        rf"programs; the machine's {os.cpu_count()} processors were busy for \d+ s of \d+\.\n")

    def test_within_the_limit_passes(self):
        result = self.run_suite(30)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('Ran 2 tests', result.stdout)
        self.assertNotIn('TOO SLOW', result.stdout)
        self.assertNotIn('CPU during the run', result.stdout)

    def test_the_cpu_of_the_machine_and_of_the_run_s_own_group_are_read_and_their_growth_reported(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('framework_runner', RUNNER)
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        root = self.root / 'sys'
        tick = os.sysconf('SC_CLK_TCK')
        stat = self.root / 'stat'   # user nice system idle iowait irq softirq steal guest
        stat.write_text(f'cpu  {10 * tick} {2 * tick} {3 * tick} {500 * tick} {40 * tick} {tick} {tick} {tick} {9 * tick}\ncpu0 1 2 3\n')
        group = self.root / 'cgroup'

        def placed(path, usage):
            group.write_text(f'0::{path}\n')
            (root / path.lstrip('/')).mkdir(parents=True, exist_ok=True)
            (root / path.lstrip('/') / 'cpu.stat').write_text(f'user_usec 1\nusage_usec {usage}\nsystem_usec 2\n')
        # Inside the computation slice the slice's time is read, which holds the services the tests start.
        placed('/user.slice/mathcompute.slice', 7_500_000)
        placed('/user.slice/mathcompute.slice/run-1.service', 1_000_000)
        self.assertEqual(runner.cpu_seconds(stat, group, root), (18.0, 7.5))
        self.assertIn('shared computation slice', runner.measured_group(group))   # other sessions' jobs count in it
        placed('/user.slice/session-2.scope', 2_250_000)
        self.assertEqual(runner.cpu_seconds(stat, group, root), (18.0, 2.25))
        self.assertEqual(runner.measured_group(group), "the run's own control group")
        # What cannot be read is None, and then nothing is reported.
        group.write_text('0::/user.slice/absent\n')
        self.assertEqual(runner.cpu_seconds(stat, group, root), (18.0, None))
        self.assertEqual(runner.cpu_seconds(self.root / 'none', group, root), (None, None))
        stat.write_text('cpu  1 2\n')
        self.assertEqual(runner.cpu_seconds(stat, group, root)[0], None)
        self.assertIsNone(runner.outside_load((1.0, None), (2.0, 3.0), 10.0, 16))
        self.assertIsNone(runner.outside_load((1.0, 1.0), (None, 3.0), 10.0, 16))
        group.write_text('0::/user.slice/session-2.scope\n')
        self.assertEqual(runner.outside_load((100.0, 20.0), (240.0, 115.0), 10.5, 16, group),
                         "CPU during the run: 95 s in the run's own control group, 45 s by other programs; the machine's "
                         '16 processors were busy for 140 s of 168.')
        group.write_text('0::/user.slice/mathcompute.slice/run-1.service\n')
        self.assertIn("95 s in the shared computation slice (this run and any other session's jobs in it), 45 s by",
                      runner.outside_load((100.0, 20.0), (240.0, 115.0), 10.5, 16, group))
        self.assertIn(', 0 s by other programs;', runner.outside_load((100.0, 20.0), (110.0, 31.0), 1.0, 16))


class TemporaryFilesInMemory(unittest.TestCase):
    """run.py gives the tests a temporary directory of the run's own on the memory filesystem, and removes it."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / 'suite'
        self.memory = Path(tmp.name) / 'memory'
        self.root.mkdir()
        self.memory.mkdir()
        shutil.copy2(RUNNER, self.root / 'run.py')
        self.log = Path(tmp.name) / 'seen.txt'
        # Two tests, so that one runs in a worker forked after the directory was chosen; each leaves a file.
        for name in ('a', 'b'):
            (self.root / f'test_{name}.py').write_text(
                # A module that asked for the directory when it was imported, before the runner chose one.
                'import tempfile, unittest\ntempfile.gettempdir()\nclass T(unittest.TestCase):\n    def test_it(self):\n'
                f'        with open({str(self.log)!r}, "a") as log: log.write(tempfile.gettempdir() + "\\n")\n'
                f'        open(tempfile.mkstemp()[1], "w").write("left behind")\n')

    def run_suite(self, memory, environment=()):
        code = f'import sys, pathlib, run; run.MEMORY = pathlib.Path({str(memory)!r}); sys.argv = ["run.py", "-j", "2"]; sys.exit(run.main())'
        plain = {key: value for key, value in os.environ.items() if key != 'TMPDIR'}
        done = subprocess.run([sys.executable, '-c', code], cwd=self.root, capture_output=True, text=True, timeout=30,
                              env={**plain, **dict(environment)})
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        return [Path(line) for line in self.log.read_text().split()]

    def test_the_tests_write_into_one_directory_in_memory_that_is_gone_afterwards(self):
        seen = self.run_suite(self.memory)
        self.assertEqual(len(seen), 2)
        self.assertEqual(len(set(seen)), 1)
        self.assertEqual(seen[0].parent, self.memory)
        self.assertTrue(seen[0].name.startswith('framework-tests-'))
        self.assertEqual(list(self.memory.iterdir()), [])

    def test_a_directory_the_caller_chose_or_no_memory_filesystem_leaves_the_tests_where_they_were(self):
        chosen = self.memory.parent / 'chosen'
        chosen.mkdir()
        self.assertEqual(set(self.run_suite(self.memory, {'TMPDIR': str(chosen)})), {chosen})
        self.assertEqual(list(self.memory.iterdir()), [])
        self.assertEqual(len(list(chosen.iterdir())), 2)   # the caller's directory is not the runner's to empty
        self.log.unlink()
        elsewhere = set(self.run_suite(self.memory / 'absent'))
        self.assertEqual(len(elsewhere), 1)
        self.assertNotIn(self.memory, [*elsewhere][0].parents)


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
