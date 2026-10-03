import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SETTINGS = ROOT / '.claude' / 'settings.json'
NEUTRAL = json.dumps({'session_id': 'hook-settings-test', 'tool_name': 'Read', 'tool_input': {'file_path': 'x'},
                      'cwd': '.'})


def commands():
    hooks = json.loads(SETTINGS.read_text())['hooks']
    return [(event, hook['command']) for event, groups in hooks.items() for group in groups
            for hook in group['hooks'] if hook.get('type') == 'command']


class HookSettingsTest(unittest.TestCase):
    """A hook command whose script is missing must not block: Python exits 2 for a missing script, and Claude
    Code reads exit status 2 from a PreToolUse hook as a refusal of the tool call.  Hooks resolve through
    $CLAUDE_PROJECT_DIR, the main checkout, which can lag a worktree that adds a hook (3 October 2026, when a
    new hook locked every tool call of a session)."""

    def run_all(self, project):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project))
        return {(event, command): subprocess.run(['sh', '-c', command], input=NEUTRAL, text=True,
                                                 capture_output=True, env=env, timeout=20)
                for event, command in commands()}

    def test_missing_scripts_warn_without_blocking(self):
        # exit 1 is a non-blocking hook error whose stderr the user sees (user, 3 October 2026: "print something
        # so I can see that it's missing, instead of failing silently")
        with tempfile.TemporaryDirectory() as empty:
            for (event, command), result in self.run_all(empty).items():
                with self.subTest(event=event, command=command):
                    self.assertEqual(result.returncode, 1)
                    self.assertIn('is missing', result.stderr)

    def test_present_scripts_allow_a_neutral_call(self):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / 'tools').symlink_to(ROOT / 'tools')
            for (event, command), result in self.run_all(root).items():
                with self.subTest(event=event, command=command):
                    self.assertEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
