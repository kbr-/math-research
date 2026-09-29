import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUB = 'import sys, pathlib\npathlib.Path("calls").open("a").write(" ".join(sys.argv[1:]) + "\\n")\n'


def git(cwd, *args):
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class CheckedPushTest(unittest.TestCase):
    """A worktree branch is published to main only after checks against origin/main."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        remote, self.work = self.tmp / 'remote.git', self.tmp / 'work'
        git(self.tmp, 'init', '-q', '--bare', '-b', 'main', str(remote))
        git(self.tmp, 'init', '-q', '-b', 'main', str(self.work))
        (self.work / 'tools').mkdir()
        shutil.copy(ROOT / 'tools/checked-push.sh', self.work / 'tools')
        for name in ('verify-checkout.py', 'check-append-only.py', 'notebook_context.py'):
            (self.work / 'tools' / name).write_text(STUB)
        (self.work / '.gitignore').write_text('calls\n')
        for cmd in (('config', 'user.email', 't@t'), ('config', 'user.name', 't'), ('add', '.'),
                    ('commit', '-qm', 'base'), ('remote', 'add', 'origin', str(remote)),
                    ('push', '-q', 'origin', 'main'), ('switch', '-qc', 'worktree-x')):
            git(self.work, *cmd)
        (self.work / 'f').write_text('x')
        git(self.work, 'add', 'f')
        git(self.work, 'commit', '-qm', 'work')
        self.remote = remote

    def run_push(self, *args):
        return subprocess.run(['bash', 'tools/checked-push.sh', *args], cwd=self.work,
                              capture_output=True, text=True, env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'})

    def test_target_branch_checks_and_fast_forwards(self):
        result = self.run_push('main')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(git(self.remote, 'rev-parse', 'main'), git(self.work, 'rev-parse', 'HEAD'))
        calls = (self.work / 'calls').read_text()
        self.assertIn('--public-history main', calls)
        self.assertIn('--base origin/main', calls)
        self.assertNotIn('worktree-x', git(self.remote, 'branch', '--list'))

    def test_refuses_non_fast_forward(self):
        git(self.work, 'switch', '-qc', 'other', 'main')
        (self.work / 'g').write_text('y')
        git(self.work, 'add', 'g')
        git(self.work, 'commit', '-qm', 'other')
        git(self.work, 'push', '-q', 'origin', 'other:main')
        git(self.work, 'switch', '-q', 'worktree-x')
        result = self.run_push('main')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('not an ancestor', result.stderr)
        self.assertFalse((self.work / 'calls').exists())


if __name__ == '__main__':
    unittest.main()
