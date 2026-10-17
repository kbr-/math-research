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
            self.assertFalse((root / 'proposal.json').exists())

    def test_summaries_checked_reaches_the_build_only_when_given(self):
        for given in (False, True):
            with self.subTest(given=given), tempfile.TemporaryDirectory() as tmp:
                root = pathlib.Path(tmp)
                (root / 'research/claims').mkdir(parents=True)
                calls = []

                def fake_run(command, cwd, check):
                    calls.append(command)
                    if 'build' in command:
                        (root / 'proposal.json').write_text('{}')

                with mock.patch.object(claim_refresh, 'ROOT', root), \
                        mock.patch.object(claim_refresh.subprocess, 'run', fake_run):
                    claim_refresh.refresh('spec.json', 'o', 'proposal.json', 'r', root=root,
                                          summaries_checked=given)
                self.assertEqual('--summaries-checked' in calls[1], given)

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

    def test_a_claim_head_already_registers_is_refused_before_any_output_is_touched(self):
        # 17 October 2026: run on a committed claim, the refresh deleted and rewrote the committed build
        # request, then failed in author build, which appends only.
        import json
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
            (root / 'research/claims').mkdir(parents=True)
            (root / claim_refresh.REGISTRY).write_text(json.dumps({'claims': [{'id': 'cor:old'}]}))
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q', '-m', 'base'],
                           cwd=root, check=True)
            (root / 'spec.json').write_text(json.dumps({'claims': [{'id': 'cor:old'}, {'id': 'lem:new'}]}))
            (root / 'request.json').write_text('committed request')
            with self.assertRaises(SystemExit) as refused:
                claim_refresh.refresh('spec.json', 'request.json', 'p.json', 'r.txt', root=root)
            self.assertIn('cor:old', str(refused.exception))
            self.assertEqual((root / 'request.json').read_text(), 'committed request')
            (root / 'spec.json').write_text(json.dumps({'claims': [{'id': 'lem:new'}]}))
            self.assertEqual(claim_refresh.committed_claims('spec.json', root), [])


if __name__ == '__main__':
    unittest.main()
