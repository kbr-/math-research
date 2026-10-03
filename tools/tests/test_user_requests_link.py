import importlib.machinery
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
loader = importlib.machinery.SourceFileLoader('compute_cli_links', str(ROOT / 'compute.sh'))
spec = importlib.util.spec_from_loader(loader.name, loader)
cli = importlib.util.module_from_spec(spec)
loader.exec_module(cli)


class UserRequestsLink(unittest.TestCase):
    """A worktree's user_requests is a link to the main checkout's file, which the user reads (3 October 2026)."""

    def test_worktree_gets_a_link_and_a_separate_file_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            main = Path(tmp) / 'main'
            main.mkdir()
            git = lambda *a, cwd=main: subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *a],
                                                      cwd=cwd, check=True, capture_output=True)
            git('init', '-q')
            git('commit', '-q', '--allow-empty', '-m', 'base')
            worktree = main / 'wt'
            git('worktree', 'add', '-q', '-b', 'side', str(worktree))
            self.assertIsNone(cli.link_user_requests(main))              # the main checkout keeps its own file
            link = cli.link_user_requests(worktree)
            self.assertTrue(link.is_symlink())
            link.open('a').write('request\n')
            self.assertEqual((main / 'user_requests').read_text(), 'request\n')
            self.assertEqual(cli.link_user_requests(worktree), link)     # idempotent
            link.unlink()
            (worktree / 'user_requests').write_text('stranded\n')
            with self.assertRaisesRegex(ValueError, 'append its entries'):
                cli.link_user_requests(worktree)


if __name__ == '__main__':
    unittest.main()
