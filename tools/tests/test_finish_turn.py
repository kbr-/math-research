#!/usr/bin/env python3
"""Focused integration checks using isolated metadata sessions and the real launcher."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class FinalizationTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='math-finish-turn-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'tools').mkdir()
        for name in ('compute.sh', 'tools/finish-turn.py', 'tools/archive-session.py'):
            shutil.copy2(ROOT / name, self.root / name)
        self.command('compute.sh', 'start', 'test_turn')

    def command(self, script, *args, check=True):
        return subprocess.run([sys.executable, str(self.root / script), *args],
                              cwd=self.root, text=True, capture_output=True, check=check)

    def events(self, name):
        return [json.loads(line) for line in
                (self.root / 'research/logs' / f'{name}.jsonl').read_text().splitlines()]

    def test_complete_and_start_next(self):
        notebook = self.root / 'notebook.html'
        notebook.write_text('earlier record\n<!-- TIMING test_turn -->\nappend here\n')
        self.command('tools/finish-turn.py', 'test_turn', '--next', 'next_turn')
        table = (self.root / 'research/results/test_turn/timing.html').read_text().strip()
        self.assertEqual(notebook.read_text(), f'earlier record\n{table}\nappend here\n')
        archive = self.root / 'research/provenance/session-records/test_turn'
        self.assertEqual((archive / 'session.jsonl').read_bytes(),
                         (self.root / 'research/logs/test_turn.jsonl').read_bytes())
        stop = next(e for e in self.events('test_turn') if e['event'] == 'stop')
        following = self.events('next_turn')
        self.assertGreaterEqual(following[0]['monotonic_s'], stop['monotonic_s'])
        self.assertTrue(any(e.get('category') == 'preparation' for e in following))
        self.assertFalse(any(e['event'] == 'stop' for e in following))
        repeated = self.command('tools/finish-turn.py', 'test_turn', check=False)
        self.assertNotEqual(repeated.returncode, 0)
        self.assertEqual(notebook.read_text(), f'earlier record\n{table}\nappend here\n')

    def test_duplicate_marker_does_not_stop_session(self):
        notebook = self.root / 'notebook.html'
        content = '<!-- TIMING test_turn -->\n' * 2
        notebook.write_text(content)
        result = self.command('tools/finish-turn.py', 'test_turn', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(notebook.read_text(), content)
        self.assertFalse(any(e['event'] == 'stop' for e in self.events('test_turn')))


if __name__ == '__main__':
    unittest.main()
