import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
sys.path.insert(0, str(ROOT/'tools/hooks'))
import codex_state as state
import codex_dispatch as hook


class CodexScratchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_cap_boundary_siblings_and_no_deletion(self):
        pad = state.scratch_directory(self.root, 'root', create=True)
        self.assertEqual(state.scratch_directory(self.root, 'root', create=True), pad)
        other = state.scratch_directory(self.root, 'child', create=True)
        (other/'other').write_bytes(b'o' * 1000)
        (pad/'subdir').mkdir()
        (pad/'subdir/a').write_bytes(b'x' * 7)
        (pad/'b').write_bytes(b'x' * 3)
        state.check_owned_scratch(self.root, 'root', cap=10)
        with self.assertRaisesRegex(ValueError, '10 logical bytes'):
            state.check_owned_scratch(self.root, 'root', cap=9)
        self.assertTrue((pad/'b').exists())
        state.check_owned_scratch(self.root, 'absent', cap=1)
        self.assertFalse(state.scratch_directory(self.root, 'absent').exists())

    def test_default_500mb_limit_uses_logical_size_of_sparse_file(self):
        pad = state.scratch_directory(self.root, 'root', create=True)
        path = pad/'sparse'
        with path.open('wb') as stream:
            stream.truncate(500_000_000)
        state.check_owned_scratch(self.root, 'root')
        with path.open('r+b') as stream:
            stream.truncate(500_000_001)
        with self.assertRaisesRegex(ValueError, '500000001 logical bytes'):
            state.check_owned_scratch(self.root, 'root')
        self.assertEqual(path.stat().st_size, 500_000_001)

    def test_symlink_files_directories_and_runtime_ancestors_refuse(self):
        outside = self.root/'outside';outside.mkdir()
        (outside/'evidence').write_text('preserve')
        pad = state.scratch_directory(self.root, 'root', create=True)
        for target in [outside/'evidence', outside]:
            link = pad/'link';link.symlink_to(target)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                state.check_owned_scratch(self.root, 'root')
            link.unlink()
        pad.rmdir();pad.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            state.scratch_directory(self.root, 'root', create=True)
        pad.unlink()
        base = self.root/'.codex/framework/scratch';base.rmdir();base.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            state.scratch_directory(self.root, 'child')
        self.assertEqual((outside/'evidence').read_text(), 'preserve')

    def test_read_errors_do_not_silently_skip_accounting(self):
        state.scratch_directory(self.root, 'root', create=True)
        with patch.object(state.os, 'scandir', side_effect=PermissionError('unreadable')):
            with self.assertRaises(PermissionError):
                state.check_owned_scratch(self.root, 'root')

    def test_native_hooks_and_shell_locator_use_actor_not_parent_for_child(self):
        parent = {'session_id': 'parent', 'hook_event_name': 'SessionStart'}
        child = {**parent, 'hook_event_name': 'SubagentStart', 'agent_id': 'child'}
        root_context = hook.dispatch(parent, self.root)['hookSpecificOutput']['additionalContext']
        child_context = hook.dispatch(child, self.root)['hookSpecificOutput']['additionalContext']
        self.assertIn(str(state.scratch_directory(self.root, 'parent')), root_context)
        self.assertIn(str(state.scratch_directory(self.root, 'child')), child_context)
        self.assertNotIn('Restore context', child_context)
        self.assertNotEqual(state.scratch_directory(self.root, 'child/a'),
                            state.scratch_directory(self.root, 'child_a'))
        for invalid in [None, '', 3]:
            with self.assertRaises(ValueError):
                state.scratch_directory(self.root, invalid)

    def test_cli_uses_runtime_identity_and_fails_when_absent(self):
        with patch.object(sys, 'argv', ['codex_state.py', 'scratch']), \
             patch.dict(os.environ, {'CODEX_THREAD_ID': 'owned'}), \
             patch.object(state, 'scratch_directory', return_value=self.root/'owned') as locate, \
             redirect_stdout(io.StringIO()) as out:
            state.main()
        locate.assert_called_once_with(Path(state.__file__).resolve().parents[1], 'owned', create=True)
        self.assertEqual(out.getvalue().strip(), str(self.root/'owned'))
        with patch.object(sys, 'argv', ['codex_state.py', 'scratch']), patch.dict(os.environ, {}, clear=True), \
             redirect_stderr(io.StringIO()) as err:
            with self.assertRaises(SystemExit) as stopped:
                state.main()
        self.assertEqual(stopped.exception.code, 1)
        self.assertIn('Codex scratch', err.getvalue())
        with patch.object(sys, 'argv', ['codex_state.py', 'unknown']), \
             patch.object(state, 'scratch_directory') as locate, redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as invalid:
                state.main()
        self.assertEqual(invalid.exception.code, 2)
        locate.assert_not_called()
        env = dict(os.environ);env.pop('CODEX_THREAD_ID', None)
        result = subprocess.run([sys.executable, str(ROOT/'tools/codex_state.py'), 'scratch'],
                                env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('actual thread identity', result.stderr)


if __name__ == '__main__':
    unittest.main()
