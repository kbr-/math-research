"""tools/haiku_judge.py against a stand-in `claude` on PATH."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import haiku_judge

ECHO = ('import json, sys\nprompt = sys.stdin.read()\n'
        'print(json.dumps({"result": json.dumps({"length": len(prompt), "tail": prompt[-5:]})}))\n')


class AskTest(unittest.TestCase):
    def setUp(self):
        self.bin = tempfile.TemporaryDirectory()
        self.addCleanup(self.bin.cleanup)

    def claude(self, body):
        """Put a `claude` running the Python `body` alone on PATH."""
        script = Path(self.bin.name) / 'claude'
        script.write_text(f'#!{sys.executable}\n{body}')
        script.chmod(0o755)
        return mock.patch.dict(os.environ, {'PATH': self.bin.name})

    def test_a_prompt_over_the_argument_limit_reaches_the_judge(self):
        prompt = 'x' * 200_000 + 'tail.'
        with self.claude(ECHO):
            verdict = haiku_judge.ask(prompt, 10)
        self.assertEqual(verdict['length'], len(prompt))
        self.assertEqual(verdict['tail'], 'tail.')

    def test_each_failure_names_its_cause(self):
        cases = (
            (None, 'claude could not run: '),
            ('import sys\nsys.stderr.write("Not logged in")\nsys.exit(1)\n',
             "claude exited 1 without its JSON output: 'Not logged in'"),
            ('print("[1]")\n', "claude printed JSON that is not an object: '[1]\\n'"),
            ('import json\nprint(json.dumps({"result": "I cannot judge this."}))\n',
             "the answer held no JSON object: 'I cannot judge this.'"),
        )
        for body, cause in cases:
            with self.subTest(cause=cause), (self.claude(body) if body else
                                             mock.patch.dict(os.environ, {'PATH': self.bin.name})):
                with self.assertRaises(haiku_judge.Failed) as raised:
                    haiku_judge.ask('prompt', 10)
                self.assertNotIsInstance(raised.exception, haiku_judge.Refused)
                self.assertTrue(str(raised.exception).startswith(cause), str(raised.exception))

    def test_an_answered_call_records_its_usage_under_the_asking_session(self):
        usage = {'input_tokens': 9, 'cache_creation_input_tokens': 6985, 'cache_read_input_tokens': 0,
                 'output_tokens': 71}
        models = {'claude-haiku-4-5-20251001': {'inputTokens': 9, 'outputTokens': 71, 'costUSD': 0.014334}}
        body = ('import json\nprint(json.dumps({"result": "{}", "usage": %r, "modelUsage": %r}))\n'
                % (usage, models))
        log = Path(self.bin.name) / 'logs' / 'model-usage.jsonl'
        with self.claude(body), mock.patch.object(haiku_judge, 'usage_log', lambda: log):
            haiku_judge.ask('prompt', 10, session='asking-session')
            with mock.patch.dict(os.environ, {'CLAUDE_CODE_SESSION_ID': 'environment-session'}):
                haiku_judge.ask('prompt', 10)
        lines = [json.loads(line) for line in log.read_text().splitlines()]
        self.assertEqual([line['session'] for line in lines], ['asking-session', 'environment-session'])
        self.assertEqual(lines[0]['usage'], usage)
        self.assertEqual(lines[0]['models'], models)
        self.assertTrue(lines[0]['at'].endswith('Z'))

    def test_a_call_without_usage_records_nothing(self):
        log = Path(self.bin.name) / 'model-usage.jsonl'
        with self.claude(ECHO), mock.patch.object(haiku_judge, 'usage_log', lambda: log):
            haiku_judge.ask('prompt', 10, session='asking-session')
        self.assertFalse(log.exists())

    def test_the_log_is_the_main_checkouts(self):
        with tempfile.TemporaryDirectory() as directory:
            main, linked = Path(directory) / 'main', Path(directory) / 'linked'
            run = lambda *args, cwd=main: __import__('subprocess').run(args, cwd=cwd, check=True, capture_output=True)
            main.mkdir()
            run('git', 'init', '-q')
            run('git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '--allow-empty', '-m', 'base')
            run('git', 'worktree', 'add', '-q', str(linked))
            self.assertEqual(haiku_judge.usage_log(linked), main.resolve() / 'research/logs/model-usage.jsonl')


if __name__ == '__main__':
    unittest.main()
