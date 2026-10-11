"""The site tests in tests/: the Pages build tests, the published client's test, and the real-browser
notebook tests. The browser tests need Playwright with Chromium, found in the node_modules of this
checkout or of another worktree of the repository; where it is missing (CI), they are skipped with the
reason. Each browser case must finish within BROWSER_LIMIT_S."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tests'))
from test_pages import *  # noqa: E402,F401,F403 -- the Pages build tests run in this suite too
from test_side_pages import *  # noqa: E402,F401,F403
from tools.build_pages import build  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

BROWSER_LIMIT_S = 5.0


def node_modules():
    """The node_modules holding Playwright: this checkout's, else another worktree's, else None."""
    listing = subprocess.run(['git', 'worktree', 'list', '--porcelain'], cwd=ROOT,
                             capture_output=True, text=True).stdout
    worktrees = [Path(line.split(' ', 1)[1]) for line in listing.splitlines() if line.startswith('worktree ')]
    for base in [ROOT, *worktrees]:
        if (base / 'node_modules/playwright').is_dir():
            return base / 'node_modules'
    return None


def node_binary():
    """Node from PATH, else the newest nvm install (the launcher's jobs get a minimal PATH), else None."""
    installs = sorted(Path.home().glob('.nvm/versions/node/v*/bin/node'),
                      key=lambda path: [int(part) for part in path.parts[-3][1:].split('.')])
    return shutil.which('node') or (str(installs[-1]) if installs else None)


def node(script, *args, modules=None, timeout=30):
    binary = node_binary()
    if not binary:
        raise unittest.SkipTest('Node.js is not installed')
    env = dict(os.environ, NODE_PATH=str(modules)) if modules else None
    start = time.monotonic()
    result = subprocess.run([binary, str(ROOT / 'tests' / script), *args], cwd=ROOT, env=env,
                            capture_output=True, text=True, timeout=timeout)
    return result, time.monotonic() - start


class PublishedClient(unittest.TestCase):
    def test_update_behavior(self):
        with tempfile.TemporaryDirectory(prefix='math-pages-client-') as temp:
            build(Path(temp) / 'site', root=ROOT)
            result, _ = node('test_pages_client.js', str(Path(temp) / 'site/index.html'))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


BROWSER_GROUPS = 3   # browsers, each running every second case, one at a time

_spec = importlib.util.spec_from_file_location('framework_runner', Path(__file__).resolve().parent / 'run.py')
RUNNER = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RUNNER)


def slow_case(case, elapsed, load):
    """What a browser case over its limit says: its time, its group's, and what else the machine did during
    the group, since a case that passes alone a minute later leaves nothing else to tell the two runs apart."""
    return (f"{case['name']} took {case['seconds']:.1f} s; its group of cases took {elapsed:.1f} s."
            + (f' {load}' if load else ''))


class SlowCase(unittest.TestCase):
    def test_a_slow_case_says_what_else_used_the_machine(self):
        load = RUNNER.outside_load((100.0, 20.0), (190.0, 40.0), 8.0, 16, Path('/nonexistent/cgroup'))
        self.assertEqual(slow_case({'name': 'math:layout', 'seconds': 5.19}, 8.04, load),
                         "math:layout took 5.2 s; its group of cases took 8.0 s. CPU during the run: 20 s in the run's own "
                         "control group, 70 s by other programs; the machine's 16 processors were busy for 90 s of 128.")
        self.assertEqual(slow_case({'name': 'math:layout', 'seconds': 5.19}, 8.04, None),
                         'math:layout took 5.2 s; its group of cases took 8.0 s.')


class Browser(unittest.TestCase):
    """Every case in tests/test_*.cjs passes within BROWSER_LIMIT_S. The cases run in BROWSER_GROUPS browsers,
    one test each, so the suite's workers run the groups in parallel, and within a group one at a time: each
    page spends about 0.75 s of CPU starting MathJax. The suite is bound by CPU, about 100 s of it on 14
    logical CPUs, so the number of groups moves no work: with two, the longer group ran for the whole of a
    10 s suite; with three, each group takes 6 to 8 s there and no case came near its limit in twelve whole
    runs (10 October 2026). Three groups had produced 5.13 s and 5.07 s cases on 9 October 2026, before the
    suite's CPU was cut. Cases remain sequential within each browser."""

    expected_seconds = 6.0  # cold worktrees have no per-test duration cache

    def test_group_0(self):
        self.run_group(0)

    def test_group_1(self):
        self.run_group(1)

    def test_group_2(self):
        self.run_group(2)

    def run_group(self, k):
        modules = node_modules()
        if not modules:
            self.skipTest('Playwright is not installed')
        used, mine, jobs = RUNNER.cpu_seconds(), RUNNER.own_seconds(), RUNNER.other_jobs()
        result, elapsed = node('run_browser_tests.cjs', '--group', f'{k}/{BROWSER_GROUPS}', modules=modules, timeout=60)
        after = RUNNER.cpu_seconds()
        load = RUNNER.outside_load(used, after, elapsed, os.cpu_count())
        # What was certainly other work during the group; a case over its limit still fails, and says this.
        busy = RUNNER.elsewhere((used[0], after[0]), (used[1], after[1]), RUNNER.jobs_growth(jobs, RUNNER.other_jobs()),
                                (mine, RUNNER.own_seconds()), elapsed, os.cpu_count())[1]
        cases = [json.loads(line) for line in result.stdout.splitlines() if line.startswith('{')]
        self.assertGreaterEqual(len(cases), 3, result.stdout + result.stderr)   # nine or more cases in all
        for case in cases:
            with self.subTest(case['name']):
                self.assertTrue(case['ok'], case.get('error'))
                self.assertLess(case['seconds'], BROWSER_LIMIT_S, slow_case(case, elapsed, ' '.join(filter(None, [load, busy]))))
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
