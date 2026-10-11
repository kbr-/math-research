"""The launcher's check that a script under research/results is committed before it is run."""
import subprocess
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CS = SourceFileLoader('compute_sh', str(ROOT / 'compute.sh')).load_module()


def git(folder, *args):
    subprocess.run(['git', '-C', str(folder), '-c', 'user.name=t', '-c', 'user.email=t@t', *args],
                   check=True, capture_output=True)


class ResultsScriptCommittedTest(unittest.TestCase):
    def test_untracked_modified_and_committed_scripts(self):
        with tempfile.TemporaryDirectory() as folder:
            results = Path(folder) / 'research' / 'results' / 'run_01'
            results.mkdir(parents=True)
            script = results / 'control.py'
            script.write_text('print(1)\n')
            git(folder, 'init', '-q')
            command = ['python3', str(script), '--out', str(results / 'out.json')]
            self.assertEqual(CS.uncommitted_results_scripts(command), [str(script)])          # untracked
            git(folder, 'add', '-A')
            git(folder, 'commit', '-q', '-m', 'script')
            self.assertEqual(CS.uncommitted_results_scripts(command), [])                     # committed
            script.write_text('print(2)\n')
            self.assertEqual(CS.uncommitted_results_scripts(command), [str(script)])          # modified

    def test_scripts_elsewhere_and_other_arguments_are_not_checked(self):
        with tempfile.TemporaryDirectory() as folder:
            script = Path(folder) / 'scratch.py'
            script.write_text('print(1)\n')
            git(folder, 'init', '-q')
            self.assertEqual(CS.uncommitted_results_scripts(['python3', str(script)]), [])
            data = Path(folder) / 'research' / 'results' / 'r' / 'table.json'
            data.parent.mkdir(parents=True)
            data.write_text('{}\n')
            self.assertEqual(CS.uncommitted_results_scripts(['python3', '-c', 'pass', str(data)]), [])


if __name__ == '__main__':
    unittest.main()
