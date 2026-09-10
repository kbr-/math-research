"""Bounded checks for portable session startup and complete evidence archival."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SESSION = '11111111-2222-3333-4444-555555555555'


class RepositoryTools(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='math-portability-')
        self.root = Path(self.temp.name)
        shutil.copy2(ROOT / 'start-codex.sh', self.root / 'start-codex.sh')
        (self.root / 'tools').mkdir()
        shutil.copy2(ROOT / 'tools/remember-codex-session.py', self.root / 'tools/remember-codex-session.py')
        (self.root / 'bin').mkdir()
        self.capture = self.root / 'capture.json'
        fake = self.root / 'bin/codex'
        fake.write_text(f'#!{sys.executable}\n' +
                        'import os,sys,json\nfrom pathlib import Path\n' +
                        'Path(os.environ["MATH_LAUNCH_CAPTURE"]).write_text(json.dumps(' +
                        '{"args":sys.argv[1:],"cwd":os.getcwd(),"editor":os.environ["EDITOR"],"visual":os.environ["VISUAL"]}))\n')
        fake.chmod(0o755)
        self.env = dict(os.environ, PATH=str(self.root / 'bin') + os.pathsep + os.environ['PATH'],
                        MATH_LAUNCH_CAPTURE=str(self.capture))

    def tearDown(self):
        self.temp.cleanup()

    def launch(self, *args):
        return subprocess.run([str(self.root / 'start-codex.sh'), *args],
                              cwd='/tmp', env=self.env, capture_output=True, text=True, timeout=5)

    def test_fresh_checkout_bootstraps_from_files(self):
        script = self.root / 'start-codex.sh'
        content = re.sub(r'CONTEXT_WINDOW_TOKENS=\d+', 'CONTEXT_WINDOW_TOKENS=640000', script.read_text())
        content = re.sub(r'AUTO_COMPACT_TOKENS=\d+', 'AUTO_COMPACT_TOKENS=530000', content)
        script.write_text(content)
        result = self.launch()
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(self.capture.read_text())
        self.assertNotIn('resume', data['args'])
        self.assertIn('research/notes/RESUME.md', data['args'][-1])
        self.assertIn('remember-codex-session.py', data['args'][-1])
        self.assertIn('model_context_window=640000', data['args'])
        self.assertIn('model_auto_compact_token_limit=530000', data['args'])
        self.assertEqual(data['cwd'], str(self.root))
        self.assertEqual((data['editor'], data['visual']), ('vim', 'vim'))

    def test_existing_checkout_uses_exact_session(self):
        (self.root / '.codex-session-id').write_text(SESSION + '\n')
        self.assertEqual(self.launch().returncode, 0)
        args = json.loads(self.capture.read_text())['args']
        self.assertEqual(args[:2], ['resume', SESSION])
        self.assertNotIn('--last', args)

    def test_explicit_new_bypasses_existing_binding(self):
        (self.root / '.codex-session-id').write_text(SESSION)
        self.assertEqual(self.launch('--new').returncode, 0)
        self.assertNotIn('resume', json.loads(self.capture.read_text())['args'])

    def test_invalid_or_missing_explicit_binding_fails(self):
        self.assertNotEqual(self.launch('--resume').returncode, 0)
        (self.root / '.codex-session-id').write_text('invalid session id')
        self.assertNotEqual(self.launch().returncode, 0)
        self.assertFalse(self.capture.exists())

    def test_main_session_binding_is_saved_locally(self):
        env = dict(self.env, CODEX_THREAD_ID=SESSION)
        result = subprocess.run([str(self.root / 'tools/remember-codex-session.py')],
                                env=env, capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / '.codex-session-id').read_text(), SESSION + '\n')

    def test_archiver_preserves_full_output_and_refuses_replacement(self):
        spec = importlib.util.spec_from_file_location('archive_session', ROOT / 'tools/archive-session.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.RESEARCH = self.root / 'research'
        module.LOGS = module.RESEARCH / 'logs'
        module.DEST = module.RESEARCH / 'provenance/session-records'
        module.LOGS.mkdir(parents=True)
        output = module.LOGS / 'sample-output.txt'
        block = b'0123456789abcdef' * (64 * 1024)
        with output.open('wb') as stream:
            for _ in range(8):
                stream.write(block)
        events = [{'event': 'start'}, {'event': 'run_start', 'output': 'logs/sample-output.txt'},
                  {'event': 'run_end'}, {'event': 'stop'}]
        journal = module.LOGS / 'sample.jsonl'
        journal.write_text(''.join(json.dumps(e) + '\n' for e in events))
        journal.with_suffix('.summary.json').write_text('{}\n')
        self.assertTrue(module.archive(journal))
        saved = module.DEST / 'sample/outputs/sample-output.txt'
        self.assertEqual(saved.stat().st_size, 8 * 1024 * 1024)
        self.assertEqual(module.digest(saved), module.digest(output))
        self.assertTrue(module.archive(journal))
        with output.open('ab') as stream:
            stream.write(b'changed')
        with self.assertRaises(RuntimeError):
            module.archive(journal)


if __name__ == '__main__':
    unittest.main()
