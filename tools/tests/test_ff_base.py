"""ff-base.sh and the base_behind hook (ported from the business framework, 3 October 2026, without its site-terms
merge driver): a worktree branch is rebased onto its base and the base fast-forwarded, without a push.

Runs the real script in a scratch repository: main checked out in one worktree, a work branch in another."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS / 'hooks'))
import base_behind  # noqa: E402


def git(cwd, *args):
    return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *args], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


class FfBaseTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.main = self.tmp / 'main'
        (self.main / 'tools').mkdir(parents=True)
        shutil.copy(TOOLS / 'ff-base.sh', self.main / 'tools' / 'ff-base.sh')
        (self.main / 'a').write_text('a\n')
        git(self.tmp, 'init', '-q', '-b', 'main', str(self.main))
        git(self.main, 'add', '.')
        git(self.main, 'commit', '-qm', 'base')
        self.work = self.tmp / 'work'
        git(self.main, 'worktree', 'add', '-q', '-b', 'main-work', str(self.work))

    def commit(self, where, name, message):
        (where / name).write_text(message + '\n')
        git(where, 'add', name)
        git(where, 'commit', '-qm', message)

    def ff(self, *args, cwd=None):
        return subprocess.run(['bash', 'tools/ff-base.sh', *args], cwd=cwd or self.work, capture_output=True,
                              text=True, env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'})

    def test_rebases_onto_a_moved_base_and_fast_forwards_it(self):
        self.commit(self.main, 'm', 'main moves')
        self.commit(self.work, 'w', 'work commits')
        result = self.ff('main')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Rebased onto main', result.stdout)
        self.assertEqual(git(self.main, 'rev-parse', 'main'), git(self.work, 'rev-parse', 'HEAD'))
        self.assertTrue((self.main / 'w').exists())                  # the checked-out worktree moved too
        self.assertEqual(git(self.main, 'status', '--porcelain', '--untracked-files=no'), '')

    def test_fast_forward_only_when_already_on_top(self):
        self.commit(self.work, 'w', 'work commits')
        result = self.ff('main')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('fast-forwarded', result.stdout)
        self.assertNotIn('Rebased', result.stdout)
        self.assertEqual(git(self.main, 'rev-parse', 'main'), git(self.work, 'rev-parse', 'HEAD'))

    def test_refuses_a_non_ancestor_and_a_dirty_checkout(self):
        self.commit(self.main, 'm', 'main moves')
        self.commit(self.work, 'w', 'work commits')
        before = git(self.main, 'rev-parse', 'main')
        result = self.ff('--no-rebase', 'main')                       # main is not an ancestor of HEAD
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('not an ancestor', result.stderr)
        (self.work / 'w').write_text('dirty\n')
        result = self.ff('main')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('uncommitted', result.stderr)
        self.assertEqual(git(self.main, 'rev-parse', 'main'), before)

    def test_refuses_to_move_a_dirty_base_worktree(self):
        self.commit(self.work, 'w', 'work commits')
        (self.main / 'a').write_text('changed\n')
        before = git(self.main, 'rev-parse', 'main')
        result = self.ff('main')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('uncommitted changes', result.stderr)
        self.assertEqual(git(self.main, 'rev-parse', 'main'), before)

    def test_no_argument_uses_the_upstream_or_refuses(self):
        result = self.ff()
        self.assertEqual(result.returncode, 2)
        self.assertIn('no local upstream', result.stderr)
        git(self.work, 'branch', '--set-upstream-to=main', 'main-work')
        self.commit(self.work, 'w', 'work commits')
        result = self.ff()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(git(self.main, 'rev-parse', 'main'), git(self.work, 'rev-parse', 'HEAD'))

    def test_hook_follows_the_upstream_whatever_the_branch_is_named(self):
        odd = self.tmp / 'odd'
        git(self.main, 'worktree', 'add', '-q', '-b', 'worktree-spin-bmd', str(odd))
        self.commit(odd, 'o', 'odd commits')
        self.assertIn('no upstream', base_behind.message('git commit -qm x', cwd=odd))
        git(odd, 'branch', '--set-upstream-to=main', 'worktree-spin-bmd')
        self.assertIn('Local main', base_behind.message('git commit -qm x', cwd=odd))
        self.assertIsNone(base_behind.message('git status', cwd=odd))
        self.assertIsNone(base_behind.message('git commit -qm x', cwd=self.main), 'the main checkout is left alone')
        result = self.ff(cwd=odd)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNone(base_behind.message('git commit -qm x', cwd=odd), 'quiet once level')

    def test_hook_ignores_a_remote_only_upstream(self):
        remote = self.tmp / 'remote.git'
        git(self.tmp, 'init', '-q', '--bare', '-b', 'main', str(remote))
        git(self.work, 'remote', 'add', 'origin', str(remote))
        git(self.work, 'push', '-q', 'origin', 'main-work')
        git(self.work, 'branch', '--set-upstream-to=origin/main-work', 'main-work')
        self.commit(self.work, 'w', 'work commits')
        self.assertIsNone(base_behind.message('git commit -qm x', cwd=self.work))


if __name__ == '__main__':
    unittest.main()
