"""Finisher status lookup and strict validation reuse one current registry parse."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('finisher_registry_test', ROOT / 'tools/finish-turn.py')
FT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FT)


class RegistrySnapshotTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / 'research/claims/index.json'
        self.path.parent.mkdir(parents=True)
        self.data = FT.read_json(ROOT / 'tools/tests/fixtures/claim-registry-sample.json')
        # This bounded fixture omits edges referenced by its full-registry review backlog.
        self.data['dependency_decisions'] = []
        self.path.write_text(json.dumps(self.data))
        FT._registry_snapshot.cache_clear()
        FT.registered_status.cache_clear()
        self.addCleanup(FT._registry_snapshot.cache_clear)
        self.addCleanup(FT.registered_status.cache_clear)

    def test_status_lookup_then_strict_load_reads_once(self):
        expected = {c['id']: c['mathematical_status'] for c in self.data['claims']}
        with mock.patch.object(FT, 'ROOT', self.root), mock.patch.object(
                sys.modules['claim_registry'], 'read_json', wraps=FT.read_json) as read:
            self.assertEqual(FT.registered_status(), expected)
            self.assertEqual(FT.load_claims(self.path), self.data)
            # the schema file is read too, by claim_registry itself; the registry is read once
            self.assertEqual([c for c in read.call_args_list if c.args == (self.path,)], [mock.call(self.path)])

    def test_changed_snapshot_is_read_and_still_validated(self):
        for version, time_delta, size_delta in ((9, 1, 0), (99, 0, 1)):
            with self.subTest(version=version):
                self.path.write_text(json.dumps(self.data))
                FT._registry_snapshot.cache_clear()
                FT.load_claims(self.path)
                before = self.path.stat()
                text = self.path.read_text()
                self.path.write_text(text.replace('"schema_version": 2', f'"schema_version": {version}', 1))
                self.assertEqual(self.path.stat().st_size, before.st_size + size_delta)
                os.utime(self.path, ns=(before.st_atime_ns, before.st_mtime_ns + time_delta))
                with self.assertRaisesRegex(ValueError, 'Unsupported claim schema version'):
                    FT.load_claims(self.path)


if __name__ == '__main__':
    unittest.main()
