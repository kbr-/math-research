"""The Stop hook's Meta checks, ported with the hook's code from another branch's tests of the same hook
(16 October 2026): an admitted mistake and a reviewer's report need the Prevention and the Meta paragraphs, and
each such paragraph names a file the turn changed."""
import importlib.util
import json
import os
import subprocess
from pathlib import Path

_spec = importlib.util.spec_from_file_location('test_stop_checks_base', Path(__file__).with_name('test_stop_checks.py'))
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)
hook = _base.hook
HookFixture = _base.HookFixture


class ReviewerMetaTest(HookFixture):
    def setUp(self):
        super().setUp()
        agents = self.dir / 'session' / 'subagents'
        agents.mkdir(parents=True)
        (agents / 'agent-r1.meta.json').write_text(json.dumps({'agentType': 'medium-reviewer'}))
        (agents / 'agent-e1.meta.json').write_text(json.dumps({'agentType': 'Explore'}))

    def report(self, agent='r1', attached=False):
        origin = {'kind': 'peer', 'from': agent, 'handback': True, 'body': 'Finding 1, should-fix: ...'}
        if attached:
            self.add({'type': 'attachment', 'attachment': {'type': 'queued_command', 'origin': origin}})
        else:
            self.add({'type': 'user', 'isMeta': True, 'origin': origin, 'message': {'content': 'report'}})

    def said(self, text):
        self.add({'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': text}]}})

    def block(self, reply='Fixed both findings.'):
        return hook.reviewer_meta_block(str(self.transcript), reply)

    def test_a_reviewer_s_report_needs_the_prevention_and_meta_paragraphs_after_it(self):
        self.said('Prevention: an earlier one.\n\nMeta: an answer to something earlier.')
        self.report()
        reason = self.block()['reason']
        self.assertIn('A reviewer reported (agent r1): answer it, once for the report, with a paragraph that starts '
                      '"Prevention"', reason)
        self.assertIn('Then a paragraph that starts "Meta"', reason)
        # Either paragraph alone still blocks: a Meta paragraph holding the prevention is the case this guards.
        self.assertIsNotNone(self.block('Fixed.\n\nMeta: the signal was the warning; the check now refuses.'))
        self.assertIsNotNone(self.block('Fixed.\n\nPrevention: the check now refuses.'))
        self.assertIsNone(self.block('Fixed.\n\nPrevention: the check now refuses.\n\nMeta: the warning was there.'))
        self.said('**Prevention.** It found none of mine.\n\n**Meta.** The brief now asks; nothing was missed.')
        self.assertIsNone(self.block())

    def test_a_second_report_needs_paragraphs_of_its_own(self):
        self.report()
        self.said('Prevention: none of mine.\n\nMeta: the first report\'s finding was in the diff I had read.')
        self.assertIsNone(self.block())
        self.report()
        self.assertIsNotNone(self.block())

    def test_a_report_on_a_transcript_s_first_line_counts(self):
        self.transcript.write_text('')
        self.report()
        self.assertIsNotNone(self.block())

    def test_a_report_attached_mid_turn_counts_and_another_agent_s_does_not(self):
        self.report(agent='e1')
        self.assertIsNone(self.block())
        self.report(attached=True)
        self.assertIsNotNone(self.block())

    def test_the_user_s_next_message_starts_a_new_turn(self):
        self.report()
        self.add({'type': 'user', 'message': {'content': 'next question'}})
        self.assertIsNone(self.block())

    def test_the_hook_blocks_a_stop_after_a_report(self):
        self.report()
        with self.fake_claude(self.verdict(kind='none')):
            out = self.run_hook(last_assistant_message='Both findings are fixed.')
        self.assertEqual(out['decision'], 'block')
        self.assertIn('A reviewer reported (agent r1)', out['reason'])



class MetaHomeTest(HookFixture):
    def test_a_meta_paragraph_names_a_file_the_turn_wrote(self):
        edit = ('Edit', {'file_path': '/repo/research/notes/WORK_RULES.md'})
        queue = ('Bash', {'command': 'python3 tools/lead_queue.py add notebook.html --build x "s" "t"'})
        # The case of 15 October 2026: a change named in prose, held by no file.
        unhomed = ('Fixed.\n\n**Meta.** The change: search the protocol for the same shape first; the Stop hook '
                   'would enforce it.\n\nNext paragraph.')
        blocked = hook.meta_home_block(unhomed, [edit, queue], ['notebook.html'])
        self.assertIn('A Meta paragraph with no home: "**Meta.** The change: search the protocol', blocked['reason'])
        self.assertNotIn('Next paragraph', blocked['reason'])
        # A file it names but the turn didn't write, and a Meta paragraph after a homed one.
        self.assertIsNotNone(hook.meta_home_block('Meta: now in `tools/hooks/bash_guard.py`.', [edit, queue], []))
        self.assertIsNotNone(hook.meta_home_block('Meta: in `WORK_RULES.md`.\n\nMeta: and the skill.', [edit], []))
        skill = ['skills/engineering-discipline/SKILL.md']
        for reply, calls, changed in (
                ('Meta: the Loops section of `research/notes/WORK_RULES.md` now says so.', [edit], []),
                ('**Meta.** A file name alone: WORK_RULES.md, its Loops section.', [edit], []),
                ('Meta: queued in notebook.html.', [queue], ['notebook.html']),
                # The replay's case: the file named without its extension, and a skill's directory.
                ('Meta: the list has an item ("MR_REVIEW_FAILURE_MODES: a claim ...").',
                 [('Edit', {'file_path': '/r/research/notes/MR_REVIEW_FAILURE_MODES.md'})], []),
                ('Meta: a lesson in the engineering-discipline skill.', [], skill),
                ('Meta: skills/engineering-discipline/SKILL.md says so.', [], skill),
                ('No paragraph of that kind.', [], [])):
            with self.subTest(reply=reply):
                self.assertIsNone(hook.meta_home_block(reply, calls, changed))
        # The case of 16 October 2026: a command's text quoting the skill's path, the skill itself unchanged.
        quoting = ('Bash', {'command': 'python3 tools/lead_queue.py edit notebook.html x "add to '
                                       'skills/engineering-discipline/SKILL.md the rule"'})
        for reply in ('Meta: that rule belongs in `skills/engineering-discipline/SKILL.md`.',
                      'Prevention: `tools/lead_queue.py close` already asks it.'):
            with self.subTest(reply=reply):
                self.assertIsNotNone(hook.meta_home_block(reply, [quoting], ['notebook.html']))
        # A record is no home, written by an edit or by a command: on 15 October 2026 a review round's Meta was kept
        # in a review file that nothing reads. Archived results and provenance are none either.
        review = ('Edit', {'file_path': '/r/research/results/review-round/PATH_REVIEW.md'})
        plan = 'research/provenance/review-round/PLAN.md'
        result = ('Write', {'file_path': '/r/research/results/framework-checks/out.txt'})
        for reply, calls, changed in (('Meta: recorded as round 10\'s Meta in PATH_REVIEW.md.', [review], []),
                                      ('Meta: in `research/results/review-round/PATH_REVIEW.md`.', [review], []),
                                      ('Meta: the plan, research/provenance/review-round/PLAN.md, says so.', [], [plan]),
                                      ('Meta: kept in research/results/framework-checks/out.txt.', [result], [])):
            with self.subTest(reply=reply):
                self.assertIsNotNone(hook.meta_home_block(reply, calls, changed))
        # Beside a record, a rule file the same turn changed still counts; a tool it only ran doesn't.
        self.assertIsNone(hook.meta_home_block('Meta: research/notes/WORK_RULES.md now says so.', [review, edit], []))
        ran = ('Bash', {'command': 'python3 tools/rewrap_md.py research/provenance/review-round/PLAN.md --changed'})
        self.assertIsNotNone(hook.meta_home_block('Meta: tools/rewrap_md.py now does it.', [ran], [plan]))
        self.assertIsNone(hook.meta_home_block('Meta: tools/rewrap_md.py now does it.', [ran], ['tools/rewrap_md.py']))
        # A paragraph runs on through the prose that resumes after its list: on 16 October 2026 a Meta naming its
        # home after a list of where its habit shows was read as ending at the list.
        skill_edit = ('Edit', {'file_path': '/r/skills/engineering-discipline/SKILL.md'})
        for reply in ('**Meta.** The habit shows in:\n- plans;\n- guards.\n\nThe change is in `skills/engineering-'
                      'discipline/SKILL.md`.',
                      '**Meta.** The habit shows in:\n\n- plans;\n  still plans.\n\nNow in the engineering-discipline '
                      'skill.',
                      '**Prevention.** Where it shows:\n\n1. plans\n\n2. guards\n\nThe skill, skills/engineering-'
                      'discipline/SKILL.md, says so.'):
            with self.subTest(reply=reply):
                self.assertIsNone(hook.meta_home_block(reply, [skill_edit], []))
        # It stops at a heading or a labelled paragraph, at prose with no list before it, and at the second prose
        # block after one, so a home the reply names elsewhere is not borrowed.
        for reply in ('**Meta.** The habit shows in:\n- plans.\n\n**Committed.** skills/engineering-discipline/'
                      'SKILL.md and the rest.',
                      '**Meta.** The habit shows in:\n- plans.\n\nCommitted locally: skills/engineering-discipline/'
                      'SKILL.md.',
                      '**Meta.** The habit shows in:\n- plans.\n\n## Changed\n\nskills/engineering-discipline/SKILL.md',
                      '**Meta.** No list here.\n\nThe skill, skills/engineering-discipline/SKILL.md, was changed.',
                      '**Meta.** The habit shows in:\n- plans.\n\nIt shows elsewhere too.\n\nskills/engineering-'
                      'discipline/SKILL.md changed.',
                      '**Meta.** The habit shows in:\n- plans.'):
            with self.subTest(reply=reply):
                self.assertIsNotNone(hook.meta_home_block(reply, [skill_edit], []))
        # A bold phrase that only starts with the word labels nothing: on 16 October 2026 a list item
        # "**Prevention paragraphs** go through the same reader" was read as a Prevention.
        for text in ('- **Prevention paragraphs** go through the same reader.', '**Meta data** is kept.',
                     '*Metadata* is kept.', 'Metadata is kept.'):
            with self.subTest(text=text):
                self.assertIsNone(hook.meta_home_block(text, [], []))
                self.assertIsNone(hook.PREVENTION.search(text) or hook.META.search(text))
        # Each form of the label alone still is one, and its paragraph still needs its home.
        for text in ('**Prevention.** None built.', '- **Prevention:** none built.', '*Prevention.* None built.',
                     '__Prevention__: none built.', '_Prevention_ none built.', 'Prevention: none built.',
                     '> Prevention. None built.', '**Prevention** none built.', '## Prevention\n\nNone built.'):
            with self.subTest(text=text):
                self.assertIsNotNone(hook.PREVENTION.search(text))
                self.assertIsNotNone(hook.meta_home_block(text, [], []))
                meta = text.replace('Prevention', 'Meta')
                self.assertIsNotNone(hook.META.search(meta))
                self.assertIsNotNone(hook.meta_home_block(meta, [], []))
        # A Prevention paragraph needs a home as a Meta does: until 15 October 2026 only its presence was required.
        hook_edit = ('Edit', {'file_path': '/r/tools/hooks/stop_checks.py'})
        blocked = hook.meta_home_block('**Prevention.** None built; I will be careful.', [hook_edit], [])
        self.assertIn('A Prevention paragraph with no home: "**Prevention.** None built', blocked['reason'])
        self.assertIsNotNone(hook.meta_home_block('Prevention: kept in research/results/a/REVIEW.md.', [review], []))
        self.assertIsNone(hook.meta_home_block('Prevention: tools/hooks/stop_checks.py now refuses it.', [hook_edit], []))
        # One that reports no mistake of the agent's needs none, and is the only kind that does.
        for reply in ('Prevention: the reviewer found no mistake of mine.', 'Prevention. None of mine: the defects were '
                      'in the library.'):
            with self.subTest(reply=reply):
                self.assertIsNone(hook.meta_home_block(reply, [], []))
        self.assertIsNotNone(hook.meta_home_block('Prevention: a mistake of mine, fixed by hand.', [], []))
        # A plain word that is a changed file's name is no home: "notebook" names nothing distinctive.
        self.assertIsNotNone(hook.meta_home_block('Meta: the notebook says so.', [queue], ['notebook.html']))
        # Only a file the turn changed counts: a Read or a Monitor of it changes nothing.
        for call in (('Read', {'file_path': '/r/notebook.html'}), ('Monitor', {'command': 'tail -f notebook.html'})):
            with self.subTest(call=call):
                self.assertIsNotNone(hook.meta_home_block('Meta: in notebook.html.', [call], []))

    def test_changed_files_are_uncommitted_and_committed_since_the_prompt_in_each_submodule(self):
        def git(where, *args):
            subprocess.run(['git', '-C', str(where), '-c', 'user.name=t', '-c', 'user.email=t@t', *args],
                           check=True, capture_output=True, env={**os.environ, 'GIT_COMMITTER_DATE': date,
                                                                  'GIT_AUTHOR_DATE': date})
        root = self.dir / 'repo'
        sub = root / 'skills' / 'one'
        sub.mkdir(parents=True)
        for where in (root, sub):
            subprocess.run(['git', 'init', '-q', str(where)], check=True)
        (root / '.gitmodules').write_text('[submodule "skills/one"]\n\tpath = skills/one\n')
        for date, (where, name) in zip(('2026-10-16T09:00:00Z', '2026-10-16T09:00:00Z', '2026-10-16T11:00:00Z',
                                         '2026-10-16T11:00:00Z'),
                                        ((root, 'old.md'), (sub, 'OLD.md'), (root, 'new.md'), (sub, 'SKILL.md'))):
            (where / name).write_text('x')
            git(where, 'add', name)
            git(where, 'commit', '-qm', name)
        (root / 'old.md').write_text('edited')
        # Uncommitted (an edit; the fixture's untracked .gitmodules too), and committed after the prompt, in the
        # repository and in a submodule; a commit before the prompt is not.
        found = hook.changed_files(root, '2026-10-16T10:00:00Z')
        self.assertLessEqual({'new.md', 'old.md', 'skills/one/SKILL.md', '.gitmodules'}, set(found))
        self.assertNotIn('skills/one/OLD.md', found)
        without_time = hook.changed_files(root, None)
        self.assertIn('old.md', without_time)
        self.assertNotIn('new.md', without_time)
        # The turn starts at the transcript's last prompt, not at a tool result after it.
        self.add({'type': 'user', 'timestamp': '2026-10-16T10:00:00Z', 'message': {'content': 'go on'}},
                 {'type': 'user', 'timestamp': '2026-10-16T10:05:00Z',
                  'message': {'content': [{'type': 'tool_result', 'content': 'ok'}]}})
        self.assertEqual(hook.turn_start(self.transcript), '2026-10-16T10:00:00Z')



FIXTURES = Path(__file__).resolve().parents[2] / 'research/results'


def fixture_report(name, marker, end):
    """The premature report quoted in a recorded fixture: the lines after `marker` up to `end`."""
    text = (FIXTURES / name / 'report-fixture.txt').read_text()
    return text.split(marker, 1)[1].split(end, 1)[0].strip()


class UnreviewedLabelTest(HookFixture):
    """A reply reporting mathematics while the cycle's mathematics is unreviewed carries the Unreviewed label."""

    def setUp(self):
        super().setUp()
        agents = self.dir / 'session' / 'subagents'
        agents.mkdir(parents=True)
        (agents / 'agent-r1.meta.json').write_text(json.dumps({'agentType': 'medium-reviewer'}))
        self.logs = self.root / 'research/logs'
        self.logs.mkdir(parents=True)

    def session(self, *phases, stopped=False, start=1000.0):
        events = [{'event': 'start', 'unix_s': start, 'agent': 'claude'}] + [{'event': 'phase', 'category': p}
                                                                             for p in phases]
        events += [{'event': 'stop'}] if stopped else []
        (self.logs / 'cycle.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in events))

    def returned(self, when):
        origin = {'kind': 'peer', 'from': 'r1', 'handback': True, 'body': 'pass'}
        self.add({'type': 'user', 'isMeta': True, 'origin': origin, 'timestamp': when, 'message': {'content': 'r'}})

    def block(self, reply):
        return hook.unreviewed_block(str(self.transcript), reply, self.root)

    def test_the_recorded_premature_reports_are_flagged(self):
        self.session('reading', 'mathematics')
        first = fixture_report('binary_star_conditional_rank_20261013', 'Premature assistant commentary:',
                               'Following correction:')
        second = fixture_report('binary_star_cell_images_20261013', 'Native pre-review progress message in this cycle:',
                                'At that message:')
        for reply in (first, second):
            with self.subTest(reply=reply[:40]):
                self.assertIn('Unreviewed', self.block(reply)['reason'])

    def test_the_label_or_a_returned_review_lets_it_through(self):
        self.session('mathematics')
        reply = 'The rank of the weighted kernel is nonzero, so the bound holds for every source.'
        self.assertIsNotNone(self.block(reply))
        self.assertIsNone(self.block('**Unreviewed:** ' + reply))
        self.returned('1970-01-01T00:10:00Z')          # 600 s: before the session started at 1000 s
        self.assertIsNotNone(self.block(reply))
        self.returned('1970-01-01T00:20:00Z')          # 1200 s: after it
        self.assertIsNone(self.block(reply))

    def test_no_open_mathematics_session_or_no_mathematics_passes(self):
        reply = 'The rank of the weighted kernel is nonzero, so the bound holds for every source.'
        self.session('coding')
        self.assertIsNone(self.block(reply))
        self.session('mathematics', stopped=True)
        self.assertIsNone(self.block(reply))
        self.session('mathematics')
        self.assertIsNone(self.block('The suite passes: 1115 tests in 8.1 s.'))

    def test_math_words_pass_outside_a_mathematics_session_and_block_inside_one(self):
        framework = 'The hook proves nothing new; its span check implies the bounds the finisher already reads.'
        self.session('coding')
        self.assertIsNone(self.block(framework))
        self.session('coding', 'mathematics')
        self.assertIsNotNone(self.block(framework))       # a stated limit: the words decide

    def test_a_bullet_of_a_list_is_read_on_its_own(self):
        self.session('mathematics')
        reply = 'Two results:\n- the suite passes\n- the rank of the kernel is nonzero'
        self.assertIn('rank of the kernel', self.block(reply)['reason'])

    def test_newer_journals_that_are_not_sessions_do_not_hide_the_open_one(self):
        self.session('mathematics')
        for n in range(6):
            (self.logs / f'cli_test_{n}.jsonl').write_text(json.dumps({'event': 'start', 'unix_s': 5}) + '\n')
            (self.logs / f'hook-notices-{n}.jsonl').write_text(json.dumps({'note': 'x'}) + '\n')
        self.assertEqual(hook.unreviewed_cycle(self.root), 1000.0)

    def test_an_older_session_left_open_does_not_count_after_a_newer_one_stopped(self):
        events = [{'event': 'start', 'unix_s': 10.0, 'agent': 'claude'}, {'event': 'phase', 'category': 'mathematics'}]
        old = self.logs / 'abandoned.jsonl'
        old.write_text(''.join(json.dumps(e) + '\n' for e in events))
        os.utime(old, (1, 1))
        self.session('coding', stopped=True)
        self.assertIsNone(hook.unreviewed_cycle(self.root))
        self.assertIsNone(self.block('The rank of the weighted kernel is nonzero.'))

    def test_only_a_reviewer_s_report_clears_it(self):
        self.session('mathematics')
        agents = self.dir / 'session' / 'subagents'
        (agents / 'agent-e1.meta.json').write_text(json.dumps({'agentType': 'Explore'}))
        origin = {'kind': 'peer', 'from': 'e1', 'handback': True, 'body': 'found'}
        self.add({'type': 'user', 'isMeta': True, 'origin': origin, 'timestamp': '1970-01-01T00:20:00Z',
                  'message': {'content': 'e'}})
        self.assertIsNotNone(self.block('The rank of the weighted kernel is nonzero.'))

    def test_the_hook_runs_the_check(self):
        self.session('mathematics')
        decision = self.run_hook(last_assistant_message='The rank of the weighted kernel is nonzero.')
        self.assertIn('Unreviewed', decision['reason'])
