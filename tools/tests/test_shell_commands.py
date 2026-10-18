"""Execution-sensitive guards preserve quoted operators and refuse ambiguous shell control flow."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shell_commands import unambiguous_commands


class ShellCommandsTest(unittest.TestCase):
    def test_quoted_operators_comments_and_conditional_commands(self) -> None:
        self.assertEqual(unambiguous_commands('echo "|" cat "tools/file.py"'),
                         [['echo', '|', 'cat', 'tools/file.py']])
        self.assertEqual(unambiguous_commands('true # ; cat tools/file.py', chain=True), [['true']])
        self.assertEqual(unambiguous_commands('cd /r && cat "tools/file.py" | head -4', chain=True),
                         [['cd', '/r'], ['cat', 'tools/file.py'], ['head', '-4']])
        for command in ('true || cat tools/file.py', 'false && cat tools/file.py ; true',
                        'exit 0 && cat tools/file.py', 'exec true && cat tools/file.py',
                        'source script && cat tools/file.py', 'trap "exit 0" DEBUG && cat tools/file.py',
                        'set -n && cat tools/file.py', 'command exec true && cat tools/file.py',
                        'cat tools/file.py > copied', 'cat tools/file.py\ntrue', 'cat "unclosed'):
            with self.subTest(command=command):
                self.assertEqual(unambiguous_commands(command, chain=True), [])
        self.assertEqual(unambiguous_commands('search query && true'), [])
        # Bash help identifies these as control/evaluation/lookup builtins. The same words as arguments
        # have no control-flow effect and must not suppress a later real reader.
        for word in ('exit', 'exec', 'logout', 'return', 'break', 'continue', 'eval', 'source', '.', 'trap',
                     'set', 'shopt', 'enable', 'alias', 'unalias', 'hash'):
            with self.subTest(word=word):
                self.assertEqual(unambiguous_commands(f'echo {word} && cat tools/file.py', chain=True),
                                 [['echo', word], ['cat', 'tools/file.py']])
