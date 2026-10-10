import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

HOOK = Path(__file__).resolve().parents[1] / 'hooks' / 'during_run.py'
sys.path.insert(0, str(HOOK.parent))
spec = importlib.util.spec_from_file_location('during_run', HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def said(text, kind='text', **extra):
    return json.dumps({'type': 'assistant', 'message': {'content': [{'type': kind, kind: text}]}, **extra}) + '\n'


class DuringRunTest(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.dir = Path(scratch.name)
        self.transcript = self.dir / 'session.jsonl'
        self.state = self.dir / 'state'
        # The checks a branch turns off are read from a tree that turns none off, not from this clone.
        import stop_checks
        own = unittest.mock.patch.object(stop_checks, 'ROOT', self.dir / 'no-clone')
        own.start()
        self.addCleanup(own.stop)

    def commit(self, command='git commit -q -m x'):
        return hook.commit({'session_id': 's', 'transcript_path': str(self.transcript),
                            'tool_input': {'command': command}}, self.state)

    def test_a_promise_written_since_the_last_commit_blocks_the_next_one_once(self):
        self.transcript.write_text(said('From now on I will time it first.'))
        # What was written before the first commit the check sees is not judged.
        self.assertIsNone(self.commit())
        with self.transcript.open('a') as stream:
            stream.write(said('The run passed.') + said('I should have measured it before the commit.', 'thinking')
                         + said('I will never again skip it.') + '[1]\nnot json\n'
                         + said('From now on I always do it.', isSidechain=True) + '{"type": "assistant", "message"')
        # Another command is not a commit, and reads nothing.
        self.assertIsNone(self.commit('git status && echo commit'))
        message = self.commit('cd repo && git -C x commit -qm y')
        self.assertTrue(message.startswith('Before this commit, in what was written since the last one: A promise about '
                                           'future behaviour, or an admission that implies one: "I should have measured '
                                           'it before the commit".'), message)
        self.assertTrue(message.endswith('Then commit again: this check has now seen that text.'))
        # The same text does not block the commit a second time; the unfinished last line is read when it is whole.
        self.assertIsNone(self.commit())
        with self.transcript.open('a') as stream:
            stream.write(': {"content": [{"type": "text", "text": "Next time I will check."}]}}\n')
        self.assertIn('"Next time I will check"', self.commit())
        self.assertIsNone(self.commit())
        self.assertIsNone(hook.commit({'session_id': 's', 'transcript_path': str(self.dir / 'missing'),
                                       'tool_input': {'command': 'git commit'}}, self.state))

    def test_the_stop_hook_s_other_checks_of_a_turn_run_at_a_commit_too(self):
        self.transcript.write_text('')
        self.assertIsNone(self.commit())

        def after(*lines, verdict=None):
            asked = []
            with self.transcript.open('a') as stream:
                stream.write(''.join(lines))
            with unittest.mock.patch.object(hook, 'judge', lambda said, calls: asked.append((said, calls)) or verdict):
                return self.commit(), asked
        # A tool's fault with no edit of the tool, in thinking as well as in text.
        message, asked = after(said('`rewrap_md.py` nested the list wrongly, so I fixed the lines by hand.', 'thinking'))
        self.assertIn("A tool's fault, worked around: ", message)
        self.assertEqual(asked, [])
        # A gap declared to the user; one in thinking alone is none, and the judge is asked about what was said.
        message, _ = after(said('The wrapper with an error really pending is not verified.'))
        self.assertIn('A declared gap: "The wrapper with an error really pending is not verified"', message)
        message, asked = after(said('That part is not verified.', 'thinking'), said('It is built.'))
        self.assertEqual((message, [text for text, _ in asked]), (None, ['It is built.']))
        # The judge's verdict blocks; no verdict, a refused call and a passing one do not; nothing said asks nothing.
        failing = {'ok': False, 'quote': 'No library has such errors', 'reason': 'Nothing was searched.'}
        message, _ = after(said('No library has such errors.'), verdict=failing)
        self.assertIn('Unchecked claim: "No library has such errors" Nothing was searched.', message)
        for verdict in (None, {'error': 'refused'}, {'ok': True, 'quote': '', 'reason': ''}):
            self.assertIsNone(after(said('Done.'), verdict=verdict)[0])
        self.assertEqual(after(said('Only a thought.', 'thinking'))[1], [])
        # A proposed loop is the stop's to catch.
        self.assertIsNone(after(said('I will repeat the review until it reports nothing.'))[0])

    def test_a_check_the_branch_turns_off_does_not_run_at_a_commit(self):
        self.transcript.write_text('')
        self.assertIsNone(self.commit())
        root = self.dir / 'clone'
        (root / 'tools' / 'hooks').mkdir(parents=True)
        gap, promise, asked = said('Its plugins are unchecked.'), said('From now on I will fetch first.'), []
        failing = {'ok': False, 'quote': 'q', 'reason': 'r'}

        def after(*lines):
            with self.transcript.open('a') as stream:
                stream.write(''.join(lines))
            return self.commit()
        with unittest.mock.patch.object(hook.stop_checks, 'ROOT', root), \
                unittest.mock.patch.object(hook, 'judge', lambda text, calls: asked.append(text) or failing):
            self.assertIn('A declared gap', after(gap))
            (root / 'tools' / 'hooks' / 'checks_off').write_text('gap\n')
            self.assertIn('promise', after(gap, promise).lower())
            self.assertEqual(asked, [])
            self.assertIn('Unchecked claim', after(gap))
            (root / 'tools' / 'hooks' / 'checks_off').write_text('gap\njudge\nno such check\n')
            self.assertEqual((after(gap), len(asked)), (None, 1))
            self.assertIn('promise', after(promise).lower())

    def theory(self, plan, **given):
        return hook.theory({'session_id': 's', 'tool_input': {'file_path': str(plan), **given}}, self.state)

    def test_a_question_added_to_the_theory_of_a_plan_under_implementation_is_asked_about_once(self):
        plan = self.dir / 'tasks' / 'alpha' / 'PLAN.md'
        plan.parent.mkdir(parents=True)
        resolved = '### Resolved\n\n- **What does it cover?** Decided.\n'
        plan.write_text(f'# alpha\n\n{resolved}\n## Path\n\n- **First.** Text.\n')
        added = {'old_string': '### Resolved\n', 'new_string': '### Resolved\n\n- **How is the\n  record shaped?** A list.\n'}
        # A plan that is not under implementation takes any entry.
        self.assertIsNone(self.theory(plan, **added))
        plan.write_text(f'# alpha\n\n{resolved}\n## Path\n\n**Current increment:** "First".\n\n- **First.** Text.\n')
        message = self.theory(plan, **added)
        self.assertTrue(message.startswith('This adds to the theory of a plan under implementation: "How is the record shaped?".'))
        self.assertIn('do not add it: build it, and say it in the commit message', message)
        # The same edit made again passes; another question is asked about in its turn.
        self.assertIsNone(self.theory(plan, **added))
        self.assertIn('"Which errors fail?"', self.theory(plan, old_string='x', new_string='- **Which errors fail?** Those.'))
        # An entry already there, rewritten or moved, a Path step and other files are no new question.
        for given in ({'old_string': '- **What does it cover?** Decided.', 'new_string': '- **What does it cover?** Decided again.'},
                      {'old_string': 'y', 'new_string': '- **What does it cover?** Moved.'},
                      {'old_string': '- **First.** Text.', 'new_string': '- **First (done).** Text.\n- **Second.** More.'},
                      {'content': plan.read_text()}):
            self.assertIsNone(self.theory(plan, **given), given)
        self.assertIn('"Is it new?"', self.theory(plan, content=plan.read_text() + '- **Is it new?** Yes.\n'))
        other = self.dir / 'tasks' / 'alpha' / 'NOTES.md'
        other.write_text('**Current increment:**')
        self.assertIsNone(self.theory(other, old_string='', new_string='- **Why?** Because.'))
        self.assertIsNone(self.theory(self.dir / 'tasks' / 'beta' / 'PLAN.md', old_string='', new_string='- **Why?** x'))

    def test_the_hook_blocks_with_exit_status_2_and_its_message(self):
        run = lambda mode, data: subprocess.run([sys.executable, str(HOOK), mode], input=json.dumps(data),
                                                capture_output=True, text=True)
        quiet = run('commit', {'session_id': 'none', 'tool_input': {'command': 'ls'}})
        self.assertEqual((quiet.returncode, quiet.stderr), (0, ''))
        self.assertEqual(run('other', {}).returncode, 0)
        self.assertEqual(subprocess.run([sys.executable, str(HOOK), 'commit'], input='not json', capture_output=True,
                                        text=True).returncode, 0)
        plan = self.dir / 'tasks' / 'alpha' / 'PLAN.md'
        plan.parent.mkdir(parents=True)
        plan.write_text('### Resolved\n\n## Path\n\n**Current increment:** x\n')
        session = f'test-during-run-{self.dir.name}'
        self.addCleanup(lambda: (hook.STATE / f'{session}.json').unlink(missing_ok=True))
        asked = run('theory', {'session_id': session, 'tool_input': {
            'file_path': str(plan), 'old_string': '### Resolved\n', 'new_string': '### Resolved\n\n- **Why so?** x\n'}})
        self.assertEqual(asked.returncode, 2)
        self.assertTrue(asked.stderr.startswith('This adds to the theory of a plan under implementation: "Why so?".'))

    def test_the_shell_guard_checks_promises_at_a_commit(self):
        guard = HOOK.with_name('bash_guard.py')
        session = f'test-during-run-{self.dir.name}'
        self.addCleanup(lambda: (hook.STATE / f'{session}.json').unlink(missing_ok=True))
        self.transcript.write_text('')

        def call(command):
            return subprocess.run([sys.executable, str(guard)], capture_output=True, text=True, input=json.dumps({
                'tool_name': 'Bash', 'session_id': session, 'transcript_path': str(self.transcript), 'cwd': str(self.dir),
                'tool_input': {'command': command}}))
        self.assertEqual(call('git commit -qm first').returncode, 0)
        with self.transcript.open('a') as stream:
            stream.write(said('From now on I will time it first.'))
        self.assertEqual(call('git status').returncode, 0)
        blocked = call('git add -A && git commit -qm second')
        self.assertEqual(blocked.returncode, 2)
        self.assertTrue(blocked.stderr.startswith('Before this commit, in what was written since the last one: A promise about future behaviour'), blocked.stderr)
        self.assertEqual(call('git add -A && git commit -qm second').returncode, 0)


if __name__ == '__main__':
    unittest.main()
