import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

SPEC = importlib.util.spec_from_file_location(
    'refusal_gate', Path(__file__).resolve().parents[1] / 'hooks' / 'refusal_gate.py')
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def use(ident, name, tool_input):
    return {'type': 'assistant', 'message': {'content': [
        {'type': 'tool_use', 'id': ident, 'name': name, 'input': tool_input}]}}


def result(ident, text, error=False):
    return {'type': 'user', 'message': {'content': [
        {'type': 'tool_result', 'tool_use_id': ident, 'content': text, 'is_error': error}]}}


class RefusalGateTest(unittest.TestCase):
    def transcript(self, entries):
        folder = tempfile.mkdtemp()
        path = Path(folder) / 't.jsonl'
        path.write_text(''.join(json.dumps(e) + '\n' for e in entries))
        return str(path)

    def run_hook(self, transcript, target):
        payload = {'tool_name': 'Edit', 'tool_input': {'file_path': target}, 'transcript_path': transcript}
        err = io.StringIO()
        with mock.patch('sys.stdin', io.StringIO(json.dumps(payload))), redirect_stderr(err):
            return gate.main(), err.getvalue()

    def test_an_edit_after_a_refusal_is_refused_until_the_code_is_read(self):
        # 18 October 2026: an append's refusal ("Where we stand is unchanged") answered by an edit of its draft.
        refused = [use('a', 'Bash', {'command': 'python3 tools/notebook-append.py /tmp/x/cs.html --notebook um'}),
                   result('a', 'Exit code 1\nnotebook-append.py: the Smallest case leaves its instance uncomputed', True)]
        code, err = self.run_hook(self.transcript(refused), '/tmp/x/cs.html')
        self.assertEqual(code, 2)
        self.assertIn('leaves its instance uncomputed', err)
        read = refused + [use('b', 'Bash', {'command': 'grep -rn "leaves its instance" tools/*.py'}), result('b', 'x')]
        self.assertEqual(self.run_hook(self.transcript(read), '/tmp/x/cs.html')[0], 0)
        opened = refused + [use('c', 'Read', {'file_path': '/repo/tools/notebook-append.py'}), result('c', 'x')]
        self.assertEqual(self.run_hook(self.transcript(opened), '/tmp/x/cs.html')[0], 0)
        # the bypass tried before the commit: an unrelated grep or file of tools/ does not count as reading the code
        unrelated = refused + [use('d', 'Bash', {'command': 'grep -c x tools/README.md'}), result('d', '0')]
        self.assertEqual(self.run_hook(self.transcript(unrelated), '/tmp/x/cs.html')[0], 2)
        other = refused + [use('e', 'Read', {'file_path': '/repo/tools/lead_queue.py'}), result('e', 'x')]
        self.assertEqual(self.run_hook(self.transcript(other), '/tmp/x/cs.html')[0], 2)
        named = refused + [use('f', 'Bash', {'command': 'sed -n 200,240p tools/notebook-append.py'}), result('f', 'x')]
        self.assertEqual(self.run_hook(self.transcript(named), '/tmp/x/cs.html')[0], 0)

    def test_a_file_the_refused_command_does_not_name_is_not_gated(self):
        refused = [use('a', 'Bash', {'command': 'python3 tools/notebook-append.py /tmp/x/cs.html'}),
                   result('a', 'Exit code 1\nnotebook-append.py: refused', True)]
        self.assertEqual(self.run_hook(self.transcript(refused), '/tmp/x/other.html')[0], 0)
        # a basename inside another word is not the file
        self.assertEqual(self.run_hook(self.transcript(refused), '/tmp/y/s.html')[0], 0)

    def test_a_later_successful_run_or_a_guard_refusal_does_not_gate(self):
        entries = [use('a', 'Bash', {'command': 'python3 tools/notebook-append.py /tmp/x/cs.html'}),
                   result('a', 'Exit code 1\nnotebook-append.py: refused', True),
                   use('b', 'Bash', {'command': 'python3 tools/notebook-append.py /tmp/x/cs.html'}),
                   result('b', 'Appended')]
        self.assertEqual(self.run_hook(self.transcript(entries), '/tmp/x/cs.html')[0], 0)
        guard = [use('a', 'Bash', {'command': 'sed -i s/a/b/ /tmp/x/cs.html'}),
                 result('a', 'PreToolUse:Bash hook error: Refused: sed -i replaces prose', True)]
        self.assertEqual(self.run_hook(self.transcript(guard), '/tmp/x/cs.html')[0], 0)

    def test_a_skeleton_check_gates_only_when_its_failures_repeat(self):
        first = [use('a', 'Bash', {'command': 'python3 tools/notebook-append.py /tmp/x/cs.html --check'}),
                 result('a', 'Exit code 1\nFAILS where we stand: unchanged\nFAILS append: no Smallest case', True)]
        self.assertEqual(self.run_hook(self.transcript(first), '/tmp/x/cs.html')[0], 0)
        changed = first + [use('b', 'Bash', {'command': 'python3 tools/notebook-append.py /tmp/x/cs.html --check'}),
                           result('b', 'Exit code 1\nFAILS where we stand: unchanged', True)]
        self.assertEqual(self.run_hook(self.transcript(changed), '/tmp/x/cs.html')[0], 0)
        same = changed + [use('c', 'Bash', {'command': 'python3 tools/notebook-append.py /tmp/x/cs.html --check'}),
                          result('c', 'Exit code 1\nFAILS where we stand: unchanged', True)]
        self.assertEqual(self.run_hook(self.transcript(same), '/tmp/x/cs.html')[0], 2)

    def test_copies_of_messages_in_other_records_are_not_calls(self):
        # 18 October 2026: a request record carried a copy of the check, which counted as its own earlier repeat.
        check = use('a', 'Bash', {'command': 'python3 tools/notebook-append.py /tmp/x/fl.html --check'})
        copy = dict(check, type='api-request')
        once = [copy, check, result('a', 'Exit code 1\nFAILS where we stand: unchanged', True)]
        self.assertEqual(self.run_hook(self.transcript(once), '/tmp/x/fl.html')[0], 0)
        twice = [check, check, result('a', 'Exit code 1\nFAILS where we stand: unchanged', True)]
        self.assertEqual(self.run_hook(self.transcript(twice), '/tmp/x/fl.html')[0], 0)

    def test_a_commit_message_refusal_gates_the_message_file(self):
        refused = [use('a', 'Bash', {'command': 'git commit -q -F /tmp/x/commit.txt'}),
                   result('a', '1 staged articles\ncommit-msg: the message does not carry its condition', True)]
        self.assertEqual(self.run_hook(self.transcript(refused), '/tmp/x/commit.txt')[0], 2)
        # 18 October 2026: a read of the module that prints the commit-msg refusals did not count.
        read = refused + [use('b', 'Bash', {'command': 'sed -n 116,160p tools/commit_message_checks.py'}),
                          result('b', 'def dropped_conditions(...)')]
        self.assertEqual(self.run_hook(self.transcript(read), '/tmp/x/commit.txt')[0], 0)
        other = refused + [use('b', 'Bash', {'command': 'sed -n 1,20p tools/lead_queue.py'}), result('b', 'x')]
        self.assertEqual(self.run_hook(self.transcript(other), '/tmp/x/commit.txt')[0], 2)

    def test_the_replay_lists_each_firing(self):
        entries = [use('a', 'Bash', {'command': 'python3 tools/notebook-append.py /tmp/x/cs.html'}),
                   result('a', 'Exit code 1\nnotebook-append.py: refused here', True),
                   use('b', 'Edit', {'file_path': '/tmp/x/cs.html'}), result('b', 'ok'),
                   use('c', 'Edit', {'file_path': '/tmp/x/other.html'}), result('c', 'ok')]
        lines = gate.replay(self.transcript(entries))
        self.assertEqual(lines[0], '3 tool calls read')
        self.assertEqual(lines[1], 'FIRES on cs.html | refused here')
        self.assertEqual(lines[-1], '2 edits or writes; 1 would be refused')

    def test_other_tools_and_a_missing_transcript_pass(self):
        payload = {'tool_name': 'Bash', 'tool_input': {'command': 'ls'}, 'transcript_path': '/nonexistent'}
        with mock.patch('sys.stdin', io.StringIO(json.dumps(payload))):
            self.assertEqual(gate.main(), 0)
        self.assertEqual(self.run_hook('/nonexistent', '/tmp/x/cs.html')[0], 0)


if __name__ == '__main__':
    unittest.main()
