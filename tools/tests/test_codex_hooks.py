import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/hooks'))
sys.path.insert(0, str(ROOT / 'tools'))
import codex_dispatch as hook
import codex_state
import resume


class CodexHooksTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'tools').mkdir()
        # read_part uses the production UTF-8 cache format; three payloads are required.
        self.manifest = resume.save_bundle(self.root, [('fixture', 'αβγ\n' * 16000, '', '')])
        self.key = self.manifest['bundle']
        self.assertGreater(len(self.manifest['parts']), 2)

    def event(self, name, command='', **fields):
        return {'hook_event_name': name, 'session_id': 'parent', 'turn_id': 'turn',
                'cwd': str(self.root), 'tool_name': 'Bash', 'tool_input': {'command': command}, **fields}

    def call(self, name, command='', **fields):
        return hook.dispatch(self.event(name, command, **fields), self.root)

    def output(self, number, key=None):
        key = key or self.key
        output = io.StringIO()
        with redirect_stdout(output):
            resume.emit_part(self.root, key, number)
        return output.getvalue()

    def prepare(self, **fields):
        header = json.dumps({'bundle': self.key}) + '\n'
        return self.call('PostToolUse', 'python3 tools/resume.py', tool_response=header + self.output(1), **fields)

    def part(self, n, text=None, **fields):
        return self.call('PostToolUse', f'python3 tools/resume.py --read {self.key} --part {n}',
                         tool_response=self.output(n) if text is None else text, **fields)

    def denied(self, **fields):
        value = self.call('PreToolUse', 'printf normal', **fields)
        return value.get('hookSpecificOutput', {}).get('permissionDecision') == 'deny'

    def test_stop_uses_optional_active_worktree_predicate(self):
        self.assertEqual(self.call('Stop'), {})
        directory=self.root/'tools/hooks';directory.mkdir()
        (directory/'codex_unchecked_claim.py').write_text(
            "def check(event):\n    return {'decision': 'block', 'reason': event['last_assistant_message']}\n")
        self.assertEqual(self.call('Stop',last_assistant_message='fixture'),
                         {'decision':'block','reason':'fixture'})
        self.assertIn('Stop',json.loads((ROOT/'.codex/hooks.json').read_text())['hooks'])

    def test_full_receipts_and_retry_not_last_marker(self):
        self.call('SessionStart', source='compact')
        self.assertTrue(self.denied())
        self.prepare()
        count = len(self.manifest['parts'])
        self.part(count)
        self.assertTrue(self.denied())
        self.part(2, self.output(2)[:120] + '\nEND RESUME BUNDLE\n')
        self.assertTrue(self.denied())
        self.part(2, 'Warning: output truncated\n' + self.output(2))
        self.assertTrue(self.denied())
        for n in range(2, count):
            self.part(n)
        self.assertFalse(self.denied())

    def test_wrong_bundle_and_changed_payload_stay_pending(self):
        self.call('SessionStart')
        self.prepare()
        with codex_state.actor_state(self.root, self.event('PostToolUse')) as state:
            state['bundle'] = '0' * 32
        self.part(2)
        self.assertTrue(self.denied())
        self.prepare()
        body = self.output(2)
        self.part(2, body.replace('α', 'x', 1))
        self.assertTrue(self.denied())
        with codex_state.actor_state(self.root, self.event('PostToolUse')) as state:
            self.assertEqual(state['delivered'], [1])

    def test_parent_children_and_sanitization_collisions_are_isolated(self):
        self.call('SessionStart')
        self.call('SessionStart', agent_id='child/a')
        self.assertFalse(self.denied(agent_id='child_a'))
        self.assertFalse(self.denied(session_id='sibling'))
        self.assertTrue(self.denied(agent_id='child/a'))
        self.prepare(agent_id='child/a')
        for n in range(2, len(self.manifest['parts']) + 1):
            self.part(n, agent_id='child/a')
        self.assertFalse(self.denied(agent_id='child/a'))
        self.assertTrue(self.denied())
        # Compaction does not clear the parent's pending restoration.
        self.call('SessionStart', agent_id='child/a', source='compact')
        self.assertTrue(self.denied())

    def test_preparation_resets_receipts_and_other_tools_refuse(self):
        self.call('SessionStart')
        self.prepare()
        self.part(2)
        self.prepare()
        with codex_state.actor_state(self.root, self.event('PostToolUse')) as state:
            self.assertEqual(state['delivered'], [1])
        result = self.call('PreToolUse', tool_name='apply_patch', tool_input={'patch': 'x'})
        self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_guards_and_only_literal_resume_are_allowed(self):
        for command in ['python3 tools/resume.py | head', './compute.sh start turn >out',
                        "python3 - <<'END'\nraise Exception()\nEND\ngit commit -am broken"]:
            with self.subTest(command=command):
                result = self.call('PreToolUse', command)
                self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')
        self.call('SessionStart')
        for command in ['echo tools/resume.py', 'python3 tools/resume.py; touch x',
                        'python3 tools/resume.py $(touch x)', 'python3 /tmp/resume.py',
                        'python3 tools/resume.py --help', 'python3 tools/resume.py && ls']:
            with self.subTest(command=command):
                self.assertEqual(self.call('PreToolUse', command)['hookSpecificOutput']['permissionDecision'], 'deny')
        for command in ['python3 tools/resume.py', './tools/resume.py --formalization',
                        f'python3 tools/resume.py --part 2 --read {self.key}']:
            self.assertEqual(self.call('PreToolUse', command), {})
        self.assertEqual(self.call('PreToolUse', 'python3 ../tools/resume.py', cwd=str(self.root/'subdir')), {})

    def test_post_commit_context_never_blocks_success(self):
        with patch.object(hook.base_behind, 'message', return_value='Run tools/ff-base.sh'):
            result = self.call('PostToolUse', 'git commit -m test', tool_response='commit succeeded')
        self.assertEqual(result, {'hookSpecificOutput': {'hookEventName': 'PostToolUse',
                                                        'additionalContext': 'Run tools/ff-base.sh'}})
        self.assertNotIn('decision', result)

    def test_corrupt_state_is_not_silently_replaced(self):
        event = self.event('PreToolUse')
        directory = codex_state.actor_directory(self.root, event)
        directory.mkdir(parents=True)
        (directory/'state.json').write_text('broken')
        with self.assertRaises(ValueError):
            self.denied()
        self.assertEqual((directory/'state.json').read_text(), 'broken')

    def test_atomic_state_and_lock_contention(self):
        event = self.event('PreToolUse')
        with codex_state.actor_state(self.root, event) as state:
            state['pending'] = True
            with self.assertRaisesRegex(ValueError, 'busy'):
                with codex_state.actor_state(self.root, event):
                    pass
        with codex_state.actor_state(self.root, event) as state:
            self.assertTrue(state['pending'])
        self.assertEqual(list(codex_state.actor_directory(self.root, event).glob('.write-*')), [])

    def test_literal_parser_validates_selectors_and_shell_forms(self):
        invalid = ['', "python3 tools/resume.py '", 'python3 tools/resume.py $ARGS',
                   'python3 tools/resume.py `pwd`', 'python3 tools/resume.py >out',
                   'python3 tools/resume.py <input', 'python3 tools/resume.py\nls',
                   'cd && python3 tools/resume.py', 'ls sub && python3 tools/resume.py', 'ls . && python3 tools/resume.py',
                   'python3 tools/resume.py --read wrong --part 2',
                   f'python3 tools/resume.py --read {self.key} --part x',
                   f'python3 tools/resume.py --read {self.key}',
                   'python3 tools/resume.py --notebook', 'python3 tools/resume.py --unknown x',
                   f'python3 tools/resume.py --read {self.key} --read {self.key}',
                   'cd . extra && python3 tools/resume.py',
                   'python3 tools/resume.py --notebook $(pwd)',
                   'python3 tools/resume.py --notebook `pwd`',
                   'python3 tools/resume.py --notebook side;ls',
                   'python3 tools/resume.py --notebook side|ls',
                   'python3 tools/resume.py --notebook side>out',
                   'python3 tools/resume.py --notebook side<input',
                   'python3 tools/resume.py --notebook \nside']
        for command in invalid:
            with self.subTest(command=command):
                self.assertIsNone(hook.resume_call(command, self.root))
        for command in ['python -u tools/resume.py', 'cd . && python3 tools/resume.py', 'cd . && ./tools/resume.py',
                        'python3 tools/resume.py --notebook side',
                        'python3 tools/resume.py --formalization --notebook side',
                        'python3 tools/resume.py --notebook side --session turn --tail 4 --formalization']:
            self.assertEqual(hook.resume_call(command, self.root), ('prepare', None, 1))
        self.assertEqual(hook.resume_call(f'./tools/resume.py --read {self.key} --part 2', self.root),
                         ('read', self.key, 2))

    def test_response_shapes_and_missing_preparation_metadata(self):
        self.assertEqual(hook.response_text({'stdout': 'a', 'output': 'b', 'text': 'c',
                                            'content': [{'text': 'd'}], 'stderr': 'ignore'}), 'a\nb\nc\nd')
        self.assertEqual(hook.response_text(42), '')
        self.assertEqual(hook.response_text(['a', 'b']), 'a\nb')
        self.call('SessionStart')
        self.call('PostToolUse', 'python3 tools/resume.py', tool_response=self.output(1))
        self.assertTrue(self.denied())
        self.call('PostToolUse', 'python3 tools/resume.py', tool_response={'stdout':
                  json.dumps({'bundle': self.key}) + '\n' + self.output(1)})
        with codex_state.actor_state(self.root, self.event('PostToolUse')) as state:
            self.assertEqual(state['bundle'], self.key)
        self.call('PreToolUse', 'python3 tools/resume.py')
        with codex_state.actor_state(self.root, self.event('PostToolUse')) as state:
            self.assertIsNone(state['bundle'])
            self.assertEqual(state['delivered'], [])

    def test_missing_identity_invalid_version_and_failed_atomic_write(self):
        for fields in [{'session_id': ''}, {'session_id': None}, {'session_id': 3}, {'agent_id': 1}]:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                codex_state.actor_directory(self.root, self.event('PreToolUse', **fields))
        directory = codex_state.actor_directory(self.root, self.event('PreToolUse'))
        directory.mkdir(parents=True)
        target = directory/'state.json'
        for value in [[], {'version': 2}]:
            target.write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                self.denied()
        target.write_text('previous')
        with patch.object(codex_state.os, 'replace', side_effect=OSError('disk error')):
            with self.assertRaises(OSError):
                codex_state.atomic_json(target, {'version': 1})
        self.assertEqual(target.read_text(), 'previous')
        self.assertEqual(list(directory.glob('.write-*')), [])

    def test_loader_and_entry_point_errors_preserve_supported_shapes(self):
        loaded = hook.load_guard()
        self.assertIsNotNone(loaded.blocked('python3 tools/resume.py | head'))
        self.assertIsNone(loaded.blocked('printf normal'))
        for payload in [self.event('PreToolUse', command=3),
                        self.event('PreToolUse', tool_input=['invalid']),
                        self.event('PreToolUse', session_id=None),
                        self.event('PostToolUse', session_id=None), []]:
            stream = io.StringIO()
            with patch.object(hook.sys, 'stdin', io.StringIO(json.dumps(payload))), redirect_stdout(stream), \
                 patch.object(hook.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, str(self.root))):
                hook.main()
            result = json.loads(stream.getvalue())
            if isinstance(payload, dict) and payload['hook_event_name'] == 'PreToolUse':
                self.assertEqual(result['hookSpecificOutput']['permissionDecision'], 'deny')
                self.assertIsInstance(result['hookSpecificOutput']['permissionDecisionReason'], str)
                self.assertGreater(len(result['hookSpecificOutput']['permissionDecisionReason']), 5)
            else:
                self.assertIn('systemMessage', result)
                self.assertIsInstance(result['systemMessage'], str)
        with patch.object(hook.sys, 'stdin', io.StringIO('broken')), redirect_stdout(io.StringIO()) as stream:
            hook.main()
        self.assertIn('systemMessage', json.loads(stream.getvalue()))

    def test_reset_and_wire_contracts_are_independent_of_formatters(self):
        start = self.call('SessionStart')
        self.assertEqual(set(start), {'hookSpecificOutput'})
        self.assertEqual(start['hookSpecificOutput']['hookEventName'], 'SessionStart')
        self.assertIn('python3 tools/resume.py', start['hookSpecificOutput']['additionalContext'])
        refused = self.call('PreToolUse', 'printf normal')['hookSpecificOutput']
        self.assertEqual(set(refused), {'hookEventName', 'permissionDecision', 'permissionDecisionReason'})
        self.assertEqual(refused['hookEventName'], 'PreToolUse')
        self.assertIn('python3 tools/resume.py', refused['permissionDecisionReason'])
        self.prepare()
        self.call('SessionStart', source='compact')
        with codex_state.actor_state(self.root, self.event('PostToolUse')) as state:
            self.assertIsNone(state['bundle'])
            self.assertEqual(state['delivered'], [])
        self.prepare()
        self.call('PreToolUse', f'python3 tools/resume.py --read {self.key} --part 2')
        with codex_state.actor_state(self.root, self.event('PostToolUse')) as state:
            self.assertEqual(state['bundle'], self.key)
            self.assertEqual(state['delivered'], [1])
        non_shell = self.call('PreToolUse', 'python3 tools/resume.py', tool_name='mcp__tool')
        self.assertEqual(non_shell['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_truncation_with_both_markers_never_counts_receipt(self):
        self.call('SessionStart')
        self.prepare()
        for prefix in ['Warning: output truncated', 'OUTPUT TRUNCATED', '3 tokens truncated']:
            self.part(2, prefix + '\n' + self.output(2))
            with codex_state.actor_state(self.root, self.event('PostToolUse')) as state:
                self.assertEqual(state['delivered'], [1])

    def test_only_pre_shell_checks_commands_and_post_shell_checks_base(self):
        command = 'python3 tools/resume.py | head'
        self.assertEqual(self.call('PostToolUse', command), {})
        self.assertEqual(self.call('PreToolUse', command, tool_name='mcp__tool'), {})
        with patch.object(hook.base_behind, 'message', return_value=None) as message:
            self.call('PreToolUse', 'git commit -m x')
            self.call('PostToolUse', 'git commit -m x', tool_name='mcp__tool')
            message.assert_not_called()
            self.call('PostToolUse', 'git commit -m x', cwd=str(self.root/'nested'))
            message.assert_called_once_with('git commit -m x', str(self.root/'nested'))
        result = self.call('PreToolUse', command)['hookSpecificOutput']
        self.assertIsInstance(result['permissionDecisionReason'], str)
        self.assertIn('restoration bundle', result['permissionDecisionReason'])

    def test_real_git_root_in_entry_point_and_nested_atomic_target(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        nested = self.root/'nested'; nested.mkdir()
        payload = self.event('SessionStart', cwd=str(nested))
        stream = io.StringIO()
        with patch.object(hook.sys, 'stdin', io.StringIO(json.dumps(payload))), redirect_stdout(stream):
            hook.main()
        self.assertEqual(json.loads(stream.getvalue())['hookSpecificOutput']['hookEventName'], 'SessionStart')
        state_dir = codex_state.actor_directory(self.root, payload)
        self.assertEqual(state_dir.parent, self.root/'.codex/framework/actors')
        self.assertTrue(json.loads((state_dir/'state.json').read_text())['pending'])
        target = self.root/'new/nested/state.json'
        replace = codex_state.os.replace
        def same_filesystem(source, destination):
            self.assertEqual(Path(source).parent, destination.parent)
            return replace(source, destination)
        with patch.object(codex_state.os, 'replace', side_effect=same_filesystem):
            codex_state.atomic_json(target, {'version': 1})
        self.assertEqual(json.loads(target.read_text()), {'version': 1})

    def test_post_pending_without_receipt_and_missing_cwd_fallback(self):
        self.call('SessionStart')
        self.assertEqual(self.call('PostToolUse', 'printf unrelated', tool_response='not a bundle'), {})
        with patch.object(hook.base_behind, 'message', return_value=None) as message:
            payload = self.event('PostToolUse', 'git commit -m x')
            del payload['cwd']
            hook.dispatch(payload, self.root)
            message.assert_called_once_with('git commit -m x', str(self.root))

    def test_git_failure_refuses_before_any_actor_state(self):
        stream = io.StringIO()
        with patch.object(hook.sys, 'stdin', io.StringIO(json.dumps(self.event('PreToolUse')))), \
             redirect_stdout(stream):
            hook.main()
        result = json.loads(stream.getvalue())['hookSpecificOutput']
        self.assertEqual(result['permissionDecision'], 'deny')
        self.assertIn('git', result['permissionDecisionReason'])
        self.assertFalse((self.root/'.codex').exists())

    def test_registration_from_subdirectory_and_missing_script(self):
        config = json.loads((ROOT/'.codex/hooks.json').read_text())
        commands = [g['hooks'][0]['command'] for groups in config['hooks'].values() for g in groups]
        self.assertTrue(all(len(g['hooks']) == 1 for groups in config['hooks'].values() for g in groups))
        self.assertEqual(len(set(commands)), 1)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        subdir = self.root/'nested'; subdir.mkdir()
        payload = self.event('PreToolUse', cwd=str(subdir), command='printf allowed')
        result = subprocess.run(['sh', '-c', commands[0]], cwd=subdir, input=json.dumps(payload),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('is missing', result.stderr)
        (self.root/'tools').rmdir()
        (self.root/'tools').symlink_to(ROOT/'tools', target_is_directory=True)
        result = subprocess.run(['sh', '-c', commands[0]], cwd=subdir, input=json.dumps(payload),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {})


if __name__ == '__main__':
    unittest.main()
