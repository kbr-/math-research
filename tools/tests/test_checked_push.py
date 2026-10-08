import os
import importlib.util
import shutil
import subprocess
import sys
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
        shutil.copy(ROOT / 'tools/ff-base.sh', self.work / 'tools')
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
        self.assertRegex(result.stdout, r'Pushing 1 commits, \d+B, to origin/main\.')
        self.assertIn(f'origin/main is at {git(self.work, "rev-parse", "--short", "HEAD")} work, the commit pushed.',
                      result.stdout)

    def test_refuses_when_head_moves_during_the_checks(self):
        checked = git(self.work, 'rev-parse', '--short', 'HEAD')
        (self.work / 'tools/notebook_context.py').write_text(
            'import pathlib, subprocess\npathlib.Path("g").write_text("y")\n'
            'subprocess.run(["git", "add", "g"], check=True)\n'
            'subprocess.run(["git", "commit", "-qm", "during"], check=True)\n')
        result = self.run_push('main')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(f'HEAD moved from {checked} while the checks ran', result.stderr)
        self.assertEqual(git(self.remote, 'rev-parse', 'main'), git(self.work, 'rev-parse', 'main'))

    def test_selected_remote_is_used_for_checks_push_and_confirmation(self):
        private = self.tmp / 'private.git'
        git(self.tmp, 'init', '-q', '--bare', '-b', 'main', str(private))
        git(self.work, 'remote', 'add', 'private', str(private))
        git(self.work, 'push', '-q', 'private', 'main')
        original = git(self.remote, 'rev-parse', 'main')
        result = self.run_push('--remote', 'private', 'main')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(git(private, 'rev-parse', 'main'), git(self.work, 'rev-parse', 'HEAD'))
        self.assertEqual(git(self.remote, 'rev-parse', 'main'), original)
        calls = (self.work / 'calls').read_text()
        self.assertIn('--public-history main --remote private', calls)
        self.assertIn('--base private/main', calls)
        self.assertNotIn('origin', calls)
        self.assertRegex(result.stdout, r'Pushing 1 commits, \d+B, to private/main\.')
        self.assertIn('private/main is at', result.stdout)

    def test_verifier_claim_base_uses_selected_remote(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        self.addCleanup(sys.path.remove, str(ROOT / 'tools'))
        spec = importlib.util.spec_from_file_location('push_checkout', ROOT / 'tools/verify-checkout.py')
        checkout = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checkout)
        checkout.ROOT = self.work
        git(self.work, 'remote', 'add', 'private', str(self.remote))
        git(self.work, 'fetch', '-q', 'private')
        self.assertEqual(checkout.claim_base('main', 'private'), 'private/main')
        self.assertEqual(checkout.claim_base('private/main', 'private'), 'private/main')
        self.assertEqual(checkout.claim_base('main', 'origin'), 'origin/main')
        self.assertEqual(checkout.claim_base('missing', 'private'), 'EMPTY')

    def test_help_and_invalid_options_do_not_publish(self):
        original = git(self.remote, 'rev-parse', 'main')
        result = self.run_push('--help')
        self.assertEqual(result.returncode, 0)
        self.assertIn('--remote NAME', result.stdout)
        for args in [('--remote',), ('--remote', ''), ('--remote', '--force'),
                     ('--unknown',), ('main', 'extra'), ('--remote', 'missing', 'main')]:
            with self.subTest(args=args):
                self.assertNotEqual(self.run_push(*args).returncode, 0)
        self.assertFalse((self.work / 'calls').exists())
        self.assertEqual(git(self.remote, 'rev-parse', 'main'), original)

    def test_fails_when_the_remote_branch_is_not_the_pushed_commit(self):
        # The remote accepts the push, then the branch moves, as a concurrent push could move it.
        base = git(self.work, 'rev-parse', 'main')
        hook = self.remote / 'hooks' / 'post-receive'
        hook.write_text(f'#!/bin/sh\ngit update-ref refs/heads/main {base}\n')
        hook.chmod(0o755)
        result = self.run_push('main')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(f'Pushed, but origin/main is at {base}', result.stderr)

    def test_refuses_long_commit_message_lines(self):
        git(self.work, 'commit', '-q', '--amend', '-m', 'work', '-m', 'x' * 101)
        result = self.run_push('main')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('over 100 characters', result.stderr)
        self.assertFalse((self.work / 'calls').exists())

    def test_push_also_fast_forwards_the_local_branch(self):
        # the work branch's commit reaches origin/main and the local main, which no worktree has checked out
        result = self.run_push('main')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Local main fast-forwarded', result.stdout)
        self.assertEqual(git(self.work, 'rev-parse', 'main'), git(self.work, 'rev-parse', 'HEAD'))

    def test_counts_characters_not_bytes(self):
        # 99 characters, over 100 bytes: accepted under the C locale too (review of 3 October 2026)
        git(self.work, 'commit', '-q', '--amend', '-m', 'work', '-m', 'é—' * 49 + 'x')
        result = subprocess.run(['bash', 'tools/checked-push.sh', 'main'], cwd=self.work, capture_output=True,
                                text=True, env={**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'LC_ALL': 'C'})
        self.assertNotIn('over 100 characters', result.stderr)
        git(self.work, 'commit', '-q', '--allow-empty', '-m', 'more', '-m', 'é—' * 51)
        result = subprocess.run(['bash', 'tools/checked-push.sh', 'main'], cwd=self.work, capture_output=True,
                                text=True, env={**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'LC_ALL': 'C'})
        self.assertIn('over 100 characters', result.stderr)

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
