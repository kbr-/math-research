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
        for name in ('compute.sh', 'tools/finish-turn.py', 'tools/archive-session.py', 'tools/claim_registry.py', 'tools/claim_notices.py', 'tools/claim_maintenance.py', 'tools/claim_reviews.py', 'tools/claim_evidence.py', 'tools/notebook-excerpt.py', 'tools/claim_registration.py'):
            shutil.copy2(ROOT / name, self.root / name)
        (self.root / 'research/claims').mkdir(parents=True)
        for schema in ('schema.json', 'schema-v1.json'):
            shutil.copy2(ROOT / 'research/claims' / schema, self.root / 'research/claims' / schema)
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
        table = table.replace('<div class="timing-report"', '<div data-generated="finish-turn-timing-v1" class="timing-report"', 1)
        expected = content.replace('<!-- TIMING test_turn -->', table).replace(
            'Status: test.</p>', 'Status: test. <span data-generated="finish-turn-producer-v1">Produced by Test agent (Test model, high).</span></p>')
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

    def test_incomplete_new_claim_is_rejected_before_clock_stops(self):
        sys.path.insert(0,str(ROOT/'tools'))
        import claim_registry as cr
        data=cr.upgrade(cr.import_markdown('# Index\n\n'+cr.HEADER+
            '| `lem:new` | New statement | Working proof | [Proof](source.md) |\n'))
        complete_path=self.root/'research/claims/index.json'
        empty=dict(data,claims=[])
        complete_path.write_text(json.dumps(empty))
        (self.root/'research/CLAIM_INDEX.md').write_text(cr.render(empty))
        (self.root/'research/source.md').write_text('Source')
        subprocess.run(['git','init','-q'],cwd=self.root,check=True)
        subprocess.run(['git','add','research'],cwd=self.root,check=True)
        subprocess.run(['git','-c','user.name=Test','-c','user.email=test@example.invalid',
                        'commit','-qm','Baseline'],cwd=self.root,check=True)
        complete_path.write_text(json.dumps(data))
        (self.root/'research/CLAIM_INDEX.md').write_text(cr.render(data))
        notebook=self.root/'notebook.html'
        notebook.write_text('<section id="research-record"><article id="new-entry">'
            '<p class="entry-meta">Status: test.</p><!-- TIMING test_turn --></article></section>')
        result=self.command('tools/finish-turn.py','test_turn',check=False)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Changed-claim metadata incomplete',result.stderr)
        self.assertFalse(any(e['event']=='stop' for e in self.events('test_turn')))
        complete_path.write_text(json.dumps(empty))
        (self.root/'research/CLAIM_INDEX.md').write_text(cr.render(empty))
        notebook.write_text('<section id="research-record"><article id="new-entry" '
            'data-claims="none" data-claim-note="Framework-only">'
            '<p class="entry-meta">Status: test.</p><code>lem:forgotten</code>'
            '<!-- TIMING test_turn --></article></section>')
        result=self.command('tools/finish-turn.py','test_turn',check=False)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('explicit claim label is unregistered',result.stderr)
        self.assertFalse(any(e['event']=='stop' for e in self.events('test_turn')))


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

    def test_append_only_check_flags_edits_but_not_link_repairs(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('cao', ROOT / 'tools/check-append-only.py')
        cao = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cao)
        base = ('<section id="research-record"><article id="a"><p>Claim one.</p></article>'
                '<article id="b"><p>See the lemma.</p></article></section>')
        appended = base.replace('</section>', '<article id="c"><p>New.</p></article></section>')
        linked = base.replace('the lemma', '<a href="#x">the lemma</a>')
        self.assertEqual(cao.violations(base, appended), ([], []))
        self.assertEqual(cao.violations(base, linked), ([], []))
        self.assertEqual(cao.violations(base, base.replace('Claim one.', 'Claim 1.')), ([], ['a']))
        self.assertEqual(cao.violations(base, base.replace('<article id="b"><p>See the lemma.</p></article>', '')),
                         (['b'], []))

    def test_duplicate_marker_does_not_stop_session(self):
        notebook = self.root / 'notebook.html'
        content = '<!-- TIMING test_turn -->\n' * 2
        notebook.write_text(content)
        result = self.command('tools/finish-turn.py', 'test_turn', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(notebook.read_text(), content)
        self.assertFalse(any(e['event'] == 'stop' for e in self.events('test_turn')))

    def test_stale_claim_view_does_not_stop_session(self):
        data = {'schema_version': 1, 'preamble': '# Index\n\n', 'claims': [], 'relationships': []}
        (self.root / 'research/claims/index.json').write_text(json.dumps(data))
        (self.root / 'research/CLAIM_INDEX.md').write_text('stale view\n')
        (self.root / 'notebook.html').write_text(
            '<section id="research-record"><article><p class="entry-meta">Status.</p>'
            '<!-- TIMING test_turn --></article></section>')
        result = self.command('tools/finish-turn.py', 'test_turn', check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('claim index is stale', result.stderr)
        self.assertFalse(any(e['event'] == 'stop' for e in self.events('test_turn')))


if __name__ == '__main__':
    unittest.main()
