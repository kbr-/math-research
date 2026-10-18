"""Evidence compression through real zstd and the installed pre-commit entry point."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import evidence_io as evidence

TOOL = Path(evidence.__file__)


class EvidenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(['git', '-C', str(self.root), *args], capture_output=True, text=True)

    def test_binary_roundtrip_refuses_overwrite_and_detects_corruption(self) -> None:
        source = self.root / 'binary.dat'
        data = bytes(range(256)) * 100
        source.write_bytes(data)
        packed = evidence.compress_file(source)
        self.assertEqual(evidence.read_bytes(packed), data)
        self.assertEqual(source.read_bytes(), data)
        with self.assertRaises(FileExistsError):
            evidence.compress_file(source)
        packed.write_bytes(packed.read_bytes()[:-2])
        with self.assertRaises(OSError):
            evidence.read_bytes(packed)

    def test_failed_compressor_leaves_source_and_no_destination(self) -> None:
        source = self.root / 'data.txt'
        source.write_text('evidence')
        with patch.object(evidence.subprocess, 'run', side_effect=FileNotFoundError('zstd')):
            with self.assertRaises(FileNotFoundError):
                evidence.compress_file(source)
        self.assertEqual(source.read_text(), 'evidence')
        self.assertFalse(source.with_suffix('.txt.zst').exists())

    def test_real_precommit_blocks_new_raw_but_keeps_legacy_and_readable_files(self) -> None:
        self.git('init', '-q')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        folder = self.root / 'research/results/example'
        folder.mkdir(parents=True)
        legacy = folder / 'old.txt'
        legacy.write_text('historical data')
        self.git('add', '.')
        self.assertEqual(self.git('commit', '-qm', 'baseline').returncode, 0)
        tools = self.root / 'tools'
        tools.mkdir()
        shutil.copy2(TOOL, tools / TOOL.name)
        hook = self.root / '.git/hooks/pre-commit'
        shutil.copy2(TOOL.parent / 'git-hooks/pre-commit', hook)
        hook.chmod(0o755)
        data = folder / 'new.txt'
        data.write_text('new data')
        (folder / 'summary.json').write_text('{}')
        (folder / 'spec.py').write_text('TESTS = []\n')
        self.git('add', '.')
        failed = self.git('commit', '-qm', 'new evidence')
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn('New result/provenance data', failed.stderr)
        packed = evidence.compress_file(data)
        data.unlink()
        self.git('add', '-A')
        # Validate the index, not an unstaged working-tree replacement.
        original = packed.read_bytes()
        packed.write_bytes(b'not a frame')
        self.assertEqual(evidence.invalid_staged_zstd(self.root), [])
        self.git('add', str(packed))
        self.assertEqual(evidence.invalid_staged_zstd(self.root), [str(packed.relative_to(self.root))])
        refused = self.git('commit', '-qm', 'invalid compressed evidence')
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn('Invalid staged zstd evidence', refused.stderr)
        packed.write_bytes(original)
        self.git('add', str(packed))
        done = self.git('commit', '-qm', 'compressed evidence')
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(legacy.read_text(), 'historical data')

    def test_cli_replace_preserves_history_and_prints_real_path(self) -> None:
        self.git('init', '-q')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        folder = self.root / 'research/results'
        folder.mkdir(parents=True)
        old = folder / 'old.txt'
        old.write_text('old')
        self.git('add', '.')
        self.git('commit', '-qm', 'old')
        result = subprocess.run([sys.executable, str(TOOL), 'pack', '--replace', str(old)],
                                cwd=self.root, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(old.exists())
        new = folder / 'new.txt'
        new.write_text('new')
        extra = folder / 'new-batch'
        extra.mkdir()
        (extra / 'data.txt').write_text('batch')
        (extra / 'summary.json').write_text('{}')
        result = subprocess.run([sys.executable, str(TOOL), 'pack', '--replace', str(new), str(extra)],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('new.txt.zst', result.stdout)
        self.assertFalse(new.exists())
        self.assertEqual(evidence.read_text(new.with_suffix('.txt.zst')), 'new')
        self.assertEqual(evidence.read_text(extra / 'data.txt.zst'), 'batch')
        self.assertTrue((extra / 'summary.json').exists())
