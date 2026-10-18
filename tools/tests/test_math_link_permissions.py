"""Shared-file permission scopes follow Git's inventory, including sibling and external worktrees."""
import json
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from math_link_permissions import literal_pattern, merge_settings, worktree_rules


class LinkPermissionsTest(unittest.TestCase):
    def test_every_registered_path_and_both_shared_files_are_covered(self) -> None:
        # Git 2.34 supports line-based porcelain; ambiguous embedded newlines fail closed.
        roots = ['/repo/main', '/repo/main/.claude/worktrees/child', '/elsewhere/sibling tree', '/tmp/external']
        inventory = b''.join(b'worktree ' + root.encode() + b'\nHEAD abc\n\n' for root in roots)
        rules = worktree_rules(inventory)
        for root in roots:
            for name in ('user_requests', 'run_state'):
                for tool in ('Edit', 'Write'):
                    self.assertIn(f'{tool}(/{root}/{name})', rules)
        self.assertEqual(len(rules), len(roots) * 4)
        self.assertFalse(any('Bash' in rule or '**' in rule for rule in rules))
        with self.assertRaisesRegex(ValueError, 'no worktrees'):
            worktree_rules(b'')
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            worktree_rules(b'worktree /tmp/new\nline\nHEAD abc\n\n')
        self.assertEqual(literal_pattern('/tmp/tree[old]*?\\name'), '/tmp/tree\\[old\\]\\*\\?\\\\name')

    def test_merge_preserves_settings_mode_original_backup_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'settings.json'
            original = {'model': 'chosen-model', 'permissions': {'defaultMode': 'auto', 'allow': ['Read']}}
            path.write_text(json.dumps(original))
            path.chmod(0o640)
            rules = worktree_rules(b'worktree /repo\n\n')
            self.assertEqual(merge_settings(path, rules), 4)
            self.assertEqual(json.loads(path.read_text())['model'], 'chosen-model')
            self.assertEqual(json.loads(path.read_text())['permissions']['defaultMode'], 'auto')
            self.assertEqual(json.loads(path.read_text())['permissions']['allow'], ['Read'] + rules)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o640)
            backup = path.with_name('settings.json.before-math-links')
            self.assertEqual(json.loads(backup.read_text()), original)
            self.assertEqual(merge_settings(path, rules), 0)
            self.assertEqual(json.loads(backup.read_text()), original)
            more = worktree_rules(b'worktree /another-repository-worktree\n\n')
            self.assertEqual(merge_settings(path, more), 4)
            self.assertEqual(json.loads(backup.read_text()), original)
            other = Path(tmp) / 'cli-settings.json'
            other.write_text(json.dumps(original))
            result = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] / 'math_link_permissions.py'),
                                     '--apply', '--settings', str(other)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            actual = json.loads(other.read_text())
            self.assertIn('Read', actual['permissions']['allow'])
            checkout = subprocess.check_output(
                ['git', '-C', str(Path(__file__).resolve().parents[2]), 'rev-parse', '--show-toplevel'],
                text=True).strip()
            self.assertIn(f'Edit(/{literal_pattern(checkout)}/user_requests)', actual['permissions']['allow'])
            self.assertEqual(json.loads(other.with_name(other.name + '.before-math-links').read_text()), original)
            linked = Path(tmp) / 'linked-settings.json'
            target = Path(tmp) / 'target-settings.json'
            target.write_text(json.dumps(original))
            linked.symlink_to(target.name)
            self.assertEqual(merge_settings(linked, rules), 4)
            self.assertTrue(linked.is_symlink())
            self.assertEqual(json.loads(target.read_text())['permissions']['allow'], ['Read'] + rules)
            self.assertEqual(json.loads(target.with_name(target.name + '.before-math-links').read_text()), original)
