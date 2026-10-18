"""Compression experiment preserves source bytes and rejects incomplete timing input."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import provenance_compression as probe


class CompressionTest(unittest.TestCase):
    def test_sample_roundtrip_and_synthetic_reproducibility(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / 'research/provenance/session-records/example'
            results = root / 'research/results/example'
            archive.mkdir(parents=True)
            results.mkdir(parents=True)
            journal = archive / 'session.jsonl'
            journal.write_text('\n'.join(json.dumps(row) for row in [
                {'event': 'run_start', 'id': 'job', 'monotonic_s': 10},
                {'event': 'run_end', 'id': 'job', 'monotonic_s': 12.5}]))
            data = b'raw output\n' * 100
            (results / 'output.txt').write_bytes(data)
            out = root / 'out'
            out.mkdir()
            result = probe.sample(root, 'example', out)
            self.assertEqual((result['runs'], result['run_seconds']), (1, 2.5))
            self.assertEqual(result['stored']['files'], 2)
            self.assertEqual((results / 'output.txt').read_bytes(), data)
            self.assertLess(result['stored']['compressed_bytes'], result['stored']['raw_bytes'])
            runs = probe.durations(journal)
            from evidence_io import compress_file
            compress_file(journal)
            journal.unlink()
            self.assertEqual(probe.durations(journal), runs)
            self.assertEqual(probe.telemetry(runs), probe.telemetry(runs))
            self.assertNotEqual(probe.telemetry(runs, 18), probe.telemetry(runs))
            self.assertIn(b'"synthetic":true', probe.telemetry(runs))

    def test_unfinished_run_is_not_fabricated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            journal = Path(temporary) / 'session.jsonl'
            journal.write_text('{"event":"run_start","id":"job","monotonic_s":10}\n')
            with self.assertRaisesRegex(ValueError, 'unfinished'):
                probe.durations(journal)
