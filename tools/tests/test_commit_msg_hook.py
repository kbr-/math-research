import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / 'git-hooks' / 'commit-msg'


class CommitMessageLength(unittest.TestCase):
    """The commit-msg hook refuses a message with a line over 100 characters when the commit is made, not only
    tools/checked-push.sh at push time, when the commit is buried under later ones (3 October 2026: a 102-character
    line made hours earlier stopped a push of 75 commits)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git('init', '-q')
        shutil.copy(HOOK, self.root / '.git' / 'hooks' / 'commit-msg')

    def git(self, *args):
        return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *args], cwd=self.root,
                              capture_output=True, text=True)

    def commit(self, message):
        (self.root / 'f').write_text(message)
        self.git('add', 'f')
        return self.git('commit', '-q', '--allow-empty', '-m', message)

    def test_a_line_of_100_characters_passes_and_101_is_refused(self):
        self.assertEqual(self.commit('Title\n\n' + 'x' * 100).returncode, 0)
        refused = self.commit('Title\n\n' + 'y' * 101)
        self.assertEqual(refused.returncode, 1)
        self.assertIn('101 characters', refused.stderr)
        self.assertEqual(self.commit('T' * 101).returncode, 1)                  # the title too

    def test_characters_are_counted_not_bytes(self):
        self.assertEqual(self.commit('Title\n\n' + 'ą—' * 50).returncode, 0)   # 100 characters, 250 bytes

    def test_git_comment_lines_are_not_counted(self):
        message = self.root / 'message'
        message.write_text('Title\n\n# ' + 'z' * 120 + '\n')
        (self.root / 'f').write_text('c')
        self.git('add', 'f')
        self.assertEqual(self.git('commit', '-q', '-F', str(message)).returncode, 0)


if __name__ == '__main__':
    unittest.main()
