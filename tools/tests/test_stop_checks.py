import importlib.util
import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

spec = importlib.util.spec_from_file_location('stop_checks', Path(__file__).resolve().parents[1] / 'hooks/stop_checks.py')
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

REPLY = 'The hook copies the staged files to a temporary directory and checks that copy.'
# The checks that rest on the task protocol are tested where the branch has the task tool they call.
MACHINERY = (Path(__file__).resolve().parents[1] / 'task_index.py').is_file()
needs_machinery = unittest.skipUnless(MACHINERY, 'this branch has no task machinery')


def tasks_with_a_request(root, judged):
    """tasks/ under `root` with task alpha's request 1 to others, waiting for the judge unless `judged`."""
    tasks = root / 'tasks'
    (tasks / 'alpha').mkdir(parents=True)
    (tasks / 'schema.json').write_text((Path(__file__).resolve().parents[2] / 'tasks/schema.json').read_text())
    (tasks / 'index.json').write_text('{"schema_version": 1, "tasks": ["alpha"]}\n')
    (tasks / 'alpha' / 'PLAN.md').write_text('# alpha\n')
    request = {'number': 1, 'title': 'Ask', 'kind': 'required', 'body': '1. x', 'next_part': 1, 'parts': [],
               **({} if judged else {'judged': False})}
    (tasks / 'alpha' / 'task.json').write_text(json.dumps({
        'title': 'Alpha', 'summary': 'S.', 'status': 'in_progress', 'status_note': 'N.', 'tickets': [],
        'relations': {'waits_for': [], 'split_from': None}, 'next_request': 2, 'requests': [request]}))


class UncheckedClaimTest(unittest.TestCase):
    """The hook around a fake `claude` that answers with a fixed verdict."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.transcript = self.dir / 'session.jsonl'
        lines = [{'type': 'user', 'message': {'content': 'earlier prompt'}},
                 {'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': 'Bash', 'input': {'command': 'git help merge'}}]}},
                 {'type': 'user', 'message': {'content': 'fix the hook'}},
                 {'type': 'assistant', 'message': {'content': [
                     {'type': 'tool_use', 'name': 'Read', 'input': {'file_path': 'tools/x.py'}},
                     {'type': 'tool_use', 'name': 'Agent', 'input': {'subagent_type': 'Explore', 'description': 'find callers'}}]}},
                 {'type': 'user', 'message': {'content': [{'type': 'tool_result', 'content': 'ok'}]}},
                 {'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': 'Bash', 'input': {'command': 'git status'}}]}}]
        self.transcript.write_text(''.join(json.dumps(line) + '\n' for line in lines))
        # The task records the gate reads are the fixture's, not this clone's.
        self.root = self.dir / 'clone'
        self.root.mkdir()
        # The fixture is a branch that works under the task protocol, where this branch has its machinery,
        # unless a test removes the file.
        (self.root / hook.PROTOCOL).parent.mkdir(parents=True)
        if MACHINERY:
            (self.root / hook.PROTOCOL).write_text('# protocol\n')
        patcher = mock.patch.object(hook, 'ROOT', self.root)
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        self.tmp.cleanup()

    def fake_claude(self, answer, sleep=0):
        """Put a `claude` on PATH that records its prompt and prints `answer` as its result."""
        script = self.dir / 'claude'
        script.write_text(
            '#!/usr/bin/env python3\nimport json, os, sys, time\n'
            f'open({str(self.dir / "prompt.txt")!r}, "w").write(sys.stdin.read())\n'
            f'open({str(self.dir / "env.txt")!r}, "w").write(os.environ.get({hook.INSIDE_JUDGE!r}, ""))\n'
            f'time.sleep({sleep})\nprint(json.dumps({{"result": {answer!r}}}))\n')
        script.chmod(0o755)
        return mock.patch.dict(os.environ, {'PATH': f"{self.dir}:{os.environ['PATH']}"})

    def run_hook(self, argv=(), **data):
        data = {'hook_event_name': 'Stop', 'stop_hook_active': False, 'transcript_path': str(self.transcript),
                'last_assistant_message': REPLY, **data}
        out = io.StringIO()
        with mock.patch('sys.stdin', io.StringIO(json.dumps(data))), redirect_stdout(out):
            self.assertEqual(hook.main(argv), 0)
        return json.loads(out.getvalue()) if out.getvalue() else None

    def verdict(self, kind='workaround', quote='copies the staged files to a temporary directory', checked=False, declared=False):
        return '```json\n' + json.dumps({'kind': kind, 'quote': quote, 'tool': 'git', 'checked': checked, 'declared': declared,
                                         'reason': 'Check git ls-files and cat-file.'}) + '\n```'

    def test_a_verdict_that_names_no_third_party_tool_does_not_block(self):
        reply = 'It copies the staged files to a temporary directory.'
        answer = {'kind': 'missing-feature', 'quote': reply, 'checked': False, 'declared': False, 'reason': 'r'}
        for tool in ('', '  ', None, 'compute.sh', 'finish-turn.py', '`tools/rewrap_md.py`', 'stop_checks', './compute.sh',
                     'tools/hooks/bash_guard.py', 'lead-queue'):
            with self.subTest(tool=tool):
                self.assertTrue(hook.validate_verdict(reply, {**answer, 'tool': tool})['ok'])
        self.assertTrue(hook.validate_verdict(reply, answer)['ok'])
        for tool in ('git', 'Claude Code', 'compute engine', 'the browser', 'rewrap', 'pytest.py'):
            with self.subTest(tool=tool):
                self.assertFalse(hook.validate_verdict(reply, {**answer, 'tool': tool})['ok'])

    def test_unchecked_workaround_blocks_with_the_quote(self):
        with self.fake_claude(self.verdict()):
            out = self.run_hook()
        self.assertEqual(out['decision'], 'block')
        self.assertIn('"copies the staged files to a temporary directory"', out['reason'])
        self.assertIn('Check git ls-files and cat-file.', out['reason'])

    def test_judge_sees_this_turns_calls_oldest_first_and_the_reply(self):
        with self.fake_claude(self.verdict(kind='other')):
            self.run_hook()
        prompt = (self.dir / 'prompt.txt').read_text()
        self.assertIn('- Read: tools/x.py\n- Agent: Explore: find callers\n- Bash: git status', prompt)
        self.assertNotIn('git help merge', prompt)
        self.assertIn(REPLY, prompt)
        self.assertEqual((self.dir / 'env.txt').read_text(), '1')

    def test_passes_other_kinds_checked_claims_and_invented_quotes(self):
        for answer in (self.verdict(kind='other'), self.verdict(checked=True), self.verdict(declared=True),
                       self.verdict(kind='missing-feature', quote='git has no such option')):
            with self.subTest(answer=answer), self.fake_claude(answer):
                self.assertIsNone(self.run_hook())

    def test_warns_without_blocking_when_the_judge_fails(self):
        for answer, cause in (('not json', "the answer held no JSON object: 'not json'"),
                              (json.dumps({'kind': 'nonsense'}), 'the answer lacked the verdict asked for: {"kind": "nonsense"}')):
            with self.subTest(answer=answer), self.fake_claude(answer):
                out = self.run_hook()
                self.assertNotIn('decision', out)
                self.assertEqual(out['systemMessage'],
                                 f'stop-checks hook: the judge failed ({cause}), so this stop passed unchecked.')
        with tempfile.TemporaryDirectory() as empty, mock.patch.dict(os.environ, {'PATH': empty}):
            self.assertIn('the judge failed (claude could not run: ', self.run_hook()['systemMessage'])
        with self.fake_claude(self.verdict(), 1), mock.patch.object(hook, 'JUDGE_TIMEOUT', 0.3):
            self.assertEqual(self.run_hook()['systemMessage'],
                             'stop-checks hook: the judge failed (no answer within 0.3 s), so this stop passed unchecked.')

    def test_the_judge_s_limit_fits_the_budget_the_settings_give_the_hook(self):
        # A limit at or over the budget has the harness kill the hook before the judge's failure is reported.
        settings = json.loads((Path(__file__).resolve().parents[2] / '.claude/settings.json').read_text())
        budgets = [entry['timeout'] for group in settings['hooks']['Stop'] for entry in group['hooks']
                   if 'stop_checks.py' in entry['command']]
        self.assertEqual(len(budgets), 1)
        self.assertLessEqual(hook.JUDGE_TIMEOUT + 0.5, budgets[0])
        self.assertEqual(hook.JUDGE_TIMEOUT, 9.5)

    def test_warns_without_blocking_when_the_api_refuses_the_model(self):
        script = self.dir / 'claude'
        script.write_text('#!/usr/bin/env python3\nimport json\nprint(json.dumps({"is_error": True, '
                          '"api_error_status": 404, "result": "There\'s an issue with the selected model."}))\n')
        script.chmod(0o755)
        with mock.patch.dict(os.environ, {'PATH': f"{self.dir}:{os.environ['PATH']}"}):
            out = self.run_hook()
        self.assertNotIn('decision', out)
        self.assertIn(f'{hook.MODEL} failed (404: ', out['systemMessage'])
        self.assertIn('every stop passes unchecked', out['systemMessage'])

    def test_never_judges_after_a_block_or_inside_the_judge(self):
        with self.fake_claude(self.verdict()):
            self.assertIsNone(self.run_hook(stop_hook_active=True))
            with mock.patch.dict(os.environ, {hook.INSIDE_JUDGE: '1'}):
                self.assertIsNone(self.run_hook())
        self.assertFalse((self.dir / 'prompt.txt').exists())

    @needs_machinery
    def test_blocks_while_a_request_waits_for_the_judge_without_asking_haiku(self):
        tasks_with_a_request(self.root, judged=False)
        with self.fake_claude(self.verdict()):
            out = self.run_hook()
            self.assertFalse((self.dir / 'prompt.txt').exists())
            self.assertIsNone(self.run_hook(stop_hook_active=True))
            with mock.patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': str(self.dir)}):
                self.assertIn('Unchecked claim', self.run_hook(argv=['--global'])['reason'])
        self.assertEqual(out['decision'], 'block')
        self.assertIn('Requests for others wait for the judge: alpha request 1. Once all', out['reason'])
        self.assertIn('run tools/task_index.py request judge SLUG', out['reason'])

    @needs_machinery
    def test_judged_requests_and_unreadable_records_leave_the_claim_check(self):
        for judged in (True, None):
            with self.subTest(judged=judged):
                shutil.rmtree(self.root / 'tasks', ignore_errors=True)
                if judged is not None:
                    tasks_with_a_request(self.root, judged)
                with self.fake_claude(self.verdict()):
                    self.assertIn('Unchecked claim', self.run_hook()['reason'])

    def add(self, *entries):
        with self.transcript.open('a') as f:
            f.write(''.join(json.dumps(entry) + '\n' for entry in entries))

    def test_a_promise_anywhere_in_the_turn_blocks_without_asking_haiku(self):
        self.add({'type': 'assistant', 'message': {'content': [{'type': 'thinking', 'thinking': (
            'Found the cause. I\'ll switch to exact matches for indented Markdown going forward, and now I\'m '
            'editing request 7.')}]}})
        with self.fake_claude(self.verdict()):
            out = self.run_hook()
            self.assertFalse((self.dir / 'prompt.txt').exists())
            self.assertIsNone(self.run_hook(stop_hook_active=True))
        self.assertEqual(out['decision'], 'block')
        self.assertIn('A promise about future behaviour, or an admission that implies one: "I\'ll switch to exact matches for indented Markdown going '
                      'forward, and now I\'m editing request 7".', out['reason'])
        self.assertIn('only the framework does', out['reason'])

    def test_a_promise_in_the_final_reply_alone_blocks_also_from_the_global_entry(self):
        with self.fake_claude(self.verdict(kind='other')):
            out = self.run_hook(last_assistant_message='Done. From now on I will background the clones.')
            with mock.patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': str(self.dir)}):
                elsewhere = self.run_hook(argv=['--global'], last_assistant_message='Next time I\'ll ask first.')
        self.assertIn('"From now on I will background the clones"', out['reason'])
        self.assertIn('"Next time I\'ll ask first"', elsewhere['reason'])

    def test_promises_from_an_earlier_turn_a_subagent_or_no_promise_pass(self):
        earlier = [{'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': 'I will always check.'}]}}]
        lines = self.transcript.read_text().splitlines(keepends=True)
        self.transcript.write_text(lines[0] + json.dumps(earlier[0]) + '\n' + ''.join(lines[1:]))
        self.add({'type': 'assistant', 'isSidechain': True,
                  'message': {'content': [{'type': 'text', 'text': 'From now on I\'ll report in tables.'}]}},
                 {'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': (
                     "I'll push softeng again. The tool always prepends origin/. Going forward, the guard refuses "
                     "it. I won't wait for it.")}]}})
        with self.fake_claude(self.verdict(kind='other')):
            self.assertIsNone(self.run_hook())

    def test_a_tool_fault_worked_around_blocks_and_one_fixed_in_the_turn_passes(self):
        fault = ('`replace_text` indented the whole replacement to match its first line, which nested the new '
                 'question. Moving it out to Resolved as a top-level entry:')
        self.add({'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': fault}]}})
        with self.fake_claude(self.verdict(kind='other')):
            out = self.run_hook()
            self.assertFalse((self.dir / 'prompt.txt').exists())
            self.add({'type': 'assistant', 'message': {'content': [
                {'type': 'tool_use', 'name': 'Edit', 'input': {'file_path': '/x/tools/tests/test_replace_text.py'}}]}})
            self.assertIsNone(self.run_hook())
        self.assertEqual(out['decision'], 'block')
        self.assertIn('A tool\'s fault, worked around: "`replace_text` indented the whole replacement to match its '
                      'first line, which nested the new question"', out['reason'])
        self.assertIn('fix it with a test in the same turn', out['reason'])

    def test_a_tool_fault_in_the_thinking_alone_blocks(self):
        self.add({'type': 'assistant', 'message': {'content': [{'type': 'thinking', 'thinking': (
            'The `rewrap_md` call nested the item, so I will fix the indentation by hand.')}]}})
        with self.fake_claude(self.verdict(kind='other')):
            out = self.run_hook(last_assistant_message='Done.')
        self.assertIn('"The `rewrap_md` call nested the item, so I will fix the indentation by hand"', out['reason'])

    def test_tool_fault_shapes(self):
        faults = ['But `checked-push.sh` points at the wrong remote for this clone',
                  'Because `lead_queue.py` has no way to change an item\'s text',
                  'I found a bug in rewrap_md.py: it wrapped it so a line misreads as a new list item',
                  'The run of tools/hooks/bash_guard refused it',
                  'The new item came out nested by `replace_text`',
                  'Then the push was refused by checked-push.sh']
        self.assertEqual([tool for _, tool in hook.tool_faults(['. '.join(faults) + '.'])],
                         ['checked-push', 'lead_queue', 'rewrap_md', 'bash_guard', 'replace_text', 'checked-push'])
        self.assertEqual(hook.tool_faults([
            'The branch was merged instead of rebased.',
            'It said "`replace_text` nested it" at the time.',
            'The `replace_text` call replaced the passage at line 15.',
            'The rebase nested nothing; replace_text worked.',
            'Its note:\n> The item came out nested by `replace_text`.']), [])

    def test_a_fenced_block_is_text_handed_over_and_is_not_checked(self):
        # A goal prompt for the user to paste (the real block): its condition names a tool beside "merged".
        prompt = ('Here is the prompt.\n\n```\n/goal Finish it. DONE: (5) business has merged softeng and its suite passes; '
                  '(6) `python3 tools/task_index.py check` passes.\nI will not do this again; the rest is unverified.\n```\n\nNotes follow.')
        self.assertEqual(hook.tool_faults([prompt]), [])
        self.assertEqual(hook.promises([prompt]), [])
        self.assertIsNone(hook.gap_block(prompt))
        # The same words outside a fence are the reply's own, before a fence, after one and with a fence never closed.
        own = 'The new item came out nested by `tools/replace_text.py`.'
        for reply in (own + '\n\n```\necho x\n```\n', '```\necho x\n```\n\n' + own, '```\necho x\n\n' + own):
            self.assertEqual([tool for _, tool in hook.tool_faults([reply])], ['replace_text'], reply)
        self.assertIn('A declared gap', hook.gap_block('```\nls\n```\nThe second cluster is unverified.')['reason'])
        # Two fenced blocks do not hide what stands between them.
        self.assertEqual(len(hook.tool_faults(['```\na\n```\n' + own + '\n```\nb\n```'])), 1)

    def test_a_missing_tool_named_mid_turn_blocks_until_it_is_queued_or_built(self):
        self.add({'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': (
            'No helper exists for hand-written mutants, so I apply each one by hand. Running mutant 1.')}]}})
        # A message the user sends mid-turn is a queued command, not a prompt: the turn goes on.
        self.add({'type': 'attachment', 'attachment': {'type': 'queued_command', 'prompt': 'Did you queue it?'}})
        with self.fake_claude(self.verdict(kind='other')):
            out = self.run_hook(last_assistant_message='All mutants killed.')
            self.assertFalse((self.dir / 'prompt.txt').exists())
            self.add({'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': 'Bash', 'input': {
                'command': 'python3 tools/lead_queue.py add notebook.html --build mutants x "A mutants tool."'}}]}})
            self.assertIsNone(self.run_hook(last_assistant_message='All mutants killed.'))
        self.assertEqual(out['decision'], 'block')
        self.assertIn('A missing tool: "No helper exists for hand-written mutants, so I apply each one by hand"',
                      out['reason'])
        self.assertIn('build the tool, with its test, or queue it', out['reason'])
        self.assertTrue(hook.followed_up([('Write', {'file_path': '/x/noemesis/tools/mutants.py'})]))
        self.assertFalse(hook.followed_up([('Write', {'file_path': '/x/scratchpad/mutants.py'}),
                                           ('Bash', {'command': 'python3 tools/lead_queue.py head notebook.html'})]))

    def test_missing_tool_shapes(self):
        missing = ['No helper exists for hand-written mutants', 'There is no script that can hard-block it',
                   'The tool does not exist yet', 'I verified the resolver with a throwaway script',
                   'That is why I wrote the scratch script', 'Nothing in tools/ does this',
                   'There\'s no utility for that']
        self.assertEqual(hook.sentences(hook.MISSING_TOOL, ['. '.join(missing) + '.']), missing)
        self.assertEqual(hook.sentences(hook.MISSING_TOOL, [
            'I deleted the scratch script.', 'There is no mechanism by which it could change the result.',
            'Callers outside GitLab, such as one-off scripts, stay unseen.', 'It said "no helper exists" then.',
            'The `no tool for` flag is off.']), [])

    @needs_machinery
    def test_a_step_handed_to_others_blocks_also_from_what_the_turn_writes(self):
        message = ('api: remove the syncs\n\nNothing reads SYNC_KEY; whether those two syncs can go\n'
                   'for every instance is left to their\nowners.')
        self.add({'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': 'Bash', 'input': {
            'command': f"git commit -q -F - <<'EOF'\n{message}\nEOF"}}]}})
        with self.fake_claude(self.verdict(kind='other')):
            out = self.run_hook(last_assistant_message='Committed.')
            self.assertFalse((self.dir / 'prompt.txt').exists())
            in_reply = self.run_hook(last_assistant_message='The rest is up to their team. Done.')
        self.assertEqual(out['decision'], 'block')
        self.assertIn('A step handed to others: "Nothing reads SYNC_KEY; whether those two syncs can go for every '
                      'instance is left to their owners"', out['reason'])
        self.assertIn('request add --to-others', out['reason'])
        self.assertIn('A step handed to others: "The rest is up to their team"', in_reply['reason'])

    def test_deferral_shapes(self):
        handed = ['Left to the owners: the sync', 'It is left to their owners', 'We leave it for the team',
                  'That is up to their team', 'It is the owners\' call', 'Deferred to the code owners',
                  'It is not ours to remove', 'This is for the owners to decide']
        self.assertEqual(hook.deferrals(['. '.join(handed) + '.']), handed)
        self.assertEqual(hook.deferrals([
            'The team left the meeting.', 'I handed the review to the user.', 'Owners left it as it was.',
            'It said "left to their owners" then.', 'The draft read:\n> It is left to their owners.']), [])
        # A sentence wrapped over lines is read whole, up to a blank line.
        self.assertEqual(hook.deferrals(['Intro\n\nWhether they\ncan go is left\nto their owners,\nnoted.\n\nNext']),
                         ['Whether they can go is left to their owners, noted'])
        self.assertEqual(hook.written([('Edit', {'file_path': 'a.md', 'new_string': 'x'}),
                                       ('Bash', {'command': 'git log'}), ('Read', {'file_path': 'b.md'})]),
                         ['x', 'git log'])
        # What is written into the checks' own code and tests is a fixture of a check, not said by the turn.
        handed = "HANDED = 'It is left to their owners.'"   # in single quotes, which the quote filter does not blank
        own = ('tools/tests/test_stop_checks.py', '/repo/tools/hooks/stop_checks.py', 'tools/tests/test_during_run.py',
               '/repo/tools/measure_stop_checks.py', 'tools/hooks/during_run.py')
        for path in own:
            with self.subTest(path=path):
                self.assertEqual(hook.written([('Edit', {'file_path': path, 'new_string': handed}),
                                               ('Write', {'file_path': path, 'content': handed})]), [])
                self.assertIsNone(hook.deferral_block([], [('Edit', {'file_path': path, 'new_string': handed})]))
        for path in ('tools/tests/test_lead_queue.py', 'src/tools/hooks.py', 'notes/tools/tests/test_stop_checks.py.md',
                     'tasks/a/PLAN.md', 'mytools/hooks/x.py'):
            with self.subTest(path=path):
                self.assertEqual(hook.written([('Edit', {'file_path': path, 'new_string': handed})]), [handed])
                self.assertIsNotNone(hook.deferral_block([], [('Edit', {'file_path': path, 'new_string': handed})]))
        # A command that writes such a file is still read: only an edit names the file it writes.
        self.assertEqual(len(hook.written([('Bash', {'command': 'cat > tools/tests/test_stop_checks.py <<EOF\nx\nEOF'})])), 1)

    def test_a_gap_declared_in_the_final_reply_asks_for_its_routes(self):
        gap = 'No kubeconfig context reaches it, so its live plugins can\'t be read either. The rest holds.'
        with self.fake_claude(self.verdict(kind='other')):
            out = self.run_hook(last_assistant_message=gap)
            self.assertFalse((self.dir / 'prompt.txt').exists())
            self.assertIsNone(self.run_hook(stop_hook_active=True, last_assistant_message=gap))
            with mock.patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': str(self.dir)}):
                elsewhere = self.run_hook(argv=['--global'], last_assistant_message='Whether it is up is unchecked.')
        self.assertIn('A declared gap: "No kubeconfig context reaches it, so its live plugins can\'t be read either"',
                      out['reason'])
        self.assertIn('cheap, a check of a few minutes, then take it now; expensive, with its cost, left to the user',
                      out['reason'])
        self.assertIn('who owns and changes its configuration: CODEOWNERS, commit history, project members',
                      out['reason'])
        self.assertIn('"Whether it is up is unchecked"', elsewhere['reason'])

    def test_gaps_only_in_the_final_reply_and_outside_quotes_code_and_narration(self):
        self.add({'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': 'That is unverified so far.'}]}})
        for reply in ('The `unchecked-claim` hook ran. I didn\'t check it then, as I said. "Not verified" was its word.',
                      'Every stop would pass unchecked-claim checks.', 'It is checked: the secret is there.'):
            with self.subTest(reply=reply), self.fake_claude(self.verdict(kind='other')):
                self.assertIsNone(self.run_hook(last_assistant_message=reply))
        gaps = ['I haven\'t checked that wl-copy is installed', 'It is outside our access', 'It wasn\'t checked',
                'They weren\'t checked', 'Clones elsewhere: not checked', 'The version hasn\'t been verified',
                'The plugins can\'t be read', 'That is unverified']
        self.assertEqual(hook.sentences(hook.GAP, ['. '.join(gaps) + '.']), gaps)
        self.assertEqual(hook.sentences(hook.GAP, ['The column `unverified` is a boolean; pass `--unchecked`.',
                                                   'The flag is_unverified and the unchecked-claim hook stay.',
                                                   'The judged unchecked claim moved; unchecked claims block.']), [])
        self.assertEqual(hook.sentences(hook.GAP, ['That claim is unchecked.']), ['That claim is unchecked'])
        # A document's sentence quoted as a blockquote is its wording, not the reply's; the reply's own
        # lines around it are still read.
        self.assertEqual(hook.sentences(hook.GAP, ['The letter now says:\n\n> Whether a workload\n'
                                                   '  > reads it is not checked.\n\nThat is unverified.']), ['That is unverified'])

    def test_the_gap_words_used_for_an_outcome_a_description_or_a_past_omission_are_no_gap(self):
        for reply in ('The tool reports such a scenario as unverified and lets you waive it.',
                      'When they differ, report the change and leave the scenario unverified.',
                      'One copy is shown as not checked, the other is flagged as "unchecked".',
                      'It is signed by an unverified signer.', 'It loses unverified chord labels.',
                      'Taking shortcuts when unchecked is a real pattern.',
                      'My last sentence was wrong, and I had not checked it.', 'It hadn\'t been verified then.',
                      'This can\'t verify that a pass was thorough.', 'The hook cannot check what it does not see.',
                      # What a tool prints, and what a proposed check would have a reply say (three real blocks).
                      'Without a names list the tool prints a warning that people\'s names weren\'t checked.',
                      'When the file is missing, it prints that no names list was found and that people\'s names weren\'t '
                      'checked, then carries on; only a name it finds fails the run.',
                      'The turn cannot end until my reply tells you names went unchecked and how to create the file.',
                      'So the names check goes unchecked on every run.', 'The tool warned that the ledger was not checked.',
                      # A gap denied (a fourth real block).
                      'It is a proposal for a change, not something unverified: the choice is yours.',
                      'Nothing in them was unverified.', 'None of the rows is unchecked.'):
            with self.subTest(reply=reply):
                self.assertIsNone(hook.gap_block(reply))
        # A gap beside such a use, and the same words about the reply's own claims, still block.
        for reply, quoted in (('The tool reports it as unverified. I haven\'t checked the second cluster.',
                               'I haven\'t checked the second cluster'),
                              ('It leaves the scenario unverified, and the rest is unverified too.',
                               'It leaves the scenario unverified, and the rest is unverified too'),
                              ('Whether to review the unchecked parts is open.', 'Whether to review the unchecked parts is open'),
                              ('I can\'t verify it from inside the session.', 'I can\'t verify it from inside the session'),
                              ('We reported it, but it is not checked.', 'We reported it, but it is not checked'),
                              ('I should tell you the second cluster wasn\'t checked.', 'I should tell you the second cluster wasn\'t checked'),
                              ('Not every claim holds: the store\'s size in the last two regions is unverified.',
                               'Not every claim holds: the store\'s size in the last two regions is unverified'),
                              ('The tool prints its table. The staging values weren\'t checked.', 'The staging values weren\'t checked'),
                              ('That leaves the claim about the store unverified.', 'That leaves the claim about the store unverified')):
            with self.subTest(reply=reply):
                self.assertIn(f'A declared gap: "{quoted}"', hook.gap_block(reply)['reason'])

    @needs_machinery
    def test_a_proposed_loop_without_a_goal_prompt_blocks(self):
        loop = 'Yes: run review rounds until one comes back clean. It costs a few reviewer runs.'
        with self.fake_claude(self.verdict(kind='other')):
            out = self.run_hook(last_assistant_message=loop)
            self.assertFalse((self.dir / 'prompt.txt').exists())
            with_prompt = self.run_hook(last_assistant_message=loop + '\n\n```\n/goal the review is clean\n```')
            for reply in ('The second round found eleven defects.', 'Wait until the build ends.',
                          'Round 4\'s reviewer is reading; I make no edits until it reports.',
                          'The word "loop until done" was theirs.', 'Pass `--loop` until it settles.'):
                with self.subTest(reply=reply):
                    self.assertIsNone(self.run_hook(last_assistant_message=reply))
        self.assertIn('A loop with no /goal prompt: "Yes: run review rounds until one comes back clean"', out['reason'])
        self.assertIn('every way out inside the goal\'s condition', out['reason'])
        self.assertIsNone(with_prompt)
        self.assertEqual(hook.sentences(hook.LOOP, ['Until the audit is clean, repeat the pass. Iterate until stable.']),
                         ['Until the audit is clean, repeat the pass', 'Iterate until stable'])

    def test_a_quoted_promise_promises_nothing(self):
        self.assertEqual(hook.promises(['1. **"From here on I\'ll write links as Markdown"** (1 October).',
                                        'You said “next time I\'ll ask”; it held.',
                                        'Your rule:\n> From now on I\'ll mark them done first.']), [])
        self.assertEqual(hook.promises(['From now on I\'ll mark them "done" first.']),
                         ['From now on I\'ll mark them "done" first'])

    def test_an_admitted_mistake_blocks_until_the_reply_says_how_the_class_is_prevented(self):
        admitted = 'It copied everything, and I never measured it on this repository. It is fixed.'
        with self.fake_claude(self.verdict()):
            out = self.run_hook(last_assistant_message=admitted)
            self.assertFalse((self.dir / 'prompt.txt').exists())
        self.assertEqual(out['decision'], 'block')
        self.assertIn('A mistake admitted with no prevention: "It copied everything, and I never measured it on this '
                      'repository". The user must not have to ask how it is prevented.', out['reason'])
        self.assertIn('A fix of the one instance is not a prevention.', out['reason'])
        for told in (admitted + '\n\n**Prevention.** A tool that copies now prints what it copies.',
                     admitted + '\n\n## Prevention\n\nA test fails on a whole-tree copy.', 'It is fixed.'):
            with self.subTest(told=told), self.fake_claude(self.verdict()):
                self.assertIsNone(self.run_hook(last_assistant_message=told))
        for text in ('That was my mistake.', 'My own error: the path.', 'I was wrong about the runner.', 'I got that wrong.',
                     'I missed the ignored files.', 'I put it badly.', 'Yes, it was avoidable.', 'I misjudged the cost.'):
            with self.subTest(text=text):
                self.assertEqual(hook.sentences(hook.MISTAKE, [text]), [text.rstrip('.')])
        # A gap declared, another's mistake, a quoted admission and a mention of prevention mid-sentence are none.
        self.assertEqual(hook.sentences(hook.MISTAKE, [
            "I didn't run it. The mistake was the tool's. You were wrong there. He said \"my mistake\"."]), [])
        self.assertIsNotNone(hook.mistake_block(['That was my mistake.'], 'That was my mistake. Its prevention is unknown.'))

    def test_promise_shapes(self):
        for text in ("From here on I'll write links as Markdown.", "I won't let that happen again.",
                     "Henceforth I am going to rerun it.", "I will never again trim the output.",
                     "In future sessions I shall load it first.",
                     "My earlier runs ran outside `./compute.sh`; from the suite on, runs went through it.",
                     "From now on, every commit stays local.",
                     "No trailer on any commits from here on.",
                     "The rule I'm following now: never batch a commit with the edit it depends on.",
                     "The time was in every output, and I should have measured it before the commit.",
                     "I shouldn't have run the whole suite to check one function.",
                     "I ought to have ported the runner's design at the start."):
            with self.subTest(text=text):
                self.assertEqual(hook.promises([text]), [text.rstrip('.')])
        self.assertEqual(hook.promises(['Runs went through it from this commit on\nThe rest followed.']),
                         ['Runs went through it from this commit on'])
        self.assertEqual(hook.promises(['I check it.\nNext time it runs alone.', 'Again, I\'ll do it.',
                                        'I checked it every time, as I always do.',
                                        'DNS, from this machine on the VPN, resolves.',
                                        'The pod is recreated from the chart on the next retry.',
                                        "That's the scope rule I'm supposed to follow, and I didn't.",
                                        "I'm now following the API server's logs live.",
                                        'The catcher misses "I should have checked" as a phrase.',
                                        "The tool should have refused it, and you should have been told."]), [])

    LOOP = 'Yes: run review rounds until one comes back clean. It costs a few reviewer runs.'
    HANDED = 'The cleanup of the old volumes is left to their owners.'
    GAP = 'No kubeconfig context reaches it, so its live plugins can\'t be read either. The rest holds.'
    PROMISE = 'From now on I will fetch before reading a branch.'

    @needs_machinery
    def test_on_a_branch_without_the_task_protocol_its_three_checks_do_not_run(self):
        with self.fake_claude(self.verdict(kind='other')):
            for reply, reason in ((self.LOOP, '/goal'), (self.HANDED, 'left to their owners')):
                self.assertIn(reason, self.run_hook(last_assistant_message=reply)['reason'])
            tasks_with_a_request(self.root, judged=False)
            self.assertIn('Requests for others wait', self.run_hook()['reason'])
            (self.root / hook.PROTOCOL).unlink()
            # The branch has no task tool either: the hook must not reach for it.
            with mock.patch.dict('sys.modules', {'task_index': None}):
                for reply in (REPLY, self.LOOP, self.HANDED):
                    self.assertIsNone(self.run_hook(last_assistant_message=reply))
                # The checks that rest on no protocol still run there.
                self.assertEqual(self.run_hook(last_assistant_message=self.PROMISE)['decision'], 'block')

    def off(self, *names):
        path = self.root / hook.CHECKS_OFF
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(''.join(name + '\n' for name in names))

    def test_a_check_named_in_the_branch_s_checks_off_does_not_run(self):
        with self.fake_claude(self.verdict()):
            # No file: the gap blocks, and a reply that passes the patterns reaches the judge.
            self.assertIn('A declared gap', self.run_hook(last_assistant_message=self.GAP)['reason'])
            self.assertIn('Unchecked claim', self.run_hook()['reason'])
            self.off('gap')
            self.assertIn('Unchecked claim', self.run_hook(last_assistant_message=self.GAP + ' ' + REPLY)['reason'])
            self.assertIn('promise', self.run_hook(last_assistant_message=self.GAP + ' ' + self.PROMISE)['reason'].lower())
            (self.dir / 'prompt.txt').unlink()
            self.off('gap', 'judge')
            self.assertIsNone(self.run_hook(last_assistant_message=self.GAP))
            self.assertIsNone(self.run_hook())
            self.assertFalse((self.dir / 'prompt.txt').exists())
            # A name of two words is one name; a line that names no check changes nothing.
            missing = 'There is no tool that lists the stale rows, so I listed them by hand.'
            self.off('judge')
            blocked = self.run_hook(last_assistant_message=missing)
            self.off('judge', 'missing tool')
            self.assertEqual((blocked['decision'], self.run_hook(last_assistant_message=missing)), ('block', None))
            self.off('judge', 'missing', 'tool', 'gaps', 'everything')
            self.assertEqual(self.run_hook(last_assistant_message=missing)['decision'], 'block')
            self.assertIn('A declared gap', self.run_hook(last_assistant_message=self.GAP)['reason'])

    def test_each_check_can_be_named_and_only_the_reader_opens_the_file(self):
        self.assertEqual(hook.CHECK_NAMES, ('promise', 'mistake', 'workaround', 'missing tool', 'deferral', 'gap', 'loop', 'judge',
                                            'review'))
        self.off(*hook.CHECK_NAMES)
        self.assertEqual(hook.checks_off(self.root), frozenset(hook.CHECK_NAMES))
        with self.fake_claude(self.verdict()):
            if MACHINERY:
                (self.root / hook.PROTOCOL).write_text('# protocol\n')
            mistake = 'That was my mistake: I read the wrong file.'
            for reply in (self.PROMISE, mistake, self.GAP, self.LOOP, self.HANDED, REPLY):
                self.assertIsNone(self.run_hook(last_assistant_message=reply))
        hooks = Path(hook.__file__).parent
        naming = sorted(path.name for path in hooks.glob('*.py') if 'checks_off' in path.read_text())
        self.assertEqual(naming, ['codex_stop_checks.py', 'during_run.py', 'stop_checks.py'])
        for name in ('codex_stop_checks.py', 'during_run.py'):
            self.assertNotIn('CHECKS_OFF', (hooks / name).read_text())
        # This branch's own file, where it has one, names only checks.
        own = hooks / 'checks_off'
        if own.is_file():
            self.assertLessEqual({line.strip() for line in own.read_text().splitlines()}, set(hook.CHECK_NAMES))

    def test_global_entry_leaves_this_clone_to_the_project_entry(self):
        with self.fake_claude(self.verdict()):
            with mock.patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': str(hook.ROOT)}):
                self.assertIsNone(self.run_hook(argv=['--global']))
                self.assertEqual(self.run_hook()['decision'], 'block')
            with mock.patch.dict(os.environ, {'CLAUDE_PROJECT_DIR': str(self.dir)}):
                self.assertEqual(self.run_hook(argv=['--global'])['decision'], 'block')


if __name__ == '__main__':
    unittest.main()
