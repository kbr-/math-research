import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location('resume_tool', TOOLS / 'resume.py')
resume = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resume)


class RunStateTest(unittest.TestCase):
    """The resume bundle carries the main checkout's run_state, the user's grants and overrides for the run."""

    def test_the_main_checkout_s_file_is_read_from_a_worktree_and_its_absence_is_said(self):
        with tempfile.TemporaryDirectory() as tmp:
            main = Path(tmp) / 'main'
            main.mkdir()
            git = lambda *a: subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *a], cwd=main,
                                            check=True, capture_output=True)
            git('init', '-q')
            git('commit', '-q', '--allow-empty', '-m', 'base')
            worktree = main / 'wt'
            git('worktree', 'add', '-q', '-b', 'side', str(worktree))
            # No file, or an empty one: no grant, in so many words.
            for root in (main, worktree):
                self.assertEqual(resume.run_state(root), resume.NO_RUN_STATE)
            (main / 'run_state').write_text(' \n')
            self.assertEqual(resume.run_state(worktree), resume.NO_RUN_STATE)
            self.assertIn('No grant or override is recorded', resume.NO_RUN_STATE)
            # The main checkout's file, also where the worktree has no link to it or a file of its own.
            (main / 'run_state').write_text('Pushes of main are granted (user, 1 May 2026: "push").\n')
            (worktree / 'run_state').write_text('a stray copy\n')
            for root in (main, worktree):
                self.assertEqual(resume.run_state(root), 'Pushes of main are granted (user, 1 May 2026: "push").\n')
            # Outside a repository the directory itself is read.
            bare = Path(tmp) / 'bare'
            bare.mkdir()
            (bare / 'run_state').write_text('here\n')
            self.assertEqual(resume.run_state(bare), 'here\n')

    def test_the_bundle_has_the_section(self):
        source = (TOOLS / 'resume.py').read_text()
        self.assertEqual(source.count("run_state(root),'run-state','current'))"), 1)


if __name__ == '__main__':
    unittest.main()
