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
        self.command('compute.sh', 'start', 'test_turn', '--agent', 'Test agent',
                     '--model', 'Test model, high')

    def command(self, script, *args, check=True):
        return subprocess.run([sys.executable, str(self.root / script), *args],
                              cwd=self.root, text=True, capture_output=True, check=check)

    def events(self, name):
        return [json.loads(line) for line in
                (self.root / 'research/logs' / f'{name}.jsonl').read_text().splitlines()]

    def test_complete_and_start_next(self):
        notebook = self.root / 'notebook.html'
        content = ('<section id="research-record">\nearlier record\n'
                   '<article id="new-entry">\n<p class="entry-meta">Status: test.</p>\n'
                   '<!-- TIMING test_turn -->\n'
                   '</article>\nappend here\n</section>\n')
        notebook.write_text(content)
        self.command('tools/finish-turn.py', 'test_turn', '--next', 'next_turn')
        table = (self.root / 'research/results/test_turn/timing.html').read_text().strip()
        expected = content.replace('<!-- TIMING test_turn -->', table).replace(
            'Status: test.</p>', 'Status: test. Produced by Test agent (Test model, high).</p>')
        self.assertEqual(notebook.read_text(), expected)
        archive = self.root / 'research/provenance/session-records/test_turn'
        self.assertEqual((archive / 'session.jsonl').read_bytes(),
                         (self.root / 'research/logs/test_turn.jsonl').read_bytes())
        stop = next(e for e in self.events('test_turn') if e['event'] == 'stop')
        following = self.events('next_turn')
        self.assertGreaterEqual(following[0]['monotonic_s'], stop['monotonic_s'])
        self.assertTrue(any(e.get('category') == 'preparation' for e in following))
        self.assertFalse(any(e['event'] == 'stop' for e in following))
        self.assertEqual((following[0]['agent'], following[0]['model']),
                         ('Test agent', 'Test model, high'))
        repeated = self.command('tools/finish-turn.py', 'test_turn', check=False)
        self.assertNotEqual(repeated.returncode, 0)
        self.assertEqual(notebook.read_text(), expected)

    def test_misplaced_marker_does_not_stop_session(self):
        notebook = self.root / 'notebook.html'
        marker = '<!-- TIMING test_turn -->'
        cases = [
            '<section id="overview"><article>' + marker + '</article></section>'
            '<section id="research-record"></section>',
            '<section id="research-record">' + marker + '</section>',
            '<section id="research-record"><article></article></section>' + marker,
            '<section id="research-record"><article>' + marker + '</article></section>',
            '<section id="research-record"><article><p class="entry-meta">Status.</p>'
            'It cost $5.' + marker + '</article></section>',
        ]
        for content in cases:
            with self.subTest(content=content):
                notebook.write_text(content)
                result = self.command('tools/finish-turn.py', 'test_turn', check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(notebook.read_text(), content)
                self.assertFalse(any(e['event'] == 'stop' for e in self.events('test_turn')))

    def test_route_review_and_status_length_are_enforced(self):
        notebook = self.root / 'notebook.html'
        marker = '<!-- TIMING test_turn -->'
        route = '<section id="remaining-route"><li data-route-item="general-step">x</li></section>'
        def record(earlier, tags, status='Status.'):
            entries = ''.join(f'<article data-kind="{kind}" data-route="general-step"></article>'
                              for kind in earlier)
            return (route + '<section id="research-record">' + entries + f'<article {tags}>'
                    f'<p class="entry-meta">{status}</p>' + marker + '</article></section>')
        tagged = 'data-kind="research" data-route="general-step"'
        rejected = [
            record([], ''),                                           # untagged entry
            record([], 'data-kind="research" data-route="sub-gap"'),  # not a declared route item
            record(['research'] * 6, tagged),                         # seventh research entry in a row
            record(['review'] + ['research', 'formalization'] * 6, tagged),
            record([], tagged, status='S' * 301),
        ]
        for content in rejected:
            with self.subTest(content=content[:160]):
                notebook.write_text(content)
                result = self.command('tools/finish-turn.py', 'test_turn', check=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(any(e['event'] == 'stop' for e in self.events('test_turn')))
        accepted = [
            record(['research'] * 6, 'data-kind="review" data-route="general-step"'),
            record(['research'] * 6 + ['review'] + ['research'] * 5, tagged),
            record(['research'] * 9, 'data-kind="formalization"'),
            record(['research'] * 3, 'data-kind="research" data-route="side-preprint"'),
        ]
        for content in accepted:
            with self.subTest(content=content[:160]):
                body = self.root / 'check.py'
                body.write_text('import importlib.util, sys\n'
                                'spec = importlib.util.spec_from_file_location("ft", "tools/finish-turn.py")\n'
                                'ft = importlib.util.module_from_spec(spec); spec.loader.exec_module(ft)\n'
                                'ft.validate_marker(open("notebook.html").read(), sys.argv[1])\n')
                notebook.write_text(content)
                self.command('check.py', marker)

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
