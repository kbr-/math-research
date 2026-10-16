"""tools/git-hooks-branch/pre-commit runs the stale-claim check unless the active hook already does."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / 'tools/git-hooks-branch/pre-commit'


class BranchPreCommitTest(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        subprocess.run(['git', 'init', '-q', str(self.dir)], check=True)
        (self.dir / 'tools').mkdir()
        (self.dir / 'research/claims').mkdir(parents=True)
        (self.dir / 'research/claims/index.json').write_text('{}')
        # A stand-in check that always refuses, so the test sees whether it ran.
        (self.dir / 'tools/staged_claims.py').write_text('import sys\nprint("stale-check ran")\nsys.exit(1)\n')

    def run_hook(self, active_text):
        hook = self.dir / '.git/hooks/pre-commit'
        hook.write_text(active_text)
        return subprocess.run(['sh', str(HOOK)], cwd=self.dir, capture_output=True, text=True,
                              env=dict(os.environ, GIT_DIR=str(self.dir / '.git')))

    def test_runs_the_check_when_the_active_hook_lacks_it(self):
        # 16 October 2026: the shared hook linked to a branch without the check, so it never ran.
        result = self.run_hook('#!/bin/sh\npython3 tools/lead_queue.py check\n')
        self.assertEqual(result.returncode, 1)
        self.assertIn('stale-check ran', result.stdout)

    def test_skips_when_the_active_hook_already_runs_it(self):
        result = self.run_hook('#!/bin/sh\npython3 "$top/tools/staged_claims.py" --base HEAD\n')
        self.assertEqual(result.returncode, 0)
        self.assertNotIn('stale-check ran', result.stdout)


if __name__ == '__main__':
    unittest.main()
