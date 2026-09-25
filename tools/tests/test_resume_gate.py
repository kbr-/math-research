import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

spec = importlib.util.spec_from_file_location('resume_gate', Path(__file__).resolve().parents[1] / 'hooks/resume-gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class ResumeGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def call(self, mode, **payload):
        payload.setdefault('session_id', 's1')
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = getattr(gate, mode)(payload, self.root)
        return code, out.getvalue(), err.getvalue()

    def bash(self, command):
        return {'tool_name': 'Bash', 'tool_input': {'command': command}}

    def test_compaction_blocks_other_tools_until_last_part(self):
        code, out, _ = self.call('start')
        self.assertIn('Resume protocol', json.loads(out)['hookSpecificOutput']['additionalContext'])
        self.assertEqual(self.call('pre', **self.bash('which gap'))[0], 2)
        self.assertEqual(self.call('pre', tool_name='Edit', tool_input={'file_path': 'x'})[0], 2)
        self.assertEqual(self.call('pre', **self.bash('python3 tools/resume.py'))[0], 0)
        self.call('post', tool_response={'stdout': 'RESUME PART 1/2 ... NEXT'}, **self.bash('python3 tools/resume.py'))
        self.assertEqual(self.call('pre', **self.bash('ls'))[0], 2)
        self.call('post', tool_response={'stdout': 'END RESUME BUNDLE'},
                  **self.bash('python3 tools/resume.py --read abc --part 2'))
        self.assertEqual(self.call('pre', **self.bash('ls'))[0], 0)

    def test_other_sessions_and_unmarked_sessions_pass(self):
        self.call('start')
        self.assertEqual(self.call('pre', session_id='s2', **self.bash('ls'))[0], 0)
        self.call('post', session_id='s2', tool_response={'stdout': 'END RESUME BUNDLE'},
                  **self.bash('python3 tools/resume.py --read a --part 1'))
        self.assertEqual(self.call('pre', **self.bash('ls'))[0], 2)

    def test_end_text_from_another_command_does_not_clear(self):
        self.call('start')
        self.call('post', tool_response={'stdout': 'END RESUME BUNDLE'}, **self.bash('echo END RESUME BUNDLE'))
        self.assertEqual(self.call('pre', **self.bash('ls'))[0], 2)

    def test_stale_marks_are_removed_at_start(self):
        old = gate.mark_path(self.root, 'old')
        old.parent.mkdir(parents=True)
        old.write_text('x')
        with redirect_stdout(io.StringIO()):
            gate.start({'session_id': 's1'}, self.root, now=lambda: old.stat().st_mtime + gate.STALE_S + 1)
        self.assertFalse(old.exists())
        self.assertTrue(gate.mark_path(self.root, 's1').exists())


if __name__ == '__main__':
    unittest.main()
