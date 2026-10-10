"""tools/haiku_judge.py against a stand-in `claude` on PATH."""
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


if __name__ == '__main__':
    unittest.main()
