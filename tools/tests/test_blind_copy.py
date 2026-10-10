import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import blind_copy  # noqa: E402

ENV = dict(os.environ, GIT_AUTHOR_NAME='A Real Author', GIT_AUTHOR_EMAIL='real@example.org', GIT_COMMITTER_NAME='A Real Author',
           GIT_COMMITTER_EMAIL='real@example.org')


class BlindCopyTest(unittest.TestCase):
    """A repository whose messages say what its change is for, and a copy that must not."""

    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.git('init', '-q', '-b', 'main')
        self.commit({'app.py': 'def run(): return 1\n', 'docs/old.md': 'gone later\n', '.gitignore': 'build/\n'}, 'the base: SECRET-BASE')
        self.git('tag', 'v1-SECRET-TAG')
        self.commit({'app.py': 'def run(): return 2\n', 'new.py': 'x = 1\n'}, 'the change fixes SECRET-PURPOSE')
        self.git('rm', '-q', 'docs/old.md')
        self.git('commit', '-q', '-m', 'the tip: SECRET-TIP')
        self.git('branch', 'other-SECRET-BRANCH', 'HEAD~2')
        (self.source / 'build').mkdir()
        (self.source / 'build' / 'ignored.bin').write_text('ignored')
        (self.source / 'uncommitted.py').write_text('SECRET-UNCOMMITTED\n')

    def git(self, *arguments, cwd=None):
        return subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', *arguments], cwd=cwd or self.source, env=ENV,
                              check=True, capture_output=True, text=True).stdout

    def commit(self, files, message):
        for name, text in files.items():
            (self.source / name).parent.mkdir(parents=True, exist_ok=True)
            (self.source / name).write_text(text)
        self.git('add', '-A')
        self.git('commit', '-q', '-m', message)

    def run_tool(self, *arguments):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = blind_copy.main([str(self.source), *arguments])
        return status, out.getvalue(), err.getvalue()

    def everything(self, copy):
        """All a reviewer in the copy can read of it: every object's content, every ref, the configuration."""
        objects = subprocess.run(['git', 'cat-file', '--batch-all-objects', '--batch'], cwd=copy, check=True,
                                 capture_output=True).stdout.decode(errors='replace')    # a tree's entries are binary
        return objects + self.git('for-each-ref', cwd=copy) + (copy / '.git' / 'config').read_text() + self.git(
            'log', '--all', '--format=%an %ae %ad %s %b', cwd=copy)

    def test_a_copy_with_a_base_holds_two_commits_and_nothing_of_the_history(self):
        copy = self.root / 'copy'
        status, out, err = self.run_tool('HEAD', str(copy), '--base', 'HEAD~2')
        self.assertEqual((status, err), (0, ''))
        self.assertEqual(out, f"{copy}: commits ['base', 'change'], refs ['refs/heads/review'], remotes []\n")
        # The files are the two revisions', and the change is the diff between them.
        self.assertEqual(self.git('rev-parse', 'HEAD^{tree}', cwd=copy), self.git('rev-parse', 'HEAD^{tree}'))
        self.assertEqual(self.git('rev-parse', 'HEAD~1^{tree}', cwd=copy), self.git('rev-parse', 'HEAD~2^{tree}'))
        self.assertEqual(self.git('diff', '--stat', 'HEAD~1', cwd=copy), self.git('diff', '--stat', 'HEAD~2', 'HEAD'))
        self.assertEqual(sorted(path.name for path in copy.iterdir()), ['.git', '.gitignore', 'app.py', 'new.py'])
        self.assertEqual(self.git('status', '--short', cwd=copy), '')
        # Nothing of the messages, the authors, the other refs or the uncommitted work is anywhere in it.
        seen = self.everything(copy)
        for secret in ('SECRET', 'Real Author', 'real@example.org', str(self.source)):
            self.assertNotIn(secret, seen)
        self.assertIn('copy copy@example.invalid Sat Jan 1 00:00:00 2000 +0000 change', seen)

    def test_a_copy_without_a_base_is_one_commit_and_an_existing_destination_is_refused(self):
        copy = self.root / 'copy'
        status, out, _ = self.run_tool('HEAD~1', str(copy))
        self.assertEqual((status, out), (0, f"{copy}: commits ['snapshot'], refs ['refs/heads/review'], remotes []\n"))
        self.assertEqual(self.git('rev-parse', 'HEAD^{tree}', cwd=copy), self.git('rev-parse', 'HEAD~1^{tree}'))
        self.assertTrue((copy / 'docs' / 'old.md').exists())
        self.assertNotIn('SECRET', self.everything(copy))
        before = self.git('rev-parse', 'HEAD', cwd=copy)
        status, out, err = self.run_tool('HEAD', str(copy))
        self.assertEqual((status, out, err), (2, '', f'{copy} exists: give a path that does not\n'))
        self.assertEqual(self.git('rev-parse', 'HEAD', cwd=copy), before)
        with self.assertRaises(SystemExit) as stop:
            self.run_tool('no-such-revision', str(self.root / 'other'))
        self.assertIn('failed in', str(stop.exception))
        self.assertFalse((self.root / 'other').exists())

    def test_files_an_archive_leaves_out_fail_the_copy(self):
        self.commit({'.gitattributes': 'new.py export-ignore\n'}, 'attributes')
        status, out, err = self.run_tool('HEAD', str(self.root / 'copy'), '--base', 'HEAD~3')
        self.assertEqual(status, 1)
        self.assertIn("The copy's files differ from the revision's for: tip (an export-ignore attribute", err)
        self.assertIn("commits ['base', 'change']", out)


if __name__ == '__main__':
    unittest.main()
