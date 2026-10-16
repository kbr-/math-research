import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import claim_refresh


class ClaimRefreshTests(unittest.TestCase):
    def test_refresh_restores_removes_builds_copies_and_renders_in_that_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / 'research/claims').mkdir(parents=True)
            for name in ('out.json', 'report.json'):
                (root / name).write_text('stale')
            calls = []

            def fake_run(command, cwd, check):
                calls.append(command)
                self.assertTrue(check)
                if 'build' in command:
                    # The stale outputs are gone before the build writes new ones.
                    self.assertFalse((root / 'out.json').exists())
                    self.assertFalse((root / 'report.json').exists())
                    (root / 'proposal.json').write_text('{"claims": []}')

            with mock.patch.object(claim_refresh.subprocess, 'run', fake_run):
                claim_refresh.refresh('spec.json', 'out.json', 'proposal.json', 'report.json', root=root)
            self.assertEqual(calls[0][:3], ['git', 'checkout', 'HEAD'])
            self.assertIn(claim_refresh.REGISTRY, calls[0])
            self.assertIn(claim_refresh.GENERATED, calls[0])
            self.assertEqual(calls[1][2:4], ['author', 'build'])
            self.assertEqual(calls[1][calls[1].index('--spec') + 1], 'spec.json')
            self.assertEqual(calls[2][2:], ['render'])
            self.assertEqual((root / claim_refresh.REGISTRY).read_text(), '{"claims": []}')

    def test_a_failed_build_stops_before_the_registry_is_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / 'research/claims').mkdir(parents=True)
            (root / claim_refresh.REGISTRY).write_text('head')

            def fake_run(command, cwd, check):
                if 'build' in command:
                    raise claim_refresh.subprocess.CalledProcessError(1, command)

            with mock.patch.object(claim_refresh.subprocess, 'run', fake_run):
                with self.assertRaises(claim_refresh.subprocess.CalledProcessError):
                    claim_refresh.refresh('spec.json', 'o', 'p', 'r', root=root)
            self.assertEqual((root / claim_refresh.REGISTRY).read_text(), 'head')


if __name__ == '__main__':
    unittest.main()
