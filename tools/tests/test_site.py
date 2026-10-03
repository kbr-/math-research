"""The site tests in tests/: the Pages build tests, the published client's test, and the real-browser
notebook tests. The browser tests need Playwright with Chromium, found in the node_modules of this
checkout or of another worktree of the repository; where it is missing (CI), they are skipped with the
reason. Each browser case must finish within BROWSER_LIMIT_S."""
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


BROWSER_GROUPS = 3   # browsers, each running every third case, one at a time


class Browser(unittest.TestCase):
    """Every case in tests/test_*.cjs passes within BROWSER_LIMIT_S. The cases run in BROWSER_GROUPS browsers,
    one test each, so the suite's workers run the groups in parallel, and within a group one at a time: each
    page spends about 0.75 s of CPU starting MathJax, whatever the notebook's size, so cases run concurrently
    in a browser timed each other's work and took 5.2-5.4 s under the suite's load where each alone takes
    0.5-1.4 s; a browser per case cost about 8 s more CPU (3 October 2026)."""

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
        result, _ = node('run_browser_tests.cjs', '--group', f'{k}/{BROWSER_GROUPS}', modules=modules, timeout=60)
        cases = [json.loads(line) for line in result.stdout.splitlines() if line.startswith('{')]
        self.assertGreaterEqual(len(cases), 3, result.stdout + result.stderr)   # nine or more cases in all
        for case in cases:
            with self.subTest(case['name']):
                self.assertTrue(case['ok'], case.get('error'))
                self.assertLess(case['seconds'], BROWSER_LIMIT_S, f"{case['name']} took {case['seconds']:.1f} s")
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
