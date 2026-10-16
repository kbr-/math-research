import contextlib
from datetime import datetime
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import unittest.mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOLS), str(TOOLS / 'hooks')]
import bash_guard  # noqa: E402
import block_log  # noqa: E402
import during_run  # noqa: E402
import stop_checks  # noqa: E402


class BlockLogTest(unittest.TestCase):
    def test_a_block_is_logged_with_its_time_and_what_the_hook_said_and_only_inside_a_session(self):
        with tempfile.TemporaryDirectory() as scratch:
            log = Path(scratch) / 'state' / 'blocks.tsv'
            block_log.record('bash_guard', log, datetime(2026, 10, 10, 10, 0, 0))
            self.assertEqual(log.read_text(), '2026-10-10T10:00:00\tbash_guard\n')
            # What the hook said follows on the line, on one line and bounded.
            block_log.record('stop_checks', log, datetime(2026, 10, 10, 10, 2, 0), what='A promise:\t"x\nwill hold" ' + 'y' * 400)
            last = log.read_text().splitlines()[-1]
            self.assertTrue(last.startswith('2026-10-10T10:02:00\tstop_checks\tA promise: "x will hold" yyy'))
            self.assertEqual((last.count('\t'), len(last.split('\t')[2])), (2, 300))
            # A test run of a hook has no session, and writes nothing to the log; a session's hook does.
            default = Path(scratch) / 'default.tsv'
            with unittest.mock.patch.object(block_log, 'LOG', default):
                with unittest.mock.patch.dict('os.environ', clear=True):
                    block_log.record('x')
                with unittest.mock.patch.dict('os.environ', {'CLAUDE_PROJECT_DIR': scratch}):
                    block_log.record('x')
                self.assertFalse(default.exists())
                with unittest.mock.patch.dict('os.environ', {'CLAUDE_PROJECT_DIR': str(TOOLS.parent)}):
                    block_log.record('x')
                self.assertTrue(default.read_text().endswith('\tx\n'))

    def test_a_block_keeps_the_files_its_refused_call_named_and_reads_them_back(self):
        with tempfile.TemporaryDirectory() as scratch:
            log = Path(scratch) / 'blocks.tsv'
            command = "python3 - <<'EOF'\np='/home/u/tmp/spec.json'; open(p,'w')\nEOF\ncat /home/u/tmp/deps.md"
            self.assertEqual(block_log.paths_in(command), ['/home/u/tmp/spec.json', '/home/u/tmp/deps.md'])
            block_log.record('bash_guard', log, datetime(2026, 10, 16, 19, 0, 0), what='Refused: x',
                             paths=block_log.paths_in(command))
            block_log.record('bash_guard', log, datetime(2026, 10, 16, 19, 1, 0))
            self.assertEqual(block_log.blocks(log), [
                (datetime(2026, 10, 16, 19, 0, 0), 'bash_guard', ['/home/u/tmp/spec.json', '/home/u/tmp/deps.md']),
                (datetime(2026, 10, 16, 19, 1, 0), 'bash_guard', [])])
            self.assertEqual(block_log.blocks(Path(scratch) / 'missing.tsv'), [])

    def test_the_stop_hook_and_the_commit_checks_hand_the_log_what_they_said(self):
        with unittest.mock.patch.object(block_log, 'record') as record, contextlib.redirect_stdout(io.StringIO()):
            stop_checks.emit_block({'decision': 'block', 'reason': 'A declared gap: "x"'})
        record.assert_called_once_with('stop_checks', what='A declared gap: "x"')
        # The Bash guard keeps what a commit's checks said, for the line it logs when it exits with a block.
        payload = json.dumps({'tool_name': 'Bash', 'tool_input': {'command': 'git commit -m x'}, 'cwd': str(TOOLS.parent)})
        del bash_guard.SAID[:]
        with unittest.mock.patch.object(during_run, 'commit', return_value='A promise: "y"'), \
                unittest.mock.patch('sys.stdin', io.StringIO(payload)), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(bash_guard.main(), 2)
        self.assertEqual(bash_guard.SAID, ['A promise: "y"'])
        del bash_guard.SAID[:]
        with unittest.mock.patch.object(during_run, 'commit', return_value=None), \
                unittest.mock.patch('sys.stdin', io.StringIO(payload)):
            self.assertEqual(bash_guard.main(), 0)
        self.assertEqual(bash_guard.SAID, [])


if __name__ == '__main__':
    unittest.main()
