from datetime import datetime
from pathlib import Path
import sys
import tempfile
import unittest
import unittest.mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS / 'hooks'))
import block_log  # noqa: E402


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


if __name__ == '__main__':
    unittest.main()
