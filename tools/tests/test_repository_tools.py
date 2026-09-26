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

ROOT = Path(__file__).resolve().parents[2]
SESSION = '11111111-2222-3333-4444-555555555555'


class RepositoryTools(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='math-portability-')
        self.root = Path(self.temp.name)
        shutil.copy2(ROOT / 'start-codex.sh', self.root / 'start-codex.sh')
        shutil.copy2(ROOT / 'start-session.sh', self.root / 'start-session.sh')
        (self.root / 'tools').mkdir()
        shutil.copy2(ROOT / 'tools/remember-codex-session.py', self.root / 'tools/remember-codex-session.py')
        shutil.copy2(ROOT / 'start-claude.sh', self.root / 'start-claude.sh')
        (self.root / 'bin').mkdir()
        self.capture = self.root / 'capture.json'
        fake = self.root / 'bin/codex'
        fake.write_text(f'#!{sys.executable}\n' +
                        'import os,sys,json\nfrom pathlib import Path\n' +
                        'p=Path(os.environ["MATH_LAUNCH_CAPTURE"])\n' +
                        'with p.with_suffix(".jsonl").open("a") as f: f.write(json.dumps(sys.argv[1:])+"\\n")\n' +
                        'if sys.argv[1:]==["remote-control","start"] and os.environ.get("MATH_FAIL_DAEMON"): sys.exit(7)\n' +
                        'p.write_text(json.dumps(' +
                        '{"args":sys.argv[1:],"cwd":os.getcwd(),"editor":os.environ["EDITOR"],"visual":os.environ["VISUAL"]}))\n')
        fake.chmod(0o755)
        # start-claude.sh drives background sessions: `claude --bg ...` starts or resumes one,
        # `claude agents --json [--all]` lists them and `claude attach SHORT` opens one.
        self.claude_calls = self.root / 'claude-calls.jsonl'
        self.claude_agents = self.root / 'claude-agents.json'
        claude = self.root / 'bin/claude'
        claude.write_text(f'#!{sys.executable}\n' + '''import json, os, sys, uuid
from pathlib import Path
capture = Path(os.environ["MATH_LAUNCH_CAPTURE"])
calls, state = capture.with_name("claude-calls.jsonl"), capture.with_name("claude-agents.json")
agents = json.loads(state.read_text()) if state.exists() else []
args = sys.argv[1:]
with calls.open("a") as f:
    f.write(json.dumps({"args": args, "cwd": os.getcwd(), "editor": os.environ["EDITOR"],
                        "visual": os.environ["VISUAL"]}) + "\\n")
if args[:1] == ["agents"]:
    print(json.dumps(agents if "--all" in args else [a for a in agents if a["running"]]))
elif args[:1] == ["attach"]:
    pass
elif "--bg" in args:
    wanted = args[args.index("--resume") + 1] if "--resume" in args else str(uuid.uuid4())
    for agent in agents:
        if agent["sessionId"] == wanted:
            agent["running"] = True
            break
    else:
        agents.append({"kind": "background", "id": "bg%d" % len(agents), "sessionId": wanted,
                       "cwd": os.getcwd(), "running": True})
    state.write_text(json.dumps(agents))
else:
    sys.exit(3)
''')
        claude.chmod(0o755)
        self.env = dict(os.environ, PATH=str(self.root / 'bin') + os.pathsep + os.environ['PATH'],
                        MATH_LAUNCH_CAPTURE=str(self.capture))

    def tearDown(self):
        self.temp.cleanup()

    def launch(self, *args):
        return subprocess.run([str(self.root / 'start-session.sh'), *args],
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
        self.assertIn('--approve-for-me', data['args'])
        self.assertIn('python3 tools/resume.py', data['args'][-1])
        self.assertIn('remember-codex-session.py', data['args'][-1])
        self.assertIn('model_context_window=640000', data['args'])
        self.assertIn('model_auto_compact_token_limit=530000', data['args'])
        self.assertEqual(data['cwd'], str(self.root))
        self.assertEqual((data['editor'], data['visual']), ('vim', 'vim'))
        self.assertEqual(data['args'][:2], ['--remote', 'unix://'])
        calls = self.capture.with_suffix('.jsonl').read_text().splitlines()
        self.assertEqual(json.loads(calls[0]), ['remote-control', 'start'])
        self.assertEqual(len(calls), 2)

    def test_existing_checkout_uses_exact_session(self):
        (self.root / '.codex-session-id').write_text(SESSION + '\n')
        for mode in ((), ('--resume',)):
            with self.subTest(mode=mode):
                self.assertEqual(self.launch(*mode).returncode, 0)
                args = json.loads(self.capture.read_text())['args']
                self.assertEqual(args[:2], ['resume', SESSION])
                self.assertEqual(args[2:4], ['--remote', 'unix://'])
                self.assertNotIn('--last', args)
                self.assertNotIn('--approve-for-me', args)
                self.assertNotIn('--sandbox', args)
                self.assertNotIn('--ask-for-approval', args)
                self.assertIn('model_context_window=600000', args)
                self.assertIn('model_auto_compact_token_limit=550000', args)

    def test_daemon_only_launcher_does_not_open_a_session(self):
        result = subprocess.run([str(self.root / 'start-codex.sh')],
                                cwd='/tmp', env=self.env, capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.capture.read_text())['args'], ['remote-control', 'start'])
        self.assertEqual(len(self.capture.with_suffix('.jsonl').read_text().splitlines()), 1)

    def test_daemon_failure_prevents_session_launch(self):
        self.env['MATH_FAIL_DAEMON'] = '1'
        self.assertEqual(self.launch().returncode, 7)
        self.assertFalse(self.capture.exists())
        self.assertEqual(len(self.capture.with_suffix('.jsonl').read_text().splitlines()), 1)

    def test_session_help_does_not_start_daemon(self):
        self.assertEqual(self.launch('--help').returncode, 0)
        self.assertFalse(self.capture.exists())
        self.assertFalse(self.capture.with_suffix('.jsonl').exists())

    def test_explicit_new_bypasses_existing_binding(self):
        (self.root / '.codex-session-id').write_text(SESSION)
        self.assertEqual(self.launch('--new').returncode, 0)
        self.assertNotIn('resume', json.loads(self.capture.read_text())['args'])
        self.assertIn('--approve-for-me', json.loads(self.capture.read_text())['args'])

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

    def launch_claude(self, *args):
        return subprocess.run([str(self.root / 'start-claude.sh'), *args],
                              cwd='/tmp', env=self.env, capture_output=True, text=True, timeout=10)

    def claude_log(self):
        if not self.claude_calls.exists():
            return []
        return [json.loads(line) for line in self.claude_calls.read_text().splitlines()]

    def claude_launches(self):
        return [c for c in self.claude_log() if c['args'][:1] not in (['agents'], ['attach'])]

    def set_claude_agents(self, agents):
        self.claude_calls.unlink(missing_ok=True)
        self.claude_agents.unlink(missing_ok=True)
        if agents:
            self.claude_agents.write_text(json.dumps(agents))

    def test_claude_fresh_checkout_binds_and_bootstraps(self):
        script = self.root / 'start-claude.sh'
        script.write_text(re.sub(r'AUTO_COMPACT_TOKENS=\d+', 'AUTO_COMPACT_TOKENS=530000', script.read_text()))
        result = self.launch_claude()
        self.assertEqual(result.returncode, 0, result.stderr)
        [launch] = self.claude_launches()
        self.assertEqual(launch['args'][:6], ['--bg', '--remote-control', '--permission-mode', 'auto',
                                              '--autocompact', '530000'])
        self.assertEqual(len(launch['args']), 7)
        self.assertIn('python3 tools/resume.py', launch['args'][-1])
        self.assertNotIn('--resume', launch['args'])
        [agent] = json.loads(self.claude_agents.read_text())
        self.assertEqual((self.root / '.claude-session-id').read_text().strip(), agent['sessionId'])
        self.assertEqual(self.claude_log()[-1]['args'], ['attach', agent['id']])
        self.assertEqual(launch['cwd'], str(self.root))
        self.assertEqual((launch['editor'], launch['visual']), ('vim', 'vim'))

    def test_claude_existing_checkout_uses_exact_session(self):
        (self.root / '.claude-session-id').write_text(SESSION + '\n')
        stopped = {'kind': 'background', 'id': 'old', 'sessionId': SESSION, 'cwd': str(self.root),
                   'running': False}
        cases = (('unknown', [], ['--resume', SESSION, '--bg', '--remote-control']),
                 ('stopped background', [stopped], ['--bg', '--resume', SESSION]),
                 ('running background', [dict(stopped, running=True)], None))
        for name, agents, expected in cases:
            with self.subTest(state=name):
                self.set_claude_agents(agents)
                result = self.launch_claude()
                self.assertEqual(result.returncode, 0, result.stderr)
                launches = [c['args'] for c in self.claude_launches()]
                if expected is None:
                    self.assertEqual(launches, [])
                elif name == 'unknown':
                    [args] = launches
                    self.assertEqual(args[:4], expected)
                else:
                    self.assertEqual(launches, [expected])
                short = [a['id'] for a in json.loads(self.claude_agents.read_text())
                         if a['sessionId'] == SESSION]
                self.assertEqual(self.claude_log()[-1]['args'], ['attach', *short])
                self.assertEqual((self.root / '.claude-session-id').read_text().strip(), SESSION)

    def test_claude_detached_does_not_attach(self):
        (self.root / '.claude-session-id').write_text(SESSION + '\n')
        result = self.launch_claude('--detached')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('attach', [c['args'][0] for c in self.claude_log()])
        self.assertIn('claude attach', result.stdout)

    def test_claude_explicit_new_replaces_binding(self):
        (self.root / '.claude-session-id').write_text(SESSION)
        result = self.launch_claude('--new')
        self.assertEqual(result.returncode, 0, result.stderr)
        [launch] = self.claude_launches()
        self.assertNotIn('--resume', launch['args'])
        bound = (self.root / '.claude-session-id').read_text().strip()
        self.assertNotEqual(bound, SESSION)
        self.assertEqual([a['sessionId'] for a in json.loads(self.claude_agents.read_text())], [bound])

    def test_claude_invalid_or_missing_explicit_binding_fails(self):
        self.assertNotEqual(self.launch_claude('--resume').returncode, 0)
        (self.root / '.claude-session-id').write_text('invalid session id')
        self.assertNotEqual(self.launch_claude().returncode, 0)
        self.assertEqual(self.claude_log(), [])

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


class ProvenanceTools(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='math-provenance-')
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        spec = importlib.util.spec_from_file_location('record_provenance', ROOT / 'tools/record-provenance.py')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.module.ROOT = self.root
        (self.root / 'sample.bin').write_bytes(b'abc')

    def tearDown(self):
        self.temp.cleanup()

    def test_known_hash_and_portable_manifest(self):
        result = self.module.record([Path('sample.bin')], Path('result.json'), 'sample')
        self.assertEqual(result, {
            'schema': 1, 'session': 'sample',
            'files': [{'path': 'sample.bin', 'bytes': 3,
                       'sha256': 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'}]})
        self.assertEqual(json.loads((self.root / 'result.json').read_text()), result)

    def test_existing_evidence_and_outside_paths_are_protected(self):
        self.module.record([Path('sample.bin')], Path('result.json'))
        before = (self.root / 'result.json').read_bytes()
        with self.assertRaises(FileExistsError):
            self.module.record([Path('sample.bin')], Path('result.json'))
        self.assertEqual((self.root / 'result.json').read_bytes(), before)
        with self.assertRaises(ValueError):
            self.module.record([Path('../outside.bin')], Path('other.json'))
        with self.assertRaises(ValueError):
            self.module.record([Path('sample.bin')], Path('../outside.json'))
        self.assertFalse((Path(self.temp.name) / 'outside.json').exists())


if __name__ == '__main__':
    unittest.main()
