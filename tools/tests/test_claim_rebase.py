import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import claim_rebase as cr


def git(cwd, *args):
    subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True, text=True)


class GuardTest(unittest.TestCase):
    def test_only_registry_paths_are_resolved(self):
        self.assertTrue(cr.is_registry_path('research/claims/index.json'))
        self.assertTrue(cr.is_registry_path('research/CLAIM_INDEX.md'))
        self.assertFalse(cr.is_registry_path('research/branches/x/notebook.html'))
        self.assertEqual(cr.foreign_conflicts(['research/claims/index.json', 'notebook.html', 'AGENTS.md']),
                         ['AGENTS.md', 'notebook.html'])
        self.assertEqual(cr.foreign_conflicts(['research/ATTENTION.md']), [])

    def test_a_claim_the_base_already_holds_is_reported(self):
        registry = {'claims': [{'id': 'lem:a'}, {'id': 'lem:b'}]}
        specs = [{'claims': [{'id': 'lem:b'}, {'id': 'lem:c'}]}, {'claims': [{'id': 'lem:a'}]}]
        self.assertEqual(cr.already_registered(registry, specs), ['lem:a', 'lem:b'])
        self.assertEqual(cr.already_registered(registry, [{'claims': [{'id': 'lem:c'}]}]), [])


class UnstagedTest(unittest.TestCase):
    def test_unstaged_tracked_changes_are_named_and_staged_ones_are_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            git(tmp, 'init', '-q', '-b', 'main')
            git(tmp, 'config', 'user.email', 't@example.org')
            git(tmp, 'config', 'user.name', 'T')
            for name in ('a.txt', 'b.txt'):
                Path(tmp, name).write_text('base\n')
            git(tmp, 'add', '.')
            git(tmp, 'commit', '-q', '-m', 'base')
            self.assertEqual(cr.unstaged(tmp), [])
            Path(tmp, 'a.txt').write_text('edited\n')
            Path(tmp, 'b.txt').write_text('staged\n')
            git(tmp, 'add', 'b.txt')
            Path(tmp, 'new.txt').write_text('untracked\n')
            self.assertEqual(cr.unstaged(tmp), ['a.txt'])
            self.assertIn('a.txt', cr.unstaged_warning(['a.txt']))
            self.assertIn('You must edit all merge conflicts', cr.unstaged_warning(['a.txt']))


class RefusalTest(unittest.TestCase):
    def repo(self, tmp):
        git(tmp, 'init', '-q', '-b', 'main')
        git(tmp, 'config', 'user.email', 't@example.org')
        git(tmp, 'config', 'user.name', 'T')
        Path(tmp, 'research/claims').mkdir(parents=True)
        Path(tmp, 'research/claims/index.json').write_text(json.dumps({'claims': []}))
        Path(tmp, 'notes.txt').write_text('base\n')
        git(tmp, 'add', '.')
        git(tmp, 'commit', '-q', '-m', 'base')

    def refuse(self, tmp, spec):
        err = io.StringIO()
        with self.assertRaises(SystemExit) as raised, contextlib.redirect_stderr(err):
            cr.main(['--spec', str(spec), '--repo', tmp])
        return str(raised.exception)

    def test_nothing_in_progress_and_foreign_conflicts_are_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.repo(tmp)
            spec = Path(tmp, 'spec.json')
            spec.write_text(json.dumps({'claims': [{'id': 'lem:c'}]}))
            self.assertIn('No rebase or cherry-pick', self.refuse(tmp, spec))
            git(tmp, 'checkout', '-q', '-b', 'side')
            Path(tmp, 'notes.txt').write_text('side\n')
            git(tmp, 'commit', '-q', '-am', 'side')
            git(tmp, 'checkout', '-q', 'main')
            Path(tmp, 'notes.txt').write_text('main\n')
            git(tmp, 'commit', '-q', '-am', 'main')
            git(tmp, 'checkout', '-q', 'side')
            subprocess.run(['git', 'rebase', 'main'], cwd=tmp, capture_output=True, text=True)
            message = self.refuse(tmp, spec)
            self.assertIn('Conflicts outside the registry', message)
            self.assertIn('notes.txt', message)
            self.assertIn('side', Path(tmp, 'notes.txt').read_text())      # left as the conflict made it


if __name__ == '__main__':
    unittest.main()
