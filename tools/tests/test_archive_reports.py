import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'archive-session.py'


class ArchiveReportsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        spec = importlib.util.spec_from_file_location('archive_reports', SOURCE)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.root = Path(self.temp.name)
        self.module.RESEARCH = self.root / 'research'
        self.module.LOGS = self.root / 'research/logs'
        self.module.DEST = self.root / 'research/provenance/session-records'
        self.module.LOGS.mkdir(parents=True)
        self.report = self.root / 'research/results/turn/verification.txt'
        self.report.parent.mkdir(parents=True)
        self.output = self.module.LOGS / 'turn-output.txt'
        self.output.write_text('complete output\n')
        self.journal = self.module.LOGS / 'turn.jsonl'
        self.journal.with_suffix('.summary.json').write_text('{}\n')
        self.events = [{'event': 'start'}, {'event': 'run_start',
                       'output': 'logs/turn-output.txt',
                       'command': ['python3', 'formalization/verify.py', '--out',
                                   'research/results/turn/verification.txt']},
                       {'event': 'run_end'}, {'event': 'stop'}]

    def archive(self):
        self.journal.write_text(''.join(json.dumps(e) + '\n' for e in self.events))
        self.module.archive(self.journal)
        manifest = self.module.DEST / 'turn/manifest.json'
        return json.loads(manifest.read_text())[-1]

    def test_identical_report_is_canonical_and_immutable(self):
        self.report.write_bytes(self.output.read_bytes())
        entry = self.archive()
        self.assertEqual(entry['canonical_path'], 'results/turn/verification.txt')
        self.assertNotIn('archived_path', entry)
        self.assertFalse((self.module.DEST / 'turn/outputs/turn-output.txt').exists())
        self.assertEqual(self.archive(), entry)
        self.report.write_text('changed\n')
        with self.assertRaises(RuntimeError):
            self.archive()
        self.report.unlink()
        with self.assertRaises(RuntimeError):
            self.archive()

    def test_different_output_keeps_all_diagnostics(self):
        self.report.write_text('only part of output\n')
        entry = self.archive()
        self.assertIn('archived_path', entry)
        self.assertEqual((self.module.DEST / 'turn' / entry['archived_path']).read_bytes(),
                         self.output.read_bytes())

    def test_existing_archive_layout_is_not_rewritten(self):
        entry = self.archive()  # No canonical report exists yet.
        self.report.write_bytes(self.output.read_bytes())
        self.assertEqual(self.archive(), entry)
        self.assertIn('archived_path', entry)

    def test_outside_results_is_never_a_canonical_report(self):
        other = self.root / 'scratch.txt'
        other.write_bytes(self.output.read_bytes())
        self.events[1]['command'][-1] = str(other)
        self.assertIn('archived_path', self.archive())


if __name__ == '__main__':
    unittest.main()
