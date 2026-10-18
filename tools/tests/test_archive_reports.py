import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evidence_io import read_bytes, compress_file

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
        self.assertTrue(entry['archived_path'].endswith('.zst'))
        self.assertEqual(read_bytes(self.module.DEST / 'turn' / entry['archived_path']),
                         self.output.read_bytes())

    def test_existing_archive_layout_is_not_rewritten(self):
        entry = self.archive()  # No canonical report exists yet.
        target = self.module.DEST / 'turn'
        manifest = json.loads((target / 'manifest.json').read_text())
        for row in manifest:
            saved = target / row['archived_path']
            if saved.suffix == '.zst':
                saved.with_suffix('').write_bytes(read_bytes(saved))
                saved.unlink()
                row['archived_path'] = row['archived_path'][:-4]
        (target / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        entry = manifest[-1]
        self.report.write_bytes(self.output.read_bytes())
        self.assertEqual(self.archive(), entry)
        self.assertIn('archived_path', entry)

    def test_outside_results_is_never_a_canonical_report(self):
        other = self.root / 'scratch.txt'
        other.write_bytes(self.output.read_bytes())
        self.events[1]['command'][-1] = str(other)
        self.assertIn('archived_path', self.archive())

    def test_large_single_line_is_lossless_utf8_and_immutable(self):
        self.module.OUTPUT_PART_BYTES = 11
        payload = ('abc🚀λXYZ' * 7).encode()
        self.output.write_bytes(payload)
        entry = self.archive()
        paths = [self.module.DEST / 'turn' / p['archived_path']
                 for p in entry['archived_parts']]
        self.assertGreater(len(paths), 1)
        self.assertEqual(b''.join(read_bytes(p) for p in paths), payload)
        for path in paths:
            self.assertLessEqual(len(read_bytes(path)), 11)
            read_bytes(path).decode('utf-8')
        self.assertEqual(self.archive(), entry)
        paths[1].write_bytes(b'changed')
        with self.assertRaises((RuntimeError, OSError)):
            self.archive()

    def test_missing_or_reordered_parts_fail(self):
        self.module.OUTPUT_PART_BYTES = 8
        self.output.write_text('0123456789abcdefghijklmnopqrstuvwxyz')
        entry = self.archive()
        target = self.module.DEST / 'turn'
        reversed_entry = dict(entry, archived_parts=list(reversed(entry['archived_parts'])))
        with self.assertRaises(RuntimeError):
            self.module.verify_parts(target, reversed_entry)
        (target / entry['archived_parts'][0]['archived_path']).unlink()
        with self.assertRaises(RuntimeError):
            self.archive()

    def test_existing_single_file_stays_single_after_limit_changes(self):
        entry = self.archive()
        self.module.OUTPUT_PART_BYTES = 8
        self.assertEqual(self.archive(), entry)

    def test_raw_bytes_are_not_dropped(self):
        self.module.OUTPUT_PART_BYTES = 8
        payload = b'abc\xff\xfe\xf0\x9f\x9a\x80xyz\xe2'
        self.output.write_bytes(payload)
        entry = self.archive()
        self.assertEqual(b''.join(read_bytes(self.module.DEST / 'turn' / p['archived_path'])
                                 for p in entry['archived_parts']), payload)

    def test_compressed_declared_report_is_canonical(self) -> None:
        self.report.write_bytes(self.output.read_bytes())
        compress_file(self.report)
        self.report.unlink()
        entry = self.archive()
        self.assertEqual(entry['canonical_path'], 'results/turn/verification.txt.zst')
        self.assertEqual(self.archive(), entry)

    def test_legacy_raw_parts_remain_byte_identical(self) -> None:
        self.module.OUTPUT_PART_BYTES = 8
        self.output.write_text('abcdefghijklmnopqrstuvwxyz')
        self.archive()
        target = self.module.DEST / 'turn'
        manifest = json.loads((target / 'manifest.json').read_text())
        for part in manifest[-1]['archived_parts']:
            packed = target / part['archived_path']
            packed.with_suffix('').write_bytes(read_bytes(packed))
            packed.unlink()
            part['archived_path'] = part['archived_path'][:-4]
        (target / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        self.assertEqual(self.archive(), manifest[-1])

    def test_manifest_cannot_redirect_archival_outside_its_directory(self) -> None:
        self.archive()
        target = self.module.DEST / 'turn'
        manifest = json.loads((target / 'manifest.json').read_text())
        manifest[-1]['archived_path'] = '../../../escaped.txt.zst'
        (target / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        with self.assertRaisesRegex(RuntimeError, 'Unsafe archived'):
            self.archive()


if __name__ == '__main__':
    unittest.main()
