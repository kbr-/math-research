"""Tests for tools/save-run-output.py."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('save_run_output', Path(__file__).resolve().parents[1] / 'save-run-output.py')
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class SaveRunOutputTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        logs = self.root / 'research' / 'logs'
        logs.mkdir(parents=True)
        (logs / 's1.jsonl').write_text(json.dumps({'event': 'run_start', 'id': 'abc', 'command': ['/scratch/kern', '7', 'x']}) + '\n')
        (logs / 's1-abc.output.txt').write_text('line one\nline two\n')

    def tearDown(self):
        self.tmp.cleanup()

    def test_copies_full_log_with_header(self):
        target = MOD.save('s1', 'abc', 'research/results/r/out.txt', ['/scratch/'], root=self.root)
        text = target.read_text()
        self.assertTrue(text.startswith('# command: kern 7 x\n# run abc, session s1; full output\n'))
        self.assertTrue(text.endswith('line one\nline two\n'))

    def test_refuses_overwrite_and_unknown_run(self):
        MOD.save('s1', 'abc', 'out.txt', root=self.root)
        with self.assertRaises(SystemExit):
            MOD.save('s1', 'abc', 'out.txt', root=self.root)
        with self.assertRaises(SystemExit):
            MOD.save('s1', 'zzz', 'other.txt', root=self.root)

    def test_refuses_path_outside_root(self):
        with self.assertRaises(ValueError):
            MOD.save('s1', 'abc', '../escape.txt', root=self.root)


if __name__ == '__main__':
    unittest.main()
