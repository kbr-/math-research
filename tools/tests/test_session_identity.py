"""Focused checks for Codex attribution and unchanged Claude precedence."""
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

loader = importlib.machinery.SourceFileLoader('compute_identity', str(Path(__file__).resolve().parents[2] / 'compute.sh'))
spec = importlib.util.spec_from_loader(loader.name, loader)
compute = importlib.util.module_from_spec(spec)
loader.exec_module(compute)


class SessionIdentityChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.thread = '11111111-1111-4111-8111-111111111111'
        self.env = patch.dict(os.environ, {'CODEX_HOME': str(self.home),
                             'CODEX_THREAD_ID': self.thread}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.log = self.home / 'sessions/2026/09/19' / f'rollout-example-{self.thread}.jsonl'
        self.log.parent.mkdir(parents=True)

    def write_turns(self, *pairs):
        self.log.write_text(''.join(json.dumps({'type': 'turn_context',
            'payload': {'model': model, 'effort': effort}})+'\n' for model, effort in pairs))

    def test_latest_runtime_settings_override_stale_labels(self):
        self.write_turns(('model-a', 'low'), ('model-b', 'medium'))
        with self.log.open('a') as f:
            f.write('{"partial":')
        self.assertEqual(compute.session_model(), 'model-b, medium reasoning')
        self.write_turns(('model-b', 'high'))
        self.assertEqual(compute.session_model(model='model-b, medium reasoning'),
                         'model-b, high reasoning')

    def test_placeholder_rejected_before_creating_a_session_when_settings_are_known(self):
        self.write_turns(('model-a', 'high'))
        with patch.object(compute, 'LOGS', self.home/'logs'):
            for label in ('unknown', 'GPT-6, unknown reasoning setting',
                          'unspecified', 'placeholder', 'MODEL, reasoning setting'):
                with self.subTest(label=label), self.assertRaisesRegex(ValueError, 'Omit --model'):
                    compute.start_session('bad-label', model=label)
            self.assertFalse((self.home/'logs').exists())
            path = compute.start_session('automatic')
        self.assertEqual(json.loads(path.read_text())['model'], 'model-a, high reasoning')

    def test_claude_keeps_explicit_and_environment_precedence(self):
        self.write_turns(('codex-model', 'medium'))
        os.environ['CLAUDECODE'] = '1'
        os.environ['MATH_AGENT_MODEL'] = 'Claude environment'
        with patch.object(compute, 'codex_session_model', side_effect=AssertionError('Codex lookup')):
            self.assertEqual(compute.session_model(model='Claude explicit'), 'Claude explicit')
            self.assertEqual(compute.session_model(), 'Claude environment')
            self.assertEqual(compute.session_model('Claude Code', 'Claude explicit'), 'Claude explicit')

    def test_missing_metadata_falls_back_without_guessing_config(self):
        (self.home/'config.toml').write_text('model = "not-active"\n')
        self.assertIsNone(compute.session_model())
        self.assertEqual(compute.session_model(model='known model, unknown reasoning'),
                         'known model, unknown reasoning')
        os.environ['MATH_AGENT_MODEL'] = 'environment fallback'
        self.assertEqual(compute.session_model(), 'environment fallback')
        self.assertEqual(compute.session_model(model='explicit fallback'), 'explicit fallback')

    def test_incomplete_latest_turn_does_not_reuse_old_effort(self):
        self.write_turns(('model-a', 'high'), ('model-b', None))
        self.assertIsNone(compute.session_model())
        os.environ['CODEX_THREAD_ID'] = '../invalid'
        self.assertIsNone(compute.session_model())

    def test_start_record_contains_model_but_no_thread_or_transcript(self):
        self.write_turns(('model-a', 'medium'))
        with patch.object(compute, 'LOGS', self.home/'logs'):
            path = compute.start_session('test')
        record = json.loads(path.read_text())
        self.assertEqual(record['agent'], 'Codex')
        self.assertEqual(record['model'], 'model-a, medium reasoning')
        self.assertNotIn(self.thread, path.read_text())
        self.assertNotIn('turn_context', path.read_text())


if __name__ == '__main__':
    unittest.main()
